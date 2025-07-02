# Final app.py that matches the new data format
from flask import Flask, render_template, request
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)

model = joblib.load('wbjee_rank_predictor.joblib')
mappings = joblib.load('mappings.joblib')
df_all_options = pd.read_csv('wbjee_2023_clean_data.csv')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    user_rank = int(request.form['user_rank'])
    user_quota = request.form['user_quota']
    user_category_from_form = request.form['user_category'] # This is 'OPEN' from the form
    is_tfw = (request.form['user_tfw'] == 'Yes')

    predict_df = df_all_options.copy()
    predict_df = predict_df[predict_df['quota'] == user_quota]

    if is_tfw:
        predict_df = predict_df[predict_df['is_tfw'] == True]
    else:
        # FIX: Convert form input 'OPEN' to data format 'Open'
        if user_category_from_form == 'OPEN':
            category_to_search = 'Open' 
        else:
            category_to_search = user_category_from_form

        predict_df = predict_df[
            (predict_df['category'] == category_to_search) &
            (predict_df['is_tfw'] == False)
        ]

    if predict_df.empty:
        return "<h3>No historical data found for this combination.</h3>"

    # The rest of the prediction logic...
    prediction_input_list = []
    predict_df.drop_duplicates(subset=['institute', 'program'], inplace=True)
    for index, row in predict_df.iterrows():
        inst_id = mappings['institute'].get(row['institute'])
        prog_id = mappings['program'].get(row['program'])
        cat_id = mappings['category'].get(row['category'])
        quot_id = mappings['quota'].get(row['quota'])
        if all(id is not None for id in [inst_id, prog_id, cat_id, quot_id]):
            prediction_input_list.append({
                'original_index': index, 'year': 2024, 'institute_id': inst_id,
                'program_id': prog_id, 'category_id': cat_id, 'quota_id': quot_id
            })
    if not prediction_input_list:
        return "<h3>No valid options found after checking against model data.</h3>"

    X_predict = pd.DataFrame(prediction_input_list)
    original_indices = X_predict.pop('original_index')
    predicted_ranks = model.predict(X_predict)
    results_df = pd.DataFrame({'predicted_rank': np.round(predicted_ranks).astype(int)}, index=original_indices)
    final_df = predict_df.join(results_df, how='inner')

    safe_options = final_df[final_df['predicted_rank'] > user_rank * 1.15].sort_values('predicted_rank')
    moderate_options = final_df[(final_df['predicted_rank'] <= user_rank * 1.15) & (final_df['predicted_rank'] >= user_rank)].sort_values('predicted_rank')
    ambitious_options = final_df[(final_df['predicted_rank'] < user_rank) & (final_df['predicted_rank'] > user_rank * 0.85)].sort_values('predicted_rank', ascending=False)
    
    return render_template('results.html',
                           user_rank=user_rank, user_quota=user_quota,
                           user_category=user_category_from_form,
                           safe_options=safe_options.to_dict('records'),
                           moderate_options=moderate_options.to_dict('records'),
                           ambitious_options=ambitious_options.to_dict('records'))

if __name__ == '__main__':
    app.run(debug=True)