# The Final, Robust process_data.py
import pandas as pd
import re # Import the regular expressions library

print("--- Data Processor (Final, Robust Version) ---")

try:
    df = pd.read_html('wbjee_data.html')[0]
    print("Step 1: Raw HTML data loaded.")
except Exception as e:
    print(f"Error reading HTML: {e}")
    exit()

# Step 2: Rename columns
df.columns = [
    'sr_no', 'round', 'institute', 'program_raw', 'stream',
    'seat_type', 'quota', 'category_raw', 'opening_rank', 'closing_rank'
]
df = df.drop(columns=['sr_no'])

# Step 3: Identify TFW seats
df['is_tfw'] = df['program_raw'].str.contains(r'\(TFW\)', na=False)
print(f"Step 2: Identified {df['is_tfw'].sum()} TFW seats.")

# Step 4: Clean program names
df['program'] = df['program_raw'].str.replace(r'\s*\(TFW\)', '', regex=True).str.strip()

# Step 5: Clean category names
def get_clean_category(row):
    if row['is_tfw']:
        return 'TFW'
    else:
        return row['category_raw'].strip()
df['category'] = df.apply(get_clean_category, axis=1)
print("Step 3: Created clean 'program' and 'category' columns.")

# --- <<< THE CRITICAL FIX IS HERE ---
# Step 6: A more robust function to clean the rank columns
def clean_rank(rank_value):
    # If the value is already a number (like an integer or float), just convert to int and return.
    if isinstance(rank_value, (int, float)):
        return int(rank_value)
    
    # If it's a string, we process it.
    if isinstance(rank_value, str):
        # Use a regular expression to find the first sequence of digits in the string.
        # This is very robust and handles cases like "1234", "456 (P-7)", etc.
        match = re.search(r'\d+', rank_value)
        if match:
            return int(match.group(0)) # .group(0) returns the matched number string
            
    # If it's not a number or a string with a number, or it's None, return None.
    return None
# --- End of FIX ---

df['opening_rank_clean'] = df['opening_rank'].apply(clean_rank)
df['closing_rank_clean'] = df['closing_rank'].apply(clean_rank)
print("Step 4: Cleaned rank columns with robust function.")

# Step 7: Select and save final columns
final_columns = [
    'round', 'institute', 'program', 'stream', 'seat_type', 'quota',
    'category', 'is_tfw', 'opening_rank_clean', 'closing_rank_clean'
]
final_df = df[final_columns]

output_filename = 'wbjee_2023_clean_data.csv'
final_df.to_csv(output_filename, index=False)

print("\n--- SUCCESS! ---")
print(f"New, correct version of '{output_filename}' has been created.")