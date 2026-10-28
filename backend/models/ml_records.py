from datetime import datetime
from backend.extensions import db

class PredictionRecord(db.Model):
    __tablename__ = 'prediction_records'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False, index=True)
    predicted_difficulty = db.Column(db.String(20), nullable=False)  # 'Low', 'Moderate', 'High'
    difficulty_score = db.Column(db.Float, nullable=False)  # 0.0 to 1.0 overall difficulty severity index
    probability_low = db.Column(db.Float, default=0.0)
    probability_moderate = db.Column(db.Float, default=0.0)
    probability_high = db.Column(db.Float, default=0.0)
    contributing_factors = db.Column(db.JSON, nullable=True)  # List/dict of key feature impacts
    model_version = db.Column(db.String(50), nullable=False, default='v1.0')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    recommendations = db.relationship('StudyRecommendation', backref='prediction', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'topic_id': self.topic_id,
            'topic_name': self.topic.name if self.topic else None,
            'predicted_difficulty': self.predicted_difficulty,
            'difficulty_score': round(self.difficulty_score, 4),
            'probability_low': round(self.probability_low, 4),
            'probability_moderate': round(self.probability_moderate, 4),
            'probability_high': round(self.probability_high, 4),
            'contributing_factors': self.contributing_factors or {},
            'model_version': self.model_version,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ModelVersion(db.Model):
    __tablename__ = 'model_versions'

    id = db.Column(db.Integer, primary_key=True)
    version_tag = db.Column(db.String(50), unique=True, nullable=False, index=True)
    model_name = db.Column(db.String(100), nullable=False)
    algorithm = db.Column(db.String(100), nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    precision_macro = db.Column(db.Float, nullable=False)
    recall_macro = db.Column(db.Float, nullable=False)
    f1_macro = db.Column(db.Float, nullable=False)
    f1_weighted = db.Column(db.Float, nullable=True)
    confusion_matrix = db.Column(db.JSON, nullable=True)
    classification_report = db.Column(db.JSON, nullable=True)
    feature_importances = db.Column(db.JSON, nullable=True)
    parameters = db.Column(db.JSON, nullable=True)
    training_sample_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=False, index=True)
    trained_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'version_tag': self.version_tag,
            'model_name': self.model_name,
            'algorithm': self.algorithm,
            'accuracy': round(self.accuracy, 4),
            'precision_macro': round(self.precision_macro, 4),
            'recall_macro': round(self.recall_macro, 4),
            'f1_macro': round(self.f1_macro, 4),
            'f1_weighted': round(self.f1_weighted, 4) if self.f1_weighted else None,
            'confusion_matrix': self.confusion_matrix,
            'classification_report': self.classification_report,
            'feature_importances': self.feature_importances,
            'parameters': self.parameters,
            'training_sample_count': self.training_sample_count,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DatasetRecord(db.Model):
    __tablename__ = 'dataset_records'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    row_count = db.Column(db.Integer, nullable=False)
    column_count = db.Column(db.Integer, nullable=False)
    columns_list = db.Column(db.JSON, nullable=True)
    validation_status = db.Column(db.String(50), default='valid')  # 'valid', 'invalid', 'warning'
    validation_details = db.Column(db.JSON, nullable=True)
    is_active_training_set = db.Column(db.Boolean, default=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_name': self.original_name,
            'row_count': self.row_count,
            'column_count': self.column_count,
            'columns_list': self.columns_list,
            'validation_status': self.validation_status,
            'validation_details': self.validation_details,
            'is_active_training_set': self.is_active_training_set,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ShadowAuditRecord(db.Model):
    __tablename__ = 'shadow_audit_records'

    id = db.Column(db.Integer, primary_key=True)
    production_record_id = db.Column(db.Integer, db.ForeignKey('prediction_records.id'), nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False, index=True)

    production_model_version = db.Column(db.String(50), nullable=False, default='v1.0.0-production-baseline')
    production_prediction = db.Column(db.String(20), nullable=True)  # 'Low', 'Moderate', 'High'

    candidate_model_version = db.Column(db.String(50), nullable=False)
    candidate_prediction = db.Column(db.String(20), nullable=True)
    candidate_difficulty_score = db.Column(db.Float, nullable=True)
    candidate_prob_low = db.Column(db.Float, nullable=True)
    candidate_prob_moderate = db.Column(db.Float, nullable=True)
    candidate_prob_high = db.Column(db.Float, nullable=True)

    disagreement = db.Column(db.Boolean, nullable=False, default=False, index=True)
    execution_status = db.Column(db.String(20), nullable=False, default='success')  # 'success', 'failed'
    error_message = db.Column(db.Text, nullable=True)
    latency_ms = db.Column(db.Float, nullable=True)

    label = db.Column(db.String(100), nullable=False, default='Pilot Estimate — Requires Instructor Review')
    review_decision = db.Column(db.String(50), nullable=True, index=True)  # 'confirmed', 'disagreement', 'needs_more_information'
    review_notes = db.Column(db.Text, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    student = db.relationship('User', foreign_keys=[student_id], lazy=True)
    subject = db.relationship('Subject', foreign_keys=[subject_id], lazy=True)
    topic = db.relationship('Topic', foreign_keys=[topic_id], lazy=True)
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], lazy=True)
    production_record = db.relationship('PredictionRecord', foreign_keys=[production_record_id], lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'production_record_id': self.production_record_id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'topic_id': self.topic_id,
            'topic_name': self.topic.name if self.topic else None,
            'production_model_version': self.production_model_version,
            'production_prediction': self.production_prediction,
            'candidate_model_version': self.candidate_model_version,
            'candidate_prediction': self.candidate_prediction,
            'candidate_difficulty_score': round(self.candidate_difficulty_score, 4) if self.candidate_difficulty_score is not None else None,
            'candidate_probabilities': {
                'low': round(self.candidate_prob_low, 4) if self.candidate_prob_low is not None else 0.0,
                'moderate': round(self.candidate_prob_moderate, 4) if self.candidate_prob_moderate is not None else 0.0,
                'high': round(self.candidate_prob_high, 4) if self.candidate_prob_high is not None else 0.0
            },
            'disagreement': self.disagreement,
            'execution_status': self.execution_status,
            'error_message': self.error_message,
            'latency_ms': round(self.latency_ms, 2) if self.latency_ms is not None else None,
            'label': self.label,
            'review_decision': self.review_decision,
            'review_notes': self.review_notes,
            'reviewed_by': self.reviewed_by,
            'reviewer_name': self.reviewer.full_name if self.reviewer else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class OutlierTelemetryRecord(db.Model):
    __tablename__ = 'outlier_telemetry_records'

    id = db.Column(db.Integer, primary_key=True)
    student_pseudo_id = db.Column(db.String(32), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True, index=True)
    feature_name = db.Column(db.String(50), nullable=False, index=True)
    raw_value = db.Column(db.Float, nullable=False)
    clamped_value = db.Column(db.Float, nullable=False)
    threshold_description = db.Column(db.String(120), nullable=False)
    context = db.Column(db.String(50), nullable=False, default='feature_generation')  # 'feature_generation' or 'input_validation'
    flag_type = db.Column(db.String(50), nullable=False, default='upper_bound_clamped')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    subject = db.relationship('Subject', foreign_keys=[subject_id], lazy=True)
    topic = db.relationship('Topic', foreign_keys=[topic_id], lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'student_pseudo_id': self.student_pseudo_id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'topic_id': self.topic_id,
            'topic_name': self.topic.name if self.topic else None,
            'feature_name': self.feature_name,
            'raw_value': round(self.raw_value, 2),
            'clamped_value': round(self.clamped_value, 2),
            'threshold_description': self.threshold_description,
            'context': self.context,
            'flag_type': self.flag_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SystemSetting(db.Model):
    __tablename__ = 'system_settings'

    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by
        }


