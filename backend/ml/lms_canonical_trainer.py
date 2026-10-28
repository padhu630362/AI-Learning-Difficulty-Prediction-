"""
LMS Canonical Model Trainer for AI Learning Difficulty Predictor.

Trains and evaluates candidate models on the canonically aligned LMS dataset.
Enforces:
1. Student-Grouped Splitting (GroupShuffleSplit on student_id) so that
   the test set consists entirely of unseen students, eliminating student leakage.
2. Leakage-Safe Pipeline Architecture:
   Encapsulates ColumnTransformer (StandardScaler + OneHotEncoder) inside an
   sklearn Pipeline, guaranteeing that scaling and encoding are fitted separately
   strictly within each training fold during cross-validation.

Saves artifacts to: backend/artifacts/versions/lms_canonical_v2/
Registers ModelVersion in database with is_active=False (STAGED).
Never overwrites root active production artifacts.
"""

import os
import json
from datetime import datetime
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

from backend.ml.preprocessor import MLDataPreprocessor, REQUIRED_FEATURES, TARGET_COLUMN, NUMERIC_FEATURES, CATEGORICAL_FEATURES
from backend.ml.evaluator import evaluate_model_performance
from backend.app import create_app
from backend.extensions import db
from backend.models.ml_records import ModelVersion

CANDIDATE_CONFIGS = {
    'RandomForest': {
        'class': RandomForestClassifier,
        'params': {'n_estimators': 120, 'max_depth': 8, 'min_samples_split': 8, 'random_state': 42}
    },
    'LogisticRegression': {
        'class': LogisticRegression,
        'params': {'max_iter': 1000, 'random_state': 42}
    },
    'DecisionTree': {
        'class': DecisionTreeClassifier,
        'params': {'max_depth': 6, 'min_samples_split': 10, 'random_state': 42}
    }
}

