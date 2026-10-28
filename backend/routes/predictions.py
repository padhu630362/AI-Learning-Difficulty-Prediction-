from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy import func
from backend.extensions import db
from backend.models.academic import Subject, Topic, Assessment, StudentAssessmentResult
from backend.models.ml_records import PredictionRecord
from backend.models.user import User
from backend.utils.decorators import token_required, roles_required
from backend.ml.predictor import MLPredictor
from backend.services.recommendation_service import RecommendationService
from backend.services.alert_service import AlertService
from backend.services.telemetry_service import TelemetryService
from backend.services.shadow_service import ShadowService, CandidateModelCache
from backend.ml.adapters import get_feature_adapter
import pandas as pd

predictions_bp = Blueprint('predictions', __name__)

def compute_student_topic_features(student_id, topic_id):
    """
    Aggregates student academic records into an ML feature vector for a specific topic.
    Returns (features_dict, None) if sufficient records exist, or (None, error_code) if
    insufficient data is available.
    """
    topic = db.session.get(Topic, topic_id)
    if not topic:
        return None, "topic_not_found"

    # Fetch assessment results for this student and topic
    results = (
        StudentAssessmentResult.query
        .join(Assessment, StudentAssessmentResult.assessment_id == Assessment.id)
        .filter(StudentAssessmentResult.student_id == student_id, Assessment.topic_id == topic_id)
        .all()
    )

    # Fetch subject-wide results
    subject_results = (
        StudentAssessmentResult.query
        .join(Assessment, StudentAssessmentResult.assessment_id == Assessment.id)
        .filter(StudentAssessmentResult.student_id == student_id, Assessment.subject_id == topic.subject_id)
        .all()
    )

    # Check if student has zero academic records in this subject
    if not results and not subject_results:
        return None, "insufficient_data"

    quizzes = [r.percentage for r in results if r.assessment and r.assessment.assessment_type == 'quiz']
    assignments = [r.percentage for r in results if r.assessment and r.assessment.assessment_type == 'assignment']
    exams = [r.percentage for r in subject_results if r.assessment and r.assessment.assessment_type == 'exam']

    # Fallback to general subject baseline if topic-specific category is empty
    general_pct = [r.percentage for r in subject_results]
    baseline_pct = sum(general_pct) / len(general_pct) if general_pct else 70.0

    quiz_score = sum(quizzes) / len(quizzes) if quizzes else baseline_pct
    assignment_score = sum(assignments) / len(assignments) if assignments else baseline_pct
    exam_score = sum(exams) / len(exams) if exams else baseline_pct

    # Study time in weekly hours
    study_mins = [r.study_time_minutes for r in results if r.study_time_minutes]
    if not study_mins and subject_results:
        study_mins = [r.study_time_minutes for r in subject_results if r.study_time_minutes]
    raw_study_time = (sum(study_mins) / len(study_mins)) / 60.0 * 7 if study_mins else 8.0
    study_time_weekly = TelemetryService.inspect_and_clamp_study_time(
        raw_study_time,
        student_id=student_id,
        topic_id=topic_id,
        subject_id=topic.subject_id,
        context='feature_generation'
    )

    # Attempts & errors
    attempts = [r.attempt_count for r in results if r.attempt_count]
    attempt_count = int(max(attempts)) if attempts else 1

    errors = [r.repeated_errors_count for r in results if r.repeated_errors_count]
    raw_errors = int(sum(errors)) if errors else 0
    repeated_errors_count = TelemetryService.inspect_and_clamp_repeated_errors(
        raw_errors,
        student_id=student_id,
        topic_id=topic_id,
        subject_id=topic.subject_id,
        context='feature_generation'
    )

    # Attendance/completion
    total_assigned = len(results) if results else len(subject_results)
    completed_count = sum(1 for r in (results or subject_results) if r.completion_status == 'completed')
    attendance_rate = (completed_count / total_assigned * 100.0) if total_assigned > 0 else 85.0

    # Previous topic mastery
    prev_topic = Topic.query.filter(
        Topic.subject_id == topic.subject_id,
        Topic.order_index < topic.order_index
    ).order_by(Topic.order_index.desc()).first()

    previous_topic_score = baseline_pct
    if prev_topic:
        prev_results = (
            StudentAssessmentResult.query
            .join(Assessment, StudentAssessmentResult.assessment_id == Assessment.id)
            .filter(StudentAssessmentResult.student_id == student_id, Assessment.topic_id == prev_topic.id)
            .all()
        )
        if prev_results:
            previous_topic_score = sum(r.percentage for r in prev_results) / len(prev_results)

    learning_pace_gap = round((quiz_score * 0.5 + assignment_score * 0.5) - 70.0, 1)

    return {
        'quiz_score': round(quiz_score, 1),
        'assignment_score': round(assignment_score, 1),
        'exam_score': round(exam_score, 1),
        'study_time_weekly': round(study_time_weekly, 1),
        'attendance_rate': round(attendance_rate, 1),
        'attempt_count': attempt_count,
        'repeated_errors_count': repeated_errors_count,
        'previous_topic_score': round(previous_topic_score, 1),
        'learning_pace_gap': learning_pace_gap,
        'topic_difficulty_level': topic.difficulty_level or 'intermediate'
    }, None

