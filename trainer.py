# The Corrected and Final trainer.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib

print("--- WBJEE AI Model Trainer ---")
print("This script will create the final .joblib files.")

# Part 1: Load the CORRECT Clean Data
try:
    df = pd.read_csv('wbjee_2023_clean_data.csv')
    df['year'] = 2023
    print("Step 1: Successfully loaded 'wbjee_2023_clean_data.csv'.")
except FileNotFoundError:
    print("FATAL ERROR: 'wbjee_2023_clean_data.csv' not found. Please run the corrected 'process_data.py' first.")
    exit()

# Part 2: Prepare the final training DataFrame
print("Step 2: Preparing data for training...")
# Drop any rows where the rank is missing, as they are unusable for training.
df_train = df.dropna(subset=['closing_rank_clean']).copy()
df_train['closing_rank_clean'] = df_train['closing_rank_clean'].astype(int)

# Part 3: Create the Mappings and Numerical IDs
# This is the most critical step. We create IDs and mappings from our final, clean data.
print("Step 3: Creating comprehensive mappings and numerical IDs...")
df_train['institute_id'] = df_train['institute'].astype('category').cat.codes
df_train['program_id'] = df_train['program'].astype('category').cat.codes
df_train['category_id'] = df_train['category'].astype('category').cat.codes
df_train['quota_id'] = df_train['quota'].astype('category').cat.codes

# Create a dictionary to save the mappings { 'name': id }
# This is what our app.py will use to look up IDs.
mappings = {
    'institute': {name: i for i, name in enumerate(df_train['institute'].astype('category').cat.categories)},
    'program': {name: i for i, name in enumerate(df_train['program'].astype('category').cat.categories)},
    'category': {name: i for i, name in enumerate(df_train['category'].astype('category').cat.categories)},
    'quota': {name: i for i, name in enumerate(df_train['quota'].astype('category').cat.categories)}
}

# Part 4: Define Features (X) and Target (y)
features = ['year', 'institute_id', 'program_id', 'category_id', 'quota_id']
target = 'closing_rank_clean'
X = df_train[features]
y = df_train[target]

# Part 5: Split Data, Train the Model, and Evaluate
print("Step 4: Splitting data and training the AI model...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# Evaluation
predictions = model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)
print(f"--- Model Training Complete ---")
print(f"Model Performance (Mean Absolute Error): {mae:.2f} ranks")

# Part 6: Save the final, correct model and mappings
print("Step 5: Saving new .joblib files...")
joblib.dump(model, 'wbjee_rank_predictor.joblib')
joblib.dump(mappings, 'mappings.joblib')

print("\n--- SUCCESS! ---")
print("New 'wbjee_rank_predictor.joblib' and 'mappings.joblib' have been created.")
print("You are now ready to run the final app.py")