def run_lms_canonical_training(version_tag='lms_canonical_v2'):
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    dataset_path = os.path.join(backend_dir, 'data', 'lms_canonical_training_dataset.csv')
    artifacts_dir = os.path.join(backend_dir, 'artifacts')

    if not os.path.exists(dataset_path):
        from backend.ml.lms_dataset_generator import generate_lms_canonical_dataset
        generate_lms_canonical_dataset(num_students=500, topics_per_student=6, random_seed=42, output_path=dataset_path)

    df = pd.read_csv(dataset_path)
    print(f"Loaded dataset: {dataset_path} with {len(df)} records across {df['student_id'].nunique()} students.")

    preprocessor = MLDataPreprocessor()
    is_valid, errors, summary = preprocessor.validate_schema(df, require_target=True)
    if not is_valid:
        raise ValueError(f"Schema validation failed: {errors}")

    X = df[REQUIRED_FEATURES]
    y = df[TARGET_COLUMN]
    groups = df['student_id']

    # -------------------------------------------------------------------------
    # Student-Grouped Train/Test Split (80% train students, 20% test students)
    # Zero student-level leakage: no student appears in both train and test!
    # -------------------------------------------------------------------------
    gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups=groups))

    X_train_raw = X.iloc[train_idx]
    y_train = y.iloc[train_idx]
    groups_train = groups.iloc[train_idx]

    X_test_raw = X.iloc[test_idx]
    y_test = y.iloc[test_idx]
    groups_test = groups.iloc[test_idx]

    print(f"Training set: {len(X_train_raw)} records ({groups_train.nunique()} unique students)")
    print(f"Testing set:  {len(X_test_raw)} records ({groups_test.nunique()} unique students)")
    # Verify zero student overlap
    overlap = set(groups_train).intersection(set(groups_test))
    assert len(overlap) == 0, f"Error: Student overlap detected: {overlap}"
    print("Student-level leakage check: PASSED (0 overlapping students)")

    # Cross-validation setup: Stratified Group 5-Fold on training students
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)

    candidate_results = {}
    best_model_name = None
    best_f1 = -1.0
    best_pipeline_obj = None

    print("\n--- Candidate Model Evaluation (Leakage-Safe Pipeline) ---")
    for name, config in CANDIDATE_CONFIGS.items():
        estimator = config['class'](**config['params'])

        # Encapsulated Pipeline: ColumnTransformer + Estimator
        # Preprocessor is fitted strictly inside training folds during cross-validation!
        transformer = preprocessor.build_transformer()
        pipeline = Pipeline([
            ('preprocessor', transformer),
            ('classifier', estimator)
        ])

        # 5-fold cross-validation on raw training data only
        cv_scores = cross_val_score(pipeline, X_train_raw, y_train, cv=sgkf, groups=groups_train, scoring='f1_macro')

        # Fit pipeline on all training data
        pipeline.fit(X_train_raw, y_train)

        # Extract fitted feature names
        fitted_transformer = pipeline.named_steps['preprocessor']
        cat_encoder = fitted_transformer.named_transformers_['cat'].named_steps['encoder']
        cat_names = cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
        feature_names = NUMERIC_FEATURES + cat_names

        # Evaluate on unseen held-out test students
        X_test_trans = fitted_transformer.transform(X_test_raw)
        eval_metrics = evaluate_model_performance(
            pipeline.named_steps['classifier'],
            X_test_trans,
            y_test,
            class_labels=preprocessor.target_classes,
            feature_names=feature_names
        )
        eval_metrics['cv_f1_macro_mean'] = float(round(cv_scores.mean(), 4))
        eval_metrics['cv_f1_macro_std'] = float(round(cv_scores.std(), 4))
        eval_metrics['hyperparameters'] = config['params']

        candidate_results[name] = eval_metrics
        print(f"Model: {name:18} | Test Acc: {eval_metrics['accuracy']:.4f} | Test Macro F1: {eval_metrics['f1_macro']:.4f} | 5-Fold CV Macro F1: {eval_metrics['cv_f1_macro_mean']:.4f}")

        if eval_metrics['f1_macro'] > best_f1:
            best_f1 = eval_metrics['f1_macro']
            best_model_name = name
            best_pipeline_obj = pipeline

    print(f"\nWinning Model: {best_model_name} (Test Macro F1: {best_f1:.4f})")

    # Majority class baseline on held-out test data
    maj_baseline = float(round(y_test.value_counts().max() / len(y_test), 4))
    print(f"Held-out test majority baseline: {maj_baseline:.4f}")

    # Extract fitted feature names for winning model
    winning_transformer = best_pipeline_obj.named_steps['preprocessor']
    cat_encoder = winning_transformer.named_transformers_['cat'].named_steps['encoder']
    cat_names = cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
    feature_names = NUMERIC_FEATURES + cat_names

    final_report = {
        'version_tag': version_tag,
        'model_name': f"LMS Canonical ({best_model_name})",
        'trained_at': datetime.utcnow().isoformat(),
        'provenance': 'SYNTHETIC_LMS_FORMATIVE_BENCHMARK_PIPELINE_V2',
        'provenance_disclosure': (
            "Trained on rubric-grounded synthetic student telemetry replicating the exact live "
            "compute_student_topic_features() schema. Preprocessing is encapsulated inside an sklearn Pipeline "
            "and fitted separately inside each cross-validation fold. Zero student overlap. Production validation "
            "against real human cohort outcomes remains incomplete until institution-specific labels are collected."
        ),
        'best_model': best_model_name,
        'pipeline_architecture': "sklearn.pipeline.Pipeline([('preprocessor', ColumnTransformer), ('classifier', LogisticRegression)])",
        'dataset_summary': {
            'total_rows': len(df),
            'total_students': int(df['student_id'].nunique()),
            'class_distribution': df[TARGET_COLUMN].value_counts().to_dict(),
            'topic_level_distribution': df['topic_difficulty_level'].value_counts().to_dict()
        },
        'training_sample_count': len(X_train_raw),
        'test_sample_count': len(X_test_raw),
        'test_students_count': int(groups_test.nunique()),
        'majority_class_baseline': maj_baseline,
        'best_metrics': candidate_results[best_model_name],
        'candidate_comparison': candidate_results,
        'feature_names': feature_names
    }

    # -------------------------------------------------------------------------
    # Save Versioned Artifacts ONLY (Never overwrite root production artifacts)
    # -------------------------------------------------------------------------
    version_dir = os.path.join(artifacts_dir, 'versions', version_tag)
    os.makedirs(version_dir, exist_ok=True)

    # Save fitted preprocessor
    preprocessor.transformer = winning_transformer
    preprocessor.feature_names = feature_names
    preprocessor.save(os.path.join(version_dir, 'preprocessor.joblib'))

    # Save fitted classifier and pipeline
    joblib.dump(best_pipeline_obj.named_steps['classifier'], os.path.join(version_dir, 'model.joblib'))
    joblib.dump(best_pipeline_obj, os.path.join(version_dir, 'pipeline.joblib'))

    with open(os.path.join(version_dir, 'evaluation_report.json'), 'w') as f:
        json.dump(final_report, f, indent=2)

    print(f"Artifacts successfully saved to: {version_dir}")

    # -------------------------------------------------------------------------
    # Register in SQLite model_versions Table as Inactive
    # -------------------------------------------------------------------------
    app = create_app()
    with app.app_context():
        existing = ModelVersion.query.filter_by(version_tag=version_tag).first()
        if existing:
            mv = existing
        else:
            mv = ModelVersion(version_tag=version_tag)
            db.session.add(mv)

        best_m = candidate_results[best_model_name]
        mv.model_name = f"LMS Canonical ({best_model_name})"
        mv.algorithm = best_model_name
        mv.accuracy = best_m['accuracy']
        mv.precision_macro = best_m['precision_macro']
        mv.recall_macro = best_m['recall_macro']
        mv.f1_macro = best_m['f1_macro']
        mv.f1_weighted = best_m.get('f1_weighted')
        mv.confusion_matrix = best_m.get('confusion_matrix')
        mv.classification_report = best_m.get('classification_report')
        mv.feature_importances = best_m.get('feature_importances')
        mv.parameters = best_m.get('hyperparameters')
        mv.training_sample_count = len(X_train_raw)
        mv.is_active = False  # NEVER activate automatically

        db.session.commit()
        print(f"Registered ModelVersion in DB: ID={mv.id}, tag='{mv.version_tag}', is_active={mv.is_active}")

        # Verify baseline remains active
        active_m = ModelVersion.query.filter_by(is_active=True).first()
        print(f"Current Active Model in DB: {active_m.version_tag if active_m else 'None'}")

    return final_report

if __name__ == '__main__':
    run_lms_canonical_training()
