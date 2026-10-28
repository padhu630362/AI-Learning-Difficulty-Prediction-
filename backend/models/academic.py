from datetime import datetime
from backend.extensions import db

class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    topics = db.relationship('Topic', backref='subject', lazy=True, cascade='all, delete-orphan')
    assessments = db.relationship('Assessment', backref='subject', lazy=True, cascade='all, delete-orphan')
    predictions = db.relationship('PredictionRecord', backref='subject', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'instructor_id': self.instructor_id,
            'instructor_name': self.instructor.full_name if self.instructor else None,
            'topic_count': len(self.topics),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Topic(db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    learning_objectives = db.Column(db.Text, nullable=True)
    difficulty_level = db.Column(db.String(20), default='intermediate')  # 'beginner', 'intermediate', 'advanced'
    order_index = db.Column(db.Integer, default=1)
    resources = db.Column(db.Text, nullable=True)  # Markdown or links
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assessments = db.relationship('Assessment', backref='topic', lazy=True)
    predictions = db.relationship('PredictionRecord', backref='topic', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'name': self.name,
            'description': self.description,
            'learning_objectives': self.learning_objectives,
            'difficulty_level': self.difficulty_level,
            'order_index': self.order_index,
            'resources': self.resources,
            'assessment_count': len(self.assessments),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True, index=True)
    title = db.Column(db.String(150), nullable=False)
    assessment_type = db.Column(db.String(30), nullable=False)  # 'quiz', 'assignment', 'exam'
    max_marks = db.Column(db.Float, nullable=False, default=100.0)
    passing_marks = db.Column(db.Float, nullable=False, default=40.0)
    weightage = db.Column(db.Float, default=1.0)
    assessment_date = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    results = db.relationship('StudentAssessmentResult', backref='assessment', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'topic_id': self.topic_id,
            'topic_name': self.topic.name if self.topic else 'General Subject',
            'title': self.title,
            'assessment_type': self.assessment_type,
            'max_marks': self.max_marks,
            'passing_marks': self.passing_marks,
            'weightage': self.weightage,
            'assessment_date': self.assessment_date.isoformat() if self.assessment_date else None,
            'submissions_count': len(self.results),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class StudentAssessmentResult(db.Model):
    __tablename__ = 'student_assessment_results'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False, index=True)
    marks_obtained = db.Column(db.Float, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    study_time_minutes = db.Column(db.Float, default=60.0)  # minutes studied
    attempt_count = db.Column(db.Integer, default=1)
    repeated_errors_count = db.Column(db.Integer, default=0)
    completion_status = db.Column(db.String(30), default='completed')  # 'completed', 'in_progress', 'missed'
    remarks = db.Column(db.Text, nullable=True)
    submission_date = db.Column(db.Date, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'assessment_id': self.assessment_id,
            'assessment_title': self.assessment.title if self.assessment else None,
            'assessment_type': self.assessment.assessment_type if self.assessment else None,
            'subject_id': self.assessment.subject_id if self.assessment else None,
            'subject_name': self.assessment.subject.name if self.assessment and self.assessment.subject else None,
            'topic_id': self.assessment.topic_id if self.assessment else None,
            'topic_name': self.assessment.topic.name if self.assessment and self.assessment.topic else None,
            'marks_obtained': self.marks_obtained,
            'max_marks': self.assessment.max_marks if self.assessment else 100.0,
            'percentage': round(self.percentage, 2),
            'study_time_minutes': self.study_time_minutes,
            'attempt_count': self.attempt_count,
            'repeated_errors_count': self.repeated_errors_count,
            'completion_status': self.completion_status,
            'remarks': self.remarks,
            'submission_date': self.submission_date.isoformat() if self.submission_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

