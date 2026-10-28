"""
LMS Canonical Dataset Generator for AI Learning Difficulty Predictor.

PROVENANCE: SYNTHETIC DATASET (Explicitly labeled)
This module generates an aligned, rubric-grounded synthetic dataset that replicates
the exact feature schema, ranges, and mathematical definitions produced by the live
application's `compute_student_topic_features()` in `backend/routes/predictions.py`.

Key Alignment Criteria:
1. Exact Feature Definitions:
   - quiz_score, assignment_score, exam_score in [0, 100]
   - study_time_weekly in [1.0, 28.0] hours
   - attendance_rate in [40.0, 100.0] percent (assignment completion proxy)
   - attempt_count in [1, 6] (quiz re-attempts)
   - repeated_errors_count in [0, 15] (formative quiz mistakes)
   - previous_topic_score in [15.0, 100.0]
   - learning_pace_gap: exact live formula round((quiz * 0.5 + assign * 0.5) - 70.0, 1)
   - topic_difficulty_level: all three tiers ('beginner', 'intermediate', 'advanced')
2. Student Identity Tracking:
   - Tracks unique student_id across multiple sequential topic observations.
   - Enables Group-Aware Splitting (GroupKFold / GroupShuffleSplit) to eliminate student leakage.
3. Ground-Truth Target Labeling Rubric:
   - Multi-dimensional academic struggle index combining assessment mastery, repeated errors,
     re-attempt frequency, submission compliance, and self-study hours.
   - Realistic pedagogical thresholds for Low, Moderate, High difficulty risk.
"""

import os
import numpy as np
import pandas as pd

