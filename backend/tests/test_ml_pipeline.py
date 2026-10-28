import os
import tempfile
import pandas as pd
from backend.ml.dataset_generator import generate_educational_dataset
from backend.ml.preprocessor import MLDataPreprocessor, REQUIRED_FEATURES, TARGET_COLUMN
from backend.ml.trainer import MLTrainingPipeline
from backend.ml.predictor import MLPredictor

def test_dataset_generation():
    df = generate_educational_dataset(num_samples=200, random_seed=99)
    assert len(df) == 200
    for feat in REQUIRED_FEATURES:
        assert feat in df.columns
    assert TARGET_COLUMN in df.columns
    assert set(df[TARGET_COLUMN].unique()).issubset({'Low', 'Moderate', 'High'})

def test_preprocessor_validation():
    preprocessor = MLDataPreprocessor()
    df = generate_educational_dataset(num_samples=100)
    is_valid, errors, summary = preprocessor.validate_schema(df, require_target=True)
    assert is_valid is True
    assert len(errors) == 0

    # Missing column test
    df_broken = df.drop(columns=['quiz_score'])
    is_valid, errors, summary = preprocessor.validate_schema(df_broken, require_target=True)
    assert is_valid is False
    assert any('quiz_score' in e for e in errors)

def test_training_pipeline_and_inference():
    temp_dir = tempfile.mkdtemp()
    dataset_file = os.path.join(temp_dir, 'test_dataset.csv')
    generate_educational_dataset(num_samples=400, random_seed=42, output_path=dataset_file)

    pipeline = MLTrainingPipeline(artifacts_dir=temp_dir)
    report = pipeline.run_training_pipeline(dataset_file, version_tag='test_v1.0')

    assert 'best_model' in report
    assert 'best_metrics' in report
    metrics = report['best_metrics']
    assert 0.0 <= metrics['accuracy'] <= 1.0
    assert 0.0 <= metrics['f1_macro'] <= 1.0
    assert 'confusion_matrix' in metrics

    # Test Predictor loading artifacts
    predictor = MLPredictor(artifacts_dir=temp_dir)
    assert predictor.is_ready() is True

    # High difficulty student features
    high_diff_student = {
        'quiz_score': 32.0,
        'assignment_score': 45.0,
        'exam_score': 38.0,
        'study_time_weekly': 3.0,
        'attendance_rate': 65.0,
        'attempt_count': 3,
        'repeated_errors_count': 7,
        'previous_topic_score': 40.0,
        'learning_pace_gap': -15.0,
        'topic_difficulty_level': 'advanced'
    }
    pred = predictor.predict_features(high_diff_student)
    assert pred['predicted_difficulty'] in ['Moderate', 'High']
    assert 0.0 <= pred['difficulty_score'] <= 1.0
    assert len(pred['contributing_factors']) > 0
    assert len(pred['recommended_actions']) > 0

    # Strong student features
    strong_student = {
        'quiz_score': 95.0,
        'assignment_score': 92.0,
        'exam_score': 90.0,
        'study_time_weekly': 14.0,
        'attendance_rate': 98.0,
        'attempt_count': 1,
        'repeated_errors_count': 0,
        'previous_topic_score': 94.0,
        'learning_pace_gap': 12.0,
        'topic_difficulty_level': 'beginner'
    }
    pred_strong = predictor.predict_features(strong_student)
    assert pred_strong['predicted_difficulty'] == 'Low'
    assert pred_strong['difficulty_score'] < 0.35

