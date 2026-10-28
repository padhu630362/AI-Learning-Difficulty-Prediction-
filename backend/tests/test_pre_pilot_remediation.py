import time
import hashlib
from datetime import datetime
import pytest
from backend.extensions import db
from backend.models.academic import Subject, Topic, Assessment, StudentAssessmentResult
from backend.models.ml_records import ShadowAuditRecord, OutlierTelemetryRecord, ModelVersion, PredictionRecord
from backend.models.support import InstructorAlert, StudyRecommendation
from backend.services.shadow_service import ShadowService, CandidateModelCache
from backend.services.telemetry_service import TelemetryService
from backend.ml.predictor import MLPredictor

@pytest.fixture
def academic_setup(app, users):
    """Sets up a subject and topic taught by users['instructor']."""
    with app.app_context():
        # Clean up prior records
        ShadowAuditRecord.query.delete()
        OutlierTelemetryRecord.query.delete()
        PredictionRecord.query.delete()
        InstructorAlert.query.delete()
        StudyRecommendation.query.delete()
        StudentAssessmentResult.query.delete()
        Assessment.query.delete()
        Topic.query.delete()
        Subject.query.delete()
        db.session.commit()

        subject = Subject(
            name="Algorithms 101",
            code="CS101",
            instructor_id=users['instructor']['id']
        )
        db.session.add(subject)
        db.session.commit()

        topic = Topic(
            subject_id=subject.id,
            name="Binary Search Trees",
            order_index=1,
            difficulty_level="intermediate"
        )
        db.session.add(topic)
        db.session.commit()

        # Add assessment results for student1
        assessment = Assessment(
            subject_id=subject.id,
            topic_id=topic.id,
            title="BST Quiz 1",
            assessment_type="quiz",
            max_marks=100.0,
            passing_marks=40.0,
            assessment_date=datetime.utcnow().date()
        )
        db.session.add(assessment)
        db.session.commit()

        result = StudentAssessmentResult(
            student_id=users['student1']['id'],
            assessment_id=assessment.id,
            marks_obtained=45.0,
            percentage=45.0,
            attempt_count=2,
            repeated_errors_count=3,
            study_time_minutes=300,  # 5 hours
            completion_status="completed"
        )
        db.session.add(result)
        db.session.commit()

        return {
            'subject_id': subject.id,
            'topic_id': topic.id,
            'student_id': users['student1']['id'],
            'instructor_id': users['instructor']['id'],
            'other_instructor_id': users['instructor2']['id']
        }

