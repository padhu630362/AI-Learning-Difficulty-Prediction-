import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from backend.extensions import db
from backend.models.user import User
from backend.utils.decorators import token_required
from backend.utils.rate_limiter import rate_limit

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@rate_limit(max_requests=20, window_seconds=60)
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    role = data.get('role', 'student').strip().lower()

    if not username or not email or not password or not full_name:
        return jsonify({'error': 'All fields (username, email, password, full_name) are required'}), 400

    # Security: Admin accounts cannot be self-registered through public registration
    if role == 'admin':
        return jsonify({
            'error': 'Administrator accounts cannot be self-registered. Admin privileges must be assigned through an authorized administrative process.'
        }), 403

    if role not in ['student', 'instructor']:
        return jsonify({'error': "Invalid role. Public registration permits 'student' or 'instructor' only."}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username is already taken'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email is already registered'}), 409

    user = User(
        username=username,
        email=email,
        full_name=full_name,
        role=role
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'Registration successful. You can now log in.',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
@rate_limit(max_requests=20, window_seconds=60)
def login():
    data = request.get_json() or {}
    identifier = data.get('identifier', '').strip()  # username or email
    password = data.get('password', '')

    if not identifier or not password:
        return jsonify({'error': 'Username/email and password are required'}), 400

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier.lower())
    ).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401

    if not user.is_active:
        return jsonify({'error': 'This account has been deactivated. Please contact support.'}), 403

    # Generate JWT
    payload = {
        'sub': str(user.id),
        'username': user.username,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRATION_HOURS']),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

    return jsonify({
        'token': token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    return jsonify({
        'user': request.current_user.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    # In a stateless JWT setup, client deletes token. Endpoint acknowledges logout.
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/forgot-password', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=60)
def forgot_password():
    data = request.get_json() or {}
    identifier = (data.get('identifier') or data.get('email') or '').strip()

    if not identifier:
        return jsonify({'error': 'Please provide your registered email or username.'}), 400

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier.lower())
    ).first()

    # Privacy preservation: uniform response prevents account enumeration
    return jsonify({
        'message': f"If an active account is associated with '{identifier}', password recovery guidance has been processed. Please check your institutional email or consult your course administrator.",
        'success': True
    }), 200


