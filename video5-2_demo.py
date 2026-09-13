import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score,
    roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------------------------------------
# LOAD AND PREPARE DATA
# --------------------------------------------------------

df = pd.read_csv('customer_churn.csv')
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df['TotalCharges'] = df['TotalCharges'].fillna(df['TotalCharges'].median())
df['MonthlyCharges'] = df['MonthlyCharges'].fillna(df['MonthlyCharges'].median())
df = df.drop(['customerID'], axis=1)

le = LabelEncoder()
for col in df.select_dtypes(include=['object']).columns:
    if col != 'Churn':
        df[col] = le.fit_transform(df[col])
df['Churn'] = df['Churn'].map({'No': 0, 'Yes': 1})

X = df.drop('Churn', axis=1)
y = df['Churn']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
numerical_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
X_train[numerical_cols] = scaler.fit_transform(X_train[numerical_cols])
X_test[numerical_cols] = scaler.transform(X_test[numerical_cols])

# --------------------------------------------------------
# TRAIN MODEL
# --------------------------------------------------------

model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

# --------------------------------------------------------
# ALL METRICS
# --------------------------------------------------------

print("=" * 50)
print("COMPLETE MODEL EVALUATION")
print("=" * 50)

print()
print("BASIC METRICS:")
print("   Accuracy: ", accuracy_score(y_test, y_pred))
print("   Precision:", precision_score(y_test, y_pred))
print("   Recall:   ", recall_score(y_test, y_pred))
print("   F1 Score: ", f1_score(y_test, y_pred))

print()
print("ADVANCED METRICS:")
print("   ROC-AUC:  ", roc_auc_score(y_test, y_pred_proba))

print()
print("DETAILED REPORT:")
print(classification_report(y_test, y_pred, target_names=['Stays', 'Churns']))

# --------------------------------------------------------
# CONFUSION MATRIX
# --------------------------------------------------------

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Predicted Stay', 'Predicted Churn'],
            yticklabels=['Actual Stay', 'Actual Churn'])
plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

print()
print("Confusion Matrix Breakdown:")
print("  True Negatives (correctly predicted stay):", cm[0,0])
print("  False Positives (false alarm):", cm[0,1])
print("  False Negatives (missed churn):", cm[1,0])
print("  True Positives (caught churn):", cm[1,1])

# --------------------------------------------------------
# ROC CURVE
# --------------------------------------------------------

fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
roc_auc = roc_auc_score(y_test, y_pred_proba)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2,
         label='ROC curve (AUC = ' + str(round(roc_auc, 3)) + ')')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve', fontsize=14, fontweight='bold')
plt.legend(loc='lower right')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# --------------------------------------------------------
# OPTIMAL THRESHOLD
# --------------------------------------------------------

thresholds_to_try = np.arange(0.1, 0.9, 0.05)
results = []

for threshold in thresholds_to_try:
    y_pred_thresh = (y_pred_proba >= threshold).astype(int)
    
    results.append({
        'threshold': threshold,
        'precision': precision_score(y_test, y_pred_thresh),
        'recall': recall_score(y_test, y_pred_thresh),
        'f1': f1_score(y_test, y_pred_thresh)
    })

df_thresholds = pd.DataFrame(results)

plt.figure(figsize=(10, 6))
plt.plot(df_thresholds['threshold'], df_thresholds['precision'],
         label='Precision', marker='o')
plt.plot(df_thresholds['threshold'], df_thresholds['recall'],
         label='Recall', marker='s')
plt.plot(df_thresholds['threshold'], df_thresholds['f1'],
         label='F1 Score', marker='^', linewidth=2)

best_idx = df_thresholds['f1'].idxmax()
best_threshold = df_thresholds.loc[best_idx, 'threshold']
plt.axvline(x=best_threshold, color='red', linestyle='--',
           label='Best F1 Threshold: ' + str(round(best_threshold, 2)))

plt.xlabel('Threshold')
plt.ylabel('Score')
plt.title('Finding the Optimal Threshold', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print()
print("Optimal threshold (by F1):", round(best_threshold, 2))
print("  Precision:", round(df_thresholds.loc[best_idx, 'precision'], 3))
print("  Recall:", round(df_thresholds.loc[best_idx, 'recall'], 3))
print("  F1:", round(df_thresholds.loc[best_idx, 'f1'], 3))

# --------------------------------------------------------
# MODEL COMPARISON
# --------------------------------------------------------

models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, class_weight='balanced'),
    'Random Forest': RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42),
    'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=5),
}

comparison_results = []

for name, mdl in models.items():
    mdl.fit(X_train, y_train)
    y_pred_m = mdl.predict(X_test)
    y_pred_proba_m = mdl.predict_proba(X_test)[:, 1]
    
    comparison_results.append({
        'Model': name,
        'Accuracy': accuracy_score(y_test, y_pred_m),
        'Precision': precision_score(y_test, y_pred_m),
        'Recall': recall_score(y_test, y_pred_m),
        'F1 Score': f1_score(y_test, y_pred_m),
        'ROC-AUC': roc_auc_score(y_test, y_pred_proba_m),
    })

df_comparison = pd.DataFrame(comparison_results)
df_comparison = df_comparison.sort_values('F1 Score', ascending=False)

print()
print("MODEL COMPARISON:")
print(df_comparison.to_string(index=False))

# Visualize comparison
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(df_comparison))
width = 0.2

ax.bar(x - width*1.5, df_comparison['Accuracy'], width, label='Accuracy')
ax.bar(x - width*0.5, df_comparison['Precision'], width, label='Precision')
ax.bar(x + width*0.5, df_comparison['Recall'], width, label='Recall')
ax.bar(x + width*1.5, df_comparison['F1 Score'], width, label='F1')

ax.set_xticks(x)
ax.set_xticklabels(df_comparison['Model'], rotation=45, ha='right')
ax.set_ylabel('Score')
ax.set_title('Model Comparison', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.show()

winner = df_comparison.iloc[0]
print()
print("WINNER:", winner['Model'])
print("  F1 Score:", round(winner['F1 Score'], 3))
print("  Recall:", round(winner['Recall'], 3))
