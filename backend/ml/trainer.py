import os
import json
import shutil
from datetime import datetime
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from backend.ml.preprocessor import MLDataPreprocessor, TARGET_COLUMN
from backend.ml.evaluator import evaluate_model_performance

CANDIDATE_MODELS = {
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

class MLTrainingPipeline:
    def __init__(self, artifacts_dir=None):
        if artifacts_dir is None:
            self.artifacts_dir = os.path.join(os.path.dirname(__file__), '..', 'artifacts')
        else:
            self.artifacts_dir = artifacts_dir
        os.makedirs(self.artifacts_dir, exist_ok=True)
        self.preprocessor = MLDataPreprocessor()

    def run_training_pipeline(self, dataset_path, version_tag=None, activate=True):
        """
        Executes full training pipeline on given CSV dataset.
        Evaluates candidate models, selects the best performing model based on test F1-macro score,
        and saves versioned artifacts. When activate=True, updates active artifacts at root.
        When activate=False, only saves versioned artifacts for evaluation and optional activation.
        """
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset file not found at {dataset_path}")

        df = pd.read_csv(dataset_path)
        is_valid, errors, summary = self.preprocessor.validate_schema(df, require_target=True)
        if not is_valid:
            raise ValueError(f"Dataset validation failed: {', '.join(errors)}")

        X = df.drop(columns=[TARGET_COLUMN])
        y = df[TARGET_COLUMN]

        # Stratified train/test split (80% train, 20% test)
        X_train_raw, X_test_raw, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42, stratify=y
        )

        # Preprocess features
        X_train_trans = self.preprocessor.fit_transform(X_train_raw)
        X_test_trans = self.preprocessor.transform(X_test_raw)

        candidate_results = {}
        best_model_name = None
        best_f1 = -1.0
        best_model_obj = None

        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        for model_name, config in CANDIDATE_MODELS.items():
            model = config['class'](**config['params'])
            
            # Cross-validation on training data only
            cv_scores = cross_val_score(model, X_train_trans, y_train, cv=cv, scoring='f1_macro')
            
            # Fit on full training data
            model.fit(X_train_trans, y_train)

            # Evaluate on held-out test data
            eval_metrics = evaluate_model_performance(
                model, 
                X_test_trans, 
                y_test, 
                class_labels=self.preprocessor.target_classes,
                feature_names=self.preprocessor.feature_names
            )
            eval_metrics['cv_f1_macro_mean'] = float(round(cv_scores.mean(), 4))
            eval_metrics['cv_f1_macro_std'] = float(round(cv_scores.std(), 4))
            eval_metrics['hyperparameters'] = config['params']

            candidate_results[model_name] = eval_metrics

            if eval_metrics['f1_macro'] > best_f1:
                best_f1 = eval_metrics['f1_macro']
                best_model_name = model_name
                best_model_obj = model

        # Generate version tag if not provided
        if not version_tag:
            version_tag = f"model_v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        final_report = {
            'version_tag': version_tag,
            'trained_at': datetime.utcnow().isoformat(),
            'best_model': best_model_name,
            'dataset_summary': summary,
            'training_sample_count': len(X_train_raw),
            'test_sample_count': len(X_test_raw),
            'best_metrics': candidate_results[best_model_name],
            'candidate_comparison': candidate_results,
            'feature_names': self.preprocessor.feature_names
        }

        # 1. Save versioned artifacts (for rollback & history)
        version_dir = os.path.join(self.artifacts_dir, 'versions', version_tag)
        os.makedirs(version_dir, exist_ok=True)
        joblib.dump(best_model_obj, os.path.join(version_dir, 'model.joblib'))
        self.preprocessor.save(os.path.join(version_dir, 'preprocessor.joblib'))
        with open(os.path.join(version_dir, 'evaluation_report.json'), 'w') as f:
            json.dump(final_report, f, indent=2)

        # 2. Update active artifacts at root only if activate=True
        if activate:
            model_artifact_path = os.path.join(self.artifacts_dir, 'model.joblib')
            preprocessor_artifact_path = os.path.join(self.artifacts_dir, 'preprocessor.joblib')
            report_path = os.path.join(self.artifacts_dir, 'evaluation_report.json')

            joblib.dump(best_model_obj, model_artifact_path)
            self.preprocessor.save(preprocessor_artifact_path)
            with open(report_path, 'w') as f:
                json.dump(final_report, f, indent=2)

        return final_report

if __name__ == '__main__':
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    dataset_file = os.path.join(backend_dir, 'data', 'learning_difficulty_dataset.csv')
    if not os.path.exists(dataset_file):
        from backend.ml.dataset_generator import generate_educational_dataset
        generate_educational_dataset(3000, 42, dataset_file)
    
    pipeline = MLTrainingPipeline()
    report = pipeline.run_training_pipeline(dataset_file, version_tag='v1.0.0-initial')
    print("Training finished! Best model:", report['best_model'])
    print("F1-macro:", report['best_metrics']['f1_macro'])
    print("Accuracy:", report['best_metrics']['accuracy'])
