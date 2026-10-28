import os
import pytest
import numpy as np
from backend.ml.adapters import (
    IdentityAdapter,
    UCIFeatureAdapter,
    get_feature_adapter
)
from backend.ml.predictor import MLPredictor
from backend.ml.preprocessor import MLDataPreprocessor

def test_identity_adapter_leaves_baseline_untouched():
    """Verify that the production baseline uses IdentityAdapter with zero modifications."""
    adapter = get_feature_adapter('v1.0.0-production-baseline')
    assert isinstance(adapter, IdentityAdapter)

    sample_features = {
        'quiz_score': 85.5,
        'assignment_score': 78.0,
        'exam_score': 82.0,
        'study_time_weekly': 18.5, # > 10h
        'attendance_rate': 95.0,
        'attempt_count': 3,
        'repeated_errors_count': 2,
        'previous_topic_score': 80.0,
        'learning_pace_gap': 11.75, # live formula
        'topic_difficulty_level': 'beginner'
    }

    adapted, meta = adapter.transform_features(sample_features)
    assert adapted == sample_features
    assert meta['adapter_applied'] is False
    assert meta['adapter_name'] == 'IdentityAdapter'
    assert len(meta['warnings']) == 0

def test_study_time_binning_boundaries():
    """Verify exact boundary behavior for weekly study hours in UCIFeatureAdapter."""
    adapter = UCIFeatureAdapter()

    # Bin 1: < 2.0 hours -> 1.5
    for val in [0.5, 1.0, 1.5, 1.99]:
        binned, desc = adapter.bin_study_time_weekly(val)
        assert binned == 1.5
        assert "bin_1" in desc

    # Bin 2: [2.0, 5.0) -> 3.5
    for val in [2.0, 2.5, 3.5, 4.0, 4.99]:
        binned, desc = adapter.bin_study_time_weekly(val)
        assert binned == 3.5
        assert "bin_2" in desc

    # Bin 3: [5.0, 10.0] -> 7.5
    for val in [5.0, 6.0, 7.5, 9.0, 10.0]:
        binned, desc = adapter.bin_study_time_weekly(val)
        assert binned == 7.5
        assert "bin_3" in desc

    # Bin 4: > 10.0 hours -> 12.0 (with documented precision loss)
    for val in [10.01, 12.0, 16.0, 24.0, 28.0]:
        binned, desc = adapter.bin_study_time_weekly(val)
        assert binned == 12.0
        assert "bin_4" in desc

    # Invalid / fallback
    binned, desc = adapter.bin_study_time_weekly("not_a_number")
    assert binned == 8.0

def test_learning_pace_gap_reconciliation():
    """Verify learning_pace_gap handling when real prior topic score exists vs first topic."""
    adapter = UCIFeatureAdapter()

    # Case A: Real previous topic exists
    features_with_prior = {
        'quiz_score': 90.0,
        'assignment_score': 80.0, # current topic avg = 85.0
        'previous_topic_score': 75.0,
        'learning_pace_gap': 15.0 # live app distance from 70
    }
    adapted, meta = adapter.transform_features(features_with_prior, context={'has_real_previous_topic': True})
    # Topic delta: 85.0 - 75.0 = +10.0
    assert adapted['learning_pace_gap'] == 10.0
    assert meta['semantic_flags']['learning_pace_gap']['status'] == 'reconciled_with_topic_delta'

    # Case B: First topic in course (no real previous topic)
    features_first_topic = {
        'quiz_score': 90.0,
        'assignment_score': 80.0,
        'previous_topic_score': 70.0, # fallback baseline
        'learning_pace_gap': 15.0
    }
    adapted_first, meta_first = adapter.transform_features(features_first_topic, context={'has_real_previous_topic': False})
    # Should flag semantic incompatibility rather than fabricating a trend
    assert 'learning_pace_gap' in meta_first['semantic_flags']
    assert meta_first['semantic_flags']['learning_pace_gap']['status'] == 'semantically_incompatible_no_prior_topic'
    assert any('semantic incompatibility' in w.lower() for w in meta_first['warnings'])

