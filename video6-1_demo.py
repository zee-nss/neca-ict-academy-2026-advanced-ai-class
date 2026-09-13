import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score
)
import matplotlib.pyplot as plt
import xgboost as xgb
import lightgbm as lgb

# --------------------------------------------------------
# LOAD AND PREPARE DATA
# --------------------------------------------------------

df = pd.read_csv('loan_applications.csv')

feature_columns = ['credit_score', 'income', 'debt_to_income',
                   'employment_years', 'loan_amount', 'late_payments',
                   'has_cosigner', 'home_owner']

X = df[feature_columns]
y = df['approved']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Training set:", len(X_train))
print("Testing set:", len(X_test))

# --------------------------------------------------------
# BASELINE MODELS
# --------------------------------------------------------

lr_model = LogisticRegression(max_iter=1000, class_weight='balanced')
lr_model.fit(X_train, y_train)
y_pred_lr = lr_model.predict(X_test)
y_pred_proba_lr = lr_model.predict_proba(X_test)[:, 1]

rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
rf_model.fit(X_train, y_train)
y_pred_rf = rf_model.predict(X_test)
y_pred_proba_rf = rf_model.predict_proba(X_test)[:, 1]

print()
print("BASELINE RESULTS:")
print("Logistic Regression F1:", round(f1_score(y_test, y_pred_lr), 3))
print("Random Forest F1:", round(f1_score(y_test, y_pred_rf), 3))

# --------------------------------------------------------
# XGBOOST
# --------------------------------------------------------

neg_count = len(y_train[y_train == 0])
pos_count = len(y_train[y_train == 1])
scale_weight = neg_count / pos_count

print()
print("Class imbalance ratio:", round(scale_weight, 2), ": 1")

xgb_model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    scale_pos_weight=scale_weight,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric='logloss'
)

xgb_model.fit(
    X_train, y_train,
    eval_set=[(X_train, y_train), (X_test, y_test)],
    verbose=False
)

y_pred_xgb = xgb_model.predict(X_test)
y_pred_proba_xgb = xgb_model.predict_proba(X_test)[:, 1]

print()
print("XGBOOST RESULTS:")
print("Accuracy:", round(accuracy_score(y_test, y_pred_xgb), 3))
print("Precision:", round(precision_score(y_test, y_pred_xgb), 3))
print("Recall:", round(recall_score(y_test, y_pred_xgb), 3))
print("F1 Score:", round(f1_score(y_test, y_pred_xgb), 3))
print("ROC-AUC:", round(roc_auc_score(y_test, y_pred_proba_xgb), 3))

# --------------------------------------------------------
# XGBOOST FEATURE IMPORTANCE
# --------------------------------------------------------

feature_importance_xgb = pd.DataFrame({
    'feature': feature_columns,
    'importance': xgb_model.feature_importances_
}).sort_values('importance', ascending=False)

print()
print("XGBOOST FEATURE IMPORTANCE:")
print(feature_importance_xgb)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

importance_types = ['weight', 'gain', 'cover']
for i, imp_type in enumerate(importance_types):
    importance = xgb_model.get_booster().get_score(importance_type=imp_type)
    importance_df = pd.DataFrame({
        'feature': list(importance.keys()),
        'importance': list(importance.values())
    }).sort_values('importance', ascending=True).tail(10)
    
    axes[i].barh(importance_df['feature'], importance_df['importance'])
    axes[i].set_title('Importance by ' + imp_type)
    axes[i].set_xlabel('Score')

plt.tight_layout()
plt.show()

# --------------------------------------------------------
# LIGHTGBM
# --------------------------------------------------------

lgb_model = lgb.LGBMClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    class_weight='balanced',
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    verbose=-1
)

lgb_model.fit(X_train, y_train)

y_pred_lgb = lgb_model.predict(X_test)
y_pred_proba_lgb = lgb_model.predict_proba(X_test)[:, 1]

print()
print("LIGHTGBM RESULTS:")
print("F1 Score:", round(f1_score(y_test, y_pred_lgb), 3))
print("ROC-AUC:", round(roc_auc_score(y_test, y_pred_proba_lgb), 3))

# --------------------------------------------------------
# FINAL COMPARISON
# --------------------------------------------------------

print()
final_comparison = pd.DataFrame({
    'Model': ['Logistic Regression', 'Random Forest', 'XGBoost', 'LightGBM'],
    'F1 Score': [
        round(f1_score(y_test, y_pred_lr), 3),
        round(f1_score(y_test, y_pred_rf), 3),
        round(f1_score(y_test, y_pred_xgb), 3),
        round(f1_score(y_test, y_pred_lgb), 3)
    ],
    'ROC-AUC': [
        round(roc_auc_score(y_test, y_pred_proba_lr), 3),
        round(roc_auc_score(y_test, y_pred_proba_rf), 3),
        round(roc_auc_score(y_test, y_pred_proba_xgb), 3),
        round(roc_auc_score(y_test, y_pred_proba_lgb), 3)
    ],
    'Explainability': ['High', 'Medium', 'Low', 'Low'],
    'Speed': ['Fast', 'Medium', 'Slow', 'Medium-Fast']
})

print("FINAL MODEL COMPARISON:")
print(final_comparison.to_string(index=False))

print()
print("RECOMMENDATION:")
print("  Start: Logistic Regression (baseline)")
print("  Improve: Random Forest (better accuracy, still explainable)")
print("  Production: XGBoost or LightGBM (best accuracy)")
print()
print("  For loan approval: Random Forest (accuracy + feature importance)")
print("  For fraud detection: XGBoost (maximum accuracy matters most)")
print("  For fast iteration: LightGBM (faster training cycles)")