import pandas as pd
import numpy as np
import os

base = os.path.expanduser("~/Desktop/neca ict academy 2026 advanced ai class")

# Load the messy data
df = pd.read_csv(os.path.join(base, "messy_sales.csv"))

# Clean it (same steps from Video 2.1)
df = df.drop_duplicates()
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['quantity'] = df['quantity'].fillna(df['quantity'].median())
df['region'] = df['region'].fillna('Unknown')
df.loc[df['unit_price'] <= 0, 'unit_price'] = None
df['unit_price'] = df.groupby('product')['unit_price'].transform(
    lambda x: x.fillna(x.median())
)
df['product'] = df['product'].str.strip().str.title()

# Add calculated columns
df['total_sale'] = df['quantity'] * df['unit_price']
df['month'] = df['date'].dt.month
df['day_of_week'] = df['date'].dt.day_name()

# Save as clean dataset
df.to_csv(os.path.join(base, "sales_data_CLEANED.csv"), index=False)

print(f" Clean dataset saved: {len(df)} rows, {len(df.columns)} columns")
print(f"   Columns: {list(df.columns)}")