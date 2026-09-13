import pandas as pd


# --------------------------------------------------------
# STEP 1: LOAD
# --------------------------------------------------------
df = pd.read_csv('messy_sales.csv')

# ALWAYS inspect first
print("SHAPE:", df.shape)# total number of rows and colums
print()
print("FIRST 5 ROWS:")
print(df.head(5))# first five row
print()
print("DATA TYPES:")
print(df.dtypes)# data type
print()
print("MISSING VALUES:")
print(df.isnull().sum())# the total number of missing value in your dataset

# df.tail()# last five row


# --------------------------------------------------------
# STEP 2: CLEAN
# --------------------------------------------------------

# 2a: Remove duplicates
before = len(df)
df = df.drop_duplicates()#remove duplicate
print("Removed", before - len(df), "duplicate rows")



# 2b: Fix dates
df['date'] = pd.to_datetime(df['date'], errors='coerce')
print("Dates converted. Invalid dates become NaT.")


# 2c: Handle missing values with RULES
#in our df, the quantity column has (1,2,3,5,6,7,9,8, , , ,)
#median_qty = (4.5)
# quality column will now be (1,2,3,5,6,7,9,8,4.5,4.5,4.5)
# code to handle missing value (fillna)

median_qty = df['quantity'].median() # median_qty =
df['quantity'] = df['quantity'].fillna(median_qty)
print("Filled missing quantities with median:", median_qty)

df['region'] = df['region'].fillna('Unknown')
print("Missing regions marked as 'Unknown'")

df.loc[df['unit_price'] <= 0, 'unit_price'] = None
df['unit_price'] = df.groupby('product')['unit_price'].transform(
    lambda x: x.fillna(x.median())
)
print("Invalid prices replaced with product median")

# product = (4 vaseline,6toothpaste, 3roll-on)
# unit price =vaseline (4500,4000,2500,6000,4000,4000 ), toothpaste (150, 200, 250,200 ), roll-on (3000, 3500, 9000,3500 3500,3500 , )
# unit price median = vaseline (4000), toothpaste (200), roll-on (3500)
# unit price overall median = 2000

# 2d: Fix text inconsistencies
df['product'] = df['product'].str.strip().str.title()
print("Product names standardized")
#vaseline, Vaseline, VASELINE
# Verify cleaning
# str.upper()# convert to uppercase
print()
print("AFTER CLEANING:")
print("Missing values remaining:")
print(df.isnull().sum())
print()
print("Rows:", len(df))
print("Columns:", len(df.columns))




# --------------------------------------------------------
# STEP 3: TRANSFORM
# --------------------------------------------------------
df['total_sale'] = df['quantity'] * df['unit_price'] # adding new column total_sale 5, 600 600*5=3000
df['month'] = df['date'].dt.month # adding new column month 2025/07/14 
df['day_of_week'] = df['date'].dt.day_name() # adding new column day_of_week

print()
print("Added calculated columns:")
print(df[['product', 'quantity', 'unit_price', 'total_sale']].head())

summary = df.groupby('region').agg({
    'total_sale': ['sum', 'mean', 'count'],
    'quantity': 'sum'
}).round(2)

print()
print("REGIONAL SUMMARY:")
print(summary)




# --------------------------------------------------------
# STEP 4: DELIVER
# --------------------------------------------------------
df.to_csv('sales_data_CLEANED.csv', index=False)
df.to_excel('sales_data_CLEANED.xlsx', index=False, engine='openpyxl')

print()
print("Cleaned data saved!")
print("  sales_data_CLEANED.csv")
print("  sales_data_CLEANED.xlsx")
print(" ", len(df), "rows,", len(df.columns), "columns")
print("Processing complete")