def test_shadow_mode_disabled_by_default(app, client, tokens):
    """TASK 3: Verifies shadow mode feature flag is disabled by default."""
    with app.app_context():
        # Ensure setting is reset
        assert ShadowService.is_shadow_mode_enabled() is False

    headers = {'Authorization': f"Bearer {tokens['admin']}"}
    res = client.get('/api/models/shadow/status', headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data['shadow_mode_enabled'] is False
    assert 'disagreement_disclaimer' in data
    assert "does not constitute proof" in data['disagreement_disclaimer']

def test_shadow_mode_admin_toggle(app, client, tokens):
    """TASK 3: Verifies admin can enable and disable shadow mode via API."""
    admin_headers = {'Authorization': f"Bearer {tokens['admin']}"}
    student_headers = {'Authorization': f"Bearer {tokens['student1']}"}

    # Students cannot toggle shadow mode
    res = client.put('/api/models/shadow/toggle', headers=student_headers, json={'enabled': True})
    assert res.status_code == 403

    # Admin enables shadow mode
    res = client.put('/api/models/shadow/toggle', headers=admin_headers, json={'enabled': True, 'candidate_version': 'lms_canonical_v1'})
    assert res.status_code == 200
    assert res.get_json()['status']['shadow_mode_enabled'] is True

    with app.app_context():
        assert ShadowService.is_shadow_mode_enabled() is True

    # Admin disables shadow mode
    res = client.put('/api/models/shadow/toggle', headers=admin_headers, json={'enabled': False})
    assert res.status_code == 200
    assert res.get_json()['status']['shadow_mode_enabled'] is False

    with app.app_context():
        assert ShadowService.is_shadow_mode_enabled() is False

def test_production_response_invariance_and_shadow_execution(app, client, tokens, academic_setup):
    """TASK 3: Verifies production response is invariant whether shadow mode is on or off."""
    instructor_headers = {'Authorization': f"Bearer {tokens['instructor']}"}
    admin_headers = {'Authorization': f"Bearer {tokens['admin']}"}

    payload = {
        'student_id': academic_setup['student_id'],
        'topic_id': academic_setup['topic_id']
    }

    # 1. Run prediction with shadow mode DISABLED
    with app.app_context():
        ShadowService.set_shadow_mode(enabled=False)

    res_off = client.post('/api/predictions/predict', headers=instructor_headers, json=payload)
    assert res_off.status_code == 201
    data_off = res_off.get_json()['prediction']
    assert data_off['model_version'] == 'v1.0.0-production-baseline'

    # 2. Run prediction with shadow mode ENABLED
    with app.app_context():
        ShadowService.set_shadow_mode(enabled=True, candidate_version='lms_canonical_v1')

    res_on = client.post('/api/predictions/predict', headers=instructor_headers, json=payload)
    assert res_on.status_code == 201
    data_on = res_on.get_json()['prediction']

    # Production response must be strictly invariant
    assert data_on['model_version'] == data_off['model_version']
    assert data_on['predicted_difficulty'] == data_off['predicted_difficulty']
    assert data_on['difficulty_score'] == data_off['difficulty_score']
    assert len(data_on['recommendations']) == len(data_off['recommendations'])

    # Allow async thread to record shadow telemetry
    time.sleep(0.5)

    with app.app_context():
        shadow_records = ShadowAuditRecord.query.filter_by(
            production_record_id=data_on['id']
        ).all()
        assert len(shadow_records) == 1
        s_rec = shadow_records[0]
        assert s_rec.production_model_version == 'v1.0.0-production-baseline'
        assert s_rec.candidate_model_version == 'lms_canonical_v1'
        assert s_rec.label == 'Pilot Estimate — Requires Instructor Review'
        assert s_rec.execution_status == 'success'
        assert s_rec.candidate_prediction in ['Low', 'Moderate', 'High']

    # Cleanup shadow setting
    with app.app_context():
        ShadowService.set_shadow_mode(enabled=False)

def test_shadow_failure_safety_never_breaks_production(app, client, tokens, academic_setup):
    """TASK 3: Verifies that an exception in shadow inference never breaks the production prediction."""
    instructor_headers = {'Authorization': f"Bearer {tokens['instructor']}"}

    # Configure shadow mode with an invalid non-existent candidate version
    with app.app_context():
        ShadowService.set_shadow_mode(enabled=True, candidate_version='non_existent_candidate_v99')

    payload = {
        'student_id': academic_setup['student_id'],
        'topic_id': academic_setup['topic_id']
    }

    # Production call MUST succeed even though shadow candidate does not exist!
    res = client.post('/api/predictions/predict', headers=instructor_headers, json=payload)
    assert res.status_code == 201
    data = res.get_json()['prediction']
    assert data['model_version'] == 'v1.0.0-production-baseline'

    time.sleep(0.5)

    with app.app_context():
        failed_shadow = ShadowAuditRecord.query.filter_by(
            production_record_id=data['id']
        ).first()
        assert failed_shadow is not None
        assert failed_shadow.execution_status == 'failed'
        assert failed_shadow.candidate_prediction is None
        assert "not found" in failed_shadow.error_message.lower()

    # Reset shadow mode
    with app.app_context():
        ShadowService.set_shadow_mode(enabled=False)

def test_candidate_prediction_generates_no_alerts_or_recommendations(app, client, tokens, academic_setup):
    """TASK 1: Candidate predictions must not trigger alerts, interventions, or recommendations."""
    instructor_headers = {'Authorization': f"Bearer {tokens['instructor']}"}

    with app.app_context():
        initial_alert_count = InstructorAlert.query.count()
        initial_rec_count = StudyRecommendation.query.count()

    payload = {
        'candidate_version': 'lms_canonical_v1',
        'features': {
            'quiz_score': 20.0,  # Critical score that would trigger alerts in production
            'assignment_score': 25.0,
            'exam_score': 30.0,
            'study_time_weekly': 4.0,
            'attendance_rate': 50.0,
            'attempt_count': 4,
            'repeated_errors_count': 8,
            'previous_topic_score': 40.0,
            'learning_pace_gap': -47.5,
            'topic_difficulty_level': 'intermediate'
        }
    }

    res = client.post('/api/predictions/predict-candidate', headers=instructor_headers, json=payload)
    assert res.status_code == 200
    data = res.get_json()

    # Must be clearly labeled
    assert data['review_status'] == 'Pilot Estimate — Requires Instructor Review'
    assert data['is_candidate'] is True
    assert data['alerts_generated'] is False
    assert data['recommendations_generated'] is False
    assert data['predicted_difficulty'] == 'High'

    with app.app_context():
        # Verify ZERO new alerts or recommendations were created
        assert InstructorAlert.query.count() == initial_alert_count
        assert StudyRecommendation.query.count() == initial_rec_count

def test_instructor_pilot_review_authorization_and_workflow(app, client, tokens, academic_setup):
    """TASK 1: Instructors can review candidate predictions for their own subjects; others are forbidden."""
    auth_instructor_headers = {'Authorization': f"Bearer {tokens['instructor']}"}
    unauth_instructor_headers = {'Authorization': f"Bearer {tokens['instructor2']}"}
    student_headers = {'Authorization': f"Bearer {tokens['student1']}"}

    # Create a shadow audit record in DB for the test subject
    with app.app_context():
        audit_rec = ShadowAuditRecord(
            student_id=academic_setup['student_id'],
            subject_id=academic_setup['subject_id'],
            topic_id=academic_setup['topic_id'],
            production_model_version='v1.0.0-production-baseline',
            production_prediction='Moderate',
            candidate_model_version='lms_canonical_v1',
            candidate_prediction='High',
            disagreement=True,
            execution_status='success',
            label='Pilot Estimate — Requires Instructor Review'
        )
        db.session.add(audit_rec)
        db.session.commit()
        record_id = audit_rec.id

    # 1. Student attempts to review -> 403 Forbidden
    res_student = client.post(f'/api/predictions/pilot-review/{record_id}', headers=student_headers, json={'decision': 'confirmed'})
    assert res_student.status_code == 403

    # 2. Unauthorized instructor (does not teach subject) -> 403 Forbidden
    res_unauth = client.post(f'/api/predictions/pilot-review/{record_id}', headers=unauth_instructor_headers, json={'decision': 'confirmed'})
    assert res_unauth.status_code == 403

    # 3. Authorized instructor submits valid review
    review_payload = {
        'decision': 'confirmed',
        'notes': 'Student demonstrated struggle during lab session on BST node deletions.'
    }
    res_auth = client.post(f'/api/predictions/pilot-review/{record_id}', headers=auth_instructor_headers, json=review_payload)
    assert res_auth.status_code == 200
    auth_data = res_auth.get_json()['record']
    assert auth_data['review_decision'] == 'confirmed'
    assert auth_data['review_notes'] == review_payload['notes']
    assert auth_data['reviewed_at'] is not None

    # 4. Query reviews list as authorized instructor
    res_list = client.get('/api/predictions/pilot-reviews', headers=auth_instructor_headers)
    assert res_list.status_code == 200
    reviews = res_list.get_json()['records']
    assert any(r['id'] == record_id for r in reviews)

    # 5. Query reviews list as unauthorized instructor -> empty or 0 records for this subject
    res_unauth_list = client.get(f'/api/predictions/pilot-reviews?subject_id={academic_setup["subject_id"]}', headers=unauth_instructor_headers)
    assert res_unauth_list.status_code == 200
    assert len(res_unauth_list.get_json()['records']) == 0

def test_outlier_telemetry_detection_and_clamping(app, client, tokens, academic_setup):
    """TASK 4: Detects and logs study time > 28h and repeated errors > 15 with pseudonymized ID."""
    with app.app_context():
        OutlierTelemetryRecord.query.delete()
        db.session.commit()

        # 1. Study time > 28.0 (e.g. 35.5 hrs)
        clamped_study = TelemetryService.inspect_and_clamp_study_time(
            raw_study_time=35.5,
            student_id=academic_setup['student_id'],
            topic_id=academic_setup['topic_id'],
            subject_id=academic_setup['subject_id'],
            context='feature_generation'
        )
        assert clamped_study == 28.0

        # 2. Repeated errors > 15 (e.g. 22 errors)
        clamped_errors = TelemetryService.inspect_and_clamp_repeated_errors(
            raw_errors=22,
            student_id=academic_setup['student_id'],
            topic_id=academic_setup['topic_id'],
            subject_id=academic_setup['subject_id'],
            context='feature_generation'
        )
        assert clamped_errors == 15

        # Check telemetry records in DB
        records = OutlierTelemetryRecord.query.all()
        assert len(records) == 2

        study_rec = next(r for r in records if r.feature_name == 'study_time_weekly')
        assert study_rec.raw_value == 35.5
        assert study_rec.clamped_value == 28.0
        assert "exceeds canonical ceiling" in study_rec.threshold_description
        # Verify pseudonymization: must NOT contain raw student ID or personal name
        assert study_rec.student_pseudo_id != str(academic_setup['student_id'])
        assert len(study_rec.student_pseudo_id) == 16

        error_rec = next(r for r in records if r.feature_name == 'repeated_errors_count')
        assert error_rec.raw_value == 22.0
        assert error_rec.clamped_value == 15.0

    # Query outlier telemetry via API as authorized instructor
    instructor_headers = {'Authorization': f"Bearer {tokens['instructor']}"}
    res = client.get('/api/predictions/telemetry/outliers', headers=instructor_headers)
    assert res.status_code == 200
    telemetry_list = res.get_json()['records']
    assert len(telemetry_list) == 2

def test_leakage_safe_training_pipeline_and_model_version_isolation(app):
    """TASK 2 & Safety Rules: Verifies lms_canonical_v2 artifacts and baseline hash preservation."""
    import os
    import joblib
    import hashlib

    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    root_model_path = os.path.join(backend_dir, 'artifacts', 'model.joblib')
    v2_dir = os.path.join(backend_dir, 'artifacts', 'versions', 'lms_canonical_v2')

    # 1. Verify root baseline hash remains untouched
    with open(root_model_path, 'rb') as f:
        root_hash = hashlib.sha256(f.read()).hexdigest().upper()
    assert root_hash == '290CC8B5BD8A721B081C214B11A2748623AA26AE26C0A8F530F4C26A4BA9F09C'

    # 2. Verify lms_canonical_v2 artifacts exist
    assert os.path.exists(os.path.join(v2_dir, 'model.joblib'))
    assert os.path.exists(os.path.join(v2_dir, 'preprocessor.joblib'))
    assert os.path.exists(os.path.join(v2_dir, 'pipeline.joblib'))
    assert os.path.exists(os.path.join(v2_dir, 'evaluation_report.json'))

    # 3. Verify pipeline is an sklearn Pipeline
    from sklearn.pipeline import Pipeline
    pipeline_obj = joblib.load(os.path.join(v2_dir, 'pipeline.joblib'))
    assert isinstance(pipeline_obj, Pipeline)
    assert 'preprocessor' in pipeline_obj.named_steps
    assert 'classifier' in pipeline_obj.named_steps

    # 4. Verify persistent database model version states in backend/data/app.db
    import sqlite3
    db_path = os.path.join(backend_dir, 'data', 'app.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    rows = {r[0]: r[1] for r in c.execute("SELECT version_tag, is_active FROM model_versions").fetchall()}

    assert rows['v1.0.0-production-baseline'] == 1
    assert rows['uci_student_perf_v1'] == 0
    assert rows['lms_canonical_v1'] == 0
    assert rows['lms_canonical_v2'] == 0

