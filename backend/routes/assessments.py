import io
import csv
from datetime import datetime
from flask import Blueprint, request, jsonify, Response
from backend.extensions import db
from backend.models.academic import Assessment, StudentAssessmentResult, Subject, Topic
from backend.models.user import User
from backend.utils.decorators import token_required, roles_required
from backend.services.alert_service import AlertService

assessments_bp = Blueprint('assessments', __name__)

@assessments_bp.route('', methods=['GET'])
@token_required
def get_assessments():
    subject_id = request.args.get('subject_id')
    topic_id = request.args.get('topic_id')
    assessment_type = request.args.get('type')

    query = Assessment.query

    # If instructor, default to their taught subjects unless explicitly specified
    if request.current_user.role == 'instructor' and request.args.get('only_mine') == 'true':
        taught_ids = [s.id for s in Subject.query.filter_by(instructor_id=request.current_user.id).all()]
        query = query.filter(Assessment.subject_id.in_(taught_ids))

    if subject_id:
        query = query.filter_by(subject_id=int(subject_id))
    if topic_id:
        query = query.filter_by(topic_id=int(topic_id))
    if assessment_type:
        query = query.filter_by(assessment_type=assessment_type)

    assessments = query.order_by(Assessment.assessment_date.desc()).all()
    return jsonify({'assessments': [a.to_dict() for a in assessments]}), 200

@assessments_bp.route('/<int:assessment_id>', methods=['GET'])
@token_required
def get_assessment_detail(assessment_id):
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        return jsonify({'error': 'Assessment not found'}), 404

    data = assessment.to_dict()
    # If instructor or admin, include submissions
    if request.current_user.role in ['instructor', 'admin']:
        # If instructor, verify they teach the subject
        if request.current_user.role == 'instructor' and assessment.subject.instructor_id != request.current_user.id:
            return jsonify({'error': 'Unauthorized to view submissions for another instructor\'s assessment.'}), 403
        data['submissions'] = [r.to_dict() for r in assessment.results]
    return jsonify({'assessment': data}), 200