@predictions_bp.route('/predict', methods=['POST'])
@token_required
def predict():
    predictor = MLPredictor.get_instance()
    if not predictor.is_ready():
        return jsonify({
            'error': 'ML prediction model is not trained yet. Please train or upload a model first.'
        }), 503

    data = request.get_json() or {}
    student_id = data.get('student_id')
    topic_id = data.get('topic_id')
    manual_features = data.get('features')

    # Security check: Student can only request prediction for themselves
    if request.current_user.role == 'student':
        student_id = request.current_user.id
    elif not student_id:
        student_id = request.current_user.id

    student = db.session.get(User, student_id)
    if not student or student.role != 'student':
        return jsonify({'error': 'Student not found'}), 404

    topic = db.session.get(Topic, topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    # Security check: Instructor can only predict for subjects they teach
    if request.current_user.role == 'instructor' and topic.subject.instructor_id != request.current_user.id:
        return jsonify({'error': 'Unauthorized: You can only predict for subjects and topics you teach.'}), 403

    # Determine features: either explicit (simulation) or auto-aggregated from database
    is_simulated = False
    if manual_features and isinstance(manual_features, dict):
        is_simulated = True
        features = manual_features
        if 'topic_difficulty_level' not in features:
            features['topic_difficulty_level'] = topic.difficulty_level or 'intermediate'
    else:
        features, err_code = compute_student_topic_features(student_id, topic_id)
        if err_code == "insufficient_data":
            return jsonify({
                'error': f"Insufficient academic records: student '{student.full_name}' has no logged quiz, assignment, or examination results in '{topic.subject.name}'. At least one assessment score is required to generate an empirical ML difficulty prediction.",
                'code': 'insufficient_data',
                'insufficient_data': True,
                'topic_id': topic.id,
                'topic_name': topic.name,
                'subject_name': topic.subject.name
            }), 422

    try:
        pred_output = predictor.predict_features(
            features,
            context={'student_id': student_id, 'topic_id': topic.id, 'subject_id': topic.subject_id}
        )
    except ValueError as ve:
        return jsonify({'error': f'Invalid prediction features: {str(ve)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Prediction engine failed: {str(e)}'}), 500

    # Persist prediction record
    pred_record = PredictionRecord(
        student_id=student_id,
        subject_id=topic.subject_id,
        topic_id=topic.id,
        predicted_difficulty=pred_output['predicted_difficulty'],
        difficulty_score=pred_output['difficulty_score'],
        probability_low=pred_output['probability_low'],
        probability_moderate=pred_output['probability_moderate'],
        probability_high=pred_output['probability_high'],
        contributing_factors=pred_output['contributing_factors'],
        model_version=pred_output['model_version']
    )
    db.session.add(pred_record)
    db.session.commit()

    # Generate study recommendations (with de-duplication)
    recs = RecommendationService.generate_recommendations_for_prediction(
        student_id=student_id,
        subject_id=topic.subject_id,
        topic_id=topic.id,
        prediction_record=pred_record
    )

    # Check early support alerts if high difficulty
    AlertService.evaluate_and_generate_alerts(
        student_id=student_id,
        subject_id=topic.subject_id,
        instructor_id=topic.subject.instructor_id,
        prediction=pred_record
    )

    # Trigger asynchronous shadow inference if enabled (Never blocks, never creates alerts)
    if ShadowService.is_shadow_mode_enabled():
        from flask import current_app
        ShadowService.dispatch_async_shadow_inference(
            app=current_app._get_current_object(),
            production_record_id=pred_record.id,
            student_id=student_id,
            subject_id=topic.subject_id,
            topic_id=topic.id,
            features=features,
            production_version=pred_output['model_version'],
            production_prediction=pred_output['predicted_difficulty']
        )

    response_data = pred_record.to_dict()
    response_data['recommendations'] = [r.to_dict() for r in recs]
    response_data['features_used'] = features
    response_data['is_simulated'] = is_simulated

    return jsonify({
        'message': 'Prediction generated successfully',
        'prediction': response_data
    }), 201

@predictions_bp.route('/my-predictions', methods=['GET'])
@token_required
def get_my_predictions():
    subject_id = request.args.get('subject_id')
    query = PredictionRecord.query.filter_by(student_id=request.current_user.id)
    if subject_id:
        query = query.filter_by(subject_id=subject_id)

    predictions = query.order_by(PredictionRecord.created_at.desc()).all()
    return jsonify({'predictions': [p.to_dict() for p in predictions]}), 200

@predictions_bp.route('/student/<int:student_id>', methods=['GET'])
@token_required
def get_student_predictions(student_id):
    # Student can only view their own
    if request.current_user.role == 'student' and request.current_user.id != student_id:
        return jsonify({'error': 'Unauthorized'}), 403

    query = PredictionRecord.query.filter_by(student_id=student_id)

    # If instructor, restrict to subjects they teach
    if request.current_user.role == 'instructor':
        taught_subject_ids = [s.id for s in Subject.query.filter_by(instructor_id=request.current_user.id).all()]
        query = query.filter(PredictionRecord.subject_id.in_(taught_subject_ids))

    subject_id = request.args.get('subject_id')
    if subject_id:
        query = query.filter_by(subject_id=subject_id)

    predictions = query.order_by(PredictionRecord.created_at.desc()).all()
    return jsonify({'predictions': [p.to_dict() for p in predictions]}), 200

@predictions_bp.route('/history', methods=['GET'])
@token_required
@roles_required('instructor', 'admin')
def get_prediction_history():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    subject_id = request.args.get('subject_id')
    difficulty = request.args.get('difficulty')

    query = PredictionRecord.query

    # If instructor, restrict to subjects they teach
    if request.current_user.role == 'instructor':
        taught_subject_ids = [s.id for s in Subject.query.filter_by(instructor_id=request.current_user.id).all()]
        query = query.filter(PredictionRecord.subject_id.in_(taught_subject_ids))

    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    if difficulty:
        query = query.filter_by(predicted_difficulty=difficulty)

    pagination = query.order_by(PredictionRecord.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'predictions': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    }), 200

