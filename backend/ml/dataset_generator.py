import os
import numpy as np
import pandas as pd

def generate_educational_dataset(num_samples=3000, random_seed=42, output_path=None):
    """
    Generates a realistic, documented synthetic educational dataset representing student learning data.
    Features:
    - quiz_score: 0-100 float
    - assignment_score: 0-100 float
    - exam_score: 0-100 float
    - study_time_weekly: 1-25 hours float
    - attendance_rate: 40-100 percent float
    - attempt_count: 1-6 integer
    - repeated_errors_count: 0-15 integer
    - previous_topic_score: 0-100 float
    - learning_pace_gap: -25 to +25 (negative = lagging behind schedule)
    - topic_difficulty_level: 'beginner', 'intermediate', 'advanced'
    
    Target:
    - difficulty_category: 'Low', 'Moderate', 'High'
    """
    np.random.seed(random_seed)
    
    # Latent student baseline ability (-2 to +2 standard normal)
    ability = np.random.normal(0, 1.2, num_samples)
    
    # Topic nominal difficulty: 0 = beginner, 1 = intermediate, 2 = advanced
    topic_diff_int = np.random.choice([0, 1, 2], size=num_samples, p=[0.3, 0.45, 0.25])
    diff_labels = ['beginner', 'intermediate', 'advanced']
    topic_difficulty_level = [diff_labels[i] for i in topic_diff_int]
    
    # Weekly study hours (mean ~ 8-12 hrs, influenced slightly by effort)
    effort = np.random.normal(0, 1.0, num_samples)
    study_time_weekly = np.clip(10 + 3.5 * effort + 1.5 * ability + np.random.normal(0, 2, num_samples), 1.0, 28.0)
    
    # Attendance rate (60% to 100%)
    attendance_rate = np.clip(80 + 8 * effort + 5 * ability + np.random.normal(0, 6, num_samples), 40.0, 100.0)
    
    # Previous topic mastery
    previous_topic_score = np.clip(70 + 15 * ability + np.random.normal(0, 8, num_samples), 20.0, 100.0)
    
    # Scores: influenced by ability, effort, topic difficulty, and previous mastery
    score_bias = (ability * 16.0) + (effort * 5.0) + (previous_topic_score * 0.15) - (topic_diff_int * 8.0)
    
    quiz_score = np.clip(68.0 + score_bias + np.random.normal(0, 7.0, num_samples), 10.0, 100.0)
    assignment_score = np.clip(72.0 + score_bias + (effort * 4.0) + np.random.normal(0, 6.0, num_samples), 15.0, 100.0)
    exam_score = np.clip(65.0 + score_bias + np.random.normal(0, 8.5, num_samples), 10.0, 100.0)
    
    # Attempt count: students struggling take more attempts
    struggle_factor = (100.0 - (quiz_score * 0.4 + assignment_score * 0.3 + exam_score * 0.3)) / 20.0
    attempt_count = np.clip(np.round(1.0 + struggle_factor * 0.6 + np.random.exponential(0.3, num_samples)), 1, 6).astype(int)
    
    # Repeated errors: high when scores are low and attempts are high
    repeated_errors_count = np.clip(np.round(struggle_factor * 1.5 + np.random.poisson(1.0, num_samples)), 0, 15).astype(int)
    
    # Learning pace gap: -20 to +20
    learning_pace_gap = np.clip(score_bias * 0.6 + np.random.normal(0, 4.0, num_samples), -30.0, 30.0)
    
    # Determine Difficulty Category based on ground-truth composite difficulty index
    # We formulate a multi-faceted academic difficulty score:
    composite_struggle = (
        0.35 * (100.0 - quiz_score) +
        0.25 * (100.0 - assignment_score) +
        0.25 * (100.0 - exam_score) +
        2.5 * repeated_errors_count +
        4.0 * (attempt_count - 1) +
        0.15 * (100.0 - previous_topic_score) -
        0.8 * study_time_weekly
    )
    
    # Introduce small realistic classroom variance (5% noise)
    composite_struggle += np.random.normal(0, 3.5, num_samples)
    
    # Define realistic thresholds:
    # composite_struggle < 28 -> Low Difficulty (student understands well)
    # 28 <= composite_struggle < 46 -> Moderate Difficulty (some gaps, requires revision)
    # composite_struggle >= 46 -> High Difficulty (critical gaps, requires intervention)
    difficulty_category = []
    for val in composite_struggle:
        if val < 28.0:
            difficulty_category.append('Low')
        elif val < 46.0:
            difficulty_category.append('Moderate')
        else:
            difficulty_category.append('High')
            
    df = pd.DataFrame({
        'quiz_score': np.round(quiz_score, 1),
        'assignment_score': np.round(assignment_score, 1),
        'exam_score': np.round(exam_score, 1),
        'study_time_weekly': np.round(study_time_weekly, 1),
        'attendance_rate': np.round(attendance_rate, 1),
        'attempt_count': attempt_count,
        'repeated_errors_count': repeated_errors_count,
        'previous_topic_score': np.round(previous_topic_score, 1),
        'learning_pace_gap': np.round(learning_pace_gap, 1),
        'topic_difficulty_level': topic_difficulty_level,
        'difficulty_category': difficulty_category
    })
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Dataset successfully created at: {output_path} with {len(df)} records.")
        print("Class distribution:")
        print(df['difficulty_category'].value_counts(normalize=True))
        
    return df

if __name__ == '__main__':
    default_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    generate_educational_dataset(3000, 42, os.path.join(default_dir, 'learning_difficulty_dataset.csv'))

