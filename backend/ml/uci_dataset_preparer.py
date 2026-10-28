"""
UCI Student Performance Dataset Preparer for AI Learning Difficulty Predictor.

Source: UCI Machine Learning Repository
URL: https://archive.ics.uci.edu/dataset/320/student+performance
Citation: P. Cortez and A. Silva. Using Data Mining to Predict Secondary School Student Performance.
          In A. Brito and J. Teixeira Eds., Proceedings of 5th FUBUTEC 2008, pp. 5-12, Porto, Portugal.
License: Creative Commons Attribution 4.0 International (CC BY 4.0)

This module loads the raw official UCI Student Performance records (Mathematics and Portuguese language),
applies domain-aligned, defensible mappings to the required 10-feature schema of the AI Learning Difficulty
Predictor, and saves the prepared dataset without target leakage.
"""

import os
import numpy as np
import pandas as pd
from backend.ml.preprocessor import MLDataPreprocessor, REQUIRED_FEATURES, TARGET_COLUMN

# Ordinal weekly study hours mapping based on category midpoint hours
STUDYTIME_HOURS_MAP = {
    1: 1.5,   # '<2 hours' -> midpoint 1.5 hrs/week
    2: 3.5,   # '2 to 5 hours' -> midpoint 3.5 hrs/week
    3: 7.5,   # '5 to 10 hours' -> midpoint 7.5 hrs/week
    4: 12.0   # '>10 hours' -> conservative estimate 12.0 hrs/week
}

def map_g3_to_difficulty_category(g3_score):
    """
    Maps final grade G3 (0-20 scale) to application difficulty risk categories.
    Portuguese Secondary Education official passing threshold is 10/20.
    
    - G3 < 10 (0-45%): Failing / Reprovado -> 'High' Difficulty / Risk
    - 10 <= G3 <= 13 (50-65%): Satisfactory / Borderline passing -> 'Moderate' Difficulty / Risk
    - G3 >= 14 (70-100%): Good to Excellent / Bom a Muito Bom -> 'Low' Difficulty / Risk
    """
    if g3_score < 10:
        return 'High'
    elif g3_score <= 13:
        return 'Moderate'
    else:
        return 'Low'

def prepare_uci_dataset(uci_raw_dir=None, output_csv_path=None):
    """
    Transforms raw UCI math and portuguese CSV files into a validated
    learning difficulty dataset conforming to REQUIRED_FEATURES and TARGET_COLUMN.
    """
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    if uci_raw_dir is None:
        uci_raw_dir = os.path.join(backend_dir, 'data', 'uci_raw')
    if output_csv_path is None:
        output_csv_path = os.path.join(backend_dir, 'data', 'uci_student_difficulty_dataset.csv')

    mat_file = os.path.join(uci_raw_dir, 'student-mat.csv')
    por_file = os.path.join(uci_raw_dir, 'student-por.csv')

    if not os.path.exists(mat_file) or not os.path.exists(por_file):
        raise FileNotFoundError(f"Raw UCI files not found at {uci_raw_dir}. Required: student-mat.csv and student-por.csv")

    df_mat = pd.read_csv(mat_file, sep=';')
    df_mat['course_subject'] = 'Math'

    df_por = pd.read_csv(por_file, sep=';')
    df_por['course_subject'] = 'Portuguese'

    df_combined = pd.concat([df_mat, df_por], ignore_index=True)

    # Apply mappings
    prepared = pd.DataFrame()
    # 1. quiz_score: Period 1 grade (0-20 mapped to 0-100%)
    prepared['quiz_score'] = (df_combined['G1'] * 5.0).round(1)

    # 2. assignment_score: Formative coursework accumulation between Period 1 and Period 2
    prepared['assignment_score'] = ((df_combined['G1'] * 0.35 + df_combined['G2'] * 0.65) * 5.0).round(1)

    # 3. exam_score: Period 2 summative midterm examination (0-20 mapped to 0-100%)
    # Note: G3 is NEVER used here to prevent target leakage.
    prepared['exam_score'] = (df_combined['G2'] * 5.0).round(1)

    # 4. study_time_weekly: Mapped from studytime ordinal categories
    prepared['study_time_weekly'] = df_combined['studytime'].map(STUDYTIME_HOURS_MAP).astype(float)

    # 5. attendance_rate: Course attendance estimated from absence counts (approx 60-90 total class sessions)
    prepared['attendance_rate'] = (100.0 - df_combined['absences'] * 1.5).clip(lower=0.0, upper=100.0).round(1)

    # 6. attempt_count: 1 + previous course failures
    prepared['attempt_count'] = (1 + df_combined['failures']).astype(int)

    # 7. repeated_errors_count: Derived from failures and extra educational remedial support
    prepared['repeated_errors_count'] = (df_combined['failures'] * 2 + (df_combined['schoolsup'] == 'yes').astype(int)).astype(int)

    # 8. previous_topic_score: Mastery in initial prerequisite concepts (Period 1 G1)
    prepared['previous_topic_score'] = (df_combined['G1'] * 5.0).round(1)

    # 9. learning_pace_gap: Progress differential from foundational G1 to midterm G2
    prepared['learning_pace_gap'] = ((df_combined['G2'] - df_combined['G1']) * 5.0).round(1)

    # 10. topic_difficulty_level: Math curriculum categorized as 'advanced', Portuguese as 'intermediate'
    prepared['topic_difficulty_level'] = df_combined['course_subject'].map({
        'Math': 'advanced',
        'Portuguese': 'intermediate'
    })

    # Target: difficulty_category derived strictly from held-out G3
    prepared[TARGET_COLUMN] = df_combined['G3'].apply(map_g3_to_difficulty_category)

    # Validate schema
    preprocessor = MLDataPreprocessor()
    is_valid, errors, summary = preprocessor.validate_schema(prepared, require_target=True)
    if not is_valid:
        raise ValueError(f"Prepared UCI dataset failed schema validation: {errors}")

    # Ensure output directory exists and write CSV
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    prepared.to_csv(output_csv_path, index=False)

    return prepared, summary

if __name__ == '__main__':
    df_prepared, summary_stats = prepare_uci_dataset()
    print("Prepared UCI dataset successfully saved.")
    print("Total records:", len(df_prepared))
    print("Class distribution:", summary_stats.get('class_distribution'))

