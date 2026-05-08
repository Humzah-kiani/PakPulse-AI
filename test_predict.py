import pandas as pd
import os
import sys

# Add FYP to path
fyp_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fyp_dir)

from predict import load_artifacts, predict_from_dataframe

print("Loading data and artifacts...")
df_in = pd.read_csv('pakpulse_250k_featured.csv')
scaler, reg, clf = load_artifacts()

print(f"Input CSV shape: {df_in.shape}")
print(f"Input columns: {list(df_in.columns[:10])}")
print(f"\nUnique diseases in input: {df_in['disease'].nunique()}")
print(df_in['disease'].unique())

print("\n" + "="*50)
print("Running predictions...")
preds = predict_from_dataframe(df_in, scaler, reg, clf)

print(f"\nPredictions shape: {preds.shape}")

# Check if district and disease are preserved
has_district = 'district' in preds.columns
has_disease = 'disease' in preds.columns

print(f"Has 'district' column: {has_district}")
print(f"Has 'disease' column: {has_disease}")

if has_disease:
    print(f"\nUnique diseases in predictions: {preds['disease'].nunique()}")
    print("Disease distribution:")
    print(preds['disease'].value_counts())
    
    print("\nSample predictions with disease names:")
    print(preds[['district', 'disease', 'cases', 'pred_cases_next', 'pred_outbreak', 'pred_outbreak_proba']].head(20))
else:
    print("\nERROR: 'disease' column not preserved in predictions!")
    print("Available columns:", list(preds.columns))