@assessments_bp.route('', methods=['POST'])
@token_required
@roles_required('instructor', 'admin')
def create_assessment():
    data = request.get_json() or {}
    subject_id = data.get('subject_id')
    topic_id = data.get('topic_id')
    title = data.get('title', '').strip()
    assessment_type = data.get('assessment_type', 'quiz').strip().lower()
    max_marks = float(data.get('max_marks', 100.0))
    passing_marks = float(data.get('passing_marks', 40.0))
    weightage = float(data.get('weightage', 1.0))
    assessment_date_str = data.get('assessment_date')

    if not subject_id or not title or not assessment_date_str:
        return jsonify({'error': 'Subject ID, title, and assessment date are required'}), 400

    subject = db.session.get(Subject, subject_id)
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404

    # Security check: Instructor can only create assessments for subjects they teach
    if request.current_user.role == 'instructor' and subject.instructor_id != request.current_user.id:
        return jsonify({'error': 'Unauthorized: You can only create assessments for your assigned subjects.'}), 403

    if max_marks <= 0:
        return jsonify({'error': 'Maximum marks must be greater than 0'}), 400
    if passing_marks < 0 or passing_marks > max_marks:
        return jsonify({'error': 'Passing marks must be between 0 and maximum marks'}), 400

    try:
        assessment_date = datetime.strptime(assessment_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid assessment_date format. Use YYYY-MM-DD'}), 400

    assessment = Assessment(
        subject_id=subject_id,
        topic_id=topic_id if topic_id else None,
        title=title,
        assessment_type=assessment_type,
        max_marks=max_marks,
        passing_marks=passing_marks,
        weightage=weightage,
        assessment_date=assessment_date,
        created_by=request.current_user.id
    )
    db.session.add(assessment)
    db.session.commit()

    return jsonify({'message': 'Assessment created successfully', 'assessment': assessment.to_dict()}), 201

@assessments_bp.route('/<int:assessment_id>/results', methods=['POST'])
@token_required
@roles_required('instructor', 'admin')
def record_result(assessment_id):
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        return jsonify({'error': 'Assessment not found'}), 404

    # Security check: Instructor can only record results for their own subject's assessment
    if request.current_user.role == 'instructor' and assessment.subject.instructor_id != request.current_user.id:
        return jsonify({'error': 'Unauthorized: You can only record grades for your assigned subjects.'}), 403

    data = request.get_json() or {}
    student_id = data.get('student_id')
    marks_obtained = data.get('marks_obtained')
    study_time_minutes = float(data.get('study_time_minutes', 60.0))
    attempt_count = int(data.get('attempt_count', 1))
    repeated_errors_count = int(data.get('repeated_errors_count', 0))
    completion_status = data.get('completion_status', 'completed')
    remarks = data.get('remarks', '').strip()

    if student_id is None or marks_obtained is None:
        return jsonify({'error': 'Student ID and marks obtained are required'}), 400

    marks_obtained = float(marks_obtained)
    if marks_obtained < 0 or marks_obtained > assessment.max_marks:
        return jsonify({'error': f'Marks obtained must be between 0 and {assessment.max_marks}'}), 400

    student = User.query.filter_by(id=student_id, role='student').first()
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    percentage = (marks_obtained / assessment.max_marks) * 100.0

    # Upsert result
    existing = StudentAssessmentResult.query.filter_by(
        student_id=student_id,
        assessment_id=assessment_id
    ).first()

    if existing:
        existing.marks_obtained = marks_obtained
        existing.percentage = percentage
        existing.study_time_minutes = study_time_minutes
        existing.attempt_count = attempt_count
        existing.repeated_errors_count = repeated_errors_count
        existing.completion_status = completion_status
        existing.remarks = remarks
        result = existing
    else:
        result = StudentAssessmentResult(
            student_id=student_id,
            assessment_id=assessment_id,
            marks_obtained=marks_obtained,
            percentage=percentage,
            study_time_minutes=study_time_minutes,
            attempt_count=attempt_count,
            repeated_errors_count=repeated_errors_count,
            completion_status=completion_status,
            remarks=remarks
        )
        db.session.add(result)

    db.session.commit()

    # Check and generate alerts if student is struggling
    AlertService.evaluate_and_generate_alerts(student_id, assessment.subject_id, request.current_user.id)

    return jsonify({'message': 'Result recorded successfully', 'result': result.to_dict()}), 200

@assessments_bp.route('/template.csv', methods=['GET'])
@token_required
@roles_required('instructor', 'admin')
def download_csv_template():
    """
    Returns an instructional CSV gradebook template for bulk imports.
    """
    csv_content = (
        "student_email,marks_obtained,study_time_minutes,attempt_count,repeated_errors_count,completion_status,remarks\n"
        "alex.miller@student.edu,88.5,120,1,0,completed,Good understanding\n"
        "maya.patel@student.edu,68.0,90,2,2,completed,Needs revision on pointers\n"
        "liam.chen@student.edu,42.0,60,3,5,completed,Scheduled for tutoring\n"
    )
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=gradebook_template.csv"}
    )

