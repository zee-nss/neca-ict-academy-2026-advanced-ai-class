import pandas as pd
import numpy as np
import joblib
import os
import sqlite3
import json
from datetime import datetime

# joblib.dump('best_fraud_model.pkl') to save model after training (run this once after training)
# os.makedirs('models', exist_ok=True) creates model directory
# --------------------------------------------------------
# LOAD MODEL
# --------------------------------------------------------
#joblib.load('weighted_fraud_model.pkl)  # Load the saved model
def load_model():
    model = joblib.load('best_fraud_model.pkl')
    return model
# model = joblib.load(best_fraud_model.pkl) this also loads saved model.

#verify load models 
#df = pd.read_csv('fraud_transaction.csv') step 1
# feature_columns = ['transaction_amount', 'account_age_days', 'transaction_hour',
#                    'previous_transactions', 'device_type', 'location_match',
#                    'amount_vs_average', 'is_new_device'] step 2
# X = df[feature_columns] step 3


# --------------------------------------------------------
# PREDICT SINGLE TRANSACTION
# --------------------------------------------------------

def predict_transaction(model, transaction):
    trans_df = pd.DataFrame([transaction])
    
    feature_order = ['transaction_amount', 'account_age_days',
                     'transaction_hour', 'previous_transactions',
                     'device_type', 'location_match',
                     'amount_vs_average', 'is_new_device']
    trans_df = trans_df[feature_order]
    
    prediction = model.predict(trans_df)[0]
    probabilities = model.predict_proba(trans_df)[0]
    fraud_probability = probabilities[1]
    
    if fraud_probability > 0.85:
        risk_level = 'HIGH'
    elif fraud_probability > 0.60:
        risk_level = 'MEDIUM'
    else:
        risk_level = 'LOW'
    
    result = {
        'prediction': 'FRAUD' if prediction == 1 else 'LEGITIMATE',
        'fraud_probability': round(fraud_probability * 100, 1),
        'risk_level': risk_level,
        'timestamp': datetime.now().isoformat()
    }
    
    return result

# --------------------------------------------------------
# LOG TO DATABASE
# --------------------------------------------------------

def log_prediction_to_db(prediction_result, db_path='predictions.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            prediction TEXT,
            fraud_probability REAL,
            risk_level TEXT,
            action_taken TEXT,
            transaction_data TEXT
        )
    ''')
    
    cursor.execute('''
        INSERT INTO predictions (timestamp, prediction, fraud_probability, 
                                 risk_level, action_taken, transaction_data)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        prediction_result['timestamp'],
        prediction_result['prediction'],
        prediction_result['fraud_probability'],
        prediction_result['risk_level'],
        prediction_result.get('action', 'none'),
        json.dumps(prediction_result.get('transaction_data', {}))
    ))
    
    conn.commit()
    conn.close()
    return True

# --------------------------------------------------------
# SEND ALERT
# --------------------------------------------------------

def send_alert(prediction_result, transaction_id):
    alert_message = (
        "ALERT: High Risk Transaction Detected\n"
        "Transaction ID: " + str(transaction_id) + "\n"
        "Prediction: " + prediction_result['prediction'] + "\n"
        "Fraud Probability: " + str(prediction_result['fraud_probability']) + "%\n"
        "Risk Level: " + prediction_result['risk_level'] + "\n"
        "Timestamp: " + prediction_result['timestamp'] + "\n"
        "Action Required: Immediate review"
    )
    
    print()
    print("=" * 50)
    print(alert_message)
    print("=" * 50)
    
    return True

# --------------------------------------------------------
# TAKE ACTION
# --------------------------------------------------------

def take_action(prediction_result, transaction_id):
    risk_level = prediction_result['risk_level']
    
    if risk_level == 'HIGH':
        action = 'AUTO_BLOCKED'
        prediction_result['action'] = action
        log_prediction_to_db(prediction_result)
        send_alert(prediction_result, transaction_id)
        print("Action: Transaction", transaction_id, "AUTO-BLOCKED")
        
    elif risk_level == 'MEDIUM':
        action = 'FLAGGED_FOR_REVIEW'
        prediction_result['action'] = action
        log_prediction_to_db(prediction_result)
        print("Action: Transaction", transaction_id, "flagged for analyst review")
        
    else:
        action = 'PASSED'
        prediction_result['action'] = action
        log_prediction_to_db(prediction_result)
        print("Action: Transaction", transaction_id, "passed automatically")
    
    prediction_result['action'] = action
    return prediction_result

# --------------------------------------------------------
# BATCH PREDICTION PIPELINE
# --------------------------------------------------------

def batch_prediction_pipeline(new_data_path, output_path):
    print("STARTING BATCH PREDICTION PIPELINE")
    print("=" * 50)
    
    print("Loading model...")
    model = load_model()
    print("Model loaded")
    
    print()
    print("Loading new transactions...")
    df_new = pd.read_csv(new_data_path)
    print("Loaded", len(df_new), "new records")
    
    results = []
    high_count = 0
    medium_count = 0
    low_count = 0
    
    print()
    print("Processing transactions...")
    
    for idx, row in df_new.iterrows():
        transaction_id = row.get('transaction_id', 'TXN-' + str(idx))
        transaction = row.to_dict()
        
        pred_result = predict_transaction(model, transaction)
        pred_result['transaction_data'] = transaction
        
        action_result = take_action(pred_result, transaction_id)
        
        if action_result['risk_level'] == 'HIGH':
            high_count += 1
        elif action_result['risk_level'] == 'MEDIUM':
            medium_count += 1
        else:
            low_count += 1
        
        results.append(action_result)
    
    df_results = pd.DataFrame(results)
    df_results.to_csv(output_path, index=False)
    
    print()
    print("=" * 50)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 50)
    print("Total processed:", len(results))
    print("HIGH risk (auto-blocked):", high_count)
    print("MEDIUM risk (flagged):", medium_count)
    print("LOW risk (passed):", low_count)
    print()
    print("Results saved to:", output_path)
    print("Audit log saved to: predictions.db")
    
    return df_results

# --------------------------------------------------------
# RUN IT
# --------------------------------------------------------

if __name__ == "__main__":
    # Test single prediction
    print("TESTING SINGLE PREDICTION")
    model = load_model()
    
    test_transaction = {
        'transaction_amount': 4500,
        'account_age_days': 15,
        'transaction_hour': 3,
        'previous_transactions': 2,
        'device_type': 1,
        'location_match': 0,
        'amount_vs_average': 8.5,
        'is_new_device': 1
    }
    
    result = predict_transaction(model, test_transaction)
    print("Prediction:", result['prediction'])
    print("Fraud Probability:", result['fraud_probability'], "%")
    print("Risk Level:", result['risk_level'])
    
    print()
    print("RUNNING BATCH PIPELINE")
    results = batch_prediction_pipeline('new_transactions.csv', 'predictions_results.csv')
    
    print()
    print("Sample results:")
    print(results[['prediction', 'fraud_probability', 'risk_level', 'action']].head(10))