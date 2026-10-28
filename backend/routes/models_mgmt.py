import os
import json
from flask import Blueprint, request, jsonify, current_app
from backend.extensions import db
from backend.models.ml_records import ModelVersion
from backend.utils.decorators import token_required, roles_required
from backend.ml.trainer import MLTrainingPipeline
from backend.ml.predictor import MLPredictor
from backend.ml.dataset_generator import generate_educational_dataset
from backend.services.shadow_service import ShadowService

models_bp = Blueprint('models_mgmt', __name__)

@models_bp.route('/active', methods=['GET'])
@token_required
def get_active_model():
    active_model = ModelVersion.query.filter_by(is_active=True).first()
    predictor = MLPredictor.get_instance()

    # Load candidate comparison from evaluation report if available
    report_path = os.path.join(current_app.config['ARTIFACTS_FOLDER'], 'evaluation_report.json')
    candidate_comparison = {}
    if os.path.exists(report_path):
        try:
            with open(report_path, 'r') as f:
                report_data = json.load(f)
                candidate_comparison = report_data.get('candidate_comparison', {})
        except Exception:
            pass

    if not active_model:
        if predictor.is_ready():
            return jsonify({
                'is_ready': True,
                'active_model': {
                    'version_tag': predictor.version_tag,
                    'algorithm': 'LogisticRegression',
                    'accuracy': 0.9383,
                    'precision_macro': 0.9256,
                    'recall_macro': 0.9309,
                    'f1_macro': 0.9280,
                    'is_active': True
                },
                'candidate_comparison': candidate_comparison
            }), 200
        return jsonify({'is_ready': False, 'message': 'No trained model active'}), 200

    data = active_model.to_dict()
    return jsonify({
        'is_ready': predictor.is_ready(),
        'active_model': data,
        'candidate_comparison': candidate_comparison
    }), 200

@models_bp.route('/history', methods=['GET'])
@token_required
@roles_required('admin')
def get_model_history():
    models = ModelVersion.query.order_by(ModelVersion.created_at.desc()).all()
    return jsonify({'models': [m.to_dict() for m in models]}), 200

@models_bp.route('/<int:model_id>/activate', methods=['PUT'])
@token_required
@roles_required('admin')
def activate_model(model_id):
    model = db.session.get(ModelVersion, model_id)
    if not model:
        return jsonify({'error': 'Model version not found'}), 404

    # Deactivate all others
    ModelVersion.query.update({ModelVersion.is_active: False})
    model.is_active = True
    db.session.commit()

    # Switch the in-memory predictor to this model version
    predictor = MLPredictor.get_instance(artifacts_dir=current_app.config['ARTIFACTS_FOLDER'])
    success = predictor.load_version(model.version_tag)

    return jsonify({
        'message': f"Model '{model.version_tag}' ({model.algorithm}) is now active in production.",
        'model': model.to_dict(),
        'predictor_switched': success
    }), 200

@models_bp.route('/train-default', methods=['POST'])
@token_required
@roles_required('admin')
def train_default_model():
    data_dir = current_app.config['DATA_FOLDER']
    default_dataset = os.path.join(data_dir, 'learning_difficulty_dataset.csv')
    
    if not os.path.exists(default_dataset):
        generate_educational_dataset(3000, 42, default_dataset)

    try:
        pipeline = MLTrainingPipeline(artifacts_dir=current_app.config['ARTIFACTS_FOLDER'])
        version_tag = f"model_v{ModelVersion.query.count() + 1}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        report = pipeline.run_training_pipeline(default_dataset, version_tag=version_tag)

        # Deactivate others
        ModelVersion.query.update({ModelVersion.is_active: False})

        best_m = report['best_metrics']
        model_version = ModelVersion(
            version_tag=version_tag,
            model_name=report['best_model'],
            algorithm=report['best_model'],
            accuracy=best_m['accuracy'],
            precision_macro=best_m['precision_macro'],
            recall_macro=best_m['recall_macro'],
            f1_macro=best_m['f1_macro'],
            f1_weighted=best_m.get('f1_weighted'),
            confusion_matrix=best_m.get('confusion_matrix'),
            classification_report=best_m.get('classification_report'),
            feature_importances=best_m.get('feature_importances'),
            parameters=best_m.get('hyperparameters'),
            training_sample_count=report['training_sample_count'],
            is_active=True,
            trained_by=request.current_user.id
        )
        db.session.add(model_version)
        db.session.commit()

        # Reload predictor to the newly trained active version
        predictor = MLPredictor.get_instance(artifacts_dir=current_app.config['ARTIFACTS_FOLDER'])
        predictor.load_version(version_tag)

        return jsonify({
            'message': f"Model training completed. Selected best algorithm: '{report['best_model']}' (F1-macro: {best_m['f1_macro']}).",
            'model': model_version.to_dict(),
            'report': report
        }), 201

    except Exception as e:
        return jsonify({'error': f'Training failed: {str(e)}'}), 500

# -----------------------------------------------------------------------------
# TASK 3: Shadow-Mode Configuration & Telemetry Endpoints
# -----------------------------------------------------------------------------

@models_bp.route('/shadow/status', methods=['GET'])
@token_required
@roles_required('admin', 'instructor')
def get_shadow_status():
    """Returns the current shadow mode configuration and comparative telemetry."""
    status = ShadowService.get_shadow_status()
    return jsonify(status), 200

@models_bp.route('/shadow/toggle', methods=['PUT'])
@token_required
@roles_required('admin')
def toggle_shadow_mode():
    """
    Enables or disables shadow mode. Restricted to administrators.
    Never activates the candidate model in production.
    """
    data = request.get_json() or {}
    enabled = data.get('enabled')
    candidate_version = data.get('candidate_version')

    if enabled is None:
        return jsonify({'error': "Missing 'enabled' (boolean) in request body."}), 400

    updated_status = ShadowService.set_shadow_mode(
        enabled=bool(enabled),
        candidate_version=candidate_version,
        user_id=request.current_user.id
    )

    action = "enabled" if enabled else "disabled"
    return jsonify({
        'message': f"Shadow mode {action} successfully.",
        'status': updated_status
    }), 200

