import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report
)
from collections import Counter
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline
from scipy.stats import randint
import joblib

# --------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------

df = pd.read_csv('fraud_transaction.csv')

feature_columns = ['transaction_amount', 'account_age_days',
                   'transaction_hour', 'previous_transactions',
                   'device_type', 'location_match',
                   'amount_vs_average', 'is_new_device']

X = df[feature_columns]
y = df['is_fraud']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("CLASS DISTRIBUTION (Training):")
class_counts = Counter(y_train)
for label, count in class_counts.items():
    pct = count / len(y_train) * 100
    print("  Class", label, ":", count, "(" + str(round(pct, 1)) + "%)")

imbalance_ratio = class_counts[0] / class_counts[1]
print()
print("Imbalance Ratio:", round(imbalance_ratio, 1), ": 1")

# --------------------------------------------------------
# BASELINE: NO IMBALANCE HANDLING
# --------------------------------------------------------

# the naive model

rf_baseline = RandomForestClassifier(n_estimators=100, random_state=42)
rf_baseline.fit(X_train, y_train)
y_pred_baseline = rf_baseline.predict(X_test)

joblib.dump(rf_baseline, 'baseline_fraud_model.pkl')

print()
print("BASELINE (No Imbalance Handling):")
print("Accuracy:", round(accuracy_score(y_test, y_pred_baseline), 3))
print("Precision:", round(precision_score(y_test, y_pred_baseline), 3))
print("Recall:", round(recall_score(y_test, y_pred_baseline), 3))
print("F1 Score:", round(f1_score(y_test, y_pred_baseline), 3))

# --------------------------------------------------------
# METHOD 1: CLASS WEIGHTS
# --------------------------------------------------------

rf_weighted = RandomForestClassifier(
    n_estimators=100,
    class_weight='balanced',
    random_state=42
)
rf_weighted.fit(X_train, y_train)
y_pred_weighted = rf_weighted.predict(X_test)
joblib.dump(rf_weighted, 'weighted_fraud_model.pkl')

print()
print("METHOD 1: CLASS WEIGHTS")
print("Recall:", round(recall_score(y_test, y_pred_weighted), 3))
print("F1 Score:", round(f1_score(y_test, y_pred_weighted), 3))

# --------------------------------------------------------
# METHOD 2: SMOTE
# --------------------------------------------------------

print()
print("Before SMOTE:")
print("  Class distribution:", dict(Counter(y_train)))

smote = SMOTE(random_state=42)
X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

print("After SMOTE:")
print("  Class distribution:", dict(Counter(y_train_smote)))

rf_smote = RandomForestClassifier(n_estimators=100, random_state=42)
rf_smote.fit(X_train_smote, y_train_smote)
y_pred_smote = rf_smote.predict(X_test)

print()
print("METHOD 2: SMOTE")
print("Recall:", round(recall_score(y_test, y_pred_smote), 3))
print("F1 Score:", round(f1_score(y_test, y_pred_smote), 3))

# --------------------------------------------------------
# METHOD 3: UNDERSAMPLING
# --------------------------------------------------------

undersampler = RandomUnderSampler(random_state=42)
X_train_under, y_train_under = undersampler.fit_resample(X_train, y_train)

print()
print("After Undersampling:")
print("  Class distribution:", dict(Counter(y_train_under)))
print("  Total samples:", len(y_train_under))

rf_under = RandomForestClassifier(n_estimators=100, random_state=42)
rf_under.fit(X_train_under, y_train_under)
y_pred_under = rf_under.predict(X_test)

print()
print("METHOD 3: UNDERSAMPLING")
print("Recall:", round(recall_score(y_test, y_pred_under), 3))
print("F1 Score:", round(f1_score(y_test, y_pred_under), 3))

# --------------------------------------------------------
# METHOD 4: SMOTE + PIPELINE
# --------------------------------------------------------

