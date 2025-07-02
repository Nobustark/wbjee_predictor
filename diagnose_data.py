# diagnose_data.py - A read-only script to inspect the current CSV file.

import pandas as pd
import os

CSV_FILENAME = 'wbjee_2023_clean_data.csv'

print("--- Data Diagnostics Tool ---")

# Check 1: Does the file exist?
if not os.path.exists(CSV_FILENAME):
    print(f"\n[FAIL] The file '{CSV_FILENAME}' does not exist.")
    print("Please run the 'process_data.py' script to create it.")
    exit()

print(f"\n[SUCCESS] Found the file '{CSV_FILENAME}'.")

# Try to load the file
try:
    df = pd.read_csv(CSV_FILENAME)
    print("[SUCCESS] The file was loaded successfully.")
except Exception as e:
    print(f"\n[FAIL] Could not read the file. It might be corrupted. Error: {e}")
    exit()

# --- Targeted Test for 'OBC - B' Non-TFW ---
print("\n--- Running Test for 'OBC - B' (Non-TFW) ---")

# Check 2: Filter for 'OBC - B' category
obc_b_filter = df['category'] == 'OBC - B'
obc_b_rows = df[obc_b_filter]

if len(obc_b_rows) == 0:
    print("\n[FAIL] Found 0 rows with the category 'OBC - B'.")
    print("This indicates a problem in how the 'category' column was created in 'process_data.py'.")
    print("\nUnique categories found in your file are:")
    print(df['category'].unique())
    exit()

print(f"\n[SUCCESS] Found {len(obc_b_rows)} rows with category 'OBC - B'.")


# Check 3: From those 'OBC - B' rows, filter for non-TFW
non_tfw_filter = obc_b_rows['is_tfw'] == False
final_rows = obc_b_rows[non_tfw_filter]

if len(final_rows) == 0:
    print("\n[FAIL] Found 0 rows that are both 'OBC - B' AND non-TFW.")
    print("This means all 'OBC - B' rows are incorrectly marked as TFW.")
    exit()

print(f"[SUCCESS] Found {len(final_rows)} rows that are 'OBC - B' AND non-TFW.")


# Check 4: Check if the ranks in these final rows are valid numbers
num_valid_ranks = final_rows['closing_rank_clean'].count() # .count() ignores empty/None values

if num_valid_ranks == 0:
    print("\n[FAIL] Found 'OBC - B' non-TFW rows, but NONE of them have a valid closing rank number.")
    print("This indicates a problem with the 'clean_rank' function in 'process_data.py'.")
    exit()

print(f"[SUCCESS] Found {num_valid_ranks} valid closing rank numbers for this category.")


# If all checks pass, show a sample
print("\n--- All Checks Passed! ---")
print("Here is a sample of the correctly identified 'OBC - B' non-TFW data:")
print(final_rows[['institute', 'program', 'category', 'is_tfw', 'closing_rank_clean']].head())