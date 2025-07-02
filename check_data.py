import pandas as pd
df = pd.read_csv('wbjee_2023_clean_data.csv')
print("--- DATA DIAGNOSIS ---")
print("\n1. Unique values in 'category' column:")
print(df['category'].unique())
print("\n2. Count of True/False in 'is_tfw' column:")
print(df['is_tfw'].value_counts())

# Correctly look for 'Open' (capital O)
test_filter = df[(df['category'] == 'Open') & (df['is_tfw'] == False)]
print(f"\n3. Found {len(test_filter)} rows for 'Open', non-TFW seats.")