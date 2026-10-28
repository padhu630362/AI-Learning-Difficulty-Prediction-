import os
from flask import Flask, jsonify
from backend.config import Config
from backend.extensions import db, cors
from backend.routes import register_blueprints
from backend.ml.predictor import MLPredictor

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})

    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
    os.makedirs(app.config['ARTIFACTS_FOLDER'], exist_ok=True)

    # Register blueprints
    register_blueprints(app)

    # Security headers middleware
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    # Health check route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        predictor = MLPredictor.get_instance(artifacts_dir=app.config['ARTIFACTS_FOLDER'])
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'model_ready': predictor.is_ready(),
            'model_version': predictor.version_tag if predictor.is_ready() else None
        }), 200

    # Readiness probe route
    @app.route('/api/ready', methods=['GET'])
    def readiness_check():
        db_ok = True
        try:
            db.session.execute(db.text("SELECT 1"))
        except Exception:
            db_ok = False

        predictor = MLPredictor.get_instance(artifacts_dir=app.config['ARTIFACTS_FOLDER'])
        model_ok = predictor.is_ready()

        status_code = 200 if (db_ok and model_ok) else 503
        return jsonify({
            'status': 'ready' if (db_ok and model_ok) else 'degraded',
            'database': 'connected' if db_ok else 'unavailable',
            'model_ready': model_ok,
            'model_version': predictor.version_tag if model_ok else None
        }), status_code

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request parameters'}), 400

    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({'error': 'Uploaded file exceeds the maximum permitted size (16MB)'}), 413

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'An internal server error occurred'}), 500

    with app.app_context():
        db.create_all()
        # Initialize predictor singleton
        MLPredictor.get_instance(artifacts_dir=app.config['ARTIFACTS_FOLDER'])

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

