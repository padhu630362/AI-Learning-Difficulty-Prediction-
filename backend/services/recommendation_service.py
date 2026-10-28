from datetime import datetime
from backend.extensions import db
from backend.models.support import StudyRecommendation

class RecommendationService:
    @staticmethod
    def generate_recommendations_for_prediction(student_id, subject_id, topic_id, prediction_record):
        """
        Creates actionable, personalized study recommendations based on ML prediction results.
        Enforces idempotency and de-duplication so duplicate uncompleted recommendations
        do not accumulate upon repeated predictions.
        """
        pred_difficulty = prediction_record.predicted_difficulty
        diff_score = prediction_record.difficulty_score
        topic = prediction_record.topic
        topic_name = topic.name if topic else 'this topic'
        resource_link = topic.resources if (topic and topic.resources) else None

        candidate_recs = []

        if pred_difficulty == 'High':
            # Critical intervention recommendations
            candidate_recs.append({
                'reason': f"Predicted High learning difficulty (severity index: {round(diff_score * 100, 1)}%) based on recent assessment history and error patterns.",
                'suggested_action': f"Revise foundational concepts in {topic_name}. Review lecture slides and step-by-step problem walkthroughs.",
                'priority': 'high',
                'resource_url': resource_link
            })
            candidate_recs.append({
                'reason': "Frequent misconceptions detected in formative assessments.",
                'suggested_action': f"Book a 1-on-1 tutoring or office-hours check-in with your instructor for {topic_name}.",
                'priority': 'high',
                'resource_url': resource_link
            })
        elif pred_difficulty == 'Moderate':
            candidate_recs.append({
                'reason': f"Moderate difficulty flagged (severity index: {round(diff_score * 100, 1)}%). Student demonstrates partial mastery.",
                'suggested_action': f"Complete targeted practice questions and re-attempt the chapter quiz for {topic_name}.",
                'priority': 'medium',
                'resource_url': resource_link
            })
        else: # Low difficulty
            candidate_recs.append({
                'reason': "Strong comprehension demonstrated across recent assessments.",
                'suggested_action': f"Reinforce mastery in {topic_name} by attempting advanced challenge problems or assisting peers in discussion groups.",
                'priority': 'low',
                'resource_url': resource_link
            })

        persisted_recs = []
        for item in candidate_recs:
            # Check for existing uncompleted recommendation with identical action
            existing = StudyRecommendation.query.filter_by(
                student_id=student_id,
                topic_id=topic_id,
                suggested_action=item['suggested_action'],
                is_completed=False
            ).first()

            if existing:
                # Update reference to latest prediction without creating duplicate
                existing.prediction_id = prediction_record.id
                existing.reason = item['reason']
                existing.priority = item['priority']
                if item['resource_url']:
                    existing.resource_url = item['resource_url']
                persisted_recs.append(existing)
            else:
                new_rec = StudyRecommendation(
                    student_id=student_id,
                    subject_id=subject_id,
                    topic_id=topic_id,
                    prediction_id=prediction_record.id,
                    reason=item['reason'],
                    suggested_action=item['suggested_action'],
                    priority=item['priority'],
                    resource_url=item['resource_url']
                )
                db.session.add(new_rec)
                persisted_recs.append(new_rec)

        db.session.commit()
        return persisted_recs

    @staticmethod
    def mark_completed(recommendation_id, student_id):
        rec = StudyRecommendation.query.filter_by(id=recommendation_id, student_id=student_id).first()
        if not rec:
            return None, "Recommendation not found or not owned by student."
        rec.is_completed = True
        rec.completed_at = datetime.utcnow()
        db.session.commit()
        return rec, None
