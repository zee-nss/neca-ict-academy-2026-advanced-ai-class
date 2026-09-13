import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Create messy sales data with deliberate problems
np.random.seed(42)

# Generate base data
n_rows = 50  # Keep it small enough to scan, big enough to show problems

data = {
    'date': [],
    'product': [],
    'region': [],
    'quantity': [],
    'unit_price': [],
    'customer_email': []
}

products = ['Laptop Pro', 'laptop pro ', 'Wireless Mouse', 'WIRELESS MOUSE', 
            'USB-C Cable', 'Monitor 24"', 'monitor 24 inch', 'Keyboard', 
            'Webcam HD', 'Docking Station']

regions = ['North', 'South', 'East', 'West', 'Central', None]

for i in range(n_rows):
    # Messy dates — some as strings, some proper
    if i % 5 == 0:
        data['date'].append('Jan 15, 2024')  # String format
    elif i % 7 == 0:
        data['date'].append('2024/03/20')     # Wrong separator
    elif i % 11 == 0:
        data['date'].append(None)              # Missing
    else:
        data['date'].append('2024-06-15')     # Proper format
    
    # Messy product names — inconsistent casing, extra spaces, typos
    data['product'].append(np.random.choice(products))
    
    # Region — some missing
    data['region'].append(np.random.choice(regions))
    
    # Quantity — some missing, some negative
    qty = np.random.choice([1, 2, 3, 5, 10, None, -2, -1, 0], p=[0.3, 0.2, 0.15, 0.1, 0.05, 0.1, 0.03, 0.02, 0.05])
    data['quantity'].append(qty)
    
    # Unit price — some negative, some zero
    price = np.random.choice([29.99, 49.99, 99.99, 199.99, 0, -15.99, None], p=[0.3, 0.25, 0.2, 0.1, 0.05, 0.05, 0.05])
    data['unit_price'].append(price)
    
    # Email — some missing
    if i % 8 == 0:
        data['customer_email'].append(None)
    else:
        data['customer_email'].append(f'customer{i}@example.com')

# Convert to DataFrame
df = pd.DataFrame(data)

# Add some duplicate rows
duplicates = df.iloc[:5].copy()
df = pd.concat([df, duplicates], ignore_index=True)

# Shuffle
df = df.sample(frac=1).reset_index(drop=True)

# Save
save_path = os.path.expanduser("~/Desktop/neca ict academy 2026 advanced ai class/messy_sales.csv")
df.to_csv(save_path, index=False)

print(f" Created messy_sales.csv with {len(df)} rows")
print(f"   - {df['date'].isnull().sum()} missing dates")
print(f"   - {df['quantity'].isnull().sum()} missing quantities")
print(f"   - {df['unit_price'].isnull().sum()} missing prices")
print(f"   - {df['region'].isnull().sum()} missing regions")
print(f"   - {df['customer_email'].isnull().sum()} missing emails")
print(f"   - 5 duplicate rows added")
print(f"   - Product names have inconsistent formatting")
print(f"   - Dates have mixed formats")