
import os
import argparse
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    mean_absolute_percentage_error,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score
)
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    _TK_AVAILABLE = True
except Exception:
    _TK_AVAILABLE = False

HERE = os.path.dirname(__file__)
MODELS_DIR = os.path.join(HERE, "models")
SCALER_PATH = os.path.join(MODELS_DIR, "feature_minmax_scaler.joblib")
REG_MODEL_PATH = os.path.join(MODELS_DIR, "lgb_reg_cases_next.joblib")
CLS_MODEL_PATH = os.path.join(MODELS_DIR, "lgb_cls_outbreak_next.joblib")

# Candidate features used in training (script mirrors training pipeline)
CANDIDATE_FEATURES = [
    "cases","lag_1","lag_2","lag_3",
    "cases_roll_mean_3","cases_roll_mean_7","cases_roll_mean_14",
    "cases_roll_std_3","cases_roll_std_7","cases_roll_std_14",
    "temperature","humidity","rainfall",
    "population_density","sanitation_index",
    "district_enc","disease_enc","month","season"
]

SEASON_MAP = {"winter":0, "spring":1, "autumn":2, "monsoon":3}


def load_artifacts():
    scaler = joblib.load(SCALER_PATH)
    reg = joblib.load(REG_MODEL_PATH)
    clf = joblib.load(CLS_MODEL_PATH)
    return scaler, reg, clf


def prepare_features(df, scaler):

    df = df.copy()

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    else:
        raise ValueError("Input dataframe must contain a 'date' column for time-based features")


    def _group_features(g):
        g = g.sort_values("date")

        for lag in [1, 2, 3]:
            if f"lag_{lag}" not in g.columns:
                g[f"lag_{lag}"] = g["cases"].shift(lag).fillna(0)

        # rolling means and std on previous values (shifted to avoid leakage)
        for w in [3, 7, 14]:
            mean_col = f"cases_roll_mean_{w}"
            std_col = f"cases_roll_std_{w}"
            if mean_col not in g.columns:
                g[mean_col] = g["cases"].shift(1).rolling(window=w, min_periods=1).mean()
            if std_col not in g.columns:
                g[std_col] = g["cases"].shift(1).rolling(window=w, min_periods=1).std().fillna(0)

        return g

    if "district" in df.columns and "disease" in df.columns:

        try:
            df = df.groupby(["district", "disease"], group_keys=False).apply(_group_features, include_groups=False).reset_index(drop=True)
        except TypeError:
  
            df = df.groupby(["district", "disease"], group_keys=False).apply(_group_features).reset_index(drop=True)
    else:

        df = _group_features(df)


    if "month" not in df.columns:
        df["month"] = df["date"].dt.month


    if "season" in df.columns and "season_enc" not in df.columns:
        df["season_enc"] = df["season"].map(SEASON_MAP).fillna(0).astype(int)

    if "district_enc" not in df.columns and "district" in df.columns:
        df["district_enc"] = pd.factorize(df["district"])[0]
    if "disease_enc" not in df.columns and "disease" in df.columns:
        df["disease_enc"] = pd.factorize(df["disease"])[0]


    if "season" in df.columns and "season_enc" not in df.columns:
        df["season_enc"] = df["season"].map(SEASON_MAP).fillna(0).astype(int)
    if "season" in df.columns:
        df = df.drop(columns=["season"])


    if "season_enc" not in df.columns:
        df["season_enc"] = 0


    features = [c for c in CANDIDATE_FEATURES if c in df.columns]
    if "season" in features and "season_enc" in df.columns:
        features[features.index("season")] = "season_enc"

    if "season_enc" in df.columns and "season_enc" not in features:
        features.append("season_enc")


    numeric_feats = [c for c in features if c not in ("district_enc", "disease_enc", "season_enc", "month")]

    numeric_feats = [c for c in numeric_feats if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]


    if len(numeric_feats) > 0:
        df_num = df[numeric_feats].fillna(0)
        try:
            if hasattr(scaler, 'feature_names_in_'):
                expected = [c for c in scaler.feature_names_in_ if c in df_num.columns]
                if expected:
                    transformed = scaler.transform(df_num[expected])
                    df.loc[:, expected] = transformed
                # For numeric_feats not seen by scaler, do per-column min-max
                for c in numeric_feats:
                    if c not in expected:
                        mn = df_num[c].min()
                        mx = df_num[c].max()
                        if pd.isna(mn) or pd.isna(mx) or mx == mn:
                            df[c] = 0
                        else:
                            df[c] = (df_num[c] - mn) / (mx - mn)
            else:

                df.loc[:, numeric_feats] = scaler.transform(df_num)
        except Exception:

            mn = df_num.min()
            mx = df_num.max()
            denom = (mx - mn).replace(0, 1)
            df.loc[:, numeric_feats] = (df_num - mn) / denom

    X = df[features].copy()
    return X, features, df


