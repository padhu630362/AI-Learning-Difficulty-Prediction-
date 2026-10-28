import os
import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import joblib
import pandas as pd
import numpy as np

from flask import current_app
from backend.extensions import db
from backend.models.ml_records import ShadowAuditRecord, SystemSetting
from backend.models.academic import Subject
from backend.ml.preprocessor import MLDataPreprocessor, REQUIRED_FEATURES
from backend.ml.adapters import get_feature_adapter

logger = logging.getLogger('shadow_inference')

# Background executor for non-blocking asynchronous shadow predictions
_shadow_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="shadow_worker")

class CandidateModelCache:
    """
    In-memory isolated cache for candidate models used during shadow evaluation.
    Guarantees that candidate inference operates entirely separately from
    the root active production model singleton.
    """
    _cache = {}

    @classmethod
    def get_candidate(cls, version_tag: str, artifacts_dir: str):
        if version_tag in cls._cache:
            return cls._cache[version_tag]

        version_dir = os.path.join(artifacts_dir, 'versions', version_tag)
        model_path = os.path.join(version_dir, 'model.joblib')
        preproc_path = os.path.join(version_dir, 'preprocessor.joblib')

        if not os.path.exists(model_path) or not os.path.exists(preproc_path):
            raise FileNotFoundError(
                f"Candidate artifacts for '{version_tag}' not found at: {version_dir}"
            )

        model = joblib.load(model_path)
        preprocessor = MLDataPreprocessor.load(preproc_path)
        candidate_obj = {
            'model': model,
            'preprocessor': preprocessor,
            'version_tag': version_tag
        }
        cls._cache[version_tag] = candidate_obj
        return candidate_obj

    @classmethod
    def clear(cls):
        cls._cache.clear()

