from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from backend.models.academic import StudentAssessmentResult, Assessment, Subject, Topic
from backend.models.ml_records import PredictionRecord
from backend.models.support import StudyRecommendation
from backend.utils.decorators import token_required

progress_bp = Blueprint('progress', __name__)

def build_student_progress_summary(student_id, allowed_subject_ids=None):
    # Assessment scores chronologically
    query = (
        StudentAssessmentResult.query
        .join(Assessment, StudentAssessmentResult.assessment_id == Assessment.id)
        .filter(StudentAssessmentResult.student_id == student_id)
    )

    if allowed_subject_ids is not None:
        query = query.filter(Assessment.subject_id.in_(allowed_subject_ids))

    results = query.order_by(StudentAssessmentResult.submission_date.asc(), StudentAssessmentResult.created_at.asc()).all()

    timeline = []
    subject_scores = {}
    for r in results:
        sub_name = r.assessment.subject.name if r.assessment and r.assessment.subject else 'General'
        timeline.append({
            'date': r.submission_date.isoformat() if r.submission_date else r.created_at.strftime('%Y-%m-%d'),
            'assessment_title': r.assessment.title if r.assessment else 'Assessment',
            'assessment_type': r.assessment.assessment_type if r.assessment else 'quiz',
            'percentage': round(r.percentage, 2),
            'subject_name': sub_name,
            'topic_name': r.assessment.topic.name if (r.assessment and r.assessment.topic) else None
        })
        if sub_name not in subject_scores:
            subject_scores[sub_name] = []
        subject_scores[sub_name].append(r.percentage)

    # Subject averages
    subject_summary = []
    for sub, scores in subject_scores.items():
        subject_summary.append({
            'subject_name': sub,
            'average_score': round(sum(scores) / len(scores), 1),
            'assessment_count': len(scores),
            'latest_score': round(scores[-1], 1)
        })

    # Historical predictions
    pred_query = PredictionRecord.query.filter_by(student_id=student_id)
    if allowed_subject_ids is not None:
        pred_query = pred_query.filter(PredictionRecord.subject_id.in_(allowed_subject_ids))

    preds = pred_query.order_by(PredictionRecord.created_at.asc()).all()
    
    pred_timeline = []
    for p in preds:
        pred_timeline.append({
            'date': p.created_at.strftime('%Y-%m-%d'),
            'topic_name': p.topic.name if p.topic else 'Topic',
            'subject_name': p.subject.name if p.subject else 'Subject',
            'predicted_difficulty': p.predicted_difficulty,
            'difficulty_score': round(p.difficulty_score * 100, 1),
            'probability_high': round(p.probability_high * 100, 1)
        })

    # Topic difficulty breakdown
    difficulty_counts = {'Low': 0, 'Moderate': 0, 'High': 0}
    # Latest prediction per topic
    latest_per_topic = {}
    for p in preds:
        latest_per_topic[p.topic_id] = p.predicted_difficulty
    for diff in latest_per_topic.values():
        if diff in difficulty_counts:
            difficulty_counts[diff] += 1

    # Recommendation completion stats
    rec_query = StudyRecommendation.query.filter_by(student_id=student_id)
    if allowed_subject_ids is not None:
        rec_query = rec_query.filter(StudyRecommendation.subject_id.in_(allowed_subject_ids))

    recs = rec_query.all()
    total_recs = len(recs)
    completed_recs = sum(1 for rec in recs if rec.is_completed)

    return {
        'timeline': timeline,
        'subject_summary': subject_summary,
        'prediction_timeline': pred_timeline,
        'difficulty_breakdown': difficulty_counts,
        'recommendation_progress': {
            'total': total_recs,
            'completed': completed_recs,
            'completion_rate': round(completed_recs / total_recs * 100, 1) if total_recs > 0 else 0.0
        }
    }

@progress_bp.route('/my-progress', methods=['GET'])
@token_required
def get_my_progress():
    data = build_student_progress_summary(request.current_user.id)
    return jsonify({'progress': data}), 200

@progress_bp.route('/student/<int:student_id>', methods=['GET'])
@token_required
def get_student_progress(student_id):
    if request.current_user.role == 'student' and request.current_user.id != student_id:
        return jsonify({'error': 'Unauthorized to view other students progress'}), 403

    allowed_subjects = None
    if request.current_user.role == 'instructor':
        allowed_subjects = [s.id for s in Subject.query.filter_by(instructor_id=request.current_user.id).all()]

    data = build_student_progress_summary(student_id, allowed_subject_ids=allowed_subjects)
    return jsonify({'progress': data}), 200
