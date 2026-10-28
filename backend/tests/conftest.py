import pytest
import os
import tempfile
from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.config import Config

test_db_file = os.path.join(tempfile.gettempdir(), 'test_app.db')
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{test_db_file}'
    WTF_CSRF_ENABLED = False
    JWT_SECRET_KEY = 'a-very-long-and-secure-test-jwt-secret-key-32bytes-min'
    UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'test_uploads')
    ARTIFACTS_FOLDER = os.path.join(backend_dir, 'artifacts')
    DATA_FOLDER = os.path.join(backend_dir, 'data')

@pytest.fixture(scope='session')
def app():
    if os.path.exists(test_db_file):
        try:
            os.remove(test_db_file)
        except Exception:
            pass

    app = create_app(TestConfig)
    with app.app_context():
        from backend.ml.predictor import MLPredictor
        MLPredictor.get_instance(artifacts_dir=TestConfig.ARTIFACTS_FOLDER).load_artifacts()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

    if os.path.exists(test_db_file):
        try:
            os.remove(test_db_file)
        except Exception:
            pass

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def users(app):
    with app.app_context():
        # Clean users if already exist
        User.query.delete()
        db.session.commit()

        admin = User(username='test_admin', email='admin@test.com', full_name='Admin User', role='admin')
        admin.set_password('AdminPass123!')

        instructor = User(username='test_instructor', email='instructor@test.com', full_name='Prof. Test', role='instructor')
        instructor.set_password('InstructorPass123!')

        instructor2 = User(username='test_instructor2', email='instructor2@test.com', full_name='Prof. Other', role='instructor')
        instructor2.set_password('InstructorPass123!')

        student1 = User(username='test_student1', email='student1@test.com', full_name='Student One', role='student')
        student1.set_password('StudentPass123!')

        student2 = User(username='test_student2', email='student2@test.com', full_name='Student Two', role='student')
        student2.set_password('StudentPass123!')

        db.session.add_all([admin, instructor, instructor2, student1, student2])
        db.session.commit()

        return {
            'admin': {'id': admin.id, 'username': admin.username},
            'instructor': {'id': instructor.id, 'username': instructor.username},
            'instructor2': {'id': instructor2.id, 'username': instructor2.username},
            'student1': {'id': student1.id, 'username': student1.username},
            'student2': {'id': student2.id, 'username': student2.username}
        }

@pytest.fixture
def tokens(client, users):
    def get_token(identifier, password):
        res = client.post('/api/auth/login', json={'identifier': identifier, 'password': password})
        return res.get_json()['token']

    return {
        'admin': get_token('test_admin', 'AdminPass123!'),
        'instructor': get_token('test_instructor', 'InstructorPass123!'),
        'instructor2': get_token('test_instructor2', 'InstructorPass123!'),
        'student1': get_token('test_student1', 'StudentPass123!'),
        'student2': get_token('test_student2', 'StudentPass123!')
    }
