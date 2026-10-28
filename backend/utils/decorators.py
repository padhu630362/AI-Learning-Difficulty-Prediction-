import jwt
from functools import wraps
from flask import request, jsonify, current_app
from backend.extensions import db
from backend.models.user import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header is missing'}), 401
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Invalid authorization header format. Expected "Bearer <token>"'}), 401
        
        token = parts[1]
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            user_id = int(payload.get('sub'))
            user = db.session.get(User, user_id)
            if not user or not user.is_active:
                return jsonify({'error': 'User account is inactive or not found'}), 401
            request.current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired. Please log in again.'}), 401
        except (jwt.InvalidTokenError, Exception) as e:
            return jsonify({'error': 'Invalid authentication token'}), 401

        return f(*args, **kwargs)
    return decorated

def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user') or not request.current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            if request.current_user.role not in allowed_roles:
                return jsonify({
                    'error': f'Access forbidden: required role one of {list(allowed_roles)}, but you have {request.current_user.role}'
                }), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