def test_topic_difficulty_level_beginner_adaptation():
    """Verify that 'beginner' is adapted to 'intermediate' with documented warning."""
    adapter = UCIFeatureAdapter()

    # Beginner topic
    adapted_beg, meta_beg = adapter.transform_features({'topic_difficulty_level': 'beginner'})
    assert adapted_beg['topic_difficulty_level'] == 'intermediate'
    assert meta_beg['semantic_flags']['topic_difficulty_level']['status'] == 'unvalidated_surrogate_mapped_to_intermediate'
    assert any('0 training samples' in w for w in meta_beg['warnings'])

    # Intermediate topic preserved
    adapted_int, meta_int = adapter.transform_features({'topic_difficulty_level': 'intermediate'})
    assert adapted_int['topic_difficulty_level'] == 'intermediate'
    assert 'topic_difficulty_level' not in meta_int.get('semantic_flags', {})

    # Advanced topic preserved
    adapted_adv, _ = adapter.transform_features({'topic_difficulty_level': 'advanced'})
    assert adapted_adv['topic_difficulty_level'] == 'advanced'

def test_attempt_count_and_repeated_errors_bounding():
    """Verify bounds and semantic flags for attempt counts and error counts."""
    adapter = UCIFeatureAdapter()

    # Extreme quiz retakes in LMS
    adapted, meta = adapter.transform_features({
        'attempt_count': 6,
        'repeated_errors_count': 12
    })
    # attempt_count clamped to UCI max 4
    assert adapted['attempt_count'] == 4
    assert meta['semantic_flags']['attempt_count']['status'] == 'unverified_proxy_risk'
    # repeated_errors clamped to UCI max 7
    assert adapted['repeated_errors_count'] == 7

def test_missing_data_fallbacks():
    """Verify that missing or None fields receive safe, non-crashing defaults."""
    adapter = UCIFeatureAdapter()
    empty_features = {}
    adapted, meta = adapter.transform_features(empty_features)

    assert adapted['quiz_score'] == 70.0
    assert adapted['assignment_score'] == 70.0
    assert adapted['exam_score'] == 70.0
    assert adapted['study_time_weekly'] == 7.5
    assert adapted['attendance_rate'] == 85.0
    assert adapted['attempt_count'] == 1
    assert adapted['repeated_errors_count'] == 0
    assert adapted['topic_difficulty_level'] == 'intermediate'

def test_end_to_end_adapted_prediction_properties():
    """Verify mathematical properties (classes, probabilities, severity score) under adapted inference."""
    # Test isolated predictor with UCI model
    staged_dir = os.path.join(os.path.dirname(__file__), '..', 'artifacts', 'versions', 'uci_student_perf_v1')
    if not os.path.exists(staged_dir):
        pytest.skip("Staged UCI model artifacts not found")

    predictor = MLPredictor(artifacts_dir=staged_dir)
    predictor.version_tag = 'uci_student_perf_v1'

    test_input = {
        'quiz_score': 88.0,
        'assignment_score': 84.0,
        'exam_score': 80.0,
        'study_time_weekly': 18.0, # will be binned to 12.0
        'attendance_rate': 100.0,
        'attempt_count': 2,
        'repeated_errors_count': 1,
        'previous_topic_score': 82.0,
        'learning_pace_gap': 16.0,
        'topic_difficulty_level': 'beginner' # will be adapted to intermediate
    }

    result = predictor.predict_features(test_input, context={'has_real_previous_topic': True})
    assert result['predicted_difficulty'] in ['Low', 'Moderate', 'High']
    assert 0.0 <= result['difficulty_score'] <= 1.0

    # Probabilities must sum strictly to 1.0
    prob_sum = result['probability_low'] + result['probability_moderate'] + result['probability_high']
    assert abs(prob_sum - 1.0) < 1e-4

    # Adapter metadata must be attached
    assert 'adapter_metadata' in result
    meta = result['adapter_metadata']
    assert meta['adapter_applied'] is True
    assert meta['adapted_features_summary']['study_time_weekly'] == 12.0
    assert meta['adapted_features_summary']['topic_difficulty_level'] == 'intermediate'

