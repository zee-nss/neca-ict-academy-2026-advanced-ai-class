import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.model_selection import StratifiedKFold, cross_validate, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score

# --------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------

df = pd.read_csv('fraud_transactions.csv')

feature_columns = ['transaction_amount', 'account_age_days',
                   'transaction_hour', 'previous_transactions',
                   'device_type', 'location_match',
                   'amount_vs_average', 'is_new_device']

X = df[feature_columns]
y = df['is_fraud']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))
print("Fraud rate in training:", round(y_train.mean() * 100, 2), "%")

# --------------------------------------------------------
# SINGLE SPLIT EVALUATION
# --------------------------------------------------------

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

single_f1 = f1_score(y_test, y_pred)

print()
print("SINGLE SPLIT EVALUATION")
print("=" * 40)
print("F1 Score:", round(single_f1, 3))
print()
print("This is ONE number from ONE split.")

# --------------------------------------------------------
# 5-FOLD CROSS-VALIDATION
# --------------------------------------------------------

print()
print("5-FOLD CROSS-VALIDATION")
print("=" * 40)

cv_scores = cross_val_score(
    model, X_train, y_train, 
    cv=5, 
    scoring='f1'
)

print("F1 Scores for each fold:")
for i, score in enumerate(cv_scores):
    print("  Fold", i+1, ":", round(score, 3))

print()
print("Average F1:", round(cv_scores.mean(), 3))
print("Standard Deviation:", round(cv_scores.std(), 3))
print("95% Confidence Interval:", 
      round(cv_scores.mean() - 2 * cv_scores.std(), 3),
      "to",
      round(cv_scores.mean() + 2 * cv_scores.std(), 3))

# --------------------------------------------------------
# MULTIPLE METRICS AT ONCE
# --------------------------------------------------------

print()
print("ALL METRICS WITH CROSS-VALIDATION")
print("=" * 40)

cv_results = cross_validate(
    model, X_train, y_train, 
    cv=5,
    scoring=['accuracy', 'precision', 'recall', 'f1']
)

for metric in cv_results:
    if metric.startswith('test_'):
        scores = cv_results[metric]
        metric_name = metric.replace('test_', '')
        print()
        print(metric_name.upper(), ":")
        print("  Scores:", [round(s, 3) for s in scores])
        print("  Average:", round(scores.mean(), 3))
        print("  Std Dev:", round(scores.std(), 3))

# --------------------------------------------------------
# STRATIFIED K-FOLD
# --------------------------------------------------------

print()
print("STRATIFIED K-FOLD")
print("=" * 40)

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for i, (train_idx, test_idx) in enumerate(skf.split(X_train, y_train)):
    train_fraud_rate = y_train.iloc[train_idx].mean()
    test_fraud_rate = y_train.iloc[test_idx].mean()
    print("Fold", i+1, 
          ": Train fraud rate =", round(train_fraud_rate * 100, 1), "%",
          " Test fraud rate =", round(test_fraud_rate * 100, 1), "%")

stratified_scores = cross_val_score(
    model, X_train, y_train, 
    cv=skf, 
    scoring='f1'
)

print()
print("Stratified CV F1:", round(stratified_scores.mean(), 3))

# --------------------------------------------------------
# GRID SEARCH WITH CROSS-VALIDATION
# --------------------------------------------------------

print()
print("GRID SEARCH WITH CROSS-VALIDATION")
print("=" * 40)

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15],
    'min_samples_split': [2, 5, 10]
}

total_combos = 1
for v in param_grid.values():
    total_combos *= len(v)
print("Testing", total_combos, "combinations with 5-fold CV")
print("Total model fits:", total_combos * 5)

grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42, class_weight='balanced'),
    param_grid,
    cv=5,
    scoring='f1',
    n_jobs=1,
    verbose=1
)

grid_search.fit(X_train, y_train)

print()
print("BEST PARAMETERS:", grid_search.best_params_)
print("BEST CV F1:", round(grid_search.best_score_, 3))

default_model = RandomForestClassifier(random_state=42, class_weight='balanced')
default_scores = cross_val_score(default_model, X_train, y_train, cv=5, scoring='f1')
default_f1 = default_scores.mean()

print()
print("Default Parameters F1:", round(default_f1, 3))
print("Tuned Parameters F1:", round(grid_search.best_score_, 3))
print("Improvement:", round(grid_search.best_score_ - default_f1, 3))