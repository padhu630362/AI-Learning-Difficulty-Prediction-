import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

REQUIRED_FEATURES = [
    'quiz_score',
    'assignment_score',
    'exam_score',
    'study_time_weekly',
    'attendance_rate',
    'attempt_count',
    'repeated_errors_count',
    'previous_topic_score',
    'learning_pace_gap',
    'topic_difficulty_level'
]

NUMERIC_FEATURES = [
    'quiz_score',
    'assignment_score',
    'exam_score',
    'study_time_weekly',
    'attendance_rate',
    'attempt_count',
    'repeated_errors_count',
    'previous_topic_score',
    'learning_pace_gap'
]

CATEGORICAL_FEATURES = [
    'topic_difficulty_level'
]

TARGET_COLUMN = 'difficulty_category'
VALID_TARGET_CLASSES = ['Low', 'Moderate', 'High']

class MLDataPreprocessor:
    def __init__(self):
        self.transformer = None
        self.feature_names = None
        self.target_classes = VALID_TARGET_CLASSES

    def validate_schema(self, df, require_target=True):
        """
        Validates column names, types, and content of input dataframe.
        Returns (is_valid, error_list, summary_stats).
        """
        errors = []
        df_cols = list(df.columns)
        
        # Check required features
        missing_features = [col for col in REQUIRED_FEATURES if col not in df_cols]
        if missing_features:
            errors.append(f"Missing required feature columns: {missing_features}")
            
        if require_target and TARGET_COLUMN not in df_cols:
            errors.append(f"Missing required target column '{TARGET_COLUMN}'")

        if errors:
            return False, errors, {}

        # Check target values if present
        if TARGET_COLUMN in df_cols:
            unique_targets = set(df[TARGET_COLUMN].dropna().unique())
            invalid_targets = unique_targets - set(VALID_TARGET_CLASSES)
            if invalid_targets:
                errors.append(f"Target contains invalid classes: {list(invalid_targets)}. Expected {VALID_TARGET_CLASSES}")

        # Basic ranges and types
        if 'quiz_score' in df:
            out_of_bounds = df[(df['quiz_score'] < 0) | (df['quiz_score'] > 100)]
            if len(out_of_bounds) > 0:
                errors.append(f"quiz_score has {len(out_of_bounds)} values outside valid range [0, 100]")

        summary = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'duplicate_rows': int(df.duplicated().sum()),
            'missing_values': int(df.isna().sum().sum()),
            'class_distribution': df[TARGET_COLUMN].value_counts().to_dict() if TARGET_COLUMN in df else {}
        }

        return len(errors) == 0, errors, summary

    def build_transformer(self):
        num_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        cat_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('encoder', OneHotEncoder(categories=[['beginner', 'intermediate', 'advanced']], handle_unknown='ignore', sparse_output=False))
        ])

        transformer = ColumnTransformer(
            transformers=[
                ('num', num_pipeline, NUMERIC_FEATURES),
                ('cat', cat_pipeline, CATEGORICAL_FEATURES)
            ]
        )
        return transformer

    def fit_transform(self, X_df):
        self.transformer = self.build_transformer()
        X_trans = self.transformer.fit_transform(X_df[REQUIRED_FEATURES])
        
        # Extract feature names
        cat_encoder = self.transformer.named_transformers_['cat'].named_steps['encoder']
        cat_names = cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
        self.feature_names = NUMERIC_FEATURES + cat_names
        
        return X_trans

    def transform(self, X_df):
        if self.transformer is None:
            raise ValueError("Preprocessor has not been fitted or loaded yet.")
        return self.transformer.transform(X_df[REQUIRED_FEATURES])

    def save(self, filepath):
        joblib.dump({
            'transformer': self.transformer,
            'feature_names': self.feature_names,
            'target_classes': self.target_classes
        }, filepath)

    @classmethod
    def load(cls, filepath):
        instance = cls()
        data = joblib.load(filepath)
        instance.transformer = data['transformer']
        instance.feature_names = data['feature_names']
        instance.target_classes = data['target_classes']
        return instance