pipeline = ImbPipeline([
    ('smote', SMOTE(random_state=42)),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

pipeline.fit(X_train, y_train)
y_pred_pipeline = pipeline.predict(X_test)

print()
print("METHOD 4: SMOTE + RANDOM FOREST (Pipeline)")
print("Recall:", round(recall_score(y_test, y_pred_pipeline), 3))
print("F1 Score:", round(f1_score(y_test, y_pred_pipeline), 3))

# --------------------------------------------------------
# COMPARE ALL METHODS
# --------------------------------------------------------

methods_comparison = pd.DataFrame({
    'Method': ['No handling', 'Class Weight', 'SMOTE', 'Undersampling', 'SMOTE + Pipeline'],
    'Precision': [
        round(precision_score(y_test, y_pred_baseline), 3),
        round(precision_score(y_test, y_pred_weighted), 3),
        round(precision_score(y_test, y_pred_smote), 3),
        round(precision_score(y_test, y_pred_under), 3),
        round(precision_score(y_test, y_pred_pipeline), 3)
    ],
    'Recall': [
        round(recall_score(y_test, y_pred_baseline), 3),
        round(recall_score(y_test, y_pred_weighted), 3),
        round(recall_score(y_test, y_pred_smote), 3),
        round(recall_score(y_test, y_pred_under), 3),
        round(recall_score(y_test, y_pred_pipeline), 3)
    ],
    'F1 Score': [
        round(f1_score(y_test, y_pred_baseline), 3),
        round(f1_score(y_test, y_pred_weighted), 3),
        round(f1_score(y_test, y_pred_smote), 3),
        round(f1_score(y_test, y_pred_under), 3),
        round(f1_score(y_test, y_pred_pipeline), 3)
    ]
})

print()
print("IMBALANCE HANDLING COMPARISON:")
print(methods_comparison.to_string(index=False))

# Hyper parameter tuning

# --------------------------------------------------------
# GRID SEARCH
# --------------------------------------------------------

param_grid = {
    'n_estimators': [50, 100],
    'max_depth': [5, 10],
    'min_samples_split': [5, 10],
    'class_weight': ['balanced', None]
}

total_combinations = 1
for v in param_grid.values():
    total_combinations *= len(v)
print()
print("Grid Search: Testing", total_combinations, "combinations with 3-fold CV")
print("Total fits:", total_combinations * 3)

grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid,
    cv=3,
    scoring='f1',
    n_jobs=1,
    verbose=1
)

grid_search.fit(X_train, y_train)

print()
print("GRID SEARCH COMPLETE")
print("Best F1:", round(grid_search.best_score_, 3))
print("Best Parameters:", grid_search.best_params_)

best_model = grid_search.best_estimator_

# --------------------------------------------------------
# RANDOMIZED SEARCH
# --------------------------------------------------------

param_dist = {
    'n_estimators': randint(50, 200),
    'max_depth': randint(3, 15),
    'min_samples_split': randint(2, 15),
    'min_samples_leaf': randint(1, 8),
    'class_weight': ['balanced', 'balanced_subsample', None]
}

print()
print("Randomized Search: Testing 30 random combinations with 3-fold CV")
print("Total fits:", 30 * 3)

random_search = RandomizedSearchCV(
    RandomForestClassifier(random_state=42),
    param_dist,
    n_iter=30,
    cv=3,
    scoring='f1',
    n_jobs=1,
    random_state=42,
    verbose=1
)

random_search.fit(X_train, y_train)

print()
print("RANDOMIZED SEARCH COMPLETE")
print("Best F1:", round(random_search.best_score_, 3))
print("Best Parameters:", random_search.best_params_)

# --------------------------------------------------------
# BEFORE VS AFTER TUNING
# --------------------------------------------------------

rf_default = RandomForestClassifier(random_state=42)
rf_default.fit(X_train, y_train)
y_pred_default = rf_default.predict(X_test)

y_pred_tuned = best_model.predict(X_test)

tuning_comparison = pd.DataFrame({
    'Model': ['Default Parameters', 'After Tuning'],
    'F1 Score': [
        round(f1_score(y_test, y_pred_default), 3),
        round(f1_score(y_test, y_pred_tuned), 3)
    ],
    'Precision': [
        round(precision_score(y_test, y_pred_default), 3),
        round(precision_score(y_test, y_pred_tuned), 3)
    ],
    'Recall': [
        round(recall_score(y_test, y_pred_default), 3),
        round(recall_score(y_test, y_pred_tuned), 3)
    ]
})

f1_improvement = tuning_comparison['F1 Score'].iloc[1] - tuning_comparison['F1 Score'].iloc[0]

print()
print("IMPACT OF HYPERPARAMETER TUNING:")
print(tuning_comparison.to_string(index=False))
print()
print("F1 Improvement:", round(f1_improvement, 3))

# --------------------------------------------------------
# SAVE MODEL
# --------------------------------------------------------

joblib.dump(best_model, 'best_fraud_model.pkl')
print()
print("Best model saved as best_fraud_model.pkl")


#joblib.load('best_fraud_model.pkl')