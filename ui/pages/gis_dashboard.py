"""
GIS Visualization Dashboard Page
Interactive maps showing disease PREDICTIONS by district
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
from streamlit_folium import st_folium
from datetime import datetime, timedelta
from src.data_loader import DataLoader
from src.gis_map import GISMap
from src.auth import AuthManager

# Check authentication
auth = AuthManager()
if not auth.require_auth():
    st.cache_data.clear()
    st.warning("Please login to access this page")
    if "authenticated" in st.session_state:
        st.session_state["authenticated"] = False
    st.stop()

st.set_page_config(
    page_title="GIS Dashboard - PakPulse AI",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add professional styling
from src.dashboard_styles import PROFESSIONAL_STYLES
st.markdown(PROFESSIONAL_STYLES, unsafe_allow_html=True)

# Enhanced Professional Styling for GIS Dashboard
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
    
    /* Sidebar text - ensure visibility */
    section[data-testid="stSidebar"] * {
        color: #1e293b !important;
    }
    
    /* Sidebar links and navigation - professional styling */
    section[data-testid="stSidebar"] a {
        color: #2563eb !important;
    }
    
    section[data-testid="stSidebar"] a:hover {
        color: #2563eb !important;
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
    
    /* All Paragraph Text - Visible */
    p, li, span {
        color: #475569 !important;
        font-size: 0.9375rem !important;
        line-height: 1.6 !important;
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
        color: #000000 !important;
    }
    
    /* Metrics / Indicator Boxes Text */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] {
        color: #000000 !important;
    }
    
    /* Map Containers - Professional */
    [data-testid="stPlotlyChart"], 
    [data-testid="stFoliumMap"] {
        background: #ffffff !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
        border: 1px solid #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

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
                # If projection fails, just return historical data
                return data
    
    # Fallback: Generate sample data with proper structure
    print("Loading fallback sample data...")
    try:
        from src.data_loader import DataLoader
        loader = DataLoader()
        diseases = loader.get_all_diseases()
    except:
        diseases = [
            'Dengue', 'Malaria', 'COVID-19', 'Influenza', 'Cholera',
            'Typhoid', 'Hepatitis-A', 'Hepatitis-E', 'Measles', 'Mumps',
            'Tuberculosis', 'Pneumonia', 'Whooping-Cough', 'Polio', 'Rotavirus',
            'Diarrhea', 'Food-Poisoning', 'Skin-Infection', 'Eye-Infection', 'Heatstroke'
        ]
    
    try:
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
    
    sample_data = []
    
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
    """Get all diseases from the loaded disease data - ensured to return 20"""
    # Always return full list of 20 diseases to ensure UI consistency
    from src.data_loader import DataLoader
    loader = DataLoader()
    return loader.get_all_diseases()

def main():
    # Professional Header - Light Theme
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
        <h1 style="margin: 0; color: #1d4ed8; font-size: 2rem; font-weight: 700;">GIS Visualization Dashboard</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.125rem; color: #475569; font-weight: 500;">Interactive Disease Risk Mapping and Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Professional Breadcrumb
    st.markdown("""
    <div style="margin-bottom: 1.5rem; padding: 0.75rem 1rem; background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0;">
        <span style="color: #64748b; font-size: 0.875rem;">
            <a href="/" style="color: #2563eb; text-decoration: none;">Home</a> 
            <span style="color: #cbd5e1; margin: 0 0.5rem;">›</span> 
            <span style="color: #1e293b; font-weight: 600;">GIS Dashboard</span>
        </span>
    </div>
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
    ">Interactive Disease Risk Maps by District</h3>
    """, unsafe_allow_html=True)
    
    # Load data
    try:
        disease_data = load_data()
        
        # Validate data structure
        if disease_data.empty:
            st.error("**No disease data available**")
            st.warning("Unable to load data from APIs or generate sample data.")
            st.info("**To fix this:**\n- Check that `districts_metadata.csv` exists in the `data/` directory\n- Verify API connections in `src/unified_api_data_fetcher.py`\n- Ensure data files have the correct format")
            with st.expander("Troubleshooting"):
                st.markdown("""
                1. **Check data directory**: Ensure `data/districts_metadata.csv` exists
                2. **Check API configuration**: Verify API keys in `.env` file (if using APIs)
                3. **Check file format**: Data files should have columns: district, latitude, longitude, disease, risk_index, date, cases_reported
                4. **Check internet connection**: Map tiles require internet access
                """)
            return
        
        # Check for required columns - CRITICAL: All map functions require these
        required_columns = ['district', 'disease', 'date', 'latitude', 'longitude', 'risk_index']
        missing_columns = [col for col in required_columns if col not in disease_data.columns]
        
        if missing_columns:
            st.error(f"**Critical Data Format Error:** Missing required columns: {missing_columns}")
            st.warning(f"**Available columns in loaded data:** {list(disease_data.columns)}")
            st.info("**Required columns:** district, disease, date, latitude, longitude, risk_index")
            st.info("**To fix this:**\n- Check that data loading functions return data with all required columns\n- Verify `convert_to_pakpulse_format()` includes 'district' and 'disease' columns\n- Ensure sample data generation includes all required columns")
            
            with st.expander("Debug Information"):
                st.write("**Data shape:**", disease_data.shape)
                st.write("**Data types:**")
                st.write(disease_data.dtypes)
                if not disease_data.empty:
                    st.write("**Sample data (first 5 rows):**")
                    st.dataframe(disease_data.head())
                    st.write("**Column details:**")
                    for col in disease_data.columns:
                        st.write(f"- {col}: {disease_data[col].dtype}")
            return
        
        # Get districts and diseases directly from loaded data
        districts = get_districts_from_data(disease_data)
        diseases = get_diseases_from_data(disease_data)
        
        # Initialize GIS map
        gis = GISMap()
        
        # Sidebar Navigation
        with st.sidebar:
            st.markdown("""
            <div style="margin-bottom: 1.5rem;">
                <h3 style="color: #1e293b; font-size: 0.9375rem; font-weight: 600; margin: 0 0 0.75rem 0;">Navigation</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Home", use_container_width=True, type="secondary"):
                st.switch_page("app.py")
            
            if st.button("GIS Dashboard", use_container_width=True, type="primary"):
                pass  # Already on this page
            
            if st.button("Risk Dashboard", use_container_width=True, type="secondary"):
                st.switch_page("pages/risk_dashboard.py")
            
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
        
        # Sidebar filters
        st.sidebar.header("🔧 Map Controls")
        
        st.sidebar.markdown("---")
        
        st.sidebar.header("🎯 Map Filters")
        
        # Map type selection
        map_type = st.sidebar.radio(
            "Map Type",
            ["Risk Heatmap", "District Markers"],
            index=0
        )
        
        # Data type selection - Historical vs Prediction
        data_type = st.sidebar.selectbox(
            "📊 Data Type",
            options=["Historical Data", "Predictions (Next 14 Days)", "Combined (Historical + Predictions)"],
            index=0
        )
        
        # Disease filter
        selected_disease = st.sidebar.selectbox(
            "Select Disease",
            options=["All"] + sorted(diseases),
            index=0
        )
        
        # Date filter
        latest_date = disease_data['date'].max()
        earliest_date = disease_data['date'].min()
        selected_date = st.sidebar.date_input(
            "Select Date",
            value=latest_date,
            min_value=earliest_date,
            max_value=latest_date
        )
        
        # District filter
        selected_district = st.sidebar.selectbox(
            "Filter by District (Optional)",
            options=["All"] + sorted(districts),
            index=0
        )
        
        # Multi-disease selection
        if map_type == "District Markers":
            st.sidebar.write("Select filters above to customize the map")
        
        st.markdown("---")
        
        # Create and display map based on selection
        if map_type == "Risk Heatmap":
            st.markdown("""
            <h3 style="
                color: #0f172a !important;
                font-size: 1.5rem !important;
                font-weight: 700 !important;
                margin-top: 0 !important;
                margin-bottom: 1.5rem !important;
                padding-bottom: 0.75rem !important;
                border-bottom: 2px solid #e2e8f0 !important;
            ">Disease Risk Heatmap</h3>
            """, unsafe_allow_html=True)
            st.info("Heat intensity represents disease risk level. Red areas indicate higher risk.")
            
            # Filter data - show ALL diseases when "All" is selected
            filtered_data = disease_data.copy()
            
            # Ensure is_prediction column exists
            if 'is_prediction' not in filtered_data.columns:
                filtered_data['is_prediction'] = False
            
            # Apply data type filter (Historical vs Prediction)
            if data_type == "Historical Data":
                filtered_data = filtered_data[filtered_data['is_prediction'] == False]
            elif data_type == "Predictions (Next 14 Days)":
                filtered_data = filtered_data[filtered_data['is_prediction'] == True]
            # else: Combined - use all data
            
            # Date filter - use closest date if exact match not found
            date_filtered = filtered_data[
                (filtered_data['date'].dt.date <= selected_date)
            ]
            if not date_filtered.empty:
                # Get closest date to selected
                date_filtered = date_filtered[
                    date_filtered['date'].dt.date == date_filtered['date'].dt.date.max()
                ]
                filtered_data = date_filtered
            else:
                # Fallback to latest available date
                filtered_data = filtered_data[
                    filtered_data['date'] == filtered_data['date'].max()
                ]
            
            # Disease filter - if "All", show all diseases (don't filter)
            if selected_disease != "All":
                filtered_data = filtered_data[filtered_data['disease'] == selected_disease]
            
            # Check if we have data
            if filtered_data.empty:
                st.warning("No data available for the selected filters. Showing all available data.")
                filtered_data = disease_data.copy()
                if selected_disease != "All":
                    filtered_data = filtered_data[filtered_data['disease'] == selected_disease]
                filtered_data = filtered_data[
                    filtered_data['date'] == filtered_data['date'].max()
                ]
            
            # Create heatmap - pass None for disease_filter when showing all
            map_obj = gis.create_risk_heatmap(
                filtered_data,
                disease_filter=None if selected_disease == "All" else selected_disease,
                date_filter=None  # Already filtered above
            )
            map_obj = gis.add_risk_legend(map_obj)
            
        elif map_type == "District Markers":
            st.markdown("""
            <h4 style="
                color: #1e293b !important;
                font-size: 1.25rem !important;
                font-weight: 600 !important;
                margin-top: 1.5rem !important;
                margin-bottom: 1rem !important;
            ">📍 District Risk Markers</h4>
            """, unsafe_allow_html=True)
            st.info("Click on markers to see detailed risk information for each district.")
            
            # Filter data - IMPORTANT: Filter by disease FIRST
            if selected_disease != "All":
                filtered_data = disease_data[disease_data['disease'] == selected_disease].copy()
            else:
                filtered_data = disease_data.copy()            
            # Ensure is_prediction column exists
            if 'is_prediction' not in filtered_data.columns:
                filtered_data['is_prediction'] = False
            
            # Apply data type filter (Historical vs Prediction)
            if data_type == "Historical Data":
                filtered_data = filtered_data[filtered_data['is_prediction'] == False]
            elif data_type == "Predictions (Next 14 Days)":
                filtered_data = filtered_data[filtered_data['is_prediction'] == True]
            # else: Combined - use all data            
            # Date filter - use closest date
            if not filtered_data.empty:
                date_filtered = filtered_data[
                    (filtered_data['date'].dt.date <= selected_date)
                ]
                if not date_filtered.empty:
                    date_filtered = date_filtered[
                        date_filtered['date'].dt.date == date_filtered['date'].dt.date.max()
                    ]
                    filtered_data = date_filtered
                else:
                    filtered_data = filtered_data[
                        filtered_data['date'] == filtered_data['date'].max()
                    ]
            
            # Check if we have data
            if filtered_data.empty:
                st.warning(f"No data available for {selected_disease if selected_disease != 'All' else 'selected filters'}. Showing all available data.")
                filtered_data = disease_data.copy()
                if selected_disease != "All":
                    filtered_data = filtered_data[filtered_data['disease'] == selected_disease]
                if not filtered_data.empty:
                    filtered_data = filtered_data[
                        filtered_data['date'] == filtered_data['date'].max()
                    ]
            
            # Debug: Show what data is being displayed
            if selected_disease != "All" and not filtered_data.empty:
                st.caption(f"Showing {len(filtered_data)} records for {selected_disease}")
                with st.expander("View Data Being Displayed"):
                    st.dataframe(filtered_data[['disease', 'district', 'cases_reported', 'risk_index', 'date']].head(10))
            
            # Create base map
            map_obj = gis.create_base_map()
            map_obj = gis.add_district_markers(
                map_obj,
                filtered_data,
                disease_filter=selected_disease if selected_disease != "All" else None
            )
            map_obj = gis.add_risk_legend(map_obj)
        
        # Display map - ensure it always shows
        if map_obj is not None:
            try:
                # Show data info
                if not filtered_data.empty:
                    st.caption(f"📊 Map Data: {len(filtered_data)} records, {filtered_data['district'].nunique()} districts, {filtered_data['disease'].nunique()} diseases")
                
                # Display the map using the more efficient st_folium component
                from streamlit_folium import st_folium
                st_folium(map_obj, width=1200, height=600, returned_objects=[])
            except Exception as e:
                st.error(f"Error displaying map: {str(e)}")
                import traceback
                with st.expander("Debug Information"):
                    st.code(traceback.format_exc())
        else:
            st.error("Map could not be created. Please check your data and selections.")
        
        # Statistics
        st.markdown("---")
        st.markdown("""
        <h3 style="
            color: #0f172a !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            margin-top: 0 !important;
            margin-bottom: 1.5rem !important;
            padding-bottom: 0.75rem !important;
            border-bottom: 2px solid #e2e8f0 !important;
        ">Map Statistics</h3>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Districts Shown", len(filtered_data['district'].unique()))
        
        with col2:
            if map_type == "Multi-Disease View":
                diseases_count = len(selected_diseases)
            elif selected_disease == "All":
                # Show all available diseases
                diseases_count = len(filtered_data['disease'].unique())
            else:
                diseases_count = 1
            st.metric("Diseases", diseases_count)
        
        with col3:
            avg_risk = filtered_data['risk_index'].mean()
            st.metric("Average Risk", f"{avg_risk:.1f}")
        
        with col4:
            max_risk = filtered_data['risk_index'].max()
            st.metric("Highest Risk", f"{max_risk:.1f}")
        
    except KeyError as e:
        error_msg = str(e)
        st.error(f"**Data format error:** Missing required column: {error_msg}")
        st.info("**Troubleshooting:**\n- Ensure data files have all required columns: district, disease, date, latitude, longitude, risk_index\n- Check that `districts_metadata.csv` exists in the `data/` directory\n- Verify data format matches expected structure")
        
        with st.expander("Technical Details"):
            st.code(f"KeyError: {error_msg}")
            try:
                disease_data = load_data()
                if not disease_data.empty:
                    st.write("**Available columns in data:**")
                    st.write(list(disease_data.columns))
            except:
                pass
    except Exception as e:
        error_msg = str(e)
        st.error(f"**Error loading map:** {error_msg}")
        st.info("**Troubleshooting:**\n- Ensure data files exist in the `data/` directory\n- Check that `disease_risk_data.csv` and `districts_metadata.csv` are present\n- Verify internet connection for map tiles\n- Check that data has required columns: district, disease, date, latitude, longitude, risk_index")
        
        with st.expander("Technical Details"):
            import traceback
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()

