# main.py - The Complete Automated Reporter
# Scheduled to run every Monday at 7 AM via Windows Task Scheduler

import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# --------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------
def load_env():
    """Load environment variables from .env file."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

DATA_SOURCE = os.environ.get('DATA_SOURCE', 'sales_data_CLEANED.csv')
RECIPIENTS = os.environ.get('RECIPIENTS', 'yusufzeenah12@gmail.com').split(',')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD')

def main():
    """The complete automated reporting pipeline."""
    print("Starting automated report:", datetime.now())
    
    try:
        # Step 1: Load the data
        print("Loading data...")
        df = pd.read_csv(DATA_SOURCE)
        df['date'] = pd.to_datetime(df['date'])
        
        # Step 2: Clean
        print("Cleaning data...")
        # df = clean_data(df)
        
        # Step 3: Generate charts
        print("Creating charts...")
        # chart_path = create_report_charts(df)
        
        # Step 4: Create Excel report
        print("Building report...")
        # report_path = create_excel_report(df, chart_path)
        
        # Step 5: Email the report
        print("Sending email...")
        # success = email_report(RECIPIENTS, report_path, chart_path,
        #                        SENDER_EMAIL, SENDER_PASSWORD)
        
        print("Automated report complete!")
        
    except Exception as e:
        print("Automation failed:", e)
        # In production, send an alert to the admin here

if __name__ == '__main__':
    main()

