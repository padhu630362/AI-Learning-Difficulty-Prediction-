from backend.routes.auth import auth_bp
from backend.routes.users import users_bp
from backend.routes.subjects import subjects_bp
from backend.routes.assessments import assessments_bp
from backend.routes.predictions import predictions_bp
from backend.routes.recommendations import recommendations_bp
from backend.routes.alerts import alerts_bp
from backend.routes.progress import progress_bp
from backend.routes.datasets import datasets_bp
from backend.routes.models_mgmt import models_bp
from backend.routes.admin_analytics import admin_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(subjects_bp, url_prefix='/api/subjects')
    app.register_blueprint(assessments_bp, url_prefix='/api/assessments')
    app.register_blueprint(predictions_bp, url_prefix='/api/predictions')
    app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')
    app.register_blueprint(alerts_bp, url_prefix='/api/alerts')
    app.register_blueprint(progress_bp, url_prefix='/api/progress')
    app.register_blueprint(datasets_bp, url_prefix='/api/datasets')
    app.register_blueprint(models_bp, url_prefix='/api/models')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

