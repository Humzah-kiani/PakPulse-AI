import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
import lightgbm as lgb
from imblearn.over_sampling import SMOTE

print("\nLoading dataset...")
df = pd.read_csv("pakpulse_250k_featured.csv")
df["cases_next"] = df.groupby(["district", "disease"])["cases"].shift(-1)
df["outbreak_next"] = (df["cases_next"] > 0).astype(int)
df = df.dropna(subset=["cases_next", "outbreak_next"])


# ------------------------------------------------------------
# 1. Clean-up: remove rows missing target
# ------------------------------------------------------------
df = df.dropna(subset=["cases_next", "outbreak_next"])

# ------------------------------------------------------------
# 2. Encode categorical features
# ------------------------------------------------------------
label_cols = ["district", "disease", "season"]
le_dict = {}

for col in label_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    le_dict[col] = le

# ------------------------------------------------------------
# 3. Train-test split (80/20)
# ------------------------------------------------------------
X = df.drop(["cases_next", "outbreak_next"], axis=1)
y_reg = df["cases_next"]
y_cls = df["outbreak_next"]

X_train, X_test, y_reg_train, y_reg_test, y_cls_train, y_cls_test = train_test_split(
    X, y_reg, y_cls, test_size=0.20, random_state=42, shuffle=True
)

print(f"Train rows: {len(X_train)}, Test rows: {len(X_test)}")

# ------------------------------------------------------------
# 4. Scale numeric features
# ------------------------------------------------------------
numeric_feats = ["cases_lag7", "cases_lag14", "cases_lag30", "temp", "humidity"]

scaler = MinMaxScaler()
X_train[numeric_feats] = scaler.fit_transform(X_train[numeric_feats])
X_test[numeric_feats] = scaler.transform(X_test[numeric_feats])

# ------------------------------------------------------------
# 5. REGRESSION MODEL (LightGBM)
# ------------------------------------------------------------
print("\nTraining LightGBM Regression (cases_next)...")

reg_model = lgb.LGBMRegressor(
    boosting_type="gbdt",
    objective="regression",
    learning_rate=0.05,
    n_estimators=500,
    max_depth=-1,
    num_leaves=31
)

reg_model.fit(X_train, y_reg_train)

# Evaluation
reg_pred = reg_model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_reg_test, reg_pred))
mae = mean_absolute_error(y_reg_test, reg_pred)

print(f"Regression RMSE: {rmse:.4f}, MAE: {mae:.4f}")

# ------------------------------------------------------------
# 6. CLASSIFICATION MODEL (Outbreak Prediction)
# ------------------------------------------------------------
print("\nBalancing outbreak classes using SMOTE...")

sm = SMOTE(random_state=42)
X_train_bal, y_cls_train_bal = sm.fit_resample(X_train, y_cls_train)

print("Before SMOTE:", sum(y_cls_train), "/", len(y_cls_train))
print("After SMOTE:", sum(y_cls_train_bal), "/", len(y_cls_train_bal))

print("\nTraining LightGBM Classifier (outbreak_next)...")

cls_model = lgb.LGBMClassifier(
    boosting_type="gbdt",
    objective="binary",
    learning_rate=0.05,
    n_estimators=500,
    max_depth=-1,
    num_leaves=31,
    is_unbalance=True   # Important for rare outbreaks
)

cls_model.fit(X_train_bal, y_cls_train_bal)

# ------------------------------------------------------------
# 7. Classification Evaluation
# ------------------------------------------------------------
print("\nEvaluating classifier...")

y_prob = cls_model.predict_proba(X_test)[:, 1]

# Lower threshold because outbreaks are rare
threshold = 0.20
y_pred = (y_prob > threshold).astype(int)

roc = roc_auc_score(y_cls_test, y_prob)
precision = precision_score(y_cls_test, y_pred, zero_division=0)
recall = recall_score(y_cls_test, y_pred, zero_division=0)
f1 = f1_score(y_cls_test, y_pred, zero_division=0)

print(f"ROC-AUC: {roc:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")

print("\nTraining complete!")
