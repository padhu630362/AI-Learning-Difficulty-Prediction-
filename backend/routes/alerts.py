from datetime import datetime
from flask import Blueprint, request, jsonify
from backend.extensions import db
from backend.models.support import InstructorAlert, AlertFollowUp
from backend.models.academic import Subject
from backend.models.user import User
from backend.utils.decorators import token_required, roles_required
from backend.services.alert_service import AlertService

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('', methods=['GET'])
@token_required
@roles_required('instructor', 'admin')
def get_alerts():
    is_reviewed_param = request.args.get('is_reviewed')
    severity = request.args.get('severity')
    subject_id = request.args.get('subject_id')

    query = InstructorAlert.query

    # If instructor, filter to subjects they teach (unless admin)
    if request.current_user.role == 'instructor':
        taught_subject_ids = [s.id for s in Subject.query.filter_by(instructor_id=request.current_user.id).all()]
        query = query.filter(
            (InstructorAlert.instructor_id == request.current_user.id) |
            (InstructorAlert.subject_id.in_(taught_subject_ids))
        )

    if is_reviewed_param is not None:
        is_rev = is_reviewed_param.lower() in ['true', '1']
        query = query.filter_by(is_reviewed=is_rev)

    if severity:
        query = query.filter_by(severity=severity)

    if subject_id:
        query = query.filter_by(subject_id=int(subject_id))

    alerts = query.order_by(InstructorAlert.created_at.desc()).all()
    
    # Enrich with follow-ups
    results = []
    for a in alerts:
        a_dict = a.to_dict()
        a_dict['follow_ups'] = [f.to_dict() for f in a.follow_ups]
        results.append(a_dict)

    return jsonify({'alerts': results}), 200

@alerts_bp.route('/<int:alert_id>/review', methods=['PUT'])
@token_required
@roles_required('instructor', 'admin')
def review_alert(alert_id):
    alert = db.session.get(InstructorAlert, alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404

    # Security check: Instructor can only review alerts for their subjects
    if request.current_user.role == 'instructor':
        if alert.instructor_id != request.current_user.id and (alert.subject and alert.subject.instructor_id != request.current_user.id):
            return jsonify({'error': 'Unauthorized: You can only review alerts for subjects you teach.'}), 403

    alert.is_reviewed = True
    alert.reviewed_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Alert marked as reviewed', 'alert': alert.to_dict()}), 200

@alerts_bp.route('/<int:alert_id>/follow-ups', methods=['POST'])
@token_required
@roles_required('instructor', 'admin')
def add_follow_up(alert_id):
    alert = db.session.get(InstructorAlert, alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404

    # Security check: Instructor can only add follow-ups for their subjects
    if request.current_user.role == 'instructor':
        if alert.instructor_id != request.current_user.id and (alert.subject and alert.subject.instructor_id != request.current_user.id):
            return jsonify({'error': 'Unauthorized: You can only log follow-ups for subjects you teach.'}), 403

    data = request.get_json() or {}
    action_taken = data.get('action_taken', '').strip()
    notes = data.get('notes', '').strip()
    outcome = data.get('outcome', 'pending').strip()

    if not action_taken:
        return jsonify({'error': 'action_taken is required'}), 400

    follow_up, err = AlertService.add_follow_up(
        alert_id=alert_id,
        instructor_id=request.current_user.id,
        action_taken=action_taken,
        notes=notes,
        outcome=outcome
    )
    if err:
        return jsonify({'error': err}), 400

    return jsonify({'message': 'Follow-up logged successfully', 'follow_up': follow_up.to_dict()}), 201

@alerts_bp.route('/scan', methods=['POST'])
@token_required
@roles_required('instructor', 'admin')
def scan_alerts():
    data = request.get_json() or {}
    subject_id = data.get('subject_id')

    if not subject_id:
        return jsonify({'error': 'subject_id is required'}), 400

    subject = db.session.get(Subject, int(subject_id))
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404

    # Security check: Instructor can only scan their own subjects
    if request.current_user.role == 'instructor' and subject.instructor_id != request.current_user.id:
        return jsonify({'error': 'Unauthorized: You can only scan subjects you teach.'}), 403

    students = User.query.filter_by(role='student', is_active=True).all()
    total_generated = 0

    for s in students:
        new_alerts = AlertService.evaluate_and_generate_alerts(
            student_id=s.id,
            subject_id=subject.id,
            instructor_id=subject.instructor_id
        )
        total_generated += len(new_alerts)

    return jsonify({
        'message': f'Early support scan completed for {subject.code}. Generated {total_generated} new alerts.',
        'new_alerts_count': total_generated
    }), 200
