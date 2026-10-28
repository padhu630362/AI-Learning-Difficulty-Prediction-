import io

def test_admin_overview(client, tokens):
    res = client.get('/api/admin/overview', headers={'Authorization': f"Bearer {tokens['admin']}"})
    assert res.status_code == 200
    data = res.get_json()
    assert 'users' in data
    assert 'academics' in data
    assert 'predictions' in data
    assert 'alerts' in data

def test_admin_upload_dataset_validation(client, tokens):
    # Valid CSV content
    valid_csv = (
        "quiz_score,assignment_score,exam_score,study_time_weekly,attendance_rate,"
        "attempt_count,repeated_errors_count,previous_topic_score,learning_pace_gap,"
        "topic_difficulty_level,difficulty_category\n"
        "85.0,90.0,88.0,12.0,95.0,1,0,88.0,10.0,intermediate,Low\n"
        "40.0,45.0,38.0,4.0,70.0,3,6,42.0,-15.0,advanced,High\n"
    )

    data = {
        'file': (io.BytesIO(valid_csv.encode('utf-8')), 'test_dataset.csv')
    }

    res = client.post('/api/datasets/upload', data=data, content_type='multipart/form-data', headers={'Authorization': f"Bearer {tokens['admin']}"})
    assert res.status_code == 201
    dataset_data = res.get_json()['dataset']
    assert dataset_data['validation_status'] == 'valid'
    assert dataset_data['row_count'] == 2

def test_reject_invalid_file_type(client, tokens):
    data = {
        'file': (io.BytesIO(b'some executable script'), 'script.sh')
    }
    res = client.post('/api/datasets/upload', data=data, content_type='multipart/form-data', headers={'Authorization': f"Bearer {tokens['admin']}"})
    assert res.status_code == 400
    assert 'Only CSV files are supported' in res.get_json()['error']

def test_student_forbidden_from_admin_datasets(client, tokens):
    res = client.get('/api/datasets', headers={'Authorization': f"Bearer {tokens['student1']}"})
    assert res.status_code == 403

def test_model_diagnostics_and_candidate_comparison(client, tokens):
    res = client.get('/api/models/active', headers={'Authorization': f"Bearer {tokens['admin']}"})
    assert res.status_code == 200
    data = res.get_json()
    assert 'active_model' in data
    assert 'candidate_comparison' in data
    if data['active_model']:
        assert 'accuracy' in data['active_model']
        assert 'f1_macro' in data['active_model']

def test_model_history_and_activation(client, tokens, app):
    from backend.models.ml_records import ModelVersion
    from backend.extensions import db

    with app.app_context():
        # Create a second dummy model version to test live activation
        m2 = ModelVersion(
            version_tag='test_rf_model_v2',
            model_name='Random Forest Classifier',
            algorithm='Random Forest Classifier',
            accuracy=0.92,
            precision_macro=0.91,
            recall_macro=0.90,
            f1_macro=0.91,
            is_active=False
        )
        db.session.add(m2)
        db.session.commit()
        m2_id = m2.id

    # Admin activates m2
    res = client.put(f'/api/models/{m2_id}/activate', headers={'Authorization': f"Bearer {tokens['admin']}"})
    assert res.status_code == 200
    assert res.get_json()['model']['is_active'] is True

    # Student cannot activate models
    res_unauth = client.put(f'/api/models/{m2_id}/activate', headers={'Authorization': f"Bearer {tokens['student1']}"})
    assert res_unauth.status_code == 403


