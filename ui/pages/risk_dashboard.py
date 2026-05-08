"""
Risk Dashboard Page
Demonstrates Risk Index Display Components
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
from src.data_loader import DataLoader
from src.risk_calculator import RiskCalculator
from src.risk_display import RiskDisplay
from src.auth import AuthManager

# Check authentication
auth = AuthManager()
if not auth.require_auth():
    # Clear cache and redirect to login
    st.cache_data.clear()
    st.warning("Please login to access this page")
    # Force redirect by clearing session
    if "authenticated" in st.session_state:
        st.session_state["authenticated"] = False
    st.stop()

st.set_page_config(
    page_title="Risk Dashboard - PakPulse AI",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add professional styling
from src.dashboard_styles import PROFESSIONAL_STYLES
st.markdown(PROFESSIONAL_STYLES, unsafe_allow_html=True)

# Enhanced Professional Styling for Risk Dashboard
st.markdown("""
<style>
    /* Ensure sidebar is visible with light professional background */
    section[data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        width: 21rem !important;
        background: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    
    /* Sidebar content styling - transparent to show gradient */
    section[data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"] [class*="css-"],
    section[data-testid="stSidebar"] [class*="st-"] {
        background: transparent !important;
    }
    
    /* Light background */
    section[data-testid="stSidebar"] {
        background: #ffffff !important;
    }
    
    /* Professional Color Scheme - All Text Visible */
    :root {
        --primary-blue: #1d4ed8;
        --primary-blue-light: #2563eb;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #64748b;
        --bg-white: #ffffff;
        --bg-light: #f8fafc;
        --border-color: #e2e8f0;
    }
    
    /* Main Content Area - Professional Background */
    .main .block-container {
        background: transparent !important;
        padding: 2rem 2.5rem !important;
    }
    
    /* All Headings - Dark, Visible Text */
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
        font-weight: 600 !important;
    }
    
    /* Section Headings - Professional Styling */
    h3 {
        color: #0f172a !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 2px solid #e2e8f0 !important;
    }
    
    h4 {
        color: #1e293b !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    /* All Paragraph Text - Visible */
    p, li, span {
        color: #475569 !important;
        font-size: 0.9375rem !important;
        line-height: 1.6 !important;
    }
    
    /* Breadcrumb Links */
    a {
        color: #2563eb !important;
        text-decoration: none !important;
    }
    
    a:hover {
        color: #2563eb !important;
        text-decoration: underline !important;
    }
    
    /* Info Boxes - Professional with Visible Text */
    .stInfo, .stSuccess, .stWarning, .stError {
        border-radius: 12px !important;
        padding: 1.25rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    .stInfo {
        background: #ffffff !important;
        border-left: 4px solid #2563eb !important;
    }
    
    .stInfo p, .stInfo strong {
        color: #1e293b !important;
    }
    
    .stWarning {
        background: #ffffff !important;
        border-left: 4px solid #f59e0b !important;
    }
    
    .stWarning p, .stWarning strong {
        color: #1e293b !important;
    }
    
    .stError {
        background: #ffffff !important;
        border-left: 4px solid #ef4444 !important;
    }
    
    .stError p, .stError strong {
        color: #1e293b !important;
    }
    
    /* Dividers - Professional */
    hr {
        border: none !important;
        border-top: 2px solid #e2e8f0 !important;
        margin: 2rem 0 !important;
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

    /* Metrics - Visible Text */
    [data-testid="stMetricValue"] {
        color: #000000 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #000000 !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #000000 !important;
        font-size: 0.875rem !important;
    }
    
    /* Dataframes - Professional Styling */
    .dataframe {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }
    
    .dataframe th {
        background: transparent !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #e2e8f0 !important;
    }
    
    .dataframe td {
        color: #475569 !important;
        border-bottom: 1px solid #f1f5f9 !important;
    }
    
    /* Expanders - Professional */
    .streamlit-expanderHeader {
        background: #ffffff !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
    }
    
    .streamlit-expanderContent {
        background: #ffffff !important;
        color: #475569 !important;
        border: 1px solid #e2e8f0 !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        padding: 1rem !important;
    }
    
    /* Captions - Visible */
    .stCaption {
        color: #64748b !important;
        font-size: 0.8125rem !important;
    }
    
    /* Code Blocks - Professional */
    .stCodeBlock {
        background: transparent !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        color: #0f172a !important;
    }
    
    /* Selectbox Labels - Visible */
    label {
        color: #0f172a !important;
        font-weight: 600 !important;
        font-size: 0.9375rem !important;
    }
    
    /* Sidebar Text - All Visible */
    section[data-testid="stSidebar"] * {
        color: #1e293b !important;
    }
    
    section[data-testid="stSidebar"] h3 {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    
    section[data-testid="stSidebar"] p {
        color: #475569 !important;
    }
    
    /* Sidebar buttons - light background friendly */
    section[data-testid="stSidebar"] .stButton > button {
        background: #ffffff !important;
        color: #475569 !important;
        border: 1px solid #cbd5e1 !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #f1f5f9 !important;
        color: #1e293b !important;
        border-color: #94a3b8 !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: #2563eb !important;
        color: #ffffff !important;
    }
    
    /* Professional Cards Background */
    .element-container {
        background: transparent !important;
    }
    
    /* Chart Containers - White Background */
    [data-testid="stPlotlyChart"] {
        background: #ffffff !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
        border: 1px solid #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize components
# List of all diseases (synchronized with GIS Dashboard and DataLoader)
def get_synchronized_diseases():
    """Get all diseases from DataLoader and combine with standard list"""
    try:
        from src.data_loader import DataLoader
        loader = DataLoader()
        return loader.get_all_diseases()
    except:
        return [
            'Dengue', 'Malaria', 'COVID-19', 'Influenza', 'Cholera',
            'Typhoid', 'Hepatitis-A', 'Hepatitis-E', 'Measles', 'Mumps',
            'Tuberculosis', 'Pneumonia', 'Whooping-Cough', 'Polio', 'Rotavirus',
            'Diarrhea', 'Food-Poisoning', 'Skin-Infection', 'Eye-Infection', 'Heatstroke'
        ]

ALL_DISEASES = get_synchronized_diseases()

@st.cache_resource  # Sub-second memory-resident cache
def get_shared_disease_data():
    """Shared across all pages for instant loading"""
    from src.data_loader import load_combined_api_data
    from datetime import datetime
    current_year = datetime.now().year
    return load_combined_api_data(use_csv_dataset=True, start_year=current_year - 1)

def load_data():
    """Load disease data using the shared memory cache"""
    try:
        data = get_shared_disease_data()
    except Exception as e:
        # If load fails, data will be empty - handle it below
        data = pd.DataFrame()
    
    if not data.empty and 'date' in data.columns:
        data['date'] = pd.to_datetime(data['date'])
        # Keep only last 30 days for faster processing
        cutoff_date = datetime.now() - timedelta(days=30)
        data = data[data['date'] >= cutoff_date]
        data = data.sort_values('date')
        data['is_prediction'] = False
        
        # Add 14-day projections
        if len(data) > 0:
            try:
                # Get latest values per district-disease
                latest_data = data.sort_values('date').groupby(['district', 'disease']).tail(1).reset_index(drop=True)
                
                # Create 14-day projections
                pred_list = []
                for i in range(1, 15):
                    pred_date = datetime.now() + timedelta(days=i)
                    pred_rows = latest_data.copy()
                    pred_rows['date'] = pd.Timestamp(pred_date)
                    
                    # Simple trend: add small random variation
                    trend_factor = 1 + (i / 14) * 0.1 + np.random.randn(len(pred_rows)) * 0.05
                    pred_rows['risk_index'] = (pred_rows['risk_index'] * trend_factor).clip(0, 100)
                    if 'cases_reported' in pred_rows.columns:
                        pred_rows['cases_reported'] = (pred_rows['cases_reported'] * trend_factor).astype(int).clip(0)
                    
                    pred_rows['is_prediction'] = True
                    pred_list.append(pred_rows)
                
                predictions_data = pd.concat(pred_list, ignore_index=True)
                
                # Combine historical and predictions
                combined_data = pd.concat([data, predictions_data], ignore_index=True)
                combined_data = combined_data.sort_values('date')
                
                # Normalize disease names to Title Case for consistency
                if 'disease' in combined_data.columns:
                    combined_data['disease'] = combined_data['disease'].str.strip().str.title()
                    # Fix special cases
                    combined_data['disease'] = combined_data['disease'].replace({
                        'Covid-19': 'COVID-19',
                        'Covid19': 'COVID-19'
                    })
                
                return combined_data
                
            except Exception as e:
                print(f"\n CSV loading failed: {str(e).encode('ascii', 'ignore').decode('ascii')}")
                return data
    
    # Fallback: Generate sample data with proper structure
    print("Loading fallback sample data...")
    
    sample_data = []
    diseases = ALL_DISEASES  # Use the global list
    
    try:
        loader = DataLoader(use_api=False, use_who=False)
        districts_meta = loader.load_districts_metadata()
    except:
        # If districts_meta fails, use 50 major Pakistan districts
        districts_data = [
            {'district': 'Karachi', 'latitude': 24.8607, 'longitude': 67.0011},
            {'district': 'Lahore', 'latitude': 31.5497, 'longitude': 74.3436},
            {'district': 'Islamabad', 'latitude': 33.6844, 'longitude': 73.0479},
            {'district': 'Quetta', 'latitude': 30.1798, 'longitude': 66.9750},
            {'district': 'Peshawar', 'latitude': 34.0151, 'longitude': 71.5249},
            {'district': 'Multan', 'latitude': 30.1575, 'longitude': 71.4454},
            {'district': 'Faisalabad', 'latitude': 31.4180, 'longitude': 72.3679},
            {'district': 'Rawalpindi', 'latitude': 33.5794, 'longitude': 73.1306},
            {'district': 'Gujranwala', 'latitude': 32.1759, 'longitude': 74.1855},
            {'district': 'Hyderabad', 'latitude': 25.3548, 'longitude': 68.3405},
            {'district': 'Sukkar', 'latitude': 27.7071, 'longitude': 68.8736},
            {'district': 'Sialkot', 'latitude': 32.4945, 'longitude': 74.5229},
            {'district': 'Sargodha', 'latitude': 32.0856, 'longitude': 72.6439},
            {'district': 'Abbottabad', 'latitude': 34.1496, 'longitude': 73.2108},
            {'district': 'Mardan', 'latitude': 34.1992, 'longitude': 72.0458},
            {'district': 'Swat', 'latitude': 34.7652, 'longitude': 72.3521},
            {'district': 'Dir', 'latitude': 35.2000, 'longitude': 71.8500},
            {'district': 'Chitral', 'latitude': 35.8500, 'longitude': 71.8000},
            {'district': 'Gilgit', 'latitude': 35.9280, 'longitude': 74.3114},
            {'district': 'Skardu', 'latitude': 35.2854, 'longitude': 75.5735},
            {'district': 'Jhang', 'latitude': 31.2732, 'longitude': 72.3179},
            {'district': 'Gujrat', 'latitude': 32.5833, 'longitude': 74.0833},
            {'district': 'Mianwali', 'latitude': 32.5833, 'longitude': 71.5667},
            {'district': 'Attock', 'latitude': 33.7667, 'longitude': 72.7333},
            {'district': 'Chakwal', 'latitude': 32.9333, 'longitude': 72.8500},
            {'district': 'Jhelum', 'latitude': 32.9333, 'longitude': 73.7333},
            {'district': 'Mirpur', 'latitude': 33.1429, 'longitude': 73.7286},
            {'district': 'Muzaffarabad', 'latitude': 34.3667, 'longitude': 73.4833},
            {'district': 'Bahawalpur', 'latitude': 29.3958, 'longitude': 71.6858},
            {'district': 'Okara', 'latitude': 30.8069, 'longitude': 73.4532},
            {'district': 'Sahiwal', 'latitude': 30.6722, 'longitude': 73.1047},
            {'district': 'Kasur', 'latitude': 31.1179, 'longitude': 74.4371},
            {'district': 'Sheikhupura', 'latitude': 31.7185, 'longitude': 73.9740},
            {'district': 'Nankana Sahib', 'latitude': 31.8743, 'longitude': 73.6692},
            {'district': 'Hafizabad', 'latitude': 32.1833, 'longitude': 73.6667},
            {'district': 'Wazirabad', 'latitude': 32.3333, 'longitude': 74.2000},
            {'district': 'Chiniot', 'latitude': 31.7333, 'longitude': 72.9833},
            {'district': 'Toba Tek Singh', 'latitude': 30.9833, 'longitude': 72.4667},
            {'district': 'Khanewal', 'latitude': 30.3030, 'longitude': 71.9360},
            {'district': 'Lodhran', 'latitude': 29.5436, 'longitude': 71.6282},
            {'district': 'Dera Ismail Khan', 'latitude': 31.8453, 'longitude': 70.9029},
            {'district': 'Bannu', 'latitude': 32.9833, 'longitude': 70.6333},
            {'district': 'Kohat', 'latitude': 33.5833, 'longitude': 71.4333},
            {'district': 'Karak', 'latitude': 33.1167, 'longitude': 71.1000},
            {'district': 'Tank', 'latitude': 32.7333, 'longitude': 70.3667},
            {'district': 'Larkana', 'latitude': 27.5649, 'longitude': 68.2075},
            {'district': 'Jacobabad', 'latitude': 28.2667, 'longitude': 68.4333},
            {'district': 'Shikarpur', 'latitude': 27.9500, 'longitude': 68.6333},
            {'district': 'Khairpur', 'latitude': 27.5333, 'longitude': 68.7667},
            {'district': 'Narowal', 'latitude': 32.1167, 'longitude': 74.8833},
        ]
        districts_meta = pd.DataFrame(districts_data)
    
    # Generate 30 days of historical data + 14-day predictions
    for _, district_row in districts_meta.iterrows():
        district = district_row.get('district', 'Unknown')
        lat = district_row.get('latitude', 30.3753)
        lon = district_row.get('longitude', 69.3451)
        
        for disease in diseases:
            # Historical data - last 30 days
            for days_ago in range(30, 0, -1):
                date = datetime.now() - timedelta(days=days_ago)
                risk_index = 30 + (hash(f"{district}{disease}") % 40)
                cases = int(risk_index * np.random.uniform(1, 3))
                
                sample_data.append({
                    'district': district,
                    'latitude': lat,
                    'longitude': lon,
                    'disease': disease,
                    'risk_index': float(risk_index),
                    'date': pd.Timestamp(date),
                    'cases_reported': cases,
                    'population': 500000,
                    'is_prediction': False
                })
            
            # Predictions - next 14 days
            for days_ahead in range(1, 15):
                date = datetime.now() + timedelta(days=days_ahead)
                trend = 1 + (days_ahead / 14) * 0.15
                risk_index = 30 + (hash(f"{district}{disease}") % 40)
                risk_index = min(100, risk_index * trend + np.random.randn() * 5)
                cases = int(max(0, risk_index * np.random.uniform(1, 3)))
                
                sample_data.append({
                    'district': district,
                    'latitude': lat,
                    'longitude': lon,
                    'disease': disease,
                    'risk_index': max(0, min(100, risk_index)),
                    'date': pd.Timestamp(date),
                    'cases_reported': cases,
                    'population': 500000,
                    'is_prediction': True
                })
    
    result = pd.DataFrame(sample_data)
    result = result.sort_values('date')
    
    print(f"[SUCCESS] Sample data created: {len(result):,} records")
    return result

def get_districts_from_data(disease_data):
    """Get all districts from the loaded disease data"""
    if disease_data.empty or 'district' not in disease_data.columns:
        # Fallback to DataLoader if no data
        loader = DataLoader()
        return loader.get_all_districts()
    return sorted(disease_data['district'].unique().tolist())

def get_diseases_from_data(disease_data):
    """Get all diseases - ensured to return 20 from global list"""
    return ALL_DISEASES

def main():
    # Sidebar Navigation
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
        
        if st.button("Risk Dashboard", use_container_width=True, type="primary"):
            pass  # Already on this page
        
        # Alert System - Only visible to Admin and Officer
        user_role = st.session_state.get('user_role', 'viewer')
        if user_role in ['admin', 'officer']:
            if st.button("Alert System", use_container_width=True, type="secondary"):
                st.switch_page("pages/alert_dashboard.py")
        
        st.markdown("---")
        
        if st.button("Logout", use_container_width=True):
            auth.logout()
            st.rerun()
        
        st.markdown("---")
    
    # Professional Header with Gradient
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #eff6ff 0%, #dfe8ff 100%);
        color: #1e293b;
        padding: 2rem 2.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
        margin-bottom: 2rem;
        border: 1px solid #bfdbfe;
    ">
        <h1 style="margin: 0; color: #1d4ed8; font-size: 2rem; font-weight: 700;">Risk Index Dashboard</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.125rem; color: #475569; font-weight: 500;">Disease Risk Index (DRI) and Composite Health Risk Score</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Breadcrumb navigation - Professional Styling
    st.markdown("""
    <div style="margin-bottom: 1.5rem; padding: 0.75rem 1rem; background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0;">
        <span style="color: #64748b; font-size: 0.875rem;">
            <a href="/" style="color: #2563eb; text-decoration: none;">Home</a> 
            <span style="color: #cbd5e1; margin: 0 0.5rem;">›</span> 
            <span style="color: #1e293b; font-weight: 600;">Risk Dashboard</span>
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    try:
        disease_data = load_data()
        
        # Initialize display components
        display = RiskDisplay()
        calculator = RiskCalculator()
        loader = DataLoader()
        
        # Sidebar filters
        st.sidebar.header("Filters")
        
        # Data type selection - Historical vs Prediction
        data_type = st.sidebar.selectbox(
            "📊 Data Type",
            options=["Historical Data", "Predictions (Next 14 Days)", "Combined (Historical + Predictions)"],
            index=0
        )
        
        # Apply data type filter to the disease_data
        filtered_data = disease_data.copy()
        
        # Ensure is_prediction column exists
        if 'is_prediction' not in filtered_data.columns:
            filtered_data['is_prediction'] = False
        
        # Apply data type filter
        if data_type == "Historical Data":
            filtered_data = filtered_data[filtered_data['is_prediction'] == False]
        elif data_type == "Predictions (Next 14 Days)":
            filtered_data = filtered_data[filtered_data['is_prediction'] == True]
        # else: Combined - use all data
        
        # Get districts and diseases from filtered data
        districts = get_districts_from_data(filtered_data)
        all_diseases = get_diseases_from_data(filtered_data)
        
        selected_district = st.sidebar.selectbox(
            "Select District",
            options=districts,
            index=0
        )
        
        # Use all diseases from the loaded data (no filtering)
        filtered_diseases = all_diseases
        
        selected_disease = st.sidebar.selectbox(
            "Select Disease (for individual view)",
            options=["All"] + sorted(filtered_diseases),
            index=0
        )
        
        # Date filter (Synchronized with GIS Dashboard)
        latest_date_cap = filtered_data['date'].max() if not filtered_data.empty else pd.Timestamp.now()
        earliest_date_cap = filtered_data['date'].min() if not filtered_data.empty else pd.Timestamp.now()
        
        selected_date = st.sidebar.date_input(
            "Select Date for Risk Status",
            value=latest_date_cap if data_type != "Predictions (Next 14 Days)" else pd.Timestamp.now().date(),
            min_value=earliest_date_cap.date(),
            max_value=latest_date_cap.date()
        )
        
        # Get latest data for selected district and SELECTED DATE from FILTERED disease_data
        if not filtered_data.empty and 'district' in filtered_data.columns:
            # Filter by district
            district_data = filtered_data[filtered_data['district'] == selected_district].copy()
            
            if not district_data.empty and 'date' in district_data.columns:
                # Filter by selected date (handling both timestamp and date)
                mask = district_data['date'].dt.date == selected_date
                latest_data = district_data[mask].copy()
                
                # If no data for exactly that date, show the closest date up to that date
                if latest_data.empty:
                    past_data = district_data[district_data['date'].dt.date <= selected_date]
                    if not past_data.empty:
                        latest_date_found = past_data['date'].max()
                        latest_data = district_data[district_data['date'] == latest_date_found].copy()
                    else:
                        # Fallback to latest available
                        latest_date_found = district_data['date'].max()
                        latest_data = district_data[district_data['date'] == latest_date_found].copy()
            else:
                latest_data = district_data.copy()
        else:
            # Fallback to loader method
            latest_data = loader.get_latest_risk_data(district=selected_district)
        
        # Validate data structure
        if not latest_data.empty:
            required_cols = ['disease', 'risk_index', 'date']
            missing_cols = [col for col in required_cols if col not in latest_data.columns]
            if missing_cols:
                st.error(f"**Data format error:** Missing required columns: {missing_cols}")
                st.info(f"**Available columns:** {list(latest_data.columns)}")
                st.info("**To fix this:** Ensure data loading functions return data with 'disease', 'risk_index', and 'date' columns")
                with st.expander("Debug Information"):
                    st.write("**Data shape:**", latest_data.shape)
                    st.write("**Sample data:**")
                    st.dataframe(latest_data.head() if not latest_data.empty else pd.DataFrame())
                return
        
        # Ensure all diseases from dataset are included, even if no data for this district
        # Create default entries for diseases without data - CASE INSENSITIVE CHECK
        diseases_in_data = {d.lower(): d for d in latest_data['disease'].unique()} if not latest_data.empty and 'disease' in latest_data.columns else {}
        
        # Add missing diseases with default values
        for disease in filtered_diseases:
            if disease.lower() not in diseases_in_data:
                # Create default row for disease without data
                default_row = pd.DataFrame([{
                    'district': selected_district,
                    'disease': disease,
                    'date': latest_date if 'latest_date' in locals() and latest_date else pd.Timestamp.now(),
                    'cases_reported': 0,
                    'risk_index': 0.0,
                    'source': 'No data available'
                }])
                latest_data = pd.concat([latest_data, default_row], ignore_index=True)
        
        if latest_data.empty:
            st.warning(f"No data available for {selected_district}")
            return
        
        # Calculate composite score (only from diseases with actual data)
        diseases_with_data = latest_data[latest_data['risk_index'] > 0]
        if not diseases_with_data.empty:
            composite = calculator.calculate_composite_health_risk_score(diseases_with_data)
        else:
            # Default composite if no data
            composite = {
                'composite_score': 0.0,
                'risk_level': 'No Data',
                'disease_count': 0,
                'recommendation': 'No data available for risk assessment',
                'breakdown': {}
            }
        
        # Ensure breakdown includes ALL diseases from dataset
        if 'breakdown' not in composite:
            composite['breakdown'] = {}
        
        # Add diseases without data to breakdown
        for disease in filtered_diseases:
            if disease not in composite['breakdown']:
                disease_data_filtered = latest_data[latest_data['disease'] == disease]
                if not disease_data_filtered.empty:
                    risk_index = disease_data_filtered.iloc[0]['risk_index']
                else:
                    risk_index = 0.0
                composite['breakdown'][disease] = {
                    'risk_index': risk_index,
                    'contribution': 0.0
                }
        
        # Update disease count to show all diseases from dataset
        composite['disease_count'] = len(filtered_diseases)
        
        # Display composite score in a professional card
        st.markdown("""
        <div style="
            background: #ffffff;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
            margin-bottom: 2rem;
        ">
        """, unsafe_allow_html=True)
        display.display_composite_score_card(composite)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Professional Divider
        st.markdown("""
        <div style="height: 2px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); margin: 2rem 0;"></div>
        """, unsafe_allow_html=True)
        
        # Display individual disease risks - Professional grid layout
        st.markdown("""
        <h3 style="
            color: #0f172a !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            margin-top: 0 !important;
            margin-bottom: 1.5rem !important;
            padding-bottom: 0.75rem !important;
            border-bottom: 2px solid #e2e8f0 !important;
        ">Individual Disease Risk Indices</h3>
        """, unsafe_allow_html=True)
        
        if selected_disease == "All":
            # Show all diseases from dataset in a professional grid layout
            # Sort by risk index (highest first)
            disease_risk_pairs = []
            for disease in sorted(filtered_diseases):
                disease_data_filtered = latest_data[latest_data['disease'] == disease]
                if not disease_data_filtered.empty:
                    risk_index = disease_data_filtered.iloc[0]['risk_index']
                else:
                    risk_index = 0.0
                disease_risk_pairs.append((disease, risk_index))
            
            # Sort by risk index (highest first)
            disease_risk_pairs.sort(key=lambda x: x[1], reverse=True)
            
            # Display in a 4-column grid
            num_cols = 4
            for row_start in range(0, len(disease_risk_pairs), num_cols):
                cols = st.columns(num_cols)
                row_diseases = disease_risk_pairs[row_start:row_start + num_cols]
                
                for col_idx, (disease, risk_index) in enumerate(row_diseases):
                    with cols[col_idx]:
                        display.display_disease_risk_card(disease, risk_index)
        else:
            # Show selected disease in a single column
            disease_data_filtered = latest_data[latest_data['disease'] == selected_disease]
            if not disease_data_filtered.empty:
                risk_index = disease_data_filtered.iloc[0]['risk_index']
            else:
                risk_index = 0.0
            display.display_disease_risk_card(selected_disease, risk_index)
        
        # Professional Divider
        st.markdown("""
        <div style="height: 2px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); margin: 2rem 0;"></div>
        """, unsafe_allow_html=True)
        
        # Charts section - Professional Styling
        st.markdown("""
        <h3 style="
            color: #0f172a !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            margin-top: 0 !important;
            margin-bottom: 1.5rem !important;
            padding-bottom: 0.75rem !important;
            border-bottom: 2px solid #e2e8f0 !important;
        ">Risk Visualizations</h3>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="
                background: #ffffff;
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border: 1px solid #e2e8f0;
                margin-bottom: 1rem;
            ">
                <h4 style="color: #1e293b; font-size: 1.25rem; font-weight: 600; margin-top: 0; margin-bottom: 1rem;">Risk Index Comparison</h4>
            </div>
            """, unsafe_allow_html=True)
            display.display_risk_chart(latest_data, chart_type="bar")
        
        with col2:
            st.markdown("""
            <div style="
                background: #ffffff;
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border: 1px solid #e2e8f0;
                margin-bottom: 1rem;
            ">
                <h4 style="color: #1e293b; font-size: 1.25rem; font-weight: 600; margin-top: 0; margin-bottom: 1rem;">Risk Gauge</h4>
            </div>
            """, unsafe_allow_html=True)
            display.display_risk_gauge(composite['composite_score'], 
                                      f"{selected_district} Composite Risk")
        
        # District summary - Professional Styling
        st.markdown("""
        <div style="height: 2px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); margin: 2rem 0;"></div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <h3 style="
            color: #0f172a !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            margin-top: 0 !important;
            margin-bottom: 1.5rem !important;
            padding-bottom: 0.75rem !important;
            border-bottom: 2px solid #e2e8f0 !important;
        ">District Risk Summary</h3>
        """, unsafe_allow_html=True)
        try:
            # Validate data before calculating summary
            if latest_data.empty:
                st.warning(f"No data available for {selected_district}")
            elif 'disease' not in latest_data.columns:
                st.error("**Data format error:** Missing 'disease' column in latest_data")
                st.info(f"**Available columns:** {list(latest_data.columns)}")
            else:
                summary = calculator.calculate_district_risk_summary(latest_data)
                display.display_district_risk_summary(summary)
        except KeyError as e:
            st.error(f"**Error calculating summary:** Missing column {str(e)}")
            st.info(f"**Available columns in latest_data:** {list(latest_data.columns)}")
            with st.expander("Debug Information"):
                st.write("**latest_data shape:**", latest_data.shape)
                st.write("**latest_data sample:**")
                st.dataframe(latest_data.head() if not latest_data.empty else pd.DataFrame())
        except Exception as e:
            st.error(f"**Error calculating summary:** {str(e)}")
            import traceback
            with st.expander("Technical Details"):
                st.code(traceback.format_exc())
        
        # Risk table - Professional Styling
        st.markdown("""
        <div style="height: 2px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); margin: 2rem 0;"></div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <h3 style="
            color: #0f172a !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            margin-top: 0 !important;
            margin-bottom: 1.5rem !important;
            padding-bottom: 0.75rem !important;
            border-bottom: 2px solid #e2e8f0 !important;
        ">Detailed Risk Data</h3>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="
            background: #ffffff;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
        ">
        """, unsafe_allow_html=True)
        display.display_risk_table(latest_data)
        st.markdown("</div>", unsafe_allow_html=True)
        
    except KeyError as e:
        error_msg = str(e)
        st.error(f"**Data format error:** Missing required column: {error_msg}")
        st.info("**Troubleshooting:**\n- Ensure data files have all required columns: district, disease, date, risk_index\n- Check that `districts_metadata.csv` exists in the `data/` directory\n- Verify data format matches expected structure")
        
        with st.expander("Technical Details"):
            st.code(f"KeyError: {error_msg}")
            try:
                disease_data = load_data()
                if not disease_data.empty:
                    st.write("**Available columns in loaded data:**")
                    st.write(list(disease_data.columns))
                    st.write("**Data sample:**")
                    st.dataframe(disease_data.head())
            except:
                pass
    except Exception as e:
        error_msg = str(e)
        st.error(f"**Error loading data:** {error_msg}")
        st.info("**Troubleshooting:**\n- Ensure data files exist in the `data/` directory\n- Run `python utils/generate_mock_data.py` to generate sample data\n- Check file permissions\n- Verify data has required columns: district, disease, date, risk_index")
        
        with st.expander("Technical Details"):
            import traceback
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()

