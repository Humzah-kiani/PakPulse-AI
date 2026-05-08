# Save as run_pakpulse_full.py
# Requirements:
# pip install pandas numpy scikit-learn lightgbm joblib

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import lightgbm as lgb
import joblib
import os

FNAME = "pakpulse_250k_featured.csv"   # ensure this file is in same folder

assert os.path.exists(FNAME), f"{FNAME} not found in current folder."

# ---------- LOAD ----------
df = pd.read_csv(FNAME)
print("Loaded:", df.shape)

# ---------- MINIMAL CLEAN ----------
# Ensure date column exists (try common names)
date_cols = [c for c in df.columns if "date" in c.lower()]
if date_cols:
    date_col = date_cols[0]
    df[date_col] = pd.to_datetime(df[date_col])
else:
    date_col = None

# Ensure target exists
if "cases" not in df.columns:
    raise ValueError("Dataset must include a 'cases' column as target.")

# If climate columns are present they will be used; if not, pipeline still runs
climate_cols = [c for c in ["temperature","temp","humidity","rainfall","wind_speed"] if any(cc for cc in df.columns if cc.lower()==c)]
# normalize names if needed
# (we won't force merges; assume all features in this file)

# ---------- SORT ----------
if date_col:
    df = df.sort_values(["district_id", date_col]).reset_index(drop=True)
else:
    df = df.sort_values(["district_id"]).reset_index(drop=True)

# ---------- FEATURE ENGINEERING ----------
if date_col:
    df["day"] = df[date_col].dt.day
    df["month"] = df[date_col].dt.month
    df["year"] = df[date_col].dt.year
    df["week"] = df[date_col].dt.isocalendar().week.astype(int)

# LAGS: 7, 14, 28 (days). If dataset is daily and has consistent dates per district this works.
for lag in [7,14,28]:
    df[f"cases_lag_{lag}"] = df.groupby("district_id")["cases"].shift(lag)

# Rolling means
for win in [7,14,28]:
    df[f"cases_roll_mean_{win}"] = df.groupby("district_id")["cases"].rolling(window=win, min_periods=1).mean().reset_index(level=0, drop=True)

# Climate rolling averages if those columns exist
possible_climate = [c for c in df.columns if c.lower() in ("temperature","temp","humidity","rainfall","wind_speed")]
for c in possible_climate:
    df[f"{c}_roll_7"] = df.groupby("district_id")[c].rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)
    df[f"{c}_roll_14"] = df.groupby("district_id")[c].rolling(window=14, min_periods=1).mean().reset_index(level=0, drop=True)

# Drop rows with NaNs created by shifts (we need complete rows for model)
df = df.dropna(subset=[f"cases_lag_7"]).reset_index(drop=True)
print("After creating lags/rolls:", df.shape)

# ---------- PREPARE X,y ----------
y = df["cases"]
X = df.drop(columns=["cases"])
# Drop raw date if present (we used date features)
if date_col and date_col in X.columns:
    X = X.drop(columns=[date_col])

# cast object columns to category for LightGBM
for col in X.select_dtypes(include="object").columns:
    X[col] = X[col].astype("category")

# ensure district_id categorical
if "district_id" in X.columns:
    X["district_id"] = X["district_id"].astype("category")

cat_cols = [c for c in X.columns if str(X[c].dtype)=="category"]

# ---------- SPLIT ----------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, shuffle=True, random_state=42)
print("Train shape:", X_train.shape, "Test shape:", X_test.shape)

# ---------- LIGHTGBM DATASET ----------
train_data = lgb.Dataset(X_train, label=y_train, categorical_feature=cat_cols, free_raw_data=False)
test_data  = lgb.Dataset(X_test,  label=y_test,  categorical_feature=cat_cols, reference=train_data, free_raw_data=False)

params = {
    "objective": "regression",
    "metric": "rmse",
    "boosting_type": "gbdt",
    "learning_rate": 0.05,
    "num_leaves": 40,
    "feature_fraction": 0.85,
    "bagging_fraction": 0.85,
    "bagging_freq": 5,
    "seed": 42,
    "verbose": -1
}

model = lgb.train(
    params,
    train_data,
    valid_sets=[train_data, test_data],
    num_boost_round=1500,
    early_stopping_rounds=100,
    verbose_eval=100
)

# ---------- PREDICT & METRICS ----------
preds = model.predict(X_test, num_iteration=model.best_iteration)
mae  = mean_absolute_error(y_test, preds)
rmse = mean_squared_error(y_test, preds, squared=False)
r2   = r2_score(y_test, preds)

print("\n===== PERFORMANCE =====")
print(f"MAE  : {mae:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"R²   : {r2:.4f}")

# ---------- SAVE MODEL + SAMPLE PREDICTIONS ----------
model_path = "pakpulse_lgb_advanced.bin"
model.save_model(model_path)
print("Model saved to", model_path)

sample_out = X_test.copy()
sample_out["true_cases"] = y_test.values
sample_out["pred_cases"] = preds
sample_out[["district_id","true_cases","pred_cases"]].to_csv("sample_predictions.csv", index=False)
print("Sample predictions saved to sample_predictions.csv")
