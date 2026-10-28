from flask import Blueprint, request, jsonify
from backend.extensions import db
from backend.models.user import User
from backend.utils.decorators import token_required, roles_required

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
@token_required
@roles_required('admin')
def list_users():
    role_filter = request.args.get('role')
    search = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    query = User.query

    if role_filter:
        query = query.filter_by(role=role_filter)

    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.full_name.ilike(f'%{search}%'))
        )

    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'users': [u.to_dict() for u in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    }), 200

@users_bp.route('/students', methods=['GET'])
@token_required
@roles_required('instructor', 'admin')
def list_students():
    search = request.args.get('search', '').strip()
    query = User.query.filter_by(role='student', is_active=True)

    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.full_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )

    students = query.order_by(User.full_name.asc()).all()
    return jsonify({
        'students': [s.to_dict() for s in students]
    }), 200

@users_bp.route('/<int:user_id>/role', methods=['PUT'])
@token_required
@roles_required('admin')
def update_user_role(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json() or {}
    new_role = data.get('role')
    if new_role not in ['student', 'instructor', 'admin']:
        return jsonify({'error': "Invalid role. Must be 'student', 'instructor', or 'admin'"}), 400

    user.role = new_role
    db.session.commit()
    return jsonify({'message': f'Role updated to {new_role}', 'user': user.to_dict()}), 200

@users_bp.route('/<int:user_id>/status', methods=['PUT'])
@token_required
@roles_required('admin')
def toggle_user_status(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Prevent admin from deactivating themselves
    if user.id == request.current_user.id:
        return jsonify({'error': 'Cannot deactivate your own account'}), 400

    data = request.get_json() or {}
    is_active = data.get('is_active')
    if is_active is None:
        user.is_active = not user.is_active
    else:
        user.is_active = bool(is_active)

    db.session.commit()
    return jsonify({'message': f"User status changed to {'active' if user.is_active else 'inactive'}", 'user': user.to_dict()}), 200
