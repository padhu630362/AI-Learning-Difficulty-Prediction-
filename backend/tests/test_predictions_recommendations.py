import pytest
from backend.models.academic import Subject, Topic
from backend.models.support import StudyRecommendation, InstructorAlert
from backend.extensions import db

def test_prediction_and_isolation(client, tokens, users, app):
    # Setup subject & topic
    with app.app_context():
        sub = Subject(code='CS50', name='Intro to CS', instructor_id=users['instructor']['id'])
        db.session.add(sub)
        db.session.commit()

        top = Topic(subject_id=sub.id, name='Recursion', difficulty_level='intermediate')
        db.session.add(top)
        db.session.commit()

        top_id = top.id

    # Student 1 requests prediction with manual features
    res = client.post('/api/predictions/predict', json={
        'topic_id': top_id,
        'features': {
            'quiz_score': 45.0,
            'assignment_score': 50.0,
            'exam_score': 48.0,
            'study_time_weekly': 4.0,
            'attendance_rate': 75.0,
            'attempt_count': 3,
            'repeated_errors_count': 5,
            'previous_topic_score': 55.0,
            'learning_pace_gap': -10.0,
            'topic_difficulty_level': 'intermediate'
        }
    }, headers={'Authorization': f"Bearer {tokens['student1']}"})
    assert res.status_code == 201
    pred_data = res.get_json()['prediction']
    assert pred_data['student_id'] == users['student1']['id']
    assert 'difficulty_score' in pred_data
    assert len(pred_data['recommendations']) > 0

    # Student 1 fetches their own predictions
    res_my_preds = client.get('/api/predictions/my-predictions', headers={'Authorization': f"Bearer {tokens['student1']}"})
    assert res_my_preds.status_code == 200
    assert len(res_my_preds.get_json()['predictions']) >= 1

    # Student 2 tries to access Student 1's predictions directly -> 403 Forbidden!
    res_forbidden = client.get(f"/api/predictions/student/{users['student1']['id']}", headers={'Authorization': f"Bearer {tokens['student2']}"})
    assert res_forbidden.status_code == 403

def test_recommendation_completion(client, tokens, users, app):
    with app.app_context():
        sub = Subject(code='PHY101', name='Mechanics')
        db.session.add(sub)
        db.session.commit()
        top = Topic(subject_id=sub.id, name='Kinematics')
        db.session.add(top)
        db.session.commit()

        rec = StudyRecommendation(
            student_id=users['student1']['id'],
            subject_id=sub.id,
            topic_id=top.id,
            reason='Struggling with projectile vectors',
            suggested_action='Practice vector decomposition problems',
            priority='high'
        )
        db.session.add(rec)
        db.session.commit()
        rec_id = rec.id

    # Student 1 marks recommendation as completed
    res = client.put(f'/api/recommendations/{rec_id}/complete', headers={'Authorization': f"Bearer {tokens['student1']}"})
    assert res.status_code == 200
    assert res.get_json()['recommendation']['is_completed'] is True

def test_alert_lifecycle(client, tokens, users, app):
    with app.app_context():
        sub = Subject(code='HIST101', name='World History', instructor_id=users['instructor']['id'])
        db.session.add(sub)
        db.session.commit()

        alert = InstructorAlert(
            student_id=users['student1']['id'],
            instructor_id=users['instructor']['id'],
            subject_id=sub.id,
            alert_type='repeated_low_score',
            severity='high',
            title='Low quiz scores in History',
            description='Student scored below 40% on consecutive quizzes'
        )
        db.session.add(alert)
        db.session.commit()
        alert_id = alert.id

    # Instructor logs follow-up
    res_follow = client.post(f'/api/alerts/{alert_id}/follow-ups', json={
        'action_taken': 'Assigned peer tutor',
        'notes': 'Paired with high performing peer for study group',
        'outcome': 'improved'
    }, headers={'Authorization': f"Bearer {tokens['instructor']}"})
    assert res_follow.status_code == 201

    # Verify alert is now marked reviewed
    res_alerts = client.get('/api/alerts?is_reviewed=true', headers={'Authorization': f"Bearer {tokens['instructor']}"})
    assert res_alerts.status_code == 200
    alerts_list = res_alerts.get_json()['alerts']
    assert any(a['id'] == alert_id and a['is_reviewed'] is True for a in alerts_list)

