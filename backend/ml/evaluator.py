import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    log_loss
)

def evaluate_model_performance(model, X_test, y_test, class_labels=None, feature_names=None):
    """
    Evaluates model on held-out test data and returns detailed metrics including
    class-wise recall (specifically for High Difficulty risk), probability calibration loss,
    and feature sensitivities.
    """
    if class_labels is None:
        class_labels = ['Low', 'Moderate', 'High']
        
    y_pred = model.predict(X_test)
    
    # Calculate macro and weighted metrics
    acc = accuracy_score(y_test, y_pred)
    prec_macro = precision_score(y_test, y_pred, labels=class_labels, average='macro', zero_division=0)
    rec_macro = recall_score(y_test, y_pred, labels=class_labels, average='macro', zero_division=0)
    f1_mac = f1_score(y_test, y_pred, labels=class_labels, average='macro', zero_division=0)
    f1_wt = f1_score(y_test, y_pred, labels=class_labels, average='weighted', zero_division=0)

    cm = confusion_matrix(y_test, y_pred, labels=class_labels).tolist()
    
    report_dict = classification_report(
        y_test, 
        y_pred, 
        labels=class_labels, 
        target_names=class_labels, 
        output_dict=True, 
        zero_division=0
    )

    # Class-specific focus for High Difficulty risk
    high_class_metrics = report_dict.get('High', {})
    high_difficulty_recall = float(round(high_class_metrics.get('recall', 0.0), 4))
    high_difficulty_precision = float(round(high_class_metrics.get('precision', 0.0), 4))
    high_difficulty_f1 = float(round(high_class_metrics.get('f1-score', 0.0), 4))

    # Majority class baseline
    try:
        import pandas as pd
        y_ser = pd.Series(y_test)
        maj_baseline = float(round(y_ser.value_counts().max() / len(y_ser), 4))
    except Exception:
        maj_baseline = None

    # Probability calibration metric (Multiclass Cross-Entropy / Log-Loss)
    calibrated_loss = None
    if hasattr(model, 'predict_proba'):
        try:
            y_proba = model.predict_proba(X_test)
            proba_labels = list(getattr(model, 'classes_', class_labels))
            calibrated_loss = float(round(log_loss(y_test, y_proba, labels=proba_labels), 4))
        except Exception:
            calibrated_loss = None

    # Feature importance extraction if model supports it
    feat_imp = {}
    if hasattr(model, 'feature_importances_') and feature_names:
        importances = model.feature_importances_
        sorted_idx = np.argsort(importances)[::-1]
        for idx in sorted_idx:
            feat_imp[feature_names[idx]] = float(round(importances[idx], 4))
    elif hasattr(model, 'coef_') and feature_names:
        # For logistic regression, average absolute coefficients across classes
        avg_coef = np.mean(np.abs(model.coef_), axis=0)
        sorted_idx = np.argsort(avg_coef)[::-1]
        for idx in sorted_idx:
            feat_imp[feature_names[idx]] = float(round(avg_coef[idx], 4))

    return {
        'accuracy': float(round(acc, 4)),
        'precision_macro': float(round(prec_macro, 4)),
        'recall_macro': float(round(rec_macro, 4)),
        'f1_macro': float(round(f1_mac, 4)),
        'f1_weighted': float(round(f1_wt, 4)),
        'majority_class_baseline': maj_baseline,
        'high_difficulty_recall': high_difficulty_recall,
        'high_difficulty_precision': high_difficulty_precision,
        'high_difficulty_f1': high_difficulty_f1,
        'calibrated_log_loss': calibrated_loss,
        'confusion_matrix': {
            'labels': class_labels,
            'matrix': cm
        },
        'classification_report': report_dict,
        'feature_importances': feat_imp
    }
