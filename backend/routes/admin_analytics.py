from flask import Blueprint, jsonify
from backend.models.user import User
from backend.models.academic import Subject, Topic, Assessment, StudentAssessmentResult
from backend.models.ml_records import PredictionRecord, ModelVersion, DatasetRecord
from backend.models.support import InstructorAlert, AuditEvent
from backend.utils.decorators import token_required, roles_required

admin_bp = Blueprint('admin_analytics', __name__)

@admin_bp.route('/overview', methods=['GET'])
@token_required
@roles_required('admin')
def get_system_overview():
    total_students = User.query.filter_by(role='student').count()
    total_instructors = User.query.filter_by(role='instructor').count()
    total_admins = User.query.filter_by(role='admin').count()

    total_subjects = Subject.query.count()
    total_topics = Topic.query.count()
    total_assessments = Assessment.query.count()
    total_submissions = StudentAssessmentResult.query.count()

    total_predictions = PredictionRecord.query.count()
    low_preds = PredictionRecord.query.filter_by(predicted_difficulty='Low').count()
    mod_preds = PredictionRecord.query.filter_by(predicted_difficulty='Moderate').count()
    high_preds = PredictionRecord.query.filter_by(predicted_difficulty='High').count()

    active_model = ModelVersion.query.filter_by(is_active=True).first()
    
    total_alerts = InstructorAlert.query.count()
    pending_alerts = InstructorAlert.query.filter_by(is_reviewed=False).count()
    datasets_count = DatasetRecord.query.count()

    return jsonify({
        'users': {
            'total': total_students + total_instructors + total_admins,
            'students': total_students,
            'instructors': total_instructors,
            'admins': total_admins
        },
        'academics': {
            'subjects': total_subjects,
            'topics': total_topics,
            'assessments': total_assessments,
            'submissions': total_submissions
        },
        'predictions': {
            'total': total_predictions,
            'low': low_preds,
            'moderate': mod_preds,
            'high': high_preds
        },
        'alerts': {
            'total': total_alerts,
            'pending': pending_alerts,
            'reviewed': total_alerts - pending_alerts
        },
        'datasets_count': datasets_count,
        'active_model': active_model.to_dict() if active_model else None
    }), 200

@admin_bp.route('/audit-logs', methods=['GET'])
@token_required
@roles_required('admin')
def get_audit_logs():
    logs = AuditEvent.query.order_by(AuditEvent.created_at.desc()).limit(100).all()
    return jsonify({'logs': [l.to_dict() for l in logs]}), 200

