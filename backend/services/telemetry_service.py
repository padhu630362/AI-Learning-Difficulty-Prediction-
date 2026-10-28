import hashlib
import logging
from datetime import datetime
from backend.extensions import db
from backend.models.ml_records import OutlierTelemetryRecord
from backend.models.academic import Subject

logger = logging.getLogger('outlier_telemetry')

class TelemetryService:
    """
    Telemetry Service for detecting, anonymizing, and logging out-of-range student features.
    
    Protects against silent clamping of extreme observations (e.g. study time > 28h, errors > 15)
    while strictly preserving student privacy by recording SHA-256 pseudonymized identifiers
    rather than raw student PII.
    """

    @staticmethod
    def pseudonymize_student_id(student_id: int) -> str:
        """Computes a one-way deterministic pseudonym for privacy preservation."""
        if not student_id:
            return "anon_unknown"
        return hashlib.sha256(f"ai_pred_student_salt_{student_id}".encode()).hexdigest()[:16]

    @classmethod
    def record_outlier(
        cls,
        student_id: int,
        feature_name: str,
        raw_value: float,
        clamped_value: float,
        threshold_description: str,
        topic_id: int = None,
        subject_id: int = None,
        context: str = 'feature_generation',
        flag_type: str = 'upper_bound_clamped'
    ):
        """
        Records an outlier telemetry event without blocking or breaking calling workflows.
        Logs structured telemetry and persists to database safely.
        """
        try:
            pseudo_id = cls.pseudonymize_student_id(student_id)
            
            logger.warning(
                f"[OUTLIER_TELEMETRY] Context={context} Feature={feature_name} "
                f"Raw={raw_value} Clamped={clamped_value} Flag={flag_type} "
                f"PseudoID={pseudo_id} TopicID={topic_id} SubjectID={subject_id} "
                f"Desc='{threshold_description}'"
            )

            record = OutlierTelemetryRecord(
                student_pseudo_id=pseudo_id,
                subject_id=subject_id,
                topic_id=topic_id,
                feature_name=feature_name,
                raw_value=float(raw_value),
                clamped_value=float(clamped_value),
                threshold_description=threshold_description,
                context=context,
                flag_type=flag_type,
                created_at=datetime.utcnow()
            )
            db.session.add(record)
            db.session.commit()
            return record
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to record outlier telemetry: {str(e)}")
            return None

    @classmethod
    def inspect_and_clamp_study_time(
        cls,
        raw_study_time: float,
        student_id: int,
        topic_id: int = None,
        subject_id: int = None,
        context: str = 'feature_generation'
    ) -> float:
        """
        Inspects weekly study time against canonical benchmark boundaries [1.0, 28.0].
        Logs telemetry if an outlier is detected and returns the safely clamped value.
        """
        try:
            val = float(raw_study_time)
        except (TypeError, ValueError):
            cls.record_outlier(
                student_id=student_id,
                feature_name='study_time_weekly',
                raw_value=0.0,
                clamped_value=8.0,
                threshold_description="Malformed or missing study time value; defaulted to baseline 8.0 hrs",
                topic_id=topic_id,
                subject_id=subject_id,
                context=context,
                flag_type='invalid_format'
            )
            return 8.0

        if val > 28.0:
            cls.record_outlier(
                student_id=student_id,
                feature_name='study_time_weekly',
                raw_value=val,
                clamped_value=28.0,
                threshold_description=f"Weekly study time ({val:.1f} hrs) exceeds canonical ceiling of 28.0 hrs",
                topic_id=topic_id,
                subject_id=subject_id,
                context=context,
                flag_type='upper_bound_clamped'
            )
            return 28.0
        elif val < 1.0:
            cls.record_outlier(
                student_id=student_id,
                feature_name='study_time_weekly',
                raw_value=val,
                clamped_value=1.0,
                threshold_description=f"Weekly study time ({val:.1f} hrs) is below canonical floor of 1.0 hr",
                topic_id=topic_id,
                subject_id=subject_id,
                context=context,
                flag_type='lower_bound_clamped'
            )
            return 1.0

        return val

    @classmethod
    def inspect_and_clamp_repeated_errors(
        cls,
        raw_errors: int,
        student_id: int,
        topic_id: int = None,
        subject_id: int = None,
        context: str = 'feature_generation'
    ) -> int:
        """
        Inspects repeated errors count against canonical benchmark boundary (max 15).
        Logs telemetry if an outlier is detected and returns the safely bounded value.
        """
        try:
            val = int(raw_errors)
        except (TypeError, ValueError):
            cls.record_outlier(
                student_id=student_id,
                feature_name='repeated_errors_count',
                raw_value=0.0,
                clamped_value=0.0,
                threshold_description="Malformed repeated errors count; defaulted to 0",
                topic_id=topic_id,
                subject_id=subject_id,
                context=context,
                flag_type='invalid_format'
            )
            return 0

        if val > 15:
            cls.record_outlier(
                student_id=student_id,
                feature_name='repeated_errors_count',
                raw_value=float(val),
                clamped_value=15.0,
                threshold_description=f"Repeated errors count ({val}) exceeds canonical maximum threshold of 15",
                topic_id=topic_id,
                subject_id=subject_id,
                context=context,
                flag_type='upper_bound_exceeded'
            )
            return min(val, 15)
        elif val < 0:
            cls.record_outlier(
                student_id=student_id,
                feature_name='repeated_errors_count',
                raw_value=float(val),
                clamped_value=0.0,
                threshold_description=f"Repeated errors count cannot be negative ({val}); clamped to 0",
                topic_id=topic_id,
                subject_id=subject_id,
                context=context,
                flag_type='lower_bound_clamped'
            )
            return 0

        return val

    @classmethod
    def get_outliers(
        cls,
        current_user,
        page: int = 1,
        per_page: int = 20,
        feature_name: str = None,
        subject_id: int = None
    ):
        """
        Queries outlier telemetry events with role-based access control.
        Instructors only see telemetry for subjects they teach.
        """
        query = OutlierTelemetryRecord.query

        if current_user.role == 'instructor':
            taught_ids = [s.id for s in Subject.query.filter_by(instructor_id=current_user.id).all()]
            query = query.filter(OutlierTelemetryRecord.subject_id.in_(taught_ids))
        elif current_user.role != 'admin':
            return {'records': [], 'total': 0, 'pages': 0, 'current_page': 1}

        if feature_name:
            query = query.filter_by(feature_name=feature_name)
        if subject_id:
            query = query.filter_by(subject_id=subject_id)

        pagination = query.order_by(OutlierTelemetryRecord.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            'records': [r.to_dict() for r in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        }

