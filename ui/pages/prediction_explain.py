"""
Prediction Explanation Dashboard with SHAP and LIME
Provides interpretable insights into disease case predictions
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import joblib
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.data_loader import DataLoader
from src.auth import AuthManager
from src.dashboard_styles import PROFESSIONAL_STYLES
from src.risk_calculator import RiskCalculator

# Check authentication
auth = AuthManager()
if not auth.require_auth():
    st.cache_data.clear()
    st.warning("Please login to access this page")
    if "authenticated" in st.session_state:
        st.session_state["authenticated"] = False
    st.stop()

st.set_page_config(
    page_title="Prediction Explainability - PakPulse AI",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(PROFESSIONAL_STYLES, unsafe_allow_html=True)

# Professional styling for explanation dashboard
st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        width: 21rem !important;
        background: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"] [class*="css-"],
    section[data-testid="stSidebar"] [class*="st-"] {
        background: transparent !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #1e293b !important;
    }
    
    .main .block-container {
        background: transparent !important;
        padding: 2rem 2.5rem !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
        font-weight: 600 !important;
    }
    
    h3 {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 2px solid #e2e8f0 !important;
    }
    
    p, li, span {
        color: #475569 !important;
        font-size: 0.9375rem !important;
        line-height: 1.6 !important;
    }
    
    [data-testid="stPlotlyChart"] {
        background: #ffffff !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* Dropdown Menus - White background, black text */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    div[data-baseweb="popover"] > div {
        background-color: #ffffff !important;
    }
    div[data-baseweb="popover"] * {
        color: #000000 !important;
    }
    div[role="listbox"] {
        background-color: #ffffff !important;
    }
    div[role="listbox"] li {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #000000 !important;
        font-size: 0.875rem !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS FOR SHAP AND LIME
# ============================================================================

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

try:
    import lime
    import lime.lime_tabular
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def load_prediction_artifacts():
    """Load trained ML models and scaler"""
    models_dir = os.path.join(parent_dir, "models")
    scaler_path = os.path.join(models_dir, "feature_minmax_scaler.joblib")
    reg_model_path = os.path.join(models_dir, "lgb_reg_cases_next.joblib")
    cls_model_path = os.path.join(models_dir, "lgb_cls_outbreak_next.joblib")
    
    try:
        scaler = joblib.load(scaler_path)
        reg_model = joblib.load(reg_model_path)
        cls_model = joblib.load(cls_model_path)
        return scaler, reg_model, cls_model
    except Exception as e:
        st.error(f"Error loading model artifacts: {e}")
        return None, None, None

def prepare_prediction_features(df, scaler):
    """Prepare features for prediction"""
    df = df.copy()
    
    CANDIDATE_FEATURES = [
        "cases", "lag_1", "lag_2", "lag_3",
        "cases_roll_mean_3", "cases_roll_mean_7", "cases_roll_mean_14",
        "cases_roll_std_3", "cases_roll_std_7", "cases_roll_std_14",
        "temperature", "humidity", "rainfall",
        "population_density", "sanitation_index",
        "district_enc", "disease_enc", "month", "season_enc"
    ]
    
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    
    # Pull cases from either column name
    if "cases" not in df.columns and "cases_reported" in df.columns:
        df["cases"] = df["cases_reported"]
    
    # Derive month from date if available
    if "month" not in df.columns and "date" in df.columns:
        df["month"] = pd.to_datetime(df["date"]).dt.month
    
    # Derive season_enc from month
    if "season_enc" not in df.columns and "month" in df.columns:
        month_val = int(df["month"].iloc[0])
        # 0=winter, 1=spring, 2=summer, 3=autumn
        df["season_enc"] = {12: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1,
                            6: 2, 7: 2, 8: 2, 9: 3, 10: 3, 11: 3}.get(month_val, 0)
    
    # Encode categoricals
    if "district_enc" not in df.columns and "district" in df.columns:
        df["district_enc"] = pd.factorize(df["district"])[0]
    if "disease_enc" not in df.columns and "disease" in df.columns:
        df["disease_enc"] = pd.factorize(df["disease"])[0]
    
    # Create truly missing features with sensible defaults
    for feature in CANDIDATE_FEATURES:
        if feature not in df.columns:
            if feature.startswith("lag_"):
                # Use current cases as lag approximation
                df[feature] = df["cases"].values[0] if "cases" in df.columns else 0
            elif "roll_mean" in feature:
                df[feature] = df["cases"].values[0] if "cases" in df.columns else 0
            elif "roll_std" in feature:
                df[feature] = 0
            elif feature == "temperature":
                df[feature] = 27.0  # Pakistan avg temp
            elif feature == "humidity":
                df[feature] = 55.0
            elif feature == "rainfall":
                df[feature] = 20.0
            elif feature == "population_density":
                df[feature] = 500.0
            elif feature == "sanitation_index":
                df[feature] = 50.0
            elif feature == "month":
                df[feature] = datetime.now().month
            elif feature == "season_enc":
                df[feature] = 0
            elif "enc" in feature:
                df[feature] = 0
            else:
                df[feature] = 0
    
    features = [c for c in CANDIDATE_FEATURES if c in df.columns]
    X = df[features].copy().fillna(0)
    
    # Scale numeric features — handle scaler feature count mismatch gracefully
    try:
        if hasattr(scaler, 'transform'):
            n_scaler_features = scaler.n_features_in_ if hasattr(scaler, 'n_features_in_') else len(features)
            if n_scaler_features == len(features):
                X_scaled = scaler.transform(X)
                X = pd.DataFrame(X_scaled, columns=features, index=df.index)
            else:
                # Scaler trained with different number of features — skip scaling
                pass
    except Exception as e:
        pass  # Use raw features if scaling fails
    
    return X, features


def create_shap_force_plot(model, X_sample, feature_names):
    """Create SHAP force plot explanation"""
    if not SHAP_AVAILABLE:
        return None
    
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_sample)
        
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        # Create feature importance visualization
        fig = go.Figure()
        
        sorted_idx = np.argsort(np.abs(shap_values[0]))[::-1][:10]
        top_features = [feature_names[i] for i in sorted_idx]
        top_values = shap_values[0][sorted_idx]
        
        # Premium color palette: Rose for positive impact (increased risk), Blue for negative
        colors = ['#f43f5e' if v > 0 else '#3b82f6' for v in top_values]
        
        fig.add_trace(go.Bar(
            y=top_features,
            x=top_values,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.5)', width=1)
            ),
            hovertemplate='<b>%{y}</b><br>Impact: %{x:.4f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Top 10 Feature Contributions (SHAP)",
            xaxis_title="SHAP Value (Impact on Prediction)",
            yaxis_title="Features",
            height=400,
            margin=dict(l=150),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(255,255,255,0)',
            font=dict(color='#000000', size=12)
        )
        
        return fig, shap_values[0], top_features
    except Exception as e:
        st.warning(f"SHAP visualization error: {e}")
        return None, None, None

def create_lime_explanation(model, X_sample, X_background, feature_names, class_names=None, mode='regression'):
    """Create LIME local explanation"""
    if not LIME_AVAILABLE:
        return None
    
    try:
        # LIME needs a background dataset to understand the distribution
        explainer = lime.lime_tabular.LimeTabularExplainer(
            X_background.values,
            feature_names=feature_names,
            class_names=class_names or ["Cases"],
            mode=mode,
            discretize_continuous=True
        )
        
        # Predict function wrapper
        if mode == 'classification':
            predict_fn = model.predict_proba
        else:
            predict_fn = model.predict
            
        exp = explainer.explain_instance(
            X_sample.iloc[0].values,
            predict_fn,
            num_features=10
        )
        
        # Extract contributions
        contributions = exp.as_list()
        features_contrib = []
        values_contrib = []
        
        for feat, val in contributions:
            features_contrib.append(feat)
            values_contrib.append(val)
        
        # Premium color palette: Rose for positive impact (increased risk), Blue for negative
        colors = ['#f43f5e' if v > 0 else '#3b82f6' for v in values_contrib]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=features_contrib,
            x=values_contrib,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.5)', width=1)
            ),
            hovertemplate='<b>%{y}</b><br>Contribution: %{x:.4f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Top 10 Feature Contributions (LIME)",
            xaxis_title="Contribution to Prediction",
            yaxis_title="Features",
            height=400,
            margin=dict(l=300),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(255,255,255,0)',
            font=dict(color='#000000', size=12)
        )
        
        return fig, contributions
    except Exception as e:
        st.warning(f"LIME visualization error: {e}")
        return None, None

def _show_feature_importance_fallback(model, feature_names):
    """Show model's built-in feature importance as fallback when SHAP/LIME fail"""
    try:
        importances = model.feature_importances_
        if len(importances) != len(feature_names):
            importances = importances[:len(feature_names)]
        
        sorted_idx = np.argsort(importances)[::-1][:10]
        top_features = [feature_names[i] for i in sorted_idx]
        top_values = importances[sorted_idx]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=top_features,
            x=top_values,
            orientation='h',
            marker=dict(color='#2563eb'),
            hovertemplate='<b>%{y}</b><br>Importance: %{x:.4f}<extra></extra>'
        ))
        fig.update_layout(
            title="Top 10 Feature Importances (Model Built-in)",
            xaxis_title="Importance Score",
            yaxis_title="Features",
            height=400,
            margin=dict(l=150),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(255,255,255,0)',
            font=dict(color='#000000', size=12)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Showing model's built-in feature importances (global, not instance-specific).")
    except Exception as e:
        st.info(f"Feature importance visualization not available: {e}")

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    st.markdown("""
    <h1 style="color: #0f172a; text-align: center; margin-bottom: 1rem;">
        🔍 Prediction Explainability Dashboard
    </h1>
    <p style="color: #475569; text-align: center; margin-bottom: 2rem;">
        Understand why the model makes specific predictions using SHAP and LIME interpretability techniques
    </p>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_shared_disease_data():
    from src.data_loader import load_combined_api_data
    from datetime import datetime
    current_year = datetime.now().year
    return load_combined_api_data(use_csv_dataset=True, start_year=current_year - 1)

def load_data():
    """Load disease data using shared memory cache"""
    return get_shared_disease_data()

def main():
    # Sidebar Search Implementation
    with st.sidebar:
        st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h3 style="color: #1e293b; font-size: 0.9375rem; font-weight: 600; margin: 0 0 0.75rem 0;">Navigation</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Home", use_container_width=True, type="secondary"):
            st.switch_page("app.py")
            
        if st.button("GIS Dashboard", use_container_width=True, type="secondary"):
            st.switch_page("pages/gis_dashboard.py")
            
        if st.button("Risk Dashboard", use_container_width=True, type="secondary"):
            st.switch_page("pages/risk_dashboard.py")
            
        if st.button("Alert System", use_container_width=True, type="secondary"):
            st.switch_page("pages/alert_dashboard.py")
            
        st.markdown("---")
        
        if st.button("Logout", use_container_width=True):
            from src.auth import AuthManager
            auth = AuthManager()
            auth.logout()
            st.rerun()

    # Sidebar configuration
    st.sidebar.markdown("### Configuration")
    
    # Load sample data - use shared memory cache
    try:
        disease_data = load_data()
        if disease_data.empty:
            raise Exception("Empty data")
    except Exception as e1:
        try:
            from src.data_loader import DataLoader
            loader = DataLoader()
            disease_data = loader.load_disease_data()
        except Exception as e2:
            try:
                import os
                csv_path = os.path.join(parent_dir, "pakpulse_250k_realistic.csv")
                disease_data = pd.read_csv(csv_path, nrows=50000)
                # Map columns
                if 'lat' in disease_data.columns:
                    disease_data['latitude'] = disease_data['lat']
                    disease_data['longitude'] = disease_data['lon']
                if 'cases' in disease_data.columns:
                    disease_data['cases_reported'] = disease_data['cases']
                disease_data['date'] = pd.to_datetime(disease_data['date'], errors='coerce')
            except Exception as e3:
                st.error(f"Could not load data: {e3}")
                return
    
    if disease_data.empty:
        st.error("No data available for predictions")
        return
    
    # Select district
    districts = sorted(disease_data['district'].unique())
    selected_district = st.sidebar.selectbox("Select District", districts)
    
    # Select disease
    diseases = sorted(disease_data[disease_data['district'] == selected_district]['disease'].unique())
    selected_disease = st.sidebar.selectbox("Select Disease", diseases)
    
    # Get district-disease data
    data_subset = disease_data[
        (disease_data['district'] == selected_district) &
        (disease_data['disease'] == selected_disease)
    ].sort_values('date').copy()
    
    if data_subset.empty:
        st.warning(f"No data for {selected_disease} in {selected_district}")
        return
    
    # Load models
    scaler, reg_model, cls_model = load_prediction_artifacts()
    
    if scaler is None or reg_model is None or cls_model is None:
        st.error("Models not available. Please train models first.")
        return
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About Interpretability")
    st.sidebar.info("""
    **SHAP (SHapley Additive exPlanations)**
    - Game theory-based approach
    - Shows how each feature contributes to the prediction
    - Provides global and local explanations
    
    **LIME (Local Interpretable Model-agnostic Explanations)**
    - Perturbs input and learns local linear model
    - Explains individual predictions
    - Model-agnostic approach
    """)
    
    # Prepare current data
    current_row = data_subset.iloc[-1:].copy()
    
    # Prepare features
    X, feature_names = prepare_prediction_features(current_row, scaler)
    
    if X.empty or len(feature_names) == 0:
        st.error("Could not prepare prediction features")
        return
    
    # Make predictions
    try:
        # 1. Regression (Case Counts)
        prediction_reg = reg_model.predict(X)[0]
        prediction_reg = max(0, prediction_reg)
        
        # 2. Classification (Outbreak Prob)
        proba_cls = cls_model.predict_proba(X)[0][1]
        
        # Use tuned threshold 0.05
        is_outbreak = proba_cls >= 0.05
        
        # Get actual cases
        if 'cases' in current_row.columns:
            actual_cases = float(current_row['cases'].values[0])
        elif 'cases_reported' in current_row.columns:
            actual_cases = float(current_row['cases_reported'].values[0])
        else:
            actual_cases = 0.0
            
        # Calculate Risk using shared logic
        risk_calc = RiskCalculator()
        # Map outbreak probability to 0-100 scale for Risk Index
        # We align 0.05 (threshold) with 60 (High Risk) so the dashboard indications match
        risk_index = min(100, (proba_cls / 0.05) * 60)
        risk_info = risk_calc.calculate_dri(risk_index, selected_disease)
        
    except Exception as e:
        st.error(f"Prediction error: {e}")
        return
    
    # Selection of which model to explain
    st.markdown("### Explanation Target")
    explanation_target = st.radio(
        "Choose which model to explain:",
        ["📈 Expected Cases (Regression)", "⚠️ Outbreak Probability (Classification)"],
        horizontal=True
    )
    
    # Prepare background data for LIME (sampled from disease_data)
    # We need a representative sample of all districts/diseases
    @st.cache_data
    def get_lime_background(data, _scaler):
        sample_size = min(500, len(data))
        sample_df = data.sample(sample_size, random_state=42)
        X_bg, _ = prepare_prediction_features(sample_df, _scaler)
        return X_bg

    X_background = get_lime_background(disease_data, scaler)

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Predicted Cases", f"{prediction_reg:.0f}", 
                  delta=f"{prediction_reg - actual_cases:+.0f}" if actual_cases > 0 else None)
    
    with col2:
        st.metric("Outbreak Risk", f"{proba_cls*100:.1f}%", 
                  delta="Outbreak Expected" if is_outbreak else "Normal")
    
    with col3:
        st.metric("Risk Level", risk_info["level"])
    
    with col4:
        st.metric("Current Cases", f"{actual_cases:.0f}")
    
    st.markdown("""
    <div style="height: 2px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); margin: 2rem 0;"></div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different explanation methods
    tab1, tab2, tab3 = st.tabs(["📊 SHAP Explanation", "🔬 LIME Explanation", "📈 Feature Details"])
    
    with tab1:
        st.markdown(f"""
        <h3 style="color: #0f172a; margin-top: 0;">
            SHAP Analysis - {explanation_target.split(' ')[1]}
        </h3>
        <p style="color: #475569;">
            SHAP values measure each feature's contribution. 
            <span style="color: #f43f5e; font-weight: bold;">Rose</span> bars increase the risk/count, 
            <span style="color: #3b82f6; font-weight: bold;">Blue</span> bars decrease it.
        </p>
        """, unsafe_allow_html=True)
        
        # Select model based on target
        active_model = reg_model if "Regression" in explanation_target else cls_model
        
        if SHAP_AVAILABLE:
            try:
                shap_fig, shap_vals, top_feats = create_shap_force_plot(active_model, X, feature_names)
                if shap_fig:
                    st.plotly_chart(shap_fig, use_container_width=True)
                    
                    # Add interpretation
                    st.markdown("#### Interpretation:")
                    with st.expander("How to read this visualization"):
                        st.write("""
                        - **Bar length** = magnitude of impact on prediction
                        - **Green** = increases predicted cases
                        - **Red** = decreases predicted cases
                        - **Top features** = most important for this prediction
                        """)
                else:
                    # Fallback: show model feature importance
                    _show_feature_importance_fallback(reg_model, feature_names)
            except Exception as e:
                st.warning(f"SHAP visualization error: {e}")
                _show_feature_importance_fallback(reg_model, feature_names)
        else:
            st.info("SHAP library not installed. Showing model feature importance instead.")
            _show_feature_importance_fallback(reg_model, feature_names)
    
    with tab2:
        st.markdown(f"""
        <h3 style="color: #0f172a; margin-top: 0;">
            LIME Analysis - {explanation_target.split(' ')[1]}
        </h3>
        <p style="color: #475569;">
            LIME fits a local linear model to explain this specific instance.
        </p>
        """, unsafe_allow_html=True)
        
        if LIME_AVAILABLE:
            try:
                lime_mode = 'regression' if "Regression" in explanation_target else 'classification'
                lime_fig, lime_contributions = create_lime_explanation(
                    active_model, X, X_background, feature_names, 
                    class_names=[f"Risk for {selected_disease}"],
                    mode=lime_mode
                )
                if lime_fig:
                    st.plotly_chart(lime_fig, use_container_width=True)
                    
                    st.markdown("#### Interpretation:")
                    with st.expander("How to read this visualization"):
                        st.write("""
                        - Shows local feature impact on this specific prediction
                        - Each feature shows its contribution magnitude
                        - Useful for understanding why this prediction is different
                        - Model-agnostic (works with any model type)
                        """)
                else:
                    _show_feature_importance_fallback(reg_model, feature_names)
            except Exception as e:
                st.warning(f"LIME visualization error: {e}")
                _show_feature_importance_fallback(reg_model, feature_names)
        else:
            st.info("LIME library not installed. Showing model feature importance instead.")
            _show_feature_importance_fallback(reg_model, feature_names)
    
    with tab3:
        st.markdown("""
        <h3 style="color: #0f172a; margin-top: 0;">
            Feature Details
        </h3>
        """, unsafe_allow_html=True)
        
        # Create feature importance dataframe
        feature_df = pd.DataFrame({
            'Feature': feature_names,
            'Value': X.iloc[0].values,
            'Type': ['Temporal' if any(x in feat for x in ['lag', 'roll', 'month']) else 
                    'Environmental' if any(x in feat for x in ['temp', 'humid', 'rain']) else
                    'Demographic' if any(x in feat for x in ['population', 'sanitation']) else
                    'Encoded' for feat in feature_names]
        }).sort_values('Feature')
        
        st.dataframe(feature_df, use_container_width=True, hide_index=True)
        
        # Feature categories
        st.markdown("#### Feature Categories:")
        
        col1, col2, col3 = st.columns(3)
        
        temporal = feature_df[feature_df['Type'] == 'Temporal']
        environmental = feature_df[feature_df['Type'] == 'Environmental']
        demographic = feature_df[feature_df['Type'] == 'Demographic']
        
        with col1:
            st.metric("Temporal Features", len(temporal))
        
        with col2:
            st.metric("Environmental Features", len(environmental))
        
        with col3:
            st.metric("Demographic Features", len(demographic))
    
    # Prediction confidence section
    st.markdown("""
    <div style="height: 2px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); margin: 2rem 0;"></div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <h3 style="color: #0f172a; margin-top: 0;">
        Prediction Summary
    </h3>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info(f"""
        **Prediction Result:** {prediction_reg:.1f} cases predicted for {selected_disease} in {selected_district}
        
        - **Previous Cases:** {actual_cases:.0f}
        - **Change:** {((prediction_reg - actual_cases) / (actual_cases + 1) * 100):.1f}%
        - **Trend:** {'Increasing' if prediction_reg > actual_cases else 'Decreasing' if prediction_reg < actual_cases else 'Stable'}
        """)
    
    with col2:
        # Use synchronized risk level
        st.markdown(f"""
        <div style="
            background: #ffffff;
            border-left: 4px solid {risk_info['color']};
            padding: 1rem;
            border-radius: 8px;
        ">
            <p style="color: #475569; margin: 0; font-size: 0.9rem;"><b>Risk Level</b></p>
            <p style="color: {risk_info['color']}; margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 700;">{risk_info['level']}</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
