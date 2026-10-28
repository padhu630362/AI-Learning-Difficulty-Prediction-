from datetime import datetime
from backend.extensions import db

class StudyRecommendation(db.Model):
    __tablename__ = 'study_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False, index=True)
    prediction_id = db.Column(db.Integer, db.ForeignKey('prediction_records.id'), nullable=True)
    reason = db.Column(db.Text, nullable=False)
    suggested_action = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high'
    resource_url = db.Column(db.String(500), nullable=True)
    is_completed = db.Column(db.Boolean, default=False, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    subject = db.relationship('Subject', lazy=True)
    topic = db.relationship('Topic', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'topic_id': self.topic_id,
            'topic_name': self.topic.name if self.topic else None,
            'prediction_id': self.prediction_id,
            'reason': self.reason,
            'suggested_action': self.suggested_action,
            'priority': self.priority,
            'resource_url': self.resource_url,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class InstructorAlert(db.Model):
    __tablename__ = 'instructor_alerts'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True)
    alert_type = db.Column(db.String(50), nullable=False)  # 'repeated_low_score', 'declining_trend', 'high_difficulty_risk', 'missing_assessments'
    severity = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high', 'critical'
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_reviewed = db.Column(db.Boolean, default=False, index=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    subject = db.relationship('Subject', lazy=True)
    topic = db.relationship('Topic', lazy=True)
    follow_ups = db.relationship('AlertFollowUp', backref='alert', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'instructor_id': self.instructor_id,
            'instructor_name': self.instructor.full_name if self.instructor else None,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'topic_id': self.topic_id,
            'topic_name': self.topic.name if self.topic else None,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'is_reviewed': self.is_reviewed,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'follow_ups_count': len(self.follow_ups),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AlertFollowUp(db.Model):
    __tablename__ = 'alert_follow_ups'

    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey('instructor_alerts.id'), nullable=False, index=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action_taken = db.Column(db.String(150), nullable=False)  # 'mentoring_session', 'custom_worksheet', 'parent_outreach', 'peer_tutoring', 'extended_deadline'
    notes = db.Column(db.Text, nullable=True)
    outcome = db.Column(db.String(100), default='pending')  # 'pending', 'improved', 'stable', 'escalated'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    instructor = db.relationship('User', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'alert_id': self.alert_id,
            'instructor_id': self.instructor_id,
            'instructor_name': self.instructor.full_name if self.instructor else None,
            'action_taken': self.action_taken,
            'notes': self.notes,
            'outcome': self.outcome,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AuditEvent(db.Model):
    __tablename__ = 'audit_events'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.String(50), nullable=True)
    details = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'System',
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

