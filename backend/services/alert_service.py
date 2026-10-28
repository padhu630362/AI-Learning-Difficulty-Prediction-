from datetime import datetime
from backend.extensions import db
from backend.models.support import InstructorAlert, AlertFollowUp
from backend.models.academic import StudentAssessmentResult, Subject, Assessment

class AlertService:
    @staticmethod
    def evaluate_and_generate_alerts(student_id, subject_id, instructor_id=None, prediction=None):
        """
        Analyzes a student's recent performance and predictions in a subject to detect early support needs.
        Ensures idempotency / no duplicate unreviewed alerts for the same underlying condition.
        """
        # If instructor_id not supplied, fetch from Subject
        subject = db.session.get(Subject, subject_id)
        if not subject:
            return []
        
        target_instructor_id = instructor_id or subject.instructor_id
        
        # Query student results for this subject
        results = (
            StudentAssessmentResult.query
            .join(Assessment, StudentAssessmentResult.assessment_id == Assessment.id)
            .filter(StudentAssessmentResult.student_id == student_id, Assessment.subject_id == subject_id)
            .order_by(StudentAssessmentResult.created_at.desc())
            .limit(5)
            .all()
        )

        generated_alerts = []

        # 1. Condition: Repeated low scores (< 50% on 2 or more recent assessments)
        low_scores = [r for r in results if r.percentage < 50.0]
        if len(low_scores) >= 2:
            existing = InstructorAlert.query.filter_by(
                student_id=student_id,
                subject_id=subject_id,
                alert_type='repeated_low_score',
                is_reviewed=False
            ).first()
            if not existing:
                alert = InstructorAlert(
                    student_id=student_id,
                    instructor_id=target_instructor_id,
                    subject_id=subject_id,
                    topic_id=low_scores[0].assessment.topic_id if low_scores[0].assessment else None,
                    alert_type='repeated_low_score',
                    severity='high',
                    title=f"Repeated Low Scores in {subject.name}",
                    description=f"Student scored below 50% on {len(low_scores)} recent assessments (latest: {low_scores[0].percentage}%). Early intervention recommended."
                )
                db.session.add(alert)
                generated_alerts.append(alert)

        # 2. Condition: Declining trend across 3 assessments
        if len(results) >= 3:
            p0 = results[0].percentage
            p1 = results[1].percentage
            p2 = results[2].percentage
            if p0 < p1 < p2:  # Most recent is lowest
                existing = InstructorAlert.query.filter_by(
                    student_id=student_id,
                    subject_id=subject_id,
                    alert_type='declining_trend',
                    is_reviewed=False
                ).first()
                if not existing:
                    alert = InstructorAlert(
                        student_id=student_id,
                        instructor_id=target_instructor_id,
                        subject_id=subject_id,
                        topic_id=results[0].assessment.topic_id if results[0].assessment else None,
                        alert_type='declining_trend',
                        severity='medium',
                        title=f"Performance Decline Detected in {subject.name}",
                        description=f"Student scores have steadily decreased over the last 3 assessments: {p2}% -> {p1}% -> {p0}%."
                    )
                    db.session.add(alert)
                    generated_alerts.append(alert)

        # 3. Condition: High Difficulty Risk predicted by ML
        if prediction and prediction.predicted_difficulty == 'High':
            existing = InstructorAlert.query.filter_by(
                student_id=student_id,
                subject_id=subject_id,
                topic_id=prediction.topic_id,
                alert_type='high_difficulty_risk',
                is_reviewed=False
            ).first()
            if not existing:
                topic_title = prediction.topic.name if prediction.topic else 'Assigned Topic'
                alert = InstructorAlert(
                    student_id=student_id,
                    instructor_id=target_instructor_id,
                    subject_id=subject_id,
                    topic_id=prediction.topic_id,
                    alert_type='high_difficulty_risk',
                    severity='critical' if prediction.probability_high > 0.75 else 'high',
                    title=f"High Learning Difficulty Predicted: {topic_title}",
                    description=f"AI model predicted High difficulty risk (Confidence: {round(prediction.probability_high * 100, 1)}%) based on topic accuracy and error rate."
                )
                db.session.add(alert)
                generated_alerts.append(alert)

        # 4. Condition: Missing assessments
        missed = [r for r in results if r.completion_status == 'missed']
        if len(missed) >= 1:
            existing = InstructorAlert.query.filter_by(
                student_id=student_id,
                subject_id=subject_id,
                alert_type='missing_assessments',
                is_reviewed=False
            ).first()
            if not existing:
                alert = InstructorAlert(
                    student_id=student_id,
                    instructor_id=target_instructor_id,
                    subject_id=subject_id,
                    topic_id=missed[0].assessment.topic_id if missed[0].assessment else None,
                    alert_type='missing_assessments',
                    severity='medium',
                    title=f"Missed Assessments in {subject.name}",
                    description=f"Student has missed {len(missed)} scheduled assessment(s). Please follow up to offer makeup opportunities or support."
                )
                db.session.add(alert)
                generated_alerts.append(alert)

        if generated_alerts:
            db.session.commit()

        return generated_alerts

    @staticmethod
    def add_follow_up(alert_id, instructor_id, action_taken, notes, outcome='pending', mark_reviewed=True):
        alert = db.session.get(InstructorAlert, alert_id)
        if not alert:
            return None, "Alert not found."

        follow_up = AlertFollowUp(
            alert_id=alert_id,
            instructor_id=instructor_id,
            action_taken=action_taken,
            notes=notes,
            outcome=outcome
        )
        db.session.add(follow_up)

        if mark_reviewed:
            alert.is_reviewed = True
            alert.reviewed_at = datetime.utcnow()

        db.session.commit()
        return follow_up, None

