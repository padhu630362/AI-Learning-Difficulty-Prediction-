import os
import pytest
import joblib
import pandas as pd
import numpy as np
from backend.ml.preprocessor import MLDataPreprocessor, REQUIRED_FEATURES, TARGET_COLUMN
from backend.ml.predictor import MLPredictor
from backend.app import create_app
from backend.models.ml_records import ModelVersion

def get_lms_canonical_dir():
    return os.path.join(
        os.path.dirname(__file__), '..', 'artifacts', 'versions', 'lms_canonical_v1'
    )

def test_lms_canonical_artifacts_exist():
    """Verify that staged LMS canonical model, preprocessor, and report exist and are non-empty."""
    version_dir = get_lms_canonical_dir()
    assert os.path.exists(version_dir), "lms_canonical_v1 directory does not exist"
    
    model_path = os.path.join(version_dir, 'model.joblib')
    preproc_path = os.path.join(version_dir, 'preprocessor.joblib')
    report_path = os.path.join(version_dir, 'evaluation_report.json')
    
    assert os.path.exists(model_path) and os.path.getsize(model_path) > 0
    assert os.path.exists(preproc_path) and os.path.getsize(preproc_path) > 0
    assert os.path.exists(report_path) and os.path.getsize(report_path) > 0

def test_feature_schema_consistency():
    """Verify preprocessor feature names and input schema match REQUIRED_FEATURES."""
    version_dir = get_lms_canonical_dir()
    preprocessor = MLDataPreprocessor.load(os.path.join(version_dir, 'preprocessor.joblib'))
    
    sample_row = {
        'quiz_score': 75.0,
        'assignment_score': 80.0,
        'exam_score': 72.0,
        'study_time_weekly': 14.0,
        'attendance_rate': 92.0,
        'attempt_count': 1,
        'repeated_errors_count': 1,
        'previous_topic_score': 70.0,
        'learning_pace_gap': 7.5,
        'topic_difficulty_level': 'intermediate'
    }
    
    df = pd.DataFrame([sample_row])
    X_trans = preprocessor.transform(df)
    
    # 9 numerics + 3 one-hot columns (beginner, intermediate, advanced) = 12
    assert X_trans.shape == (1, 12)
    assert len(preprocessor.feature_names) == 12
    for req in REQUIRED_FEATURES:
        if req != 'topic_difficulty_level':
            assert req in preprocessor.feature_names

def test_all_three_topic_difficulty_levels():
    """Verify that beginner, intermediate, and advanced are natively supported without surrogate warnings."""
    version_dir = get_lms_canonical_dir()
    predictor = MLPredictor(artifacts_dir=version_dir)
    predictor.version_tag = 'lms_canonical_v1'
    
    base_input = {
        'quiz_score': 75.0,
        'assignment_score': 78.0,
        'exam_score': 70.0,
        'study_time_weekly': 12.0,
        'attendance_rate': 95.0,
        'attempt_count': 1,
        'repeated_errors_count': 0,
        'previous_topic_score': 75.0,
        'learning_pace_gap': 6.5
    }
    
    for level in ['beginner', 'intermediate', 'advanced']:
        inp = dict(base_input)
        inp['topic_difficulty_level'] = level
        res = predictor.predict_features(inp)
        assert res['predicted_difficulty'] in ['Low', 'Moderate', 'High']
        assert 0.0 <= res['difficulty_score'] <= 1.0
        # Confirms IdentityAdapter was used (no surrogate warnings)
        assert 'adapter_metadata' not in res or not res['adapter_metadata'].get('adapter_applied')

def test_missing_data_robustness():
    """Verify safe median/most-frequent imputation when inputs are missing."""
    version_dir = get_lms_canonical_dir()
    predictor = MLPredictor(artifacts_dir=version_dir)
    predictor.version_tag = 'lms_canonical_v1'
    
    # Partial dictionary (missing several fields)
    partial_input = {
        'quiz_score': 65.0,
        'exam_score': 60.0
    }
    res = predictor.predict_features(partial_input)
    assert res['predicted_difficulty'] in ['Low', 'Moderate', 'High']
    assert 0.0 <= res['difficulty_score'] <= 1.0

def test_probability_mapping_and_severity():
    """Verify probabilities sum to 1.0 and severity scores are monotonic with struggle."""
    version_dir = get_lms_canonical_dir()
    predictor = MLPredictor(artifacts_dir=version_dir)
    predictor.version_tag = 'lms_canonical_v1'
    
    # Strong student input
    strong_student = {
        'quiz_score': 95.0,
        'assignment_score': 92.0,
        'exam_score': 90.0,
        'study_time_weekly': 18.0,
        'attendance_rate': 98.0,
        'attempt_count': 1,
        'repeated_errors_count': 0,
        'previous_topic_score': 92.0,
        'learning_pace_gap': 23.5,
        'topic_difficulty_level': 'intermediate'
    }
    res_strong = predictor.predict_features(strong_student)
    prob_sum_s = res_strong['probability_low'] + res_strong['probability_moderate'] + res_strong['probability_high']
    assert abs(prob_sum_s - 1.0) < 1e-4
    assert res_strong['predicted_difficulty'] == 'Low'
    assert res_strong['difficulty_score'] < 0.25
    
    # Struggling student input
    struggling_student = {
        'quiz_score': 32.0,
        'assignment_score': 42.0,
        'exam_score': 35.0,
        'study_time_weekly': 3.0,
        'attendance_rate': 55.0,
        'attempt_count': 4,
        'repeated_errors_count': 7,
        'previous_topic_score': 38.0,
        'learning_pace_gap': -33.0,
        'topic_difficulty_level': 'advanced'
    }
    res_struggle = predictor.predict_features(struggling_student)
    prob_sum_h = res_struggle['probability_low'] + res_struggle['probability_moderate'] + res_struggle['probability_high']
    assert abs(prob_sum_h - 1.0) < 1e-4
    assert res_struggle['predicted_difficulty'] in ['Moderate', 'High']
    assert res_struggle['difficulty_score'] > res_strong['difficulty_score']

def test_model_version_isolation():
    """Verify that staging lms_canonical_v1 preserves database states and active baseline."""
    app = create_app()
    with app.app_context():
        baseline_mv = ModelVersion.query.filter_by(version_tag='v1.0.0-production-baseline').first()
        uci_mv = ModelVersion.query.filter_by(version_tag='uci_student_perf_v1').first()
        lms_mv = ModelVersion.query.filter_by(version_tag='lms_canonical_v1').first()
        
        assert baseline_mv is not None and baseline_mv.is_active is True
        assert uci_mv is not None and uci_mv.is_active is False
        assert lms_mv is not None and lms_mv.is_active is False

