import joblib
import pandas as pd
import sys
sys.path.append(r'c:/Users/user/OneDrive - Higher Education Commission/Desktop/FYP')
import predict

scaler = joblib.load(r'c:/Users/user/OneDrive - Higher Education Commission/Desktop/FYP/models/feature_minmax_scaler.joblib')
df = pd.read_csv(r'c:/Users/user/OneDrive - Higher Education Commission/Desktop/FYP/pakpulse_250k_featured.csv')
X, features, df2 = predict.prepare_features(df, scaler)
print('Prepared count', len(features))
print('Prepared features:', features)

reg = joblib.load(r'c:/Users/user/OneDrive - Higher Education Commission/Desktop/FYP/models/lgb_reg_cases_next.joblib')
try:
    expected = reg.booster_.feature_name()
except Exception:
    expected = getattr(reg, 'feature_name_', None)
print('Expected count', len(expected) if expected else None)
print('Expected features:', expected)

miss = [c for c in expected if c not in features]
extra = [c for c in features if c not in expected]
print('Missing features:', miss)
print('Extra features:', extra)
print('X shape:', X.shape)