class ShadowService:
    """
    Manages asynchronous shadow-mode inference, audit telemetry logging,
    and instructor pilot reviews for candidate ML models.
    """

    @classmethod
    def is_shadow_mode_enabled(cls) -> bool:
        """
        Checks whether shadow inference is enabled.
        Defaults to False (disabled by default) unless explicitly enabled in database or config.
        """
        try:
            setting = SystemSetting.query.filter_by(key='shadow_mode_enabled').first()
            if setting:
                return setting.value.strip().lower() in ['true', '1', 'yes']
        except Exception:
            pass

        return current_app.config.get('SHADOW_MODE_ENABLED', False)

    @classmethod
    def get_shadow_candidate_version(cls) -> str:
        """Returns the configured candidate model version tag for shadow evaluation."""
        try:
            setting = SystemSetting.query.filter_by(key='shadow_candidate_version').first()
            if setting and setting.value:
                return setting.value.strip()
        except Exception:
            pass

        return current_app.config.get('SHADOW_CANDIDATE_VERSION', 'lms_canonical_v1')

    @classmethod
    def set_shadow_mode(cls, enabled: bool, candidate_version: str = None, user_id: int = None) -> dict:
        """
        Enables or disables shadow mode. Restricted to authorized administrators.
        Does NOT activate the candidate model in production.
        """
        # Shadow mode flag setting
        setting_flag = SystemSetting.query.filter_by(key='shadow_mode_enabled').first()
        if not setting_flag:
            setting_flag = SystemSetting(key='shadow_mode_enabled')
            db.session.add(setting_flag)
        setting_flag.value = 'true' if enabled else 'false'
        setting_flag.description = 'Feature flag for asynchronous candidate shadow inference'
        setting_flag.updated_at = datetime.utcnow()
        setting_flag.updated_by = user_id

        # Candidate version setting if provided
        if candidate_version:
            setting_ver = SystemSetting.query.filter_by(key='shadow_candidate_version').first()
            if not setting_ver:
                setting_ver = SystemSetting(key='shadow_candidate_version')
                db.session.add(setting_ver)
            setting_ver.value = candidate_version
            setting_ver.description = 'Candidate model version evaluated in shadow mode'
            setting_ver.updated_at = datetime.utcnow()
            setting_ver.updated_by = user_id

        db.session.commit()
        return cls.get_shadow_status()

    @classmethod
    def get_shadow_status(cls) -> dict:
        """Returns the current shadow mode status and summary telemetry."""
        enabled = cls.is_shadow_mode_enabled()
        cand_ver = cls.get_shadow_candidate_version()

        artifacts_dir = current_app.config.get('ARTIFACTS_FOLDER', '')
        version_dir = os.path.join(artifacts_dir, 'versions', cand_ver)
        artifacts_exist = os.path.exists(os.path.join(version_dir, 'model.joblib'))

        total_shadow = ShadowAuditRecord.query.count()
        disagreements = ShadowAuditRecord.query.filter_by(disagreement=True).count()
        successes = ShadowAuditRecord.query.filter_by(execution_status='success').count()
        failures = ShadowAuditRecord.query.filter_by(execution_status='failed').count()

        disagreement_rate = (disagreements / total_shadow * 100.0) if total_shadow > 0 else 0.0

        return {
            'shadow_mode_enabled': enabled,
            'candidate_model_version': cand_ver,
            'candidate_artifacts_exist': artifacts_exist,
            'total_shadow_predictions': total_shadow,
            'successful_executions': successes,
            'failed_executions': failures,
            'disagreements_count': disagreements,
            'disagreement_rate_pct': round(disagreement_rate, 2),
            'disagreement_disclaimer': (
                "Model agreement is a comparative telemetry metric and does not constitute "
                "proof of ground-truth diagnostic correctness."
            )
        }

    @classmethod
    def dispatch_async_shadow_inference(
        cls,
        app,
        production_record_id: int,
        student_id: int,
        subject_id: int,
        topic_id: int,
        features: dict,
        production_version: str,
        production_prediction: str
    ):
        """
        Dispatches candidate model inference asynchronously in a background thread.
        Guarantees that production API response latency and reliability are completely unaffected.
        """
        cand_ver = cls.get_shadow_candidate_version()
        artifacts_dir = app.config['ARTIFACTS_FOLDER']

        def _async_task():
            with app.app_context():
                start_time = time.perf_counter()
                try:
                    candidate = CandidateModelCache.get_candidate(cand_ver, artifacts_dir)
                    model = candidate['model']
                    preprocessor = candidate['preprocessor']

                    # Apply adapter if registered for candidate version (IdentityAdapter for canonical)
                    adapter = get_feature_adapter(cand_ver)
                    adapted_features, _ = adapter.transform_features(features)

                    df_input = pd.DataFrame([adapted_features])
                    X_trans = preprocessor.transform(df_input)

                    pred_class = model.predict(X_trans)[0]

                    prob_dict = {'Low': 0.0, 'Moderate': 0.0, 'High': 0.0}
                    if hasattr(model, 'predict_proba'):
                        probs = model.predict_proba(X_trans)[0]
                        for c_name, p in zip(model.classes_, probs):
                            prob_dict[c_name] = float(p)
                    else:
                        prob_dict[pred_class] = 1.0

                    diff_score = (prob_dict.get('Moderate', 0.0) * 0.5) + (prob_dict.get('High', 0.0) * 1.0)
                    latency_ms = (time.perf_counter() - start_time) * 1000.0

                    disagreement = (production_prediction != pred_class)

                    audit_rec = ShadowAuditRecord(
                        production_record_id=production_record_id,
                        student_id=student_id,
                        subject_id=subject_id,
                        topic_id=topic_id,
                        production_model_version=production_version,
                        production_prediction=production_prediction,
                        candidate_model_version=cand_ver,
                        candidate_prediction=pred_class,
                        candidate_difficulty_score=diff_score,
                        candidate_prob_low=prob_dict.get('Low', 0.0),
                        candidate_prob_moderate=prob_dict.get('Moderate', 0.0),
                        candidate_prob_high=prob_dict.get('High', 0.0),
                        disagreement=disagreement,
                        execution_status='success',
                        error_message=None,
                        latency_ms=latency_ms,
                        label='Pilot Estimate — Requires Instructor Review',
                        created_at=datetime.utcnow()
                    )
                    db.session.add(audit_rec)
                    db.session.commit()

                    logger.info(
                        f"[SHADOW_SUCCESS] RecordID={production_record_id} Prod={production_prediction} "
                        f"Cand={pred_class} Disagreement={disagreement} Latency={latency_ms:.2f}ms"
                    )

                except Exception as e:
                    db.session.rollback()
                    latency_ms = (time.perf_counter() - start_time) * 1000.0
                    err_msg = str(e)
                    logger.error(f"[SHADOW_FAILURE] Error during shadow inference: {err_msg}")
                    try:
                        failed_rec = ShadowAuditRecord(
                            production_record_id=production_record_id,
                            student_id=student_id,
                            subject_id=subject_id,
                            topic_id=topic_id,
                            production_model_version=production_version,
                            production_prediction=production_prediction,
                            candidate_model_version=cand_ver,
                            candidate_prediction=None,
                            execution_status='failed',
                            error_message=err_msg[:500],
                            latency_ms=latency_ms,
                            label='Pilot Estimate — Execution Failed',
                            created_at=datetime.utcnow()
                        )
                        db.session.add(failed_rec)
                        db.session.commit()
                    except Exception as inner_e:
                        db.session.rollback()
                        logger.error(f"[SHADOW_FATAL] Failed to write failure audit record: {inner_e}")

        # Submit background task
        _shadow_executor.submit(_async_task)

    @classmethod
    def record_instructor_review(
        cls,
        record_id: int,
        instructor_user,
        decision: str,
        notes: str = None
    ) -> tuple:
        """
        Records an instructor's review decision for a pilot candidate prediction.
        
        Enforces authorization: Instructors can only review predictions for subjects they teach.
        Permitted decisions: 'confirmed', 'disagreement', 'needs_more_information'
        
        Guarantees:
        - NEVER generates an alert or study recommendation.
        - NEVER modifies student academic status.
        """
        record = db.session.get(ShadowAuditRecord, record_id)
        if not record:
            return None, "Pilot prediction record not found", 404

        # Authorization check
        if instructor_user.role == 'instructor':
            if record.subject.instructor_id != instructor_user.id:
                return None, "Unauthorized: You can only review predictions for subjects you teach.", 403
        elif instructor_user.role != 'admin':
            return None, "Unauthorized: Only instructors and administrators may submit pilot reviews.", 403

        normalized_decision = decision.strip().lower()
        valid_decisions = ['confirmed', 'disagreement', 'needs_more_information', 'disagreed']
        if normalized_decision not in valid_decisions:
            return None, f"Invalid decision. Must be one of: {valid_decisions}", 400

        if normalized_decision == 'disagreed':
            normalized_decision = 'disagreement'

        record.review_decision = normalized_decision
        record.review_notes = notes.strip() if notes else None
        record.reviewed_by = instructor_user.id
        record.reviewed_at = datetime.utcnow()
        record.label = f"Pilot Estimate — {normalized_decision.replace('_', ' ').title()}"

        db.session.commit()
        return record.to_dict(), None, 200

    @classmethod
    def get_pilot_reviews(
        cls,
        current_user,
        page: int = 1,
        per_page: int = 20,
        subject_id: int = None,
        topic_id: int = None,
        review_decision: str = None,
        disagreement: bool = None
    ) -> dict:
        """
        Retrieves paginated pilot estimates and review records with strict access controls.
        Instructors only see records for subjects they teach.
        """
        query = ShadowAuditRecord.query

        if current_user.role == 'instructor':
            taught_ids = [s.id for s in Subject.query.filter_by(instructor_id=current_user.id).all()]
            query = query.filter(ShadowAuditRecord.subject_id.in_(taught_ids))
        elif current_user.role != 'admin':
            return {'records': [], 'total': 0, 'pages': 0, 'current_page': 1}

        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        if topic_id:
            query = query.filter_by(topic_id=topic_id)
        if review_decision:
            if review_decision == 'pending':
                query = query.filter(ShadowAuditRecord.review_decision.is_(None))
            else:
                query = query.filter_by(review_decision=review_decision)
        if disagreement is not None:
            query = query.filter_by(disagreement=disagreement)

        pagination = query.order_by(ShadowAuditRecord.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            'records': [r.to_dict() for r in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        }

