import pandas as pd
import os

csv_path = os.path.join(os.path.dirname(__file__), 'pakpulse_250k_featured.csv')
df = pd.read_csv(csv_path)

print('=== TRAINING DATA INFO ===')
print(f'Total rows: {len(df)}')
print(f'\nUnique diseases: {df.disease.nunique()}')
print(df['disease'].unique())

print(f'\nUnique districts: {df.district.nunique()}')

print(f'\nDisease counts:')
print(df['disease'].value_counts())

print(f'\n\nSample of data:')
print(df[['date', 'district', 'disease', 'cases']].head(15))

# Now check predictions
pred_path = os.path.join(os.path.dirname(__file__), 'models', 'predictions_on_train.csv')
if os.path.exists(pred_path):
    preds = pd.read_csv(pred_path)
    print(f'\n\n=== PREDICTIONS INFO ===')
    print(f'Total prediction rows: {len(preds)}')
    print(f'\nUnique diseases in predictions: {preds.disease.nunique()}')
    print(preds['disease'].unique())
    print(f'\nDisease counts in predictions:')
    print(preds['disease'].value_counts())
else:
    print(f'\nPredictions file not found at {pred_path}')
