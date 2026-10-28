def test_register_success(client):
    res = client.post('/api/auth/register', json={
        'username': 'new_student',
        'email': 'new_student@school.edu',
        'password': 'SecurePassword123!',
        'full_name': 'New Student',
        'role': 'student'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['user']['username'] == 'new_student'
    assert data['user']['role'] == 'student'

def test_register_duplicate_username(client, users):
    res = client.post('/api/auth/register', json={
        'username': 'test_student1',
        'email': 'different_email@test.com',
        'password': 'Password123!',
        'full_name': 'Another User',
        'role': 'student'
    })
    assert res.status_code == 409
    assert 'already taken' in res.get_json()['error']

def test_login_success(client, users):
    res = client.post('/api/auth/login', json={
        'identifier': 'test_student1',
        'password': 'StudentPass123!'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert 'token' in data
    assert data['user']['username'] == 'test_student1'

def test_login_invalid_password(client, users):
    res = client.post('/api/auth/login', json={
        'identifier': 'test_student1',
        'password': 'WrongPassword!'
    })
    assert res.status_code == 401

def test_get_current_user_me(client, tokens):
    res = client.get('/api/auth/me', headers={'Authorization': f"Bearer {tokens['student1']}"})
    assert res.status_code == 200
    assert res.get_json()['user']['username'] == 'test_student1'

def test_unauthorized_without_token(client):
    res = client.get('/api/auth/me')
    assert res.status_code == 401

def test_security_headers_present(client):
    res = client.get('/api/health')
    assert res.status_code == 200
    assert res.headers.get('X-Content-Type-Options') == 'nosniff'
    assert res.headers.get('X-Frame-Options') == 'SAMEORIGIN'
    assert '1; mode=block' in res.headers.get('X-XSS-Protection', '')

def test_readiness_probe(client):
    res = client.get('/api/ready')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'ready'
    assert data['database'] == 'connected'
    assert data['model_ready'] is True

def test_rate_limiter_protection(client):
    from backend.utils.rate_limiter import reset_rate_limits
    reset_rate_limits()

    # Trigger rate limit on login endpoint with test header
    hit_rate_limit = False
    for _ in range(25):
        res = client.post('/api/auth/login', json={
            'identifier': 'nonexistent',
            'password': 'bad'
        }, headers={'X-Test-Rate-Limit': '1'})
        if res.status_code == 429:
            hit_rate_limit = True
            assert 'Too many requests' in res.get_json()['error']
            assert 'Retry-After' in res.headers
            break
    assert hit_rate_limit is True
    reset_rate_limits()

def test_admin_self_registration_forbidden(client):
    res = client.post('/api/auth/register', json={
        'username': 'rogue_admin',
        'email': 'rogue@school.edu',
        'password': 'AdminPassword123!',
        'full_name': 'Rogue Admin',
        'role': 'admin'
    })
    assert res.status_code == 403
    data = res.get_json()
    assert 'Administrator accounts cannot be self-registered' in data['error']

def test_forgot_password_endpoint(client):
    # Missing email
    res = client.post('/api/auth/forgot-password', json={})
    assert res.status_code == 400
    assert 'Please provide your registered email' in res.get_json()['error']

    # Valid email (uniform response for security)
    res = client.post('/api/auth/forgot-password', json={'email': 'student@school.edu'})
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'If an active account is associated with' in data['message']



