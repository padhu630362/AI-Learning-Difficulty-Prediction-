import os
import uuid
import pandas as pd
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app
from backend.extensions import db
from backend.models.ml_records import DatasetRecord, ModelVersion
from backend.utils.decorators import token_required, roles_required
from backend.ml.preprocessor import MLDataPreprocessor
from backend.ml.trainer import MLTrainingPipeline
from backend.ml.predictor import MLPredictor

datasets_bp = Blueprint('datasets', __name__)

@datasets_bp.route('', methods=['GET'])
@token_required
@roles_required('admin')
def list_datasets():
    datasets = DatasetRecord.query.order_by(DatasetRecord.created_at.desc()).all()
    return jsonify({'datasets': [d.to_dict() for d in datasets]}), 200

@datasets_bp.route('/<int:dataset_id>', methods=['GET'])
@token_required
@roles_required('admin')
def get_dataset_details(dataset_id):
    dataset = db.session.get(DatasetRecord, dataset_id)
    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404

    data = dataset.to_dict()

    # Read preview rows
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], dataset.filename)
    preview = []
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path, nrows=10)
            preview = df.to_dict(orient='records')
        except Exception:
            preview = []

    data['preview'] = preview
    return jsonify({'dataset': data}), 200

@datasets_bp.route('/upload', methods=['POST'])
@token_required
@roles_required('admin')
def upload_dataset():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request. Expected key "file"'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error': 'Only CSV files are supported'}), 400

    orig_filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{orig_filename}"
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_filename)

    file.save(file_path)

    # Validate using MLDataPreprocessor
    preprocessor = MLDataPreprocessor()
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': f'Failed to parse CSV: {str(e)}'}), 400

    is_valid, errors, summary = preprocessor.validate_schema(df, require_target=True)
    status = 'valid' if is_valid else 'invalid'

    dataset_record = DatasetRecord(
        filename=unique_filename,
        original_name=orig_filename,
        row_count=len(df),
        column_count=len(df.columns),
        columns_list=list(df.columns),
        validation_status=status,
        validation_details={
            'errors': errors,
            'summary': summary
        },
        uploaded_by=request.current_user.id
    )
    db.session.add(dataset_record)
    db.session.commit()

    return jsonify({
        'message': 'Dataset uploaded and validated successfully',
        'dataset': dataset_record.to_dict()
    }), 201

@datasets_bp.route('/<int:dataset_id>', methods=['DELETE'])
@token_required
@roles_required('admin')
def delete_dataset(dataset_id):
    dataset = db.session.get(DatasetRecord, dataset_id)
    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], dataset.filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass

    db.session.delete(dataset)
    db.session.commit()
    return jsonify({'message': 'Dataset deleted successfully'}), 200

@datasets_bp.route('/<int:dataset_id>/train', methods=['POST'])
@token_required
@roles_required('admin')
def train_from_dataset(dataset_id):
    dataset = db.session.get(DatasetRecord, dataset_id)
    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404

    if dataset.validation_status != 'valid':
        return jsonify({'error': 'Cannot train on an invalid dataset. Please review validation errors.'}), 400

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], dataset.filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'Dataset file is missing from server storage.'}), 404

    try:
        pipeline = MLTrainingPipeline(artifacts_dir=current_app.config['ARTIFACTS_FOLDER'])
        version_tag = f"model_{dataset.original_name.split('.')[0]}_{uuid.uuid4().hex[:6]}"
        report = pipeline.run_training_pipeline(file_path, version_tag=version_tag)

        # Deactivate existing active models
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
        dataset.is_active_training_set = True
        db.session.commit()

        # Reload predictor instance with newly trained version
        MLPredictor.get_instance().load_version(version_tag)

        return jsonify({
            'message': f"Model training completed successfully using {report['best_model']}.",
            'model_version': model_version.to_dict(),
            'training_report': report
        }), 200

    except Exception as e:
        return jsonify({'error': f'Training failed: {str(e)}'}), 500