def test_insufficient_data_error(client, tokens, users, app):
    # Setup subject & topic with NO assessment records
    with app.app_context():
        sub = Subject(code='CS999', name='Advanced Quantum Computing', instructor_id=users['instructor']['id'])
        db.session.add(sub)
        db.session.commit()

        top = Topic(subject_id=sub.id, name='Qubits and Superposition')
        db.session.add(top)
        db.session.commit()
        topic_id = top.id

    # Student 1 attempts prediction with zero assessments
    res = client.post('/api/predictions/predict', json={
        'topic_id': topic_id
    }, headers={'Authorization': f"Bearer {tokens['student1']}"})
    assert res.status_code == 422
    data = res.get_json()
    assert data['insufficient_data'] is True
    assert 'Insufficient academic records' in data['error']

def test_recommendation_deduplication(client, tokens, users, app):
    with app.app_context():
        sub = Subject(code='MATH100', name='College Algebra', instructor_id=users['instructor']['id'])
        db.session.add(sub)
        db.session.commit()

        top = Topic(subject_id=sub.id, name='Quadratic Equations')
        db.session.add(top)
        db.session.commit()
        top_id = top.id

    features = {
        'quiz_score': 35.0,
        'assignment_score': 40.0,
        'exam_score': 38.0,
        'study_time_weekly': 2.0,
        'attendance_rate': 60.0,
        'attempt_count': 4,
        'repeated_errors_count': 6,
        'previous_topic_score': 45.0,
        'learning_pace_gap': -20.0,
        'topic_difficulty_level': 'intermediate'
    }

    # First prediction generates recommendations
    res1 = client.post('/api/predictions/predict', json={
        'topic_id': top_id,
        'features': features
    }, headers={'Authorization': f"Bearer {tokens['student1']}"})
    assert res1.status_code == 201

    # Check pending recommendations count
    res_recs1 = client.get('/api/recommendations/my-recommendations?status=pending', headers={'Authorization': f"Bearer {tokens['student1']}"})
    recs1 = [r for r in res_recs1.get_json()['recommendations'] if r['topic_id'] == top_id]
    count1 = len(recs1)
    assert count1 > 0

    # Second prediction for the same topic
    res2 = client.post('/api/predictions/predict', json={
        'topic_id': top_id,
        'features': features
    }, headers={'Authorization': f"Bearer {tokens['student1']}"})
    assert res2.status_code == 201

    # Verify recommendations were de-duplicated and didn't double
    res_recs2 = client.get('/api/recommendations/my-recommendations?status=pending', headers={'Authorization': f"Bearer {tokens['student1']}"})
    recs2 = [r for r in res_recs2.get_json()['recommendations'] if r['topic_id'] == top_id]
    assert len(recs2) == count1

def test_instructor_batch_predict_isolation(client, tokens, users, app):
    with app.app_context():
        sub = Subject(code='CS888', name='Instructor 1 Course', instructor_id=users['instructor']['id'])
        db.session.add(sub)
        db.session.commit()

        top = Topic(subject_id=sub.id, name='Topic 1')
        db.session.add(top)
        db.session.commit()
        topic_id = top.id

    # Instructor 2 tries to run batch predictions on Instructor 1's topic -> 403 Forbidden
    res = client.post(f'/api/predictions/batch-predict-topic/{topic_id}', headers={'Authorization': f"Bearer {tokens['instructor2']}"})
    assert res.status_code == 403

