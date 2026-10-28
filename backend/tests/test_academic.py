import pytest

def test_subject_crud_by_instructor(client, tokens):
    # Instructor can create subject
    res = client.post('/api/subjects', json={
        'code': 'CS202',
        'name': 'Algorithms & Graph Theory',
        'description': 'Advanced Graph Algorithms'
    }, headers={'Authorization': f"Bearer {tokens['instructor']}"})
    assert res.status_code == 201
    subject_id = res.get_json()['subject']['id']

    # Update subject
    res_put = client.put(f'/api/subjects/{subject_id}', json={
        'name': 'Advanced Algorithms & Graph Theory'
    }, headers={'Authorization': f"Bearer {tokens['instructor']}"})
    assert res_put.status_code == 200
    assert res_put.get_json()['subject']['name'] == 'Advanced Algorithms & Graph Theory'

    # Student cannot create subject
    res_student = client.post('/api/subjects', json={
        'code': 'CS303',
        'name': 'Hacking 101'
    }, headers={'Authorization': f"Bearer {tokens['student1']}"})
    assert res_student.status_code == 403

def test_topic_crud(client, tokens):
    # Create subject first
    res = client.post('/api/subjects', json={
        'code': 'CHEM101',
        'name': 'Organic Chemistry',
        'description': 'Intro to organic molecules'
    }, headers={'Authorization': f"Bearer {tokens['instructor']}"})
    assert res.status_code == 201
    subject_id = res.get_json()['subject']['id']

    # Create topic
    res_topic = client.post(f'/api/subjects/{subject_id}/topics', json={
        'name': 'Alkanes and Alkenes',
        'description': 'Hydrocarbon bonding structures',
        'learning_objectives': 'Identify sigma and pi bonds',
        'difficulty_level': 'beginner',
        'order_index': 1,
        'resources': 'https://en.wikipedia.org/wiki/Alkane'
    }, headers={'Authorization': f"Bearer {tokens['instructor']}"})
    assert res_topic.status_code == 201
    topic_id = res_topic.get_json()['topic']['id']

    # Update topic
    res_topic_put = client.put(f'/api/subjects/topics/{topic_id}', json={
        'difficulty_level': 'intermediate'
    }, headers={'Authorization': f"Bearer {tokens['instructor']}"})
    assert res_topic_put.status_code == 200
    assert res_topic_put.get_json()['topic']['difficulty_level'] == 'intermediate'

def test_assessment_creation_and_result_validation(client, tokens, users):
    # Create subject and topic
    res = client.post('/api/subjects', json={
        'code': 'BIO101',
        'name': 'Cell Biology',
        'description': 'Cellular processes'
    }, headers={'Authorization': f"Bearer {tokens['instructor']}"})
    assert res.status_code == 201
    subject_id = res.get_json()['subject']['id']

    # Create assessment
    res_ass = client.post('/api/assessments', json={
        'subject_id': subject_id,
        'title': 'Quiz 1: Mitochondria & ATP',
        'assessment_type': 'quiz',
        'max_marks': 50.0,
        'passing_marks': 25.0,
        'assessment_date': '2026-10-15'
    }, headers={'Authorization': f"Bearer {tokens['instructor']}"})
    assert res_ass.status_code == 201
    assessment_id = res_ass.get_json()['assessment']['id']

    # Invalid marks: greater than max_marks
    res_invalid_marks = client.post(f'/api/assessments/{assessment_id}/results', json={
        'student_id': users['student1']['id'],
        'marks_obtained': 60.0
    }, headers={'Authorization': f"Bearer {tokens['instructor']}"})
    assert res_invalid_marks.status_code == 400
    assert 'must be between 0 and 50.0' in res_invalid_marks.get_json()['error']

    # Valid score
    res_valid = client.post(f'/api/assessments/{assessment_id}/results', json={
        'student_id': users['student1']['id'],
        'marks_obtained': 45.0,
        'study_time_minutes': 90,
        'attempt_count': 1,
        'repeated_errors_count': 0
    }, headers={'Authorization': f"Bearer {tokens['instructor']}"})
    assert res_valid.status_code == 200
    data = res_valid.get_json()['result']
    assert data['marks_obtained'] == 45.0
    assert data['percentage'] == 90.0

def test_gradebook_csv_template_download(client, tokens):
    res = client.get('/api/assessments/template.csv', headers={'Authorization': f"Bearer {tokens['instructor']}"})
    assert res.status_code == 200
    assert 'text/csv' in res.content_type
    assert 'attachment' in res.headers.get('Content-Disposition', '')
    data_str = res.data.decode('utf-8')
    assert 'student_email' in data_str
    assert 'marks_obtained' in data_str
    assert 'study_time_minutes' in data_str

def test_instructor_subject_isolation(client, tokens, users):
    # Instructor 1 creates a subject
    res = client.post('/api/subjects', json={
        'code': 'PHYS301',
        'name': 'Quantum Mechanics',
        'description': 'Wave equations'
    }, headers={'Authorization': f"Bearer {tokens['instructor']}"})
    assert res.status_code == 201
    subject_id = res.get_json()['subject']['id']

    # Instructor 1 creates an assessment
    res_ass = client.post('/api/assessments', json={
        'subject_id': subject_id,
        'title': 'Midterm Exam',
        'assessment_type': 'exam',
        'max_marks': 100.0,
        'passing_marks': 50.0,
        'assessment_date': '2026-10-20'
    }, headers={'Authorization': f"Bearer {tokens['instructor']}"})
    assert res_ass.status_code == 201
    assessment_id = res_ass.get_json()['assessment']['id']

    # Instructor 2 attempts to create an assessment on Instructor 1's subject -> 403
    res_unauth_ass = client.post('/api/assessments', json={
        'subject_id': subject_id,
        'title': 'Unauthorized Quiz',
        'assessment_type': 'quiz',
        'max_marks': 20.0,
        'passing_marks': 10.0,
        'assessment_date': '2026-10-21'
    }, headers={'Authorization': f"Bearer {tokens['instructor2']}"})
    assert res_unauth_ass.status_code == 403

    # Instructor 2 attempts to record student results on Instructor 1's assessment -> 403
    res_unauth_rec = client.post(f'/api/assessments/{assessment_id}/results', json={
        'student_id': users['student1']['id'],
        'marks_obtained': 80.0
    }, headers={'Authorization': f"Bearer {tokens['instructor2']}"})
    assert res_unauth_rec.status_code == 403

    # Instructor 2 attempts to delete Instructor 1's subject -> 403
    res_unauth_del = client.delete(f'/api/subjects/{subject_id}', headers={'Authorization': f"Bearer {tokens['instructor2']}"})
    assert res_unauth_del.status_code == 403