@predictions_bp.route('/batch-predict-topic/<int:topic_id>', methods=['POST'])
@token_required
@roles_required('instructor', 'admin')
def batch_predict_topic(topic_id):
    predictor = MLPredictor.get_instance()
    if not predictor.is_ready():
        return jsonify({'error': 'ML model is not ready. Train model first.'}), 503

    topic = db.session.get(Topic, topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404

    # Security check: Instructor can only batch predict topics for subjects they teach
    if request.current_user.role == 'instructor' and topic.subject.instructor_id != request.current_user.id:
        return jsonify({'error': 'Unauthorized: You can only batch predict for topics you teach.'}), 403

    # Fetch active students
    students = User.query.filter_by(role='student', is_active=True).all()
    generated = []

    for s in students:
        features, err_code = compute_student_topic_features(s.id, topic_id)
        if not features:
            continue
        try:
            pred_output = predictor.predict_features(features)
            pred_record = PredictionRecord(
                student_id=s.id,
                subject_id=topic.subject_id,
                topic_id=topic.id,
                predicted_difficulty=pred_output['predicted_difficulty'],
                difficulty_score=pred_output['difficulty_score'],
                probability_low=pred_output['probability_low'],
                probability_moderate=pred_output['probability_moderate'],
                probability_high=pred_output['probability_high'],
                contributing_factors=pred_output['contributing_factors'],
                model_version=pred_output['model_version']
            )
            db.session.add(pred_record)
            generated.append(pred_record)
        except Exception:
            continue

    db.session.commit()

    # Generate recommendations & alerts for all
    for rec in generated:
        RecommendationService.generate_recommendations_for_prediction(
            rec.student_id, topic.subject_id, topic.id, rec
        )
        if rec.predicted_difficulty == 'High':
            AlertService.evaluate_and_generate_alerts(
                rec.student_id, topic.subject_id, topic.subject.instructor_id, rec
            )

    return jsonify({
        'message': f'Cohort prediction completed for {len(generated)} students.',
        'count': len(generated)
    }), 200

# -----------------------------------------------------------------------------
# TASK 1 & TASK 3: Pilot Candidate Reviews & Shadow Audit Endpoints
# -----------------------------------------------------------------------------

@predictions_bp.route('/pilot-reviews', methods=['GET'])
@token_required
@roles_required('instructor', 'admin')
def get_pilot_reviews():
    """
    Retrieves pilot candidate predictions for instructor review and shadow telemetry.
    Strictly scoped to subjects taught by the requesting instructor (or all for admin).
    """
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    subject_id = request.args.get('subject_id', type=int)
    topic_id = request.args.get('topic_id', type=int)
    review_decision = request.args.get('review_decision')
    disagreement_param = request.args.get('disagreement')
    disagreement = None
    if disagreement_param is not None:
        disagreement = disagreement_param.strip().lower() in ['true', '1']

    result = ShadowService.get_pilot_reviews(
        current_user=request.current_user,
        page=page,
        per_page=per_page,
        subject_id=subject_id,
        topic_id=topic_id,
        review_decision=review_decision,
        disagreement=disagreement
    )

    return jsonify(result), 200

@predictions_bp.route('/pilot-review/<int:record_id>', methods=['POST', 'PUT'])
@token_required
@roles_required('instructor', 'admin')
def submit_pilot_review(record_id):
    """
    Records an instructor confirmation, disagreement, or needs-more-information decision
    for a staged pilot candidate prediction.
    
    Guarantees:
    - Never triggers alerts, interventions, or changes to student status.
    - Restricts review to instructors teaching the relevant subject.
    """
    data = request.get_json() or {}
    decision = data.get('decision')
    notes = data.get('notes', '')

    if not decision:
        return jsonify({'error': "Missing 'decision' in request body. Must be 'confirmed', 'disagreement', or 'needs_more_information'."}), 400

    record_dict, err_msg, status_code = ShadowService.record_instructor_review(
        record_id=record_id,
        instructor_user=request.current_user,
        decision=decision,
        notes=notes
    )

    if err_msg:
        return jsonify({'error': err_msg}), status_code

    return jsonify({
        'message': f"Pilot review recorded successfully as '{record_dict['review_decision']}'.",
        'record': record_dict
    }), 200

# -----------------------------------------------------------------------------
# TASK 4: Outlier Telemetry Query Endpoint
# -----------------------------------------------------------------------------

@predictions_bp.route('/telemetry/outliers', methods=['GET'])
@token_required
@roles_required('instructor', 'admin')
def get_outlier_telemetry():
    """
    Retrieves outlier telemetry events.
    Instructors can only view outliers for subjects they teach.
    All student identifiers are pseudonymized for privacy protection.
    """
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    feature_name = request.args.get('feature_name')
    subject_id = request.args.get('subject_id', type=int)

    result = TelemetryService.get_outliers(
        current_user=request.current_user,
        page=page,
        per_page=per_page,
        feature_name=feature_name,
        subject_id=subject_id
    )

    return jsonify(result), 200

# -----------------------------------------------------------------------------
# On-Demand Candidate Inference (Safe Test Mode)
# -----------------------------------------------------------------------------

@predictions_bp.route('/predict-candidate', methods=['POST'])
@token_required
@roles_required('instructor', 'admin')
def predict_candidate():
    """
    Runs isolated inference using a staged candidate model version for evaluation.
    Clearly labeled 'Pilot Estimate — Requires Instructor Review'.
    Guaranteed NEVER to generate alerts, study recommendations, or student record mutations.
    """
    from flask import current_app
    data = request.get_json() or {}
    candidate_version = data.get('candidate_version') or ShadowService.get_shadow_candidate_version()
    features = data.get('features')
    student_id = data.get('student_id')
    topic_id = data.get('topic_id')

    if not features and (student_id and topic_id):
        features, err_code = compute_student_topic_features(student_id, topic_id)
        if not features:
            return jsonify({'error': 'Insufficient academic records for student/topic'}), 422

    if not features:
        return jsonify({'error': "Either 'features' dictionary or ('student_id' and 'topic_id') must be provided."}), 400

    try:
        candidate = CandidateModelCache.get_candidate(candidate_version, current_app.config['ARTIFACTS_FOLDER'])
        model = candidate['model']
        preprocessor = candidate['preprocessor']

        adapter = get_feature_adapter(candidate_version)
        adapted_features, adapter_meta = adapter.transform_features(features)

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

        # Output payload explicitly marked with pilot estimate disclosure
        return jsonify({
            'review_status': 'Pilot Estimate — Requires Instructor Review',
            'is_candidate': True,
            'alerts_generated': False,
            'recommendations_generated': False,
            'candidate_model_version': candidate_version,
            'predicted_difficulty': pred_class,
            'difficulty_score': round(float(diff_score), 4),
            'probabilities': {k: round(v, 4) for k, v in prob_dict.items()},
            'disclaimer': (
                "Candidate prediction estimate for instructor review only. "
                "Not authorized for autonomous student alerting or academic intervention."
            )
        }), 200

    except FileNotFoundError as fnf:
        return jsonify({'error': str(fnf)}), 404
    except Exception as e:
        return jsonify({'error': f'Candidate inference failed: {str(e)}'}), 500

