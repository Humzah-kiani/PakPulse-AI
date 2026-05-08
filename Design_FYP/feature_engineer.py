# feature_engineer.py
# Feature engineering for PakPulse FYP
# Input: pakpulse_250k_realistic.csv
# Output: pakpulse_250k_featured.csv + saved scalers/encoders

import os
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
import joblib

INPUT_CSV = "pakpulse_250k_realistic.csv"
OUTPUT_CSV = "pakpulse_250k_featured.csv"
ENC_DIR = "scalers_and_encoders"

os.makedirs(ENC_DIR, exist_ok=True)

print("Loading dataset:", INPUT_CSV)
df = pd.read_csv(INPUT_CSV, parse_dates=["date"])

# Ensure correct sorting for rolling/lags
df = df.sort_values(["district", "disease", "date"]).reset_index(drop=True)

# ------------------------
# 1) Time features
# ------------------------
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day
df["dayofweek"] = df["date"].dt.dayofweek  # 0=Mon
df["is_weekend"] = df["dayofweek"].isin([5,6]).astype(int)

# season bucket (monsoon, winter, etc.) - simple mapping
def season_of_month(m):
    if m in [7,8,9]:
        return "monsoon"
    if m in [12,1,2]:
        return "winter"
    if m in [3,4]:
        return "spring"
    return "autumn"
df["season"] = df["month"].apply(season_of_month)

# ------------------------
# 2) Lag features (already computed as lag_1..lag_3 by generator)
# ensure integer type
for c in ["lag_1", "lag_2", "lag_3"]:
    if c in df.columns:
        df[c] = df[c].fillna(0).astype(int)
    else:
        df[c] = 0

# ------------------------
# 3) Rolling features (per district,disease)
#    windows in number of timepoints (these are evenly sampled timepoints across years)
#    choose windows that make sense for your model: 3, 7, 14 timepoints
# ------------------------
group = df.groupby(["district", "disease"])

# rolling mean/std for cases
for w in (3, 7, 14):
    col_mean = f"cases_roll_mean_{w}"
    col_std = f"cases_roll_std_{w}"
    df[col_mean] = group["cases"].transform(lambda x: x.rolling(window=w, min_periods=1).mean())
    df[col_std]  = group["cases"].transform(lambda x: x.rolling(window=w, min_periods=1).std().fillna(0))

# rolling sums (useful for outbreak detection)
for w in (3, 7, 14):
    col_sum = f"cases_roll_sum_{w}"
    df[col_sum] = group["cases"].transform(lambda x: x.rolling(window=w, min_periods=1).sum())

# rate-of-change features
df["cases_pct_change_3"] = group["cases"].transform(lambda x: x.pct_change(periods=3).replace([np.inf, -np.inf], 0).fillna(0))

# ------------------------
# 4) Environmental anomalies
# compute monthly mean per district to create anomaly features
# ------------------------
env_cols = ["temperature", "humidity", "rainfall"]
for col in env_cols:
    monthly_avg = df.groupby(["district", "month"])[col].transform("mean")
    df[f"{col}_anom"] = df[col] - monthly_avg

# ------------------------
# 5) Cumulative / historical features
# cumulative cases in past year (approx past X timepoints). Because we have 250 timepoints across 11 years,
# "past year" is roughly 250/11 ≈ 23 timepoints. We'll use 24 as approx 1-year window.
# ------------------------
one_year_tp = 24
df["cases_last_1yr"] = group["cases"].transform(lambda x: x.rolling(window=one_year_tp, min_periods=1).sum())

# ------------------------
# 6) Risk factor / CERS components
# Normalize components then compute CERS as weighted sum.
# Components used: recent cases (mean over 7), population_density, sanitation_index (inverted), rainfall (recent mean)
# ------------------------
# prepare scalers but compute normalization after we have full df (below)
# create base CERS components (raw)
df["cases_component_raw"] = df["cases_roll_mean_7"]
df["pop_component_raw"] = df["population_density"]
df["sanitation_component_raw"] = 100 - df["sanitation_index"]  # inverse: higher -> more risk
df["rain_component_raw"] = df["cases_roll_mean_7"] * (df["rainfall"] / (df["rainfall"].max() + 1))  # amplification proxy

# ------------------------
# 7) Outbreak labeling (two variants)
#  - outbreak_z: local z-score based (cases > mean + 2*std per district+disease)
#  - outbreak_threshold: absolute threshold based on distribution (top 5% per disease)
# ------------------------
# compute mean/std per group
group_stats = df.groupby(["district","disease"])["cases"].agg(["mean","std"]).reset_index().rename(columns={"mean":"g_mean","std":"g_std"})
df = df.merge(group_stats, on=["district","disease"], how="left")
df["g_std"] = df["g_std"].fillna(0)

