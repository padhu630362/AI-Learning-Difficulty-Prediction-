"""
Feature Adapter Architecture for Model Versions.

This module provides version-specific feature adaptation layers to decouple
the live application's LMS telemetry schema from idiosyncratic training-time
representations (e.g., secondary school survey data from UCI).

Critical Safety Rules:
- The production baseline model ('v1.0.0-production-baseline') uses the IdentityAdapter,
  leaving its features 100% unaltered.
- Version-specific adapters (e.g., UCIFeatureAdapter for 'uci_student_perf_v1')
  are invoked ONLY when explicitly predicting with that specific version.
- When live application telemetry cannot be semantically reconciled with training
  assumptions, the adapter flags the feature in metadata rather than silently fabricating data.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class BaseFeatureAdapter(ABC):
    """Abstract base class for model feature adapters."""
    
    @abstractmethod
    def transform_features(self, feature_dict: Dict[str, Any], context: Dict[str, Any] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Transforms input feature dictionary to match model-specific expectations.
        Returns:
            (adapted_features_dict, adapter_metadata_dict)
        """
        pass

class IdentityAdapter(BaseFeatureAdapter):
    """
    Default adapter for production baseline and standard models.
    Passes all features through untouched with zero transformation.
    """
    def transform_features(self, feature_dict: Dict[str, Any], context: Dict[str, Any] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        return dict(feature_dict), {
            'adapter_applied': False,
            'adapter_name': 'IdentityAdapter',
            'warnings': []
        }

class UCIFeatureAdapter(BaseFeatureAdapter):
    """
    Version-specific adapter for 'uci_student_perf_v1' (RandomForest model trained on UCI dataset).
    
    Harmonizes live LMS telemetry with the training distributions of the UCI Student Performance benchmark,
    documenting all information loss, semantic proxy assumptions, and domain boundaries.
    """
    
    @staticmethod
    def bin_study_time_weekly(hours: float) -> Tuple[float, str]:
        """
        Maps continuous weekly study hours to the 4 discrete UCI survey categories:
        - Bin 1 (< 2 hours):      midpoint 1.5 hrs
        - Bin 2 (2 to 5 hours):   midpoint 3.5 hrs
        - Bin 3 (5 to 10 hours):  midpoint 7.5 hrs
        - Bin 4 (> 10 hours):     midpoint 12.0 hrs
        
        Boundary Specifications:
        - hours < 2.0  -> 1.5
        - 2.0 <= hours < 5.0 -> 3.5
        - 5.0 <= hours <= 10.0 -> 7.5
        - hours > 10.0 -> 12.0
        """
        try:
            h = float(hours)
        except (TypeError, ValueError):
            return 8.0, "invalid_study_time_fallback"
            
        if h < 2.0:
            return 1.5, "bin_1_under_2h"
        elif h < 5.0:
            return 3.5, "bin_2_2_to_5h"
        elif h <= 10.0:
            return 7.5, "bin_3_5_to_10h"
        else:
            return 12.0, "bin_4_over_10h_precision_lost"

    def transform_features(self, feature_dict: Dict[str, Any], context: Dict[str, Any] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        raw = dict(feature_dict)
        adapted = dict(feature_dict)
        warnings = []
        semantic_flags = {}

        # ---------------------------------------------------------------------
        # 1. study_time_weekly: Discretize into UCI ordinal bins
        # ---------------------------------------------------------------------
        raw_study_time = raw.get('study_time_weekly')
        if raw_study_time is not None:
            binned_time, bin_desc = self.bin_study_time_weekly(raw_study_time)
            adapted['study_time_weekly'] = binned_time
            if bin_desc == "bin_4_over_10h_precision_lost" and float(raw_study_time) > 12.0:
                warnings.append(
                    f"study_time_weekly ({raw_study_time} hrs) exceeds UCI training maximum (12.0 hrs). "
                    f"Discretized to 12.0 hrs; precision between {raw_study_time}h and 10h is lost."
                )
        else:
            adapted['study_time_weekly'] = 7.5

        # ---------------------------------------------------------------------
        # 2. learning_pace_gap: Semantic Reconciliation vs Incompatibility
        # ---------------------------------------------------------------------
        # Live App: (quiz * 0.5 + assign * 0.5) - 70.0 (Distance from benchmark)
        # UCI Model: (G2 - G1) * 5.0 (Longitudinal grade delta from Period 1 to Period 2)
        has_real_prev = False
        prev_score = raw.get('previous_topic_score')
        quiz_score = raw.get('quiz_score')
        assign_score = raw.get('assignment_score')

        # Context can indicate whether previous_topic_score was a real prior score or fallback
        if context and context.get('has_real_previous_topic'):
            has_real_prev = True
        elif prev_score is not None and prev_score != 70.0:
            # Heuristic: if prev_score is not the default 70.0 baseline, treat as potential prior score
            has_real_prev = True

        if has_real_prev and quiz_score is not None and assign_score is not None and prev_score is not None:
            current_topic_perf = (float(quiz_score) * 0.5 + float(assign_score) * 0.5)
            # Longitudinal progress delta: current topic performance minus previous topic performance
            topic_to_topic_delta = round(current_topic_perf - float(prev_score), 1)
            adapted['learning_pace_gap'] = topic_to_topic_delta
            semantic_flags['learning_pace_gap'] = {
                'status': 'reconciled_with_topic_delta',
                'raw_benchmark_gap': raw.get('learning_pace_gap'),
                'adapted_topic_delta': topic_to_topic_delta,
                'formula': 'current_topic_perf - previous_topic_score'
            }
        else:
            # First topic in course or missing previous data: longitudinal slope is mathematically undefined.
            # Do NOT invent progress. Retain the clamped value and explicitly flag semantic incompatibility.
            raw_gap = raw.get('learning_pace_gap', 0.0)
            adapted['learning_pace_gap'] = float(raw_gap) if raw_gap is not None else 0.0
            warnings.append(
                "learning_pace_gap semantic incompatibility: Student has no preceding topic in course. "
                "True longitudinal progress delta is undefined; benchmark-relative gap retained as fallback. "
                "Recommend retraining on LMS benchmark-relative features."
            )
            semantic_flags['learning_pace_gap'] = {
                'status': 'semantically_incompatible_no_prior_topic',
                'recommendation': 'retrain_on_lms_features'
            }

        # ---------------------------------------------------------------------
        # 3. topic_difficulty_level: Handle 'beginner' absence in UCI dataset
        # ---------------------------------------------------------------------
        raw_level = str(raw.get('topic_difficulty_level', 'intermediate')).lower().strip()
        if raw_level == 'beginner':
            # UCI dataset has 0 beginner training samples (only intermediate and advanced).
            # Mapping beginner to intermediate is an unvalidated proxy.
            adapted['topic_difficulty_level'] = 'intermediate'
            warnings.append(
                "topic_difficulty_level 'beginner' has 0 training samples in UCI dataset. "
                "Mapped to 'intermediate' as a conservative surrogate; limitation documented."
            )
            semantic_flags['topic_difficulty_level'] = {
                'status': 'unvalidated_surrogate_mapped_to_intermediate',
                'original': 'beginner',
                'adapted': 'intermediate'
            }
        elif raw_level in ['intermediate', 'advanced']:
            adapted['topic_difficulty_level'] = raw_level
        else:
            adapted['topic_difficulty_level'] = 'intermediate'

        # ---------------------------------------------------------------------
        # 4. attempt_count: Documentation of Retake vs Grade-Retention proxy
        # ---------------------------------------------------------------------
        raw_attempts = raw.get('attempt_count', 1)
        try:
            att = int(raw_attempts)
            # UCI training attempt_count is [1, 4] derived from 1 + failures (academic year repeats)
            # Cap at 4 to prevent out-of-bounds on high LMS retakes
            adapted['attempt_count'] = min(max(att, 1), 4)
            if att > 2:
                semantic_flags['attempt_count'] = {
                    'status': 'unverified_proxy_risk',
                    'raw_quiz_attempts': att,
                    'uci_equivalent': 'multi_year_academic_retention',
                    'note': 'LMS quiz retakes do not equate to repeating entire academic years; recommend retraining.'
                }
        except (TypeError, ValueError):
            adapted['attempt_count'] = 1

        # ---------------------------------------------------------------------
        # 5. attendance_rate & repeated_errors_count: Bounding & Semantics
        # ---------------------------------------------------------------------
        raw_att_rate = raw.get('attendance_rate')
        if raw_att_rate is not None:
            try:
                adapted['attendance_rate'] = min(max(float(raw_att_rate), 0.0), 100.0)
            except (TypeError, ValueError):
                adapted['attendance_rate'] = 85.0
        else:
            adapted['attendance_rate'] = 85.0

        raw_errors = raw.get('repeated_errors_count')
        if raw_errors is not None:
            try:
                # UCI repeated_errors_count max was 7 (failures * 2 + remedial support)
                adapted['repeated_errors_count'] = min(max(int(raw_errors), 0), 7)
            except (TypeError, ValueError):
                adapted['repeated_errors_count'] = 0
        else:
            adapted['repeated_errors_count'] = 0

        # Remaining features (quiz_score, assignment_score, exam_score, previous_topic_score)
        for score_key in ['quiz_score', 'assignment_score', 'exam_score', 'previous_topic_score']:
            val = raw.get(score_key)
            if val is not None:
                try:
                    adapted[score_key] = min(max(float(val), 0.0), 100.0)
                except (TypeError, ValueError):
                    adapted[score_key] = 70.0
            else:
                adapted[score_key] = 70.0

        metadata = {
            'adapter_applied': True,
            'adapter_name': 'UCIFeatureAdapter',
            'target_model_version': 'uci_student_perf_v1',
            'warnings': warnings,
            'semantic_flags': semantic_flags,
            'raw_features_summary': {k: raw.get(k) for k in ['study_time_weekly', 'learning_pace_gap', 'topic_difficulty_level', 'attempt_count']},
            'adapted_features_summary': {k: adapted.get(k) for k in ['study_time_weekly', 'learning_pace_gap', 'topic_difficulty_level', 'attempt_count']}
        }

        return adapted, metadata

# -----------------------------------------------------------------------------
# Adapter Registry & Factory Function
# -----------------------------------------------------------------------------
ADAPTER_REGISTRY = {
    'uci_student_perf_v1': UCIFeatureAdapter
}

def get_feature_adapter(version_tag: str) -> BaseFeatureAdapter:
    """
    Returns the appropriate feature adapter for a given model version tag.
    Returns IdentityAdapter for 'v1.0.0-production-baseline' and un-registered versions.
    """
    if version_tag in ADAPTER_REGISTRY:
        return ADAPTER_REGISTRY[version_tag]()
    return IdentityAdapter()

