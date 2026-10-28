from flask import Blueprint, request, jsonify
from backend.extensions import db
from backend.models.academic import Subject, Topic
from backend.utils.decorators import token_required, roles_required

subjects_bp = Blueprint('subjects', __name__)

@subjects_bp.route('', methods=['GET'])
@token_required
def get_subjects():
    user = request.current_user
    # Instructors can see all or their own, students can see all offered subjects
    if user.role == 'instructor' and request.args.get('only_mine') == 'true':
        subjects = Subject.query.filter_by(instructor_id=user.id).order_by(Subject.name.asc()).all()
    else:
        subjects = Subject.query.order_by(Subject.name.asc()).all()

    return jsonify({'subjects': [s.to_dict() for s in subjects]}), 200

@subjects_bp.route('/<int:subject_id>', methods=['GET'])
@token_required
def get_subject_detail(subject_id):
    subject = db.session.get(Subject, subject_id)
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404

    topics = Topic.query.filter_by(subject_id=subject_id).order_by(Topic.order_index.asc()).all()
    data = subject.to_dict()
    data['topics'] = [t.to_dict() for t in topics]
    return jsonify({'subject': data}), 200

@subjects_bp.route('', methods=['POST'])
@token_required
@roles_required('instructor', 'admin')
def create_subject():
    data = request.get_json() or {}
    code = data.get('code', '').strip().upper()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()

    # Instructors can only assign themselves as instructor
    if request.current_user.role == 'instructor':
        instructor_id = request.current_user.id
    else:
        instructor_id = data.get('instructor_id') or request.current_user.id

    if not code or not name:
        return jsonify({'error': 'Subject code and name are required'}), 400

    if Subject.query.filter_by(code=code).first():
        return jsonify({'error': f'Subject with code {code} already exists'}), 409

    subject = Subject(
        code=code,
        name=name,
        description=description,
        instructor_id=instructor_id
    )
    db.session.add(subject)
    db.session.commit()

    return jsonify({'message': 'Subject created successfully', 'subject': subject.to_dict()}), 201

@subjects_bp.route('/<int:subject_id>', methods=['PUT'])
@token_required
@roles_required('instructor', 'admin')
def update_subject(subject_id):
    subject = db.session.get(Subject, subject_id)
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404

    # Instructor can only edit their own subject unless admin
    if request.current_user.role == 'instructor' and subject.instructor_id != request.current_user.id:
        return jsonify({'error': 'You can only edit subjects you teach'}), 403

    data = request.get_json() or {}
    if 'name' in data and data['name'].strip():
        subject.name = data['name'].strip()
    if 'description' in data:
        subject.description = data['description'].strip()
    if 'instructor_id' in data and request.current_user.role == 'admin':
        subject.instructor_id = data['instructor_id']

    db.session.commit()
    return jsonify({'message': 'Subject updated successfully', 'subject': subject.to_dict()}), 200

@subjects_bp.route('/<int:subject_id>', methods=['DELETE'])
@token_required
@roles_required('instructor', 'admin')
def delete_subject(subject_id):
    subject = db.session.get(Subject, subject_id)
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404

    if request.current_user.role == 'instructor' and subject.instructor_id != request.current_user.id:
        return jsonify({'error': 'You can only delete subjects you teach'}), 403

    db.session.delete(subject)
    db.session.commit()
    return jsonify({'message': 'Subject deleted successfully'}), 200

# Topic Routes
@subjects_bp.route('/<int:subject_id>/topics', methods=['GET'])
@token_required
def get_subject_topics(subject_id):
    topics = Topic.query.filter_by(subject_id=subject_id).order_by(Topic.order_index.asc()).all()
    return jsonify({'topics': [t.to_dict() for t in topics]}), 200

@subjects_bp.route('/<int:subject_id>/topics', methods=['POST'])
@token_required
@roles_required('instructor', 'admin')
def create_topic(subject_id):
    subject = db.session.get(Subject, subject_id)
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404

    if request.current_user.role == 'instructor' and subject.instructor_id != request.current_user.id:
        return jsonify({'error': 'You can only add topics to subjects you teach'}), 403

    data = request.get_json() or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    learning_objectives = data.get('learning_objectives', '').strip()
    difficulty_level = data.get('difficulty_level', 'intermediate').strip().lower()
    order_index = int(data.get('order_index', 1))
    resources = data.get('resources', '').strip()

    if not name:
        return jsonify({'error': 'Topic name is required'}), 400

    topic = Topic(
        subject_id=subject_id,
        name=name,
        description=description,
        learning_objectives=learning_objectives,
        difficulty_level=difficulty_level,
        order_index=order_index,
        resources=resources
    )
    db.session.add(topic)
    db.session.commit()

    return jsonify({'message': 'Topic created successfully', 'topic': topic.to_dict()}), 201

@subjects_bp.route('/topics/<int:topic_id>', methods=['PUT'])
@token_required
@roles_required('instructor', 'admin')
def update_topic(topic_id):
    topic = db.session.get(Topic, topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    if request.current_user.role == 'instructor' and topic.subject.instructor_id != request.current_user.id:
        return jsonify({'error': 'You can only modify topics for subjects you teach'}), 403

    data = request.get_json() or {}
    if 'name' in data: topic.name = data['name'].strip()
    if 'description' in data: topic.description = data['description'].strip()
    if 'learning_objectives' in data: topic.learning_objectives = data['learning_objectives'].strip()
    if 'difficulty_level' in data: topic.difficulty_level = data['difficulty_level'].strip().lower()
    if 'order_index' in data: topic.order_index = int(data['order_index'])
    if 'resources' in data: topic.resources = data['resources'].strip()

    db.session.commit()
    return jsonify({'message': 'Topic updated successfully', 'topic': topic.to_dict()}), 200

@subjects_bp.route('/topics/<int:topic_id>', methods=['DELETE'])
@token_required
@roles_required('instructor', 'admin')
def delete_topic(topic_id):
    topic = db.session.get(Topic, topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    if request.current_user.role == 'instructor' and topic.subject.instructor_id != request.current_user.id:
        return jsonify({'error': 'You can only delete topics for subjects you teach'}), 403

    db.session.delete(topic)
    db.session.commit()
    return jsonify({'message': 'Topic deleted successfully'}), 200