def generate_lms_canonical_dataset(
    num_students=500,
    topics_per_student=6,
    random_seed=42,
    output_path=None
):
    """
    Generates a student-grouped, curriculum-aligned synthetic dataset.
    Total records = num_students * topics_per_student (e.g. 500 * 6 = 3,000 records).
    """
    np.random.seed(random_seed)
    total_records = num_students * topics_per_student

    # Pre-define topic sequence across curriculum with all 3 difficulty tiers
    curriculum_topics = [
        {'order': 1, 'level': 'beginner',     'subject': 'Data Structures', 'base_difficulty': 0.0},
        {'order': 2, 'level': 'intermediate', 'subject': 'Data Structures', 'base_difficulty': 0.5},
        {'order': 3, 'level': 'intermediate', 'subject': 'Data Structures', 'base_difficulty': 0.7},
        {'order': 4, 'level': 'advanced',     'subject': 'Data Structures', 'base_difficulty': 1.2},
        {'order': 1, 'level': 'beginner',     'subject': 'Linear Algebra',  'base_difficulty': 0.0},
        {'order': 2, 'level': 'intermediate', 'subject': 'Linear Algebra',  'base_difficulty': 0.6},
    ]

    records = []

    for s_idx in range(1, num_students + 1):
        # Latent student characteristics
        # Ability: baseline intellectual grasp (-2.5 to +2.5)
        ability = float(np.random.normal(0.0, 1.1))
        # Diligence: consistent study effort (-2.0 to +2.0)
        diligence = float(np.random.normal(0.0, 1.0))
        # Grit / perseverance when facing hard topics
        grit = float(np.random.normal(0.0, 0.8))

        # Overall student subject exam baseline (term-wide exam percentage)
        base_exam = np.clip(70.0 + ability * 12.0 + diligence * 5.0 + np.random.normal(0, 4.0), 20.0, 98.0)

        # Baseline previous mastery for initial topic (Topic 1)
        prev_topic_score = np.clip(72.0 + ability * 14.0 + np.random.normal(0, 5.0), 25.0, 98.0)

        for t_info in curriculum_topics[:topics_per_student]:
            t_order = t_info['order']
            t_level = t_info['level']
            diff_penalty = t_info['base_difficulty'] * 8.0

            # Topic-specific performance factors
            # Study time in weekly hours [1.0 to 28.0] (matching live app formula)
            base_study = 11.0 + diligence * 4.5 + (0.8 if t_level == 'advanced' else 0.0) + np.random.normal(0, 2.5)
            study_time_weekly = float(np.clip(base_study, 1.0, 28.0))

            # Assignment completion / attendance rate [40.0 to 100.0] (matching live app)
            base_att = 85.0 + diligence * 8.0 + ability * 3.0 + np.random.normal(0, 5.0)
            attendance_rate = float(np.clip(base_att, 40.0, 100.0))

            # Assessment scores: influenced by ability, diligence, topic difficulty, and previous topic mastery
            score_momentum = (ability * 14.0) + (diligence * 5.0) + ((prev_topic_score - 70.0) * 0.15) - diff_penalty

            quiz_score = float(np.clip(68.0 + score_momentum + np.random.normal(0, 6.5), 10.0, 99.0))
            assignment_score = float(np.clip(72.0 + score_momentum + (diligence * 4.0) + np.random.normal(0, 5.5), 15.0, 99.0))
            exam_score = float(np.clip(base_exam - (diff_penalty * 0.4) + np.random.normal(0, 5.0), 10.0, 98.0))

            # Quiz attempts: struggling students take multiple attempts [1 to 6]
            curr_avg = (quiz_score * 0.5 + assignment_score * 0.5)
            attempt_bias = max(0.0, (75.0 - curr_avg) / 15.0)
            attempt_count = int(np.clip(round(1.0 + attempt_bias * 0.8 + np.random.exponential(0.35)), 1, 6))

            # Repeated errors: high when scores are low and attempts are elevated [0 to 15]
            error_bias = max(0.0, (72.0 - quiz_score) / 10.0)
            repeated_errors_count = int(np.clip(round(error_bias * 1.8 + np.random.poisson(0.8)), 0, 15))

            # EXACT Live Application Formula for learning_pace_gap:
            # round((quiz_score * 0.5 + assignment_score * 0.5) - 70.0, 1)
            learning_pace_gap = round((quiz_score * 0.5 + assignment_score * 0.5) - 70.0, 1)

            # -----------------------------------------------------------------
            # Ground-Truth Target Labeling: Multi-Dimensional Mastery Rubric
            # -----------------------------------------------------------------
            # Weighted assessment mastery M:
            mastery = (0.40 * quiz_score + 0.35 * assignment_score + 0.25 * exam_score)

            # Composite Academic Struggle Score S in [0, 100]:
            # S increases with low mastery, high repeated errors, high retakes, low attendance
            struggle_score = (
                (100.0 - mastery) * 0.65 +
                min(repeated_errors_count * 2.8, 18.0) +
                min((attempt_count - 1) * 3.0, 12.0) +
                max(0.0, (80.0 - attendance_rate) * 0.25) -
                min(study_time_weekly * 0.4, 6.0)
            )

            # Add realistic minor classroom noise (+/- 2.5)
            struggle_score += float(np.random.normal(0, 2.5))
            struggle_score = float(np.clip(struggle_score, 0.0, 100.0))

            # Pedagogical Risk Thresholds:
            # Low Difficulty:      mastery > 75%, few errors, consistent submission (struggle < 28.0)
            # Moderate Difficulty: borderline mastery 55-75%, occasional gaps (28.0 <= struggle < 48.0)
            # High Difficulty:     critical risk, mastery < 55%, chronic errors (struggle >= 48.0)
            if struggle_score < 28.0:
                difficulty_category = 'Low'
            elif struggle_score < 48.0:
                difficulty_category = 'Moderate'
            else:
                difficulty_category = 'High'

            records.append({
                'student_id': s_idx,
                'quiz_score': round(quiz_score, 1),
                'assignment_score': round(assignment_score, 1),
                'exam_score': round(exam_score, 1),
                'study_time_weekly': round(study_time_weekly, 1),
                'attendance_rate': round(attendance_rate, 1),
                'attempt_count': attempt_count,
                'repeated_errors_count': repeated_errors_count,
                'previous_topic_score': round(prev_topic_score, 1),
                'learning_pace_gap': learning_pace_gap,
                'topic_difficulty_level': t_level,
                'difficulty_category': difficulty_category
            })

            # Update previous_topic_score for the next topic in curriculum sequence
            prev_topic_score = curr_avg

    df = pd.DataFrame(records)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"LMS Canonical Dataset successfully generated at: {output_path}")
        print(f"Total rows: {len(df)} across {num_students} unique students.")
        print("Class distribution:")
        print(df['difficulty_category'].value_counts(normalize=True).round(4))
        print("Topic difficulty levels:")
        print(df['topic_difficulty_level'].value_counts(normalize=True).round(4))

    return df

if __name__ == '__main__':
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    out_file = os.path.join(backend_dir, 'data', 'lms_canonical_training_dataset.csv')
    generate_lms_canonical_dataset(num_students=500, topics_per_student=6, random_seed=42, output_path=out_file)

