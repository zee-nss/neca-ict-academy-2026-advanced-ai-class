import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime

# --------------------------------------------------------
# LOAD SAVED MODEL AND PREPROCESSING
# --------------------------------------------------------
print("Loading saved model...")

loaded_model = joblib.load('models/classifier.pkl')
loaded_scaler = joblib.load('models/scaler.pkl')
loaded_features = joblib.load('models/feature_columns.pkl')

print("Model loaded:", type(loaded_model).__name__)
print("Scaler loaded:", type(loaded_scaler).__name__)
print("Feature columns:", loaded_features)
print()
print("Everything loaded successfully.")

# --------------------------------------------------------
# SINGLE PREDICTION TEST
# --------------------------------------------------------

print()
print("SINGLE PREDICTION TEST")
print("=" * 40)

new_transaction = {
    'transaction_amount': 6500,
    'account_age_days': 7,
    'transaction_hour': 2,
    'previous_transactions': 1,
    'device_type': 1,
    'location_match': 0,
    'amount_vs_average': 9.5,
    'is_new_device': 1
}

# Fixed: Use DataFrame to avoid feature names warning
new_data = pd.DataFrame([new_transaction])
new_data = new_data[loaded_features]
new_data_scaled = loaded_scaler.transform(new_data)

prediction = loaded_model.predict(new_data_scaled)[0]
probabilities = loaded_model.predict_proba(new_data_scaled)[0]
confidence = max(probabilities)

print("Transaction Details:")
print("  Amount: $" + str(new_transaction['transaction_amount']))
print("  Account Age:", new_transaction['account_age_days'], "days")
print("  Time:", new_transaction['transaction_hour'], ":00")
print("  New Device:", "Yes" if new_transaction['is_new_device'] else "No")

print()
print("Prediction:", "FRAUD" if prediction == 1 else "LEGITIMATE")
print("Confidence:", str(round(confidence * 100, 1)) + "%")

if prediction == 1 and confidence > 0.85:
    print("Action: AUTO-BLOCK and alert security team")
elif prediction == 1:
    print("Action: Flag for manual review")
else:
    print("Action: Approve transaction")

# --------------------------------------------------------
# BATCH PREDICTION PIPELINE
# --------------------------------------------------------

def batch_predict(input_csv, output_csv):
    print()
    print("BATCH PREDICTION PIPELINE")
    print("=" * 40)
    
    print("Loading model...")
    model = joblib.load('models/classifier.pkl')
    scaler = joblib.load('models/scaler.pkl')
    features = joblib.load('models/feature_columns.pkl')
    print("Model loaded successfully")
    
    print()
    print("Loading new transactions...")
    df = pd.read_csv(input_csv)
    print("Loaded", len(df), "records")
    
    X = df[features]
    X_scaled = scaler.transform(X)
    
    print("Making predictions...")
    df['prediction'] = model.predict(X_scaled)
    df['fraud_probability'] = model.predict_proba(X_scaled)[:, 1]
    df['confidence'] = model.predict_proba(X_scaled).max(axis=1)
    
    # Lower thresholds for better demo visibility
    def assign_risk_level(prob):
        if prob > 0.45:
            return 'HIGH'
        elif prob > 0.30:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    df['risk_level'] = df['fraud_probability'].apply(assign_risk_level)
    df['prediction_timestamp'] = datetime.now().isoformat()
    
    df.to_csv(output_csv, index=False)
    
    print()
    print("=" * 40)
    print("BATCH COMPLETE")
    print("=" * 40)
    print("Total processed:", len(df))
    print()
    
    for level in ['HIGH', 'MEDIUM', 'LOW']:
        count = len(df[df['risk_level'] == level])
        print(level, "risk:", count)
    
    print()
    print("Results saved to:", output_csv)
    
    return df

results = batch_predict('new_batch_transactions.csv', 'batch_predictions.csv')

print()
print("Sample results:")
sample_cols = ['transaction_amount', 'prediction', 'fraud_probability', 'risk_level']
print(results[sample_cols].head(10))

# --------------------------------------------------------
# PRODUCTION PREDICTION FUNCTION
# --------------------------------------------------------

def predict_transaction(transaction_dict):
    model = joblib.load('models/classifier.pkl')
    scaler = joblib.load('models/scaler.pkl')
    features = joblib.load('models/feature_columns.pkl')
    
    # Fixed: Use DataFrame to avoid feature names warning
    data = pd.DataFrame([transaction_dict])
    data = data[features]
    data_scaled = scaler.transform(data)
    
    prediction = model.predict(data_scaled)[0]
    probabilities = model.predict_proba(data_scaled)[0]
    fraud_prob = probabilities[1]
    confidence = max(probabilities)
    
    # Lower thresholds for better demo visibility
    if prediction == 1 and fraud_prob > 0.45:
        action = 'AUTO_BLOCK'
        note = 'High confidence fraud. Block immediately.'
    elif prediction == 1 and fraud_prob > 0.30:
        action = 'MANUAL_REVIEW'
        note = 'Possible fraud. Add to analyst queue.'
    elif fraud_prob > 0.20:
        action = 'MONITOR'
        note = 'Slightly unusual. Log for monitoring.'
    else:
        action = 'APPROVE'
        note = 'Transaction appears normal.'
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'prediction': 'FRAUD' if prediction == 1 else 'LEGITIMATE',
        'fraud_probability': round(fraud_prob * 100, 1),
        'confidence': round(confidence * 100, 1),
        'action': action,
        'note': note
    }
    
    return result

print()
print("TESTING PRODUCTION PREDICTION FUNCTION")
print("=" * 40)

test_cases = [
    {'transaction_amount': 7500, 'account_age_days': 3, 'transaction_hour': 4,
     'previous_transactions': 0, 'device_type': 1, 'location_match': 0,
     'amount_vs_average': 10, 'is_new_device': 1},
    {'transaction_amount': 85, 'account_age_days': 450, 'transaction_hour': 14,
     'previous_transactions': 45, 'device_type': 0, 'location_match': 1,
     'amount_vs_average': 1.2, 'is_new_device': 0},
    {'transaction_amount': 1200, 'account_age_days': 90, 'transaction_hour': 20,
     'previous_transactions': 12, 'device_type': 2, 'location_match': 1,
     'amount_vs_average': 3.5, 'is_new_device': 0},
]

for i, txn in enumerate(test_cases):
    result = predict_transaction(txn)
    print()
    print("Transaction", i+1)
    print("  Amount: $" + str(txn['transaction_amount']))
    print("  Prediction:", result['prediction'])
    print("  Fraud Probability:", result['fraud_probability'], "%")
    print("  Action:", result['action'])
    print("  Note:", result['note'])