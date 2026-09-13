import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# --------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------

df = pd.read_csv('support_tickets.csv')

print("Dataset shape:", df.shape)
print()
print("Team distribution:")
print(df['assigned_team'].value_counts())
print()
print("Sample tickets:")
print(df[['subject', 'assigned_team']].head())

# --------------------------------------------------------
# PREPARE FEATURES
# --------------------------------------------------------

df['ticket_text'] = df['subject'] + ' ' + df['description']

X = df['ticket_text']
y = df['assigned_team']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print()
print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))
print()
print("Training set distribution:")
print(y_train.value_counts())

# --------------------------------------------------------
# BUILD THE ROUTING PIPELINE
# --------------------------------------------------------

pipeline = Pipeline([
    ('vectorizer', TfidfVectorizer(max_features=1000, stop_words='english')),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

pipeline.fit(X_train, y_train)
print()
print("Router trained successfully")

# --------------------------------------------------------
# EVALUATE THE ROUTER
# --------------------------------------------------------

y_pred = pipeline.predict(X_test)

print()
print("ROUTING ACCURACY:", round(accuracy_score(y_test, y_pred), 3))
print()
print("CLASSIFICATION REPORT:")
print(classification_report(y_test, y_pred))

# --------------------------------------------------------
# CONFUSION MATRIX
# --------------------------------------------------------

cm = confusion_matrix(y_test, y_pred)
cm_df = pd.DataFrame(
    cm, 
    index=pipeline.classes_, 
    columns=pipeline.classes_
)

print()
print("CONFUSION MATRIX:")
print(cm_df)
print()

teams = pipeline.classes_
for i, actual_team in enumerate(teams):
    total = cm[i].sum()
    correct = cm[i, i]
    pct = correct / total * 100
    print(actual_team, "tickets: Routed correctly", str(round(pct, 1)) + "% of the time")
    
    for j, predicted_team in enumerate(teams):
        if i != j and cm[i, j] > 0:
            print("  Misrouted to", predicted_team, ":", cm[i, j], "times")

# --------------------------------------------------------
# PREDICT ON NEW TICKETS
# --------------------------------------------------------

def route_ticket(subject, description):
    text = subject + ' ' + description
    
    team = pipeline.predict([text])[0]
    probabilities = pipeline.predict_proba([text])[0]
    confidence = max(probabilities)
    
    if confidence < 0.70:
        return {
            'team': 'General Support',
            'confidence': round(confidence * 100, 1),
            'needs_review': True,
            'note': 'Low confidence. Routed to general queue for manual review.'
        }
    
    return {
        'team': team,
        'confidence': round(confidence * 100, 1),
        'needs_review': False
    }

print()
print("=" * 50)
print("TESTING THE AUTO-ROUTER")
print("=" * 50)

test_tickets = [
    ("Cannot access account", "Password reset link is not working and I cannot log in."),
    ("Overcharged this month", "My bill shows two hundred dollars but my plan is only one hundred."),
    ("Product question", "Does this laptop model have a USB-C port for charging?"),
    ("Refund not received", "I returned an item three weeks ago and haven't gotten my money back."),
    ("App keeps crashing", "Every time I open the app it closes immediately after the logo screen.")
]

for subject, description in test_tickets:
    result = route_ticket(subject, description)
    print()
    print("Subject:", subject)
    print("  Routed to:", result['team'])
    print("  Confidence:", result['confidence'], "%")
    if result['needs_review']:
        print("  Note:", result['note'])