# outbreak_z
df["outbreak_z"] = ((df["cases"] > (df["g_mean"] + 2 * df["g_std"])).astype(int))

# outbreak_threshold per disease (global)
disease_thresh = df.groupby("disease")["cases"].quantile(0.95).to_dict()
df["outbreak_disease95"] = df["disease"].map(lambda d: disease_thresh.get(d, 0))
df["outbreak_threshold"] = (df["cases"] >= df["outbreak_disease95"]).astype(int)

# drop helper columns used for outbreak
df = df.drop(columns=["g_mean", "g_std", "outbreak_disease95"])

# ------------------------
# 8) CERS normalization & final score (0-100)
# ------------------------
# Choose features to normalize
cers_features = ["cases_component_raw", "pop_component_raw", "sanitation_component_raw", "rain_component_raw"]
scaler_cers = MinMaxScaler()
df_cers_scaled = scaler_cers.fit_transform(df[cers_features].fillna(0))
# save scaler
joblib.dump(scaler_cers, os.path.join(ENC_DIR, "scaler_cers.joblib"))

# weights (tuneable)
w_cases = 0.45
w_pop = 0.25
w_san = 0.20
w_rain = 0.10

df["CERS"] = (
    w_cases * df_cers_scaled[:, 0] +
    w_pop   * df_cers_scaled[:, 1] +
    w_san   * df_cers_scaled[:, 2] +
    w_rain  * df_cers_scaled[:, 3]
) * 100.0

# ------------------------
# 9) Encoding categorical features
# ------------------------
# district and disease label encoders
le_district = LabelEncoder()
le_disease = LabelEncoder()
df["district_enc"] = le_district.fit_transform(df["district"])
df["disease_enc"] = le_disease.fit_transform(df["disease"])

joblib.dump(le_district, os.path.join(ENC_DIR, "labelencoder_district.joblib"))
joblib.dump(le_disease, os.path.join(ENC_DIR, "labelencoder_disease.joblib"))

# ------------------------
# 10) Scaling numeric features for ML (save scaler)
# ------------------------
numeric_for_scaling = [
    "cases","lag_1","lag_2","lag_3",
    "cases_roll_mean_3","cases_roll_mean_7","cases_roll_mean_14",
    "cases_roll_std_3","cases_roll_std_7","cases_roll_std_14",
    "cases_roll_sum_3","cases_roll_sum_7","cases_roll_sum_14",
    "cases_pct_change_3","cases_last_1yr",
    "temperature","humidity","rainfall",
    "temperature_anom","humidity_anom","rainfall_anom" if "rainfall_anom" in df.columns else "rainfall"
]

# Ensure only existing columns
numeric_for_scaling = [c for c in numeric_for_scaling if c in df.columns]

scaler = MinMaxScaler()
df[numeric_for_scaling] = scaler.fit_transform(df[numeric_for_scaling].fillna(0))
joblib.dump(scaler, os.path.join(ENC_DIR, "minmax_scaler_features.joblib"))

# ------------------------
# 11) Final column ordering & save
# ------------------------
final_cols = [
    "date","district","district_enc","lat","lon","disease","disease_enc",
    "cases","lag_1","lag_2","lag_3",
    "cases_roll_mean_3","cases_roll_mean_7","cases_roll_mean_14",
    "cases_roll_std_3","cases_roll_std_7","cases_roll_std_14",
    "cases_roll_sum_3","cases_roll_sum_7","cases_roll_sum_14",
    "cases_pct_change_3","cases_last_1yr",
    "temperature","humidity","rainfall",
    "temperature_anom","humidity_anom","rainfall_anom" if "rainfall_anom" in df.columns else "rainfall",
    "population_density","sanitation_index",
    "CERS","outbreak_z","outbreak_threshold","season","month","year","dayofweek","is_weekend"
]

# Filter to existing columns and keep order
final_cols = [c for c in final_cols if c in df.columns]
df_final = df[final_cols].copy()

# Save
df_final.to_csv(OUTPUT_CSV, index=False)
print("Feature engineering COMPLETE.")
print("Saved featured dataset to:", os.path.abspath(OUTPUT_CSV))
print("Saved encoders/scalers to folder:", os.path.abspath(ENC_DIR))
print("Rows:", len(df_final))
print(df_final.head(5))
