import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from backend.ml.preprocessor import MLDataPreprocessor, REQUIRED_FEATURES
from backend.ml.adapters import get_feature_adapter

class MLPredictor:
    _instance = None

    def __init__(self, artifacts_dir=None):
        if artifacts_dir is None:
            self.artifacts_dir = os.path.join(os.path.dirname(__file__), '..', 'artifacts')
        else:
            self.artifacts_dir = artifacts_dir
        self.model = None
        self.preprocessor = None
        self.version_tag = 'v1.0'
        self.load_artifacts()

    @classmethod
    def get_instance(cls, artifacts_dir=None):
        if cls._instance is None:
            cls._instance = cls(artifacts_dir)
        return cls._instance

    def load_artifacts(self):
        model_path = os.path.join(self.artifacts_dir, 'model.joblib')
        preproc_path = os.path.join(self.artifacts_dir, 'preprocessor.joblib')
        report_path = os.path.join(self.artifacts_dir, 'evaluation_report.json')

        if os.path.exists(model_path) and os.path.exists(preproc_path):
            try:
                self.model = joblib.load(model_path)
                self.preprocessor = MLDataPreprocessor.load(preproc_path)
                if os.path.exists(report_path):
                    import json
                    with open(report_path, 'r') as f:
                        data = json.load(f)
                        self.version_tag = data.get('version_tag', 'v1.0')
            except Exception as e:
                print(f"Error loading model artifacts: {e}")
                self.model = None
                self.preprocessor = None
        else:
            self.model = None
            self.preprocessor = None

    def load_version(self, version_tag):
        """
        Switches the in-memory active inference engine to a specific versioned model.
        Supports seamless rollback and model activation without application restart.
        """
        version_dir = os.path.join(self.artifacts_dir, 'versions', version_tag)
        model_path = os.path.join(version_dir, 'model.joblib')
        preproc_path = os.path.join(version_dir, 'preprocessor.joblib')
        report_path = os.path.join(version_dir, 'evaluation_report.json')

        if os.path.exists(model_path) and os.path.exists(preproc_path):
            self.model = joblib.load(model_path)
            self.preprocessor = MLDataPreprocessor.load(preproc_path)
            self.version_tag = version_tag
            # Also copy to root active artifacts
            try:
                import shutil
                shutil.copy(model_path, os.path.join(self.artifacts_dir, 'model.joblib'))
                shutil.copy(preproc_path, os.path.join(self.artifacts_dir, 'preprocessor.joblib'))
                if os.path.exists(report_path):
                    shutil.copy(report_path, os.path.join(self.artifacts_dir, 'evaluation_report.json'))
            except Exception:
                pass
            return True
        else:
            # Fall back to load_artifacts
            self.load_artifacts()
            return False

    def is_ready(self):
        return self.model is not None and self.preprocessor is not None

    def validate_inputs(self, feature_dict, student_id=None, topic_id=None, subject_id=None, context='input_validation'):
        """
        Validates feature ranges and formats before running model transformation.
        Detects and logs outliers via TelemetryService for values exceeding canonical benchmarks.
        """
        from backend.services.telemetry_service import TelemetryService
        cleaned = {}
        for feat in REQUIRED_FEATURES:
            val = feature_dict.get(feat)
            if val is not None:
                if feat in ['quiz_score', 'assignment_score', 'exam_score', 'attendance_rate', 'previous_topic_score']:
                    try:
                        f_val = float(val)
                        if f_val < 0.0 or f_val > 100.0:
                            raise ValueError(f"Feature '{feat}' must be between 0 and 100 (got {val})")
                        cleaned[feat] = f_val
                    except (TypeError, ValueError) as e:
                        raise ValueError(f"Invalid numeric value for '{feat}': {str(e)}")
                elif feat == 'study_time_weekly':
                    try:
                        f_val = float(val)
                        if f_val < 0.0:
                            raise ValueError(f"Feature '{feat}' cannot be negative (got {val})")
                        # Detect and log outlier, clamping between 1.0 and 28.0
                        clamped_study = TelemetryService.inspect_and_clamp_study_time(
                            f_val,
                            student_id=student_id or 0,
                            topic_id=topic_id,
                            subject_id=subject_id,
                            context=context
                        )
                        cleaned[feat] = clamped_study
                    except (TypeError, ValueError) as e:
                        raise ValueError(f"Invalid numeric value for '{feat}': {str(e)}")
                elif feat in ['attempt_count', 'repeated_errors_count']:
                    try:
                        i_val = int(val)
                        if i_val < 0:
                            raise ValueError(f"Feature '{feat}' cannot be negative (got {val})")
                        if feat == 'repeated_errors_count':
                            bounded_errors = TelemetryService.inspect_and_clamp_repeated_errors(
                                i_val,
                                student_id=student_id or 0,
                                topic_id=topic_id,
                                subject_id=subject_id,
                                context=context
                            )
                            cleaned[feat] = bounded_errors
                        else:
                            cleaned[feat] = max(i_val, 1)
                    except (TypeError, ValueError) as e:
                        raise ValueError(f"Invalid integer value for '{feat}': {str(e)}")
                elif feat == 'learning_pace_gap':
                    try:
                        cleaned[feat] = float(val)
                    except (TypeError, ValueError):
                        cleaned[feat] = 0.0
                elif feat == 'topic_difficulty_level':
                    s_val = str(val).lower().strip()
                    if s_val not in ['beginner', 'intermediate', 'advanced']:
                        s_val = 'intermediate'
                    cleaned[feat] = s_val
            else:
                # Default fallbacks
                if feat == 'topic_difficulty_level':
                    cleaned[feat] = 'intermediate'
                elif feat in ['quiz_score', 'assignment_score', 'exam_score', 'attendance_rate', 'previous_topic_score']:
                    cleaned[feat] = 70.0
                elif feat == 'study_time_weekly':
                    cleaned[feat] = 8.0
                elif feat == 'attempt_count':
                    cleaned[feat] = 1
                elif feat == 'repeated_errors_count':
                    cleaned[feat] = 0
                elif feat == 'learning_pace_gap':
                    cleaned[feat] = 0.0

        return cleaned

    def predict_features(self, feature_dict, context=None):
        """
        Receives dict of student learning features, applies version-specific adaptation if registered,
        validates, transforms, and produces difficulty prediction.
        """
        if not self.is_ready():
            raise RuntimeError("ML model has not been trained or loaded yet.")

        # Apply version-specific feature adapter (IdentityAdapter for production baseline)
        adapter = get_feature_adapter(self.version_tag)
        adapted_features, adapter_meta = adapter.transform_features(feature_dict, context=context)

        # Clean and validate input features
        student_id = context.get('student_id') if context else None
        topic_id = context.get('topic_id') if context else None
        subject_id = context.get('subject_id') if context else None
        row = self.validate_inputs(
            adapted_features,
            student_id=student_id,
            topic_id=topic_id,
            subject_id=subject_id,
            context='input_validation'
        )

        df_input = pd.DataFrame([row])
        X_trans = self.preprocessor.transform(df_input)

        # Get class prediction
        pred_class = self.model.predict(X_trans)[0]

        # Get probabilities if supported
        prob_dict = {'Low': 0.0, 'Moderate': 0.0, 'High': 0.0}
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(X_trans)[0]
            classes = self.model.classes_
            for cls_name, prob in zip(classes, probabilities):
                prob_dict[cls_name] = float(prob)
        else:
            prob_dict[pred_class] = 1.0

        # Composite difficulty severity index [0.0 to 1.0]
        # Weighted mixture: 0.0 for pure Low, 0.5 for Moderate, 1.0 for High
        diff_score = (prob_dict.get('Moderate', 0.0) * 0.5) + (prob_dict.get('High', 0.0) * 1.0)
        diff_score = float(np.clip(diff_score, 0.0, 1.0))

        # Explainable contributing factors
        factors = []
        if float(row['quiz_score']) < 50.0:
            factors.append({
                'feature': 'quiz_score',
                'impact': 'High Risk',
                'description': f"Quiz performance is critically low ({row['quiz_score']}%), reflecting conceptual difficulty."
            })
        elif float(row['quiz_score']) < 65.0:
            factors.append({
                'feature': 'quiz_score',
                'impact': 'Moderate Risk',
                'description': f"Quiz performance ({row['quiz_score']}%) indicates room for revision."
            })

        if int(row['repeated_errors_count']) >= 4:
            factors.append({
                'feature': 'repeated_errors_count',
                'impact': 'High Risk',
                'description': f"Repeated mistakes count ({row['repeated_errors_count']}) indicates recurring misconceptions."
            })

        if float(row['study_time_weekly']) < 4.0:
            factors.append({
                'feature': 'study_time_weekly',
                'impact': 'Moderate Risk',
                'description': f"Weekly study time ({row['study_time_weekly']} hrs) is below recommended levels."
            })

        if float(row['previous_topic_score']) < 50.0:
            factors.append({
                'feature': 'previous_topic_score',
                'impact': 'High Risk',
                'description': f"Prerequisite topic score ({row['previous_topic_score']}%) indicates foundational gap."
            })

        if int(row['attempt_count']) > 2:
            factors.append({
                'feature': 'attempt_count',
                'impact': 'Moderate Risk',
                'description': f"Multiple re-attempts ({row['attempt_count']}) required to complete tasks."
            })

        if not factors:
            factors.append({
                'feature': 'overall_stability',
                'impact': 'Low Risk',
                'description': 'Student assessment scores, attempt frequency, and study habits align with good understanding.'
            })

        # Generate action recommendation hints
        actions = []
        if pred_class == 'High':
            actions.append('Schedule 1-on-1 mentoring or peer tutoring for prerequisite concepts.')
            actions.append('Complete guided revision worksheets with step-by-step solutions.')
            actions.append('Review instructor-provided lecture materials before re-attempting quizzes.')
        elif pred_class == 'Moderate':
            actions.append('Practice targeted formative quizzes on missed questions.')
            actions.append('Dedicate 2 additional study hours weekly to this topic.')
        else:
            actions.append('Continue current study habits and progress to extension topics.')

        result = {
            'predicted_difficulty': pred_class,
            'difficulty_score': round(diff_score, 4),
            'probability_low': round(prob_dict['Low'], 4),
            'probability_moderate': round(prob_dict['Moderate'], 4),
            'probability_high': round(prob_dict['High'], 4),
            'contributing_factors': factors,
            'recommended_actions': actions,
            'model_version': self.version_tag,
            'timestamp': datetime.utcnow().isoformat()
        }

        if adapter_meta and adapter_meta.get('adapter_applied'):
            result['adapter_metadata'] = adapter_meta

        return result