def _generate_missing_group_rows(df, group_cols=('district', 'disease')):
    """Generate one synthetic next-row per group where the group's last date
    is older than the dataset global latest date. The synthetic row uses the
    group's last-known row and advances the date by the group's median interval
    (or dataset median if unavailable). Lags are shifted appropriately.
    """
    df = df.copy()

    if not all(c in df.columns for c in group_cols):
        if 'district_enc' in df.columns and 'disease_enc' in df.columns:
            group_cols = ('district_enc', 'disease_enc')
        else:
            return df

    df['date'] = pd.to_datetime(df['date'])
    df['date'] = pd.to_datetime(df['date'])
    global_latest = df['date'].max()


    all_diffs = df.sort_values('date').groupby(list(group_cols))['date'].diff().dt.days.dropna()
    if len(all_diffs) > 0:
        global_med = int(max(1, all_diffs.median()))
    else:
        global_med = 1

    synth_rows = []


    for name, g in df.groupby(list(group_cols)):
        last_date = g['date'].max()
        diffs = g.sort_values('date')['date'].diff().dt.days.dropna()
        med = int(max(1, diffs.median())) if len(diffs) > 0 else global_med
        last_row = g.sort_values('date').iloc[-1].copy()
        new_row = last_row.copy()
        new_date = last_date + pd.Timedelta(days=med)
        new_row['date'] = new_date
        if 'cases' in last_row.index:
            new_row['lag_1'] = float(last_row.get('cases', 0))
        if 'lag_1' in last_row.index:
            new_row['lag_2'] = float(last_row.get('lag_1', 0))
        if 'lag_2' in last_row.index:
            new_row['lag_3'] = float(last_row.get('lag_2', 0))
        new_row['month'] = new_date.month
        if 'season_enc' in df.columns:
            if new_date.month in (12, 1, 2):
                new_row['season_enc'] = 0
            elif new_date.month in (3, 4, 5):
                new_row['season_enc'] = 1
            elif new_date.month in (6, 7, 8):
                new_row['season_enc'] = 3
            else:
                new_row['season_enc'] = 2
        synth_rows.append(new_row)


    districts = df['district'].unique() if 'district' in df.columns else []
    diseases = df['disease'].unique() if 'disease' in df.columns else []
    existing_pairs = set(tuple(x) for x in df[list(group_cols)].drop_duplicates().values)
    for d in districts:
        for dis in diseases:
            if (d, dis) in existing_pairs:
                continue

            district_rows = df[df['district'] == d]
            if len(district_rows) > 0:
                template = district_rows.sort_values('date').iloc[-1].copy()
            else:
                template = df.sort_values('date').iloc[-1].copy()

            new_row = template.copy()

            new_row['disease'] = dis

            new_date = global_latest + pd.Timedelta(days=global_med)
            new_row['date'] = new_date

            if 'cases' in template.index:
                new_row['lag_1'] = float(template.get('cases', 0))
            if 'lag_1' in template.index:
                new_row['lag_2'] = float(template.get('lag_1', 0))
            if 'lag_2' in template.index:
                new_row['lag_3'] = float(template.get('lag_2', 0))
            new_row['month'] = new_date.month
            if 'season_enc' in df.columns:
                if new_date.month in (12, 1, 2):
                    new_row['season_enc'] = 0
                elif new_date.month in (3, 4, 5):
                    new_row['season_enc'] = 1
                elif new_date.month in (6, 7, 8):
                    new_row['season_enc'] = 3
                else:
                    new_row['season_enc'] = 2
            synth_rows.append(new_row)

    if synth_rows:
        df = pd.concat([df, pd.DataFrame(synth_rows)], ignore_index=True, axis=0)
    return df


