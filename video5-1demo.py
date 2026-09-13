import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score, recall_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

# --------------------------------------------------------
# STEP 1: LOAD DATA
# --------------------------------------------------------

df = pd.read_csv('customer_churn.csv')

print("Customers:", len(df))
print("Churn rate:")
print(df['Churn'].value_counts(normalize=True))

# --------------------------------------------------------
# STEP 2: EXPLORE AND CLEAN
# --------------------------------------------------------

print()
print("Missing values:")
print(df.isnull().sum())

df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df['TotalCharges'] = df['TotalCharges'].fillna(df['TotalCharges'].median())
df['MonthlyCharges'] = df['MonthlyCharges'].fillna(df['MonthlyCharges'].median())
df = df.drop(['customerID'], axis=1)

# --------------------------------------------------------
# STEP 3: PREPARE FEATURES
# --------------------------------------------------------

le = LabelEncoder()
categorical_cols = df.select_dtypes(include=['object']).columns

for col in categorical_cols:
    if col != 'Churn':
        df[col] = le.fit_transform(df[col])

df['Churn'] = df['Churn'].map({'No': 0, 'Yes': 1})

X = df.drop('Churn', axis=1)
y = df['Churn']


# for x 80% of x for training, 20% of x for testing and thesame goes for y
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
numerical_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
X_train[numerical_cols] = scaler.fit_transform(X_train[numerical_cols])
X_test[numerical_cols] = scaler.transform(X_test[numerical_cols])

print()
print("Training set:", len(X_train))
print("Testing set:", len(X_test))

# --------------------------------------------------------
# STEP 4: TRAIN
# --------------------------------------------------------

from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier

# Balance the training data
smote = SMOTE(random_state=42)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

model = GradientBoostingClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=10,
    random_state=42
)

model.fit(X_train_balanced, y_train_balanced)
y_pred = model.predict(X_test)

print("Gradient Boosting with SMOTE:")
print("F1:", round(f1_score(y_test, y_pred), 3))
print("Recall:", round(recall_score(y_test, y_pred), 3))

# --------------------------------------------------------
# STEP 5: EVALUATE
# --------------------------------------------------------

y_pred = model.predict(X_test) # predicts with 20% of x and y

print()
print("MODEL PERFORMANCE:")
print(classification_report(y_test, y_pred, target_names=['Stays', 'Churns']))

# --------------------------------------------------------
# BUSINESS IMPACT
# --------------------------------------------------------

cm = confusion_matrix(y_test, y_pred)

print("Confusion Matrix:")
print("  Predicted Stay, Actual Stay:", cm[0,0])
print("  Predicted Churn, Actual Stay:", cm[0,1], "(False alarm)")
print("  Predicted Stay, Actual Churn:", cm[1,0], "(Missed)")
print("  Predicted Churn, Actual Churn:", cm[1,1], "(Caught)")

false_alarms = cm[0,1]
caught_churn = cm[1,1]
missed_churn = cm[1,0]

print()
print("BUSINESS IMPACT:")
print("  Caught", caught_churn, "churning customers")
print("  Missed", missed_churn, "churning customers")
print("  False alarms:", false_alarms)

cost_of_retention = false_alarms * 50
value_of_retained = caught_churn * 500 * 0.5

print()
print("  Cost of retention offers: $" + str(cost_of_retention))
print("  Value of retained customers: $" + str(int(value_of_retained)))
print("  NET IMPACT: $" + str(int(value_of_retained - cost_of_retention)))