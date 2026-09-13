import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report
)
import matplotlib.pyplot as plt

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
print("Approval rate:", round(y_train.mean() * 100, 1), "%")

# --------------------------------------------------------
# TRAIN DECISION TREE
# --------------------------------------------------------

dt_model = DecisionTreeClassifier(
    max_depth=4,
    min_samples_split=50,
    min_samples_leaf=25,
    random_state=42
)

dt_model.fit(X_train, y_train)
y_pred_dt = dt_model.predict(X_test)

print()
print("DECISION TREE RESULTS:")
print("Accuracy:", round(accuracy_score(y_test, y_pred_dt), 3))
print()
print(classification_report(y_test, y_pred_dt, target_names=['Rejected', 'Approved']))

# --------------------------------------------------------
# VISUALIZE THE TREE
# --------------------------------------------------------

plt.figure(figsize=(20, 10))
plot_tree(
    dt_model,
    feature_names=feature_columns,
    class_names=['Rejected', 'Approved'],
    filled=True,
    rounded=True,
    fontsize=10,
    proportion=True
)
plt.title('Loan Approval Decision Tree', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('decision_tree.png', dpi=150, bbox_inches='tight')
plt.show()

print("Tree visualization saved as decision_tree.png")

# --------------------------------------------------------
# EXPLAIN A SPECIFIC PREDICTION
# --------------------------------------------------------

def explain_decision_path(model, sample, feature_names, class_names):
    feature = model.tree_.feature
    threshold = model.tree_.threshold
    children_left = model.tree_.children_left
    children_right = model.tree_.children_right
    
    prediction = model.predict([sample])[0]
    
    print()
    print("PREDICTION:", class_names[prediction])
    print()
    print("DECISION PATH:")
    
    node_index = 0
    step = 1
    
    while children_left[node_index] != children_right[node_index]:
        feature_idx = feature[node_index]
        feature_name = feature_names[feature_idx]
        feature_value = sample[feature_idx]
        threshold_value = threshold[node_index]
        
        if feature_value <= threshold_value:
            print("  Step", step, ":", feature_name, "=", round(feature_value, 2),
                  "is less than or equal to", round(threshold_value, 2), "--> Go LEFT")
            node_index = children_left[node_index]
        else:
            print("  Step", step, ":", feature_name, "=", round(feature_value, 2),
                  "is greater than", round(threshold_value, 2), "--> Go RIGHT")
            node_index = children_right[node_index]
        
        step += 1
    
    leaf_values = model.tree_.value[node_index][0]
    total = leaf_values.sum()
    
    print()
    print("Reached leaf node with", int(total), "training samples:")
    for i, count in enumerate(leaf_values):
        pct = count / total * 100
        print("  ", class_names[i], ":", int(count), "(" + str(round(pct, 1)) + "%)")

sample = X_test.iloc[0].values
explain_decision_path(dt_model, sample, feature_columns, ['Rejected', 'Approved'])

# --------------------------------------------------------
# TRAIN RANDOM FOREST
# --------------------------------------------------------

rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=20,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)
y_pred_rf = rf_model.predict(X_test)

print()
print("RANDOM FOREST RESULTS:")
print("Accuracy:", round(accuracy_score(y_test, y_pred_rf), 3))
print("Precision:", round(precision_score(y_test, y_pred_rf), 3))
print("Recall:", round(recall_score(y_test, y_pred_rf), 3))
print("F1 Score:", round(f1_score(y_test, y_pred_rf), 3))

# --------------------------------------------------------
# FEATURE IMPORTANCE
# --------------------------------------------------------

feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print()
print("FEATURE IMPORTANCE:")
print(feature_importance)

plt.figure(figsize=(10, 6))
plt.barh(feature_importance['feature'][:8],
         feature_importance['importance'][:8],
         color='#4ECDC4')
plt.xlabel('Importance Score')
plt.title('What Drives Loan Approval Decisions?', fontsize=14, fontweight='bold')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()

print()
print("INTERPRETATION:")
for idx, row in feature_importance.head(3).iterrows():
    pct = row['importance'] * 100
    print("  ", row['feature'], ":", round(pct, 1), "% of decision weight")

# --------------------------------------------------------
# MODEL COMPARISON
# --------------------------------------------------------

print()
comparison = pd.DataFrame({
    'Model': ['Decision Tree', 'Random Forest'],
    'Accuracy': [
        round(accuracy_score(y_test, y_pred_dt), 3),
        round(accuracy_score(y_test, y_pred_rf), 3)
    ],
    'F1 Score': [
        round(f1_score(y_test, y_pred_dt), 3),
        round(f1_score(y_test, y_pred_rf), 3)
    ],
    'Explainability': ['Excellent', 'Good (via feature importance)'],
    'Overfitting Risk': ['High', 'Low'],
    'Production Ready': ['Medium', 'High']
})

print("MODEL COMPARISON:")
print(comparison.to_string(index=False))

print()
print("RULE OF THUMB:")
print("  Decision Tree: When you NEED to explain every single decision")
print("  Random Forest: When accuracy matters more than per-decision explainability")
print("  Use feature importance to explain Random Forest at a high level")