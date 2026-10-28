from flask import Blueprint, request, jsonify
from backend.models.support import StudyRecommendation
from backend.models.academic import Subject
from backend.services.recommendation_service import RecommendationService
from backend.utils.decorators import token_required

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/my-recommendations', methods=['GET'])
@token_required
def get_my_recommendations():
    status = request.args.get('status')  # 'completed' or 'pending'
    query = StudyRecommendation.query.filter_by(student_id=request.current_user.id)
    
    if status == 'completed':
        query = query.filter_by(is_completed=True)
    elif status == 'pending':
        query = query.filter_by(is_completed=False)

    recs = query.order_by(StudyRecommendation.created_at.desc()).all()
    return jsonify({'recommendations': [r.to_dict() for r in recs]}), 200

@recommendations_bp.route('/student/<int:student_id>', methods=['GET'])
@token_required
def get_student_recommendations(student_id):
    if request.current_user.role == 'student' and request.current_user.id != student_id:
        return jsonify({'error': 'Unauthorized to view other students recommendations'}), 403

    query = StudyRecommendation.query.filter_by(student_id=student_id)

    # If instructor, restrict to subjects they teach
    if request.current_user.role == 'instructor':
        taught_ids = [s.id for s in Subject.query.filter_by(instructor_id=request.current_user.id).all()]
        query = query.filter(StudyRecommendation.subject_id.in_(taught_ids))

    recs = query.order_by(StudyRecommendation.created_at.desc()).all()
    return jsonify({'recommendations': [r.to_dict() for r in recs]}), 200

@recommendations_bp.route('/<int:rec_id>/complete', methods=['PUT'])
@token_required
def mark_completed(rec_id):
    rec, err = RecommendationService.mark_completed(rec_id, request.current_user.id)
    if err:
        return jsonify({'error': err}), 400
    return jsonify({'message': 'Recommendation marked as completed', 'recommendation': rec.to_dict()}), 200