def predict_from_dataframe(df, scaler, reg, clf):
    """
    Apply feature engineering and run both regression and classification models
    on the input dataframe.
    
    Args:
        df: Input DataFrame
        scaler: Loaded MinMaxScaler
        reg: Loaded regression model
        clf: Loaded classification model
        
    Returns:
        DataFrame with added prediction columns: 
        pred_cases_next, pred_outbreak_proba, pred_outbreak
    """
    X, features, df_processed = prepare_features(df, scaler)
    
    # Run regression
    df_processed['pred_cases_next'] = reg.predict(X)
    
    # Run classification
    df_processed['pred_outbreak_proba'] = clf.predict_proba(X)[:, 1]
    
    # Use the optimized threshold of 0.05 for real-world outbreak detection
    # This was tuned for optimal F1-score (~0.74)
    OUTBREAK_THRESHOLD = 0.05
    df_processed['pred_outbreak'] = (df_processed['pred_outbreak_proba'] >= OUTBREAK_THRESHOLD).astype(int)
    
    return df_processed
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Input CSV file with features")
    parser.add_argument("--output", help="Output CSV to write predictions to")
    parser.add_argument("--no-fill-missing", action='store_true', help="Disable automatic generation of missing district×disease rows")
    parser.add_argument("--print-head", type=int, help="Print head N rows of predictions and exit")
    parser.add_argument("--single", help="Single JSON record to predict, e.g. '{\"cases\":1, ...}'")
    args = parser.parse_args()

    if not os.path.exists(SCALER_PATH) or not os.path.exists(REG_MODEL_PATH) or not os.path.exists(CLS_MODEL_PATH):
        raise FileNotFoundError("One or more model artifacts not found in models/. Run training pipeline first.")

    scaler, reg, clf = load_artifacts()

    if args.single:
        record = json.loads(args.single)
        df = pd.DataFrame([record])
        preds = predict_from_dataframe(df, scaler, reg, clf)
        print(preds.to_csv(index=False))
        return


    if not args.input:
        if _TK_AVAILABLE:
            root = tk.Tk()
            root.withdraw()
            input_path = filedialog.askopenfilename(
                title='Select input CSV',
                filetypes=[('CSV files', '*.csv'), ('All files', '*.*')]
            )
            if not input_path:
                print('No input file selected. Exiting.')
                return
            args.input = input_path

            default_out = os.path.join(MODELS_DIR, 'predictions_on_train.csv')
            output_path = filedialog.asksaveasfilename(
                title='Save predictions as',
                defaultextension='.csv',
                initialfile='predictions_on_train.csv',
                initialdir=MODELS_DIR,
                filetypes=[('CSV files', '*.csv'), ('All files', '*.*')]
            )
            if not output_path:
                output_path = default_out
            args.output = output_path
            root.destroy()
        else:
            parser.print_help()
            return

    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Input file not found: {args.input}")

    df_in = pd.read_csv(args.input)

    fill_missing = not args.no_fill_missing
    if fill_missing:
        try:
            df_in = _generate_missing_group_rows(df_in)
            print(f"Augmented input with synthetic rows; new shape: {df_in.shape}")
        except Exception as e:
            print(f"Warning: could not generate synthetic rows: {e}")
    preds = predict_from_dataframe(df_in, scaler, reg, clf)

    if args.output:
        preds.to_csv(args.output, index=False)
        print(f"Wrote predictions to {args.output}")


    if 'cases_next' not in preds.columns and 'cases' in preds.columns:
        if 'district' in preds.columns and 'disease' in preds.columns:
            grp = ['district', 'disease']
        elif 'district_enc' in preds.columns and 'disease_enc' in preds.columns:
            grp = ['district_enc', 'disease_enc']
        else:
            grp = None
        if grp is not None:
            preds['cases_next'] = preds.groupby(grp)['cases'].shift(-1).fillna(0).astype(float)


    if 'outbreak_next' not in preds.columns:

        if 'district' in preds.columns and 'disease' in preds.columns:
            grp = ['district', 'disease']
        elif 'district_enc' in preds.columns and 'disease_enc' in preds.columns:
            grp = ['district_enc', 'disease_enc']
        else:
            grp = None

        if 'outbreak_z' in preds.columns and grp is not None:
            preds['outbreak_next'] = preds.groupby(grp)['outbreak_z'].shift(-1).fillna(0).astype(int)
        elif 'disease' in preds.columns and 'cases' in preds.columns and grp is not None:
            disease95 = preds.groupby('disease')['cases'].quantile(0.95).to_dict()
            preds['outbreak_next'] = preds.apply(lambda r: int((r['cases'] >= disease95.get(r['disease'], 0))), axis=1)
            preds['outbreak_next'] = preds.groupby(grp)['outbreak_next'].shift(-1).fillna(0).astype(int)


    metrics = {}
    try:
        if 'cases_next' in preds.columns:
            y_true_reg = preds['cases_next'].astype(float)
            y_pred_reg = preds['pred_cases_next'].astype(float)
            metrics['regression'] = {
                'rmse': float(mean_squared_error(y_true_reg, y_pred_reg, squared=False)),
                'mae': float(mean_absolute_error(y_true_reg, y_pred_reg)),
                'mape': float(mean_absolute_percentage_error(y_true_reg, y_pred_reg))
            }
            print('\nRegression metrics:')
            print(f"RMSE: {metrics['regression']['rmse']:.4f}, MAE: {metrics['regression']['mae']:.4f}, MAPE: {metrics['regression']['mape']:.4f}")

        if 'outbreak_next' in preds.columns:
            y_true_clf = preds['outbreak_next'].astype(int)
            y_proba = preds['pred_outbreak_proba'].astype(float)
            y_pred_clf = preds['pred_outbreak'].astype(int)
            clf_metrics = {}

            try:
                if len(y_true_clf.unique()) > 1:
                    clf_metrics['roc_auc'] = float(roc_auc_score(y_true_clf, y_proba))
                else:
                    clf_metrics['roc_auc'] = None
            except Exception:
                clf_metrics['roc_auc'] = None

            clf_metrics.update({
                'precision': float(precision_score(y_true_clf, y_pred_clf, zero_division=0)),
                'recall': float(recall_score(y_true_clf, y_pred_clf, zero_division=0)),
                'f1': float(f1_score(y_true_clf, y_pred_clf, zero_division=0)),
                'accuracy': float(accuracy_score(y_true_clf, y_pred_clf))
            })
            metrics['classification'] = clf_metrics
            print('\nClassification metrics:')
            print(f"ROC-AUC: {clf_metrics.get('roc_auc')}, Precision: {clf_metrics['precision']:.4f}, Recall: {clf_metrics['recall']:.4f}, F1: {clf_metrics['f1']:.4f}, Accuracy: {clf_metrics['accuracy']:.4f}")

        # Save metrics JSON into models folder
        if metrics:
            import json as _json
            metrics_path = os.path.join(MODELS_DIR, 'prediction_metrics.json')
            with open(metrics_path, 'w') as mf:
                _json.dump(metrics, mf, indent=2)
            print(f"Saved metrics to {metrics_path}")
    except Exception as e:
        print(f"Warning: could not compute metrics: {e}")

    if args.print_head:
        print(preds.head(args.print_head).to_string(index=False))
    else:
        print(preds.head(10).to_string(index=False))


if __name__ == '__main__':
    main()