@assessments_bp.route('/<int:assessment_id>/import-results', methods=['POST'])
@token_required
@roles_required('instructor', 'admin')
def import_results_csv(assessment_id):
    assessment = db.session.get(Assessment, assessment_id)
    if not assessment:
        return jsonify({'error': 'Assessment not found'}), 404

    # Security check: Instructor can only import results for their assigned subject
    if request.current_user.role == 'instructor' and assessment.subject.instructor_id != request.current_user.id:
        return jsonify({'error': 'Unauthorized: You can only import grades for your assigned subjects.'}), 403

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded. Expected multipart form with key "file"'}), 400

    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Uploaded file must be a .csv file'}), 400

    try:
        stream = io.StringIO(file.stream.read().decode('utf-8-sig'), newline=None)
        reader = csv.DictReader(stream)
    except Exception as e:
        return jsonify({'error': f'Failed to parse CSV: {str(e)}'}), 400

    success_count = 0
    errors = []
    row_num = 1

    for row in reader:
        row_num += 1
        identifier = row.get('student_email') or row.get('student_username') or row.get('student_id')
        marks_str = row.get('marks_obtained')

        if not identifier or marks_str is None:
            errors.append(f"Row {row_num}: Missing student identifier or marks_obtained")
            continue

        student = User.query.filter(
            (User.email == identifier.strip().lower()) |
            (User.username == identifier.strip()) |
            (User.id == identifier.strip() if identifier.strip().isdigit() else False)
        ).first()

        if not student:
            errors.append(f"Row {row_num}: Student '{identifier}' not found in system")
            continue

        try:
            marks = float(marks_str)
            if marks < 0 or marks > assessment.max_marks:
                errors.append(f"Row {row_num}: Marks {marks} out of range [0, {assessment.max_marks}] for student '{student.full_name}'")
                continue
        except ValueError:
            errors.append(f"Row {row_num}: Invalid numeric marks '{marks_str}'")
            continue

        study_time = float(row.get('study_time_minutes', 60.0) or 60.0)
        attempts = int(row.get('attempt_count', 1) or 1)
        errors_cnt = int(row.get('repeated_errors_count', 0) or 0)
        status = row.get('completion_status', 'completed') or 'completed'
        remarks = row.get('remarks', '')

        percentage = (marks / assessment.max_marks) * 100.0

        existing = StudentAssessmentResult.query.filter_by(
            student_id=student.id,
            assessment_id=assessment_id
        ).first()

        if existing:
            existing.marks_obtained = marks
            existing.percentage = percentage
            existing.study_time_minutes = study_time
            existing.attempt_count = attempts
            existing.repeated_errors_count = errors_cnt
            existing.completion_status = status
            existing.remarks = remarks
        else:
            rec = StudentAssessmentResult(
                student_id=student.id,
                assessment_id=assessment_id,
                marks_obtained=marks,
                percentage=percentage,
                study_time_minutes=study_time,
                attempt_count=attempts,
                repeated_errors_count=errors_cnt,
                completion_status=status,
                remarks=remarks
            )
            db.session.add(rec)
        
        success_count += 1
        # Check alerts for imported student
        AlertService.evaluate_and_generate_alerts(student.id, assessment.subject_id, request.current_user.id)

    db.session.commit()

    return jsonify({
        'message': f'CSV import completed: {success_count} records imported/updated successfully.',
        'success_count': success_count,
        'rejected_count': len(errors),
        'errors': errors[:50]
    }), 200

@assessments_bp.route('/my-results', methods=['GET'])
@token_required
def get_my_results():
    results = StudentAssessmentResult.query.filter_by(
        student_id=request.current_user.id
    ).order_by(StudentAssessmentResult.created_at.desc()).all()
    return jsonify({'results': [r.to_dict() for r in results]}), 200

@assessments_bp.route('/student/<int:student_id>', methods=['GET'])
@token_required
def get_student_results(student_id):
    # Student can only view their own; instructor and admin can view any
    if request.current_user.role == 'student' and request.current_user.id != student_id:
        return jsonify({'error': 'Unauthorized to view other students records'}), 403

    query = StudentAssessmentResult.query.filter_by(student_id=student_id)

    # If instructor, restrict results to subjects they teach
    if request.current_user.role == 'instructor':
        taught_ids = [s.id for s in Subject.query.filter_by(instructor_id=request.current_user.id).all()]
        query = query.join(Assessment, StudentAssessmentResult.assessment_id == Assessment.id).filter(Assessment.subject_id.in_(taught_ids))

    results = query.order_by(StudentAssessmentResult.created_at.desc()).all()
    return jsonify({'results': [r.to_dict() for r in results]}), 200
