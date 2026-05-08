"""
PakPulse AI - Multi-Disease Early Warning System
Main Streamlit Application Entry Point
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load env variables so DB and APIs can authenticate
load_dotenv()

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.data_loader import DataLoader
from src.auth import AuthManager, show_welcome_page

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["user_role"] = None
    st.session_state["user_name"] = None

# Page configuration (only if authenticated)
st.set_page_config(
    page_title="PakPulseAI - Disease Early Warning System",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add professional styling
from src.dashboard_styles import PROFESSIONAL_STYLES
st.markdown(PROFESSIONAL_STYLES, unsafe_allow_html=True)

@st.cache_resource  # sub-second memory-resident cache
def get_shared_disease_data():
    """Shared across all pages for instant loading"""
    from src.data_loader import load_combined_api_data
    from datetime import datetime
    current_year = datetime.now().year
    return load_combined_api_data(use_csv_dataset=True, start_year=current_year - 1)

def load_disease_data():
    """Load disease data using the ultra-fast memory cache"""
    return get_shared_disease_data()

@st.cache_data
def load_districts_metadata():
    """Load districts metadata (cached for performance)"""
    loader = DataLoader()
    return loader.get_all_districts()

def main():
    """Main application function"""
    # Add sidebar-specific styling
    st.markdown("""
    <style>
    /* Sidebar Search Styling */
    .sidebar-search {
        margin-bottom: 1.5rem;
    }
    
    /* Search input styling */
    div[data-testid="stTextInput"] input {
        border-radius: 6px;
        border: 1px solid #e2e8f0;
        padding: 0.5rem 0.75rem;
        font-size: 0.875rem;
        background: #ffffff;
    }
    
    div[data-testid="stTextInput"] input:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
    }
    
    .sidebar-search-suggestions {
        margin-top: 0.5rem;
        padding-left: 0;
    }
    
    .sidebar-search-suggestions p {
        color: #cbd5e1;
        font-size: 0.8125rem;
        margin: 0.25rem 0;
        cursor: pointer;
        padding: 0.25rem 0;
        border-radius: 4px;
        transition: color 0.2s;
        font-weight: 400;
    }
    
    .sidebar-search-suggestions p:hover {
        color: #ffffff;
    }
    
    /* Sidebar Branding */
    .sidebar-branding {
        margin-bottom: 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .sidebar-branding h2 {
        color: #1e293b !important;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0 0 0.25rem 0;
        line-height: 1.2;
    }
    
    .sidebar-branding p {
        color: #475569 !important;
        font-size: 0.875rem;
        margin: 0;
        font-weight: 400;
    }
    
    /* User Information Section */
    .sidebar-user-info {
        margin-bottom: 0.25rem;
        margin-top: 0;
        padding-top: 0.5rem;
    }
    
    .sidebar-user-info h3 {
        color: #1e293b !important;
        font-size: 0.9375rem;
        font-weight: 600;
        margin: 0 0 0.75rem 0;
        text-transform: none;
        letter-spacing: 0;
    }
    
    .sidebar-user-info p {
        color: #1e293b !important;
        font-size: 0.875rem;
        margin: 0.5rem 0;
        line-height: 1.5;
    }
    
    /* Navigation Section */
    .sidebar-navigation {
        margin-bottom: 1.5rem;
        margin-top: 0.25rem;
    }
    
    .sidebar-navigation h3 {
        color: #1e293b !important;
        font-size: 0.9375rem;
        font-weight: 600;
        margin: 0 0 0.75rem 0;
        text-transform: none;
        letter-spacing: 0;
    }
    
    /* Navigation Button Styling */
    .nav-button {
        width: 100%;
        padding: 0.625rem 1rem;
        margin: 0.375rem 0;
        border-radius: 6px;
        border: none;
        background: transparent;
        color: #475569;
        font-size: 0.9375rem;
        font-weight: 500;
        text-align: left;
        cursor: pointer;
        transition: all 0.2s ease;
        font-family: 'Inter', sans-serif;
    }
    
    .nav-button:hover {
        background-color: #f1f5f9;
        color: #0f172a;
    }
    
    .nav-button.active {
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
        color: white;
        font-weight: 600;
    }
    
    /* Primary button styling - lighter, more vibrant blue for better visibility */
    .stButton > button[kind="primary"] {
        background: #2563eb !important; /* Bright, vibrant blue - clearly visible */
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.3) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #2563eb !important; /* Slightly darker on hover */
        color: white !important;
        box-shadow: 0 4px 8px rgba(37, 99, 235, 0.4) !important;
    }
    
    /* Secondary button styling - white with light blue border */
    .stButton > button[kind="secondary"] {
        background: #ffffff !important;
        color: #475569 !important;
        border: 1px solid #cbd5e1 !important; /* Light blue-gray border */
        font-weight: 500 !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #f8fafc !important;
        color: #1e293b !important;
        border-color: #94a3b8 !important;
    }
    
    /* Ensure sidebar buttons have proper styling */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #2563eb !important;
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background: #ffffff !important;
        color: #475569 !important;
        border: 1px solid #cbd5e1 !important;
    }
    
    /* Sidebar overall styling - Light professional background - Ensure it's always visible */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%) !important;
        padding: 1.5rem 1rem;
        border-right: 1px solid #e2e8f0 !important;
        display: block !important;
        visibility: visible !important;
    }
    
    /* Sidebar content - transparent to show gradient */
    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }
    
    /* Override any dark theme defaults */
    section[data-testid="stSidebar"] [class*="css-"] {
        background: transparent !important;
    }
    
    /* Ensure sidebar is not collapsed */
    section[data-testid="stSidebar"] > div {
        display: block !important;
        background: transparent !important;
    }
    
    /* Show sidebar toggle button */
    button[data-testid="baseButton-header"] {
        display: block !important;
    }
    
    /* Main content area - Transparent so theme background shows */
    .main {
        background: transparent !important;
    }
    
    div[data-testid="stAppViewContainer"] {
        background: transparent !important;
    }
    
    div[data-testid="stAppViewContainer"] > div:first-child {
        background: transparent !important;
    }
    
    /* Remove any white containers */
    div[data-testid="stAppViewContainer"] > div > div {
        background: transparent !important;
    }
    
    /* Ensure main content wrapper is transparent */
    [data-testid="stAppViewContainer"] > div[class*="main"] {
        background: transparent !important;
    }
    
    /* Remove white backgrounds from content blocks */
    .block-container {
        background: transparent !important;
        padding: 1.5rem 2rem !important;
    }
    
    /* Remove all white backgrounds from main content */
    .main .element-container {
        background: transparent !important;
    }
    
    /* Section headings - Dark grey/black text */
    .main h3 {
        color: #1e293b !important;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Text in main content area - Dark grey */
    .main p, .main li {
        color: #475569 !important;
    }
    
    /* Info boxes - white background on light grey */
    .stInfo {
        background: #ffffff !important;
        border-left: 4px solid #2563eb !important;
        border-radius: 8px !important;
        padding: 1rem 1.25rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* Remove divider line styling */
    .main hr {
        border-color: #e2e8f0 !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Metrics styling - ensure they're visible on light background */
    [data-testid="stMetricValue"] {
        color: #000000 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #000000 !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
    }
    
    .streamlit-expanderContent {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
    }
    
    /* Sidebar text color - dark on light background */
    section[data-testid="stSidebar"] * {
        color: #1e293b !important;
    }
    
    /* Override specific elements that need different colors */
    section[data-testid="stSidebar"] .sidebar-search-suggestions p {
        color: #64748b !important; /* Grey for suggestions */
    }
    
    section[data-testid="stSidebar"] .sidebar-search-suggestions p:hover {
        color: #2563eb !important; /* Light blue on hover */
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
    
    /* Search input on white background */
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] input {
        background: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
    }
    
    /* Branding text - dark */
    section[data-testid="stSidebar"] .sidebar-branding h2,
    section[data-testid="stSidebar"] .sidebar-branding p {
        color: #1e293b !important;
    }
    
    /* User info text - dark */
    section[data-testid="stSidebar"] .sidebar-user-info h3,
    section[data-testid="stSidebar"] .sidebar-user-info p {
        color: #1e293b !important;
    }
    
    /* Navigation heading - dark */
    section[data-testid="stSidebar"] .sidebar-navigation h3 {
        color: #1e293b !important;
    }
    
    /* Divider lines - grey on white background */
    section[data-testid="stSidebar"] hr {
        border-color: #e2e8f0 !important;
    }
    
    /* Primary button (active) - Light blue background with white text */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #3b82f6 !important; /* Light blue */
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(96, 165, 250, 0.3) !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: #2563eb !important; /* Slightly darker blue on hover */
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(96, 165, 250, 0.4) !important;
    }
    
    /* Secondary button (inactive) - Light blue border with light blue text */
    section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background: #ffffff !important;
        color: #3b82f6 !important; /* Light blue text */
        border: 1px solid #3b82f6 !important; /* Light blue border */
        font-weight: 500 !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background: #eff6ff !important; /* Very light blue background on hover */
        color: #2563eb !important; /* Darker blue text on hover */
        border-color: #2563eb !important;
    }
    
    section[data-testid="stSidebar"] .stButton {
        margin-bottom: 0.5rem;
    }
    
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        padding: 0.85rem 1.2rem;
        border-radius: 8px;
        transition: all 0.2s ease;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        text-transform: capitalize !important;
        letter-spacing: 0.5px;
    }
    
    /* Hide default Streamlit sidebar elements if needed */
    .sidebar .stMarkdown {
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Ensure sidebar is expanded and visible
    st.markdown("""
    <style>
    /* Force sidebar to be visible and expanded with clear background */
    section[data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: 21rem !important;
        min-width: 21rem !important;
        background: #ffffff !important;
    }
    
    /* Show sidebar content with transparent background */
    section[data-testid="stSidebar"] > div {
        display: block !important;
        visibility: visible !important;
        width: 100% !important;
        background: transparent !important;
    }
    
    /* Override any Streamlit dark theme classes */
    section[data-testid="stSidebar"] [class*="css-"],
    section[data-testid="stSidebar"] [class*="st-"],
    section[data-testid="stSidebar"] div {
        background: transparent !important;
    }
    
    /* Ensure sidebar is not collapsed */
    section[data-testid="stSidebar"][aria-expanded="false"] {
        display: block !important;
        width: 21rem !important;
    }
    
    /* Show sidebar toggle button */
    button[kind="header"] {
        display: block !important;
    }
    
    /* Make sure sidebar content is visible */
    section[data-testid="stSidebar"] .element-container {
        display: block !important;
        visibility: visible !important;
    }
    </style>
    <script>
    // Force sidebar to be visible on page load
    window.addEventListener('load', function() {
        const sidebar = document.querySelector('section[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.style.display = 'block';
            sidebar.style.visibility = 'visible';
            sidebar.style.width = '21rem';
            sidebar.setAttribute('aria-expanded', 'true');
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Sidebar with branding, user info, and navigation
    with st.sidebar:
        # SVG Logo (scaled for sidebar)
        sidebar_logo_svg = '<svg width="60" height="60" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M50 8 V92 M8 50 H92" stroke="#1d4ed8" stroke-width="1.5" stroke-dasharray="3 3" /><path d="M25 25 L75 75 M25 75 L75 25" stroke="#3b82f6" stroke-width="1.2" stroke-dasharray="2 3" /><rect x="36" y="15" width="28" height="70" rx="3" fill="none" stroke="#1d4ed8" stroke-width="3" /><rect x="15" y="36" width="70" height="28" rx="3" fill="none" stroke="#1d4ed8" stroke-width="3" /><rect x="37.5" y="37.5" width="25" height="25" fill="#eff6ff" /><circle cx="50" cy="50" r="10" fill="#ffffff" stroke="#2563eb" stroke-width="2.5" /><path d="M45 45 L55 55 M45 55 L55 45" stroke="#2563eb" stroke-width="1.5" /><circle cx="50" cy="15" r="3.5" fill="#1e40af" /><circle cx="50" cy="85" r="3.5" fill="#1e40af" /><circle cx="15" cy="50" r="3.5" fill="#1e40af" /><circle cx="85" cy="50" r="3.5" fill="#1e40af" /><circle cx="36" cy="36" r="3.5" fill="#2563eb" /><circle cx="64" cy="64" r="3.5" fill="#2563eb" /><circle cx="36" cy="64" r="3.5" fill="#2563eb" /><circle cx="64" cy="36" r="3.5" fill="#2563eb" /></svg>'

        # Beautiful unified styling for the top branding section
        st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 0.5rem 0 1rem 0; text-align: center;">
            <div style="width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, #e0f2fe 0%, #bfdbfe 100%); margin-bottom: 0.8rem; box-shadow: 0 4px 10px rgba(37,99,235,0.15);">
                {sidebar_logo_svg}
            </div>
            <h2 style="color: #1e293b; font-size: 1.4rem; font-weight: 700; margin: 0; letter-spacing: -0.5px;">PakPulse.AI</h2>
            <p style="color: #475569; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.5px; margin-top: 2px;">EARLY WARNING SYSTEM</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User details elegantly formatted
        user_name = st.session_state.get('user_name', 'Unknown')
        user_role = st.session_state.get('user_role', 'viewer').title()
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%); padding: 0.8rem; border-radius: 10px; border: 1px solid #bfdbfe; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 1rem; box-shadow: 0 2px 5px rgba(37,99,235,0.05);">
            <div style="width: 40px; height: 40px; border-radius: 50%; background: #2563eb; color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.2rem; min-width: 40px;">
                {user_name[0].upper() if user_name else 'U'}
            </div>
            <div style="display: flex; flex-direction: column;">
                <span style="color: #1e293b; font-weight: 600; font-size: 0.95rem; line-height: 1.2;">{user_name}</span>
                <span style="color: #2563eb; font-size: 0.75rem; font-weight: 500; text-transform: uppercase; margin-top: 2px;">
                    <span style="display: inline-block; width: 6px; height: 6px; background: #10b981; border-radius: 50%; margin-right: 4px;"></span>
                    {user_role}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Professional Navigation Section
        st.markdown("""
        <div class="sidebar-navigation">
            <h3 style="color: #1e293b !important; font-size: 0.9375rem; font-weight: 600; margin: 0 0 0.75rem 0; text-transform: uppercase; letter-spacing: 0.05em;">Navigation</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Detect current page based on script path
        try:
            import os
            script_path = os.path.basename(__file__)
            if script_path == "app.py" or script_path == "Home.py":
                current_page = "Home"
            else:
                current_page = "Other"
        except:
            current_page = "Home"
        
        # Navigation buttons - linked to existing pages
        if st.button("Home", use_container_width=True, type="primary"):
            pass  # Already on home page
        
        if st.button("GIS Dashboard", use_container_width=True, type="secondary"):
            st.switch_page("pages/gis_dashboard.py")
        
        if st.button("Risk Dashboard", use_container_width=True, type="secondary"):
            st.switch_page("pages/risk_dashboard.py")
        
        if st.button("Prediction Explainability", use_container_width=True, type="secondary"):
            st.switch_page("pages/prediction_explain.py")
        
        # Alert System - Only visible to Admin and Officer
        user_role = st.session_state.get('user_role', 'viewer')
        if user_role in ['admin', 'officer']:
            if st.button("Alert System", use_container_width=True, type="secondary"):
                st.switch_page("pages/alert_dashboard.py")
        
        st.markdown("---")
        
        if st.button("Logout", use_container_width=True, type="secondary"):
            from src.auth import AuthManager
            auth_manager = AuthManager()
            auth_manager.logout()
            st.rerun()
    
    user_name = st.session_state.get('user_name', 'User')
    
    # SVG Logo (re-used from auth to maintain brand consistency)
    logo_svg = '<svg width="110" height="110" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M50 8 V92 M8 50 H92" stroke="#1d4ed8" stroke-width="1.5" stroke-dasharray="3 3" /><path d="M25 25 L75 75 M25 75 L75 25" stroke="#3b82f6" stroke-width="1.2" stroke-dasharray="2 3" /><rect x="36" y="15" width="28" height="70" rx="3" fill="none" stroke="#1d4ed8" stroke-width="3" /><rect x="15" y="36" width="70" height="28" rx="3" fill="none" stroke="#1d4ed8" stroke-width="3" /><rect x="37.5" y="37.5" width="25" height="25" fill="#eff6ff" /><circle cx="50" cy="50" r="10" fill="#ffffff" stroke="#2563eb" stroke-width="2.5" /><path d="M45 45 L55 55 M45 55 L55 45" stroke="#2563eb" stroke-width="1.5" /><circle cx="50" cy="15" r="3.5" fill="#1e40af" /><circle cx="50" cy="85" r="3.5" fill="#1e40af" /><circle cx="15" cy="50" r="3.5" fill="#1e40af" /><circle cx="85" cy="50" r="3.5" fill="#1e40af" /><circle cx="36" cy="36" r="3.5" fill="#2563eb" /><circle cx="64" cy="64" r="3.5" fill="#2563eb" /><circle cx="36" cy="64" r="3.5" fill="#2563eb" /><circle cx="64" cy="36" r="3.5" fill="#2563eb" /></svg>'

    dashboard_header_html = f'''
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; margin-top: 1rem; margin-bottom: 2.5rem;">
        <div style="width: 140px; height: 140px; background: radial-gradient(circle, rgba(255,255,255,1) 0%, rgba(220,240,255,0.6) 45%, transparent 75%); border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; margin-bottom: 1rem; pointer-events: none;">
            <div style="position: absolute; width: 200px; height: 200px; background: radial-gradient(circle, rgba(255,255,255,0.5) 0%, rgba(230,245,255,0.1) 60%, transparent 100%); border-radius: 50%; z-index: -1;"></div>
            <div style="z-index: 1; display: flex; flex-direction: column; align-items: center; transform: scale(0.85);">
                {logo_svg}
            </div>
        </div>
        <h1 style="color: #1e293b; font-size: 2.4rem; font-weight: 700; margin-bottom: 0.5rem; text-align: center; letter-spacing: -0.5px;">PakPulse.AI</h1>
        <p style="color: #0c3e75; font-size: 0.75rem; font-weight: 700; letter-spacing: 1.5px; margin-top: 0px; margin-bottom: 1.5rem; text-align: center;">DISEASE EARLY WARNING SYSTEM</p>
        <div style="background: #ffffff; padding: 1.5rem 2.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.08); border: 1px solid #e0f2fe; text-align: center; width: 100%; max-width: 800px;">
            <h2 style="color: #1d4ed8; margin: 0 0 0.5rem 0; font-size: 1.5rem; font-weight: 600;">Welcome, {user_name}!</h2>
            <p style="color: #475569; margin: 0; font-size: 1rem; font-weight: 400;">You are successfully logged into the PakPulse AI Dashboard.</p>
        </div>
    </div>
    <div style="height: 1px; background: linear-gradient(90deg, transparent, #bfdbfe, transparent); margin: 2.5rem 0;"></div>
    '''
    
    st.markdown(dashboard_header_html, unsafe_allow_html=True)
    
    # Professional System Overview Section
    st.markdown("""
    <h3 style="
        color: #0f172a !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-top: 0 !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.75rem !important;
        border-bottom: 2px solid #e2e8f0 !important;
    ">System Overview</h3>
    """, unsafe_allow_html=True)
    
    # Professional Feature Cards with Icons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            padding: 2rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
            height: 100%;
            transition: transform 0.2s, box-shadow 0.2s;
        ">
            <h4 style="color: #0f172a; margin-top: 0; margin-bottom: 0.75rem; font-size: 1.25rem; font-weight: 700;">GIS Visualization</h4>
            <p style="color: #475569; margin: 0; line-height: 1.6; font-size: 0.9375rem;">Interactive maps with disease risk visualization at district level</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            padding: 2rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
            height: 100%;
            transition: transform 0.2s, box-shadow 0.2s;
        ">
            <h4 style="color: #0f172a; margin-top: 0; margin-bottom: 0.75rem; font-size: 1.25rem; font-weight: 700;">Risk Assessment</h4>
            <p style="color: #475569; margin: 0; line-height: 1.6; font-size: 0.9375rem;">Comprehensive risk index calculation and composite health scoring</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            padding: 2rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
            height: 100%;
            transition: transform 0.2s, box-shadow 0.2s;
        ">
            <h4 style="color: #0f172a; margin-top: 0; margin-bottom: 0.75rem; font-size: 1.25rem; font-weight: 700;">Alert System</h4>
            <p style="color: #475569; margin: 0; line-height: 1.6; font-size: 0.9375rem;">Real-time email and SMS notifications for outbreak warnings</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Professional Divider
    st.markdown("""
    <div style="height: 2px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); margin: 2rem 0;"></div>
    """, unsafe_allow_html=True)
    
    # Professional Data Sources Section
    st.markdown("""
    <h3 style="
        color: #0f172a !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-top: 0 !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.75rem !important;
        border-bottom: 2px solid #e2e8f0 !important;
    ">Data Sources</h3>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="
        background: #ffffff;
        border-left: 4px solid #2563eb;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
    ">
        <p style="color: #1e293b; margin: 0; font-size: 0.9375rem; line-height: 1.6;">
            <strong style="color: #0f172a;">Live API Integration:</strong> Real-time data is fetched from WHO Global Health Observatory (GHO), HealthMap, and GDELT APIs. Data is cached for optimal performance and refreshed hourly.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data from all APIs
    try:
        with st.spinner("Loading data from live APIs..."):
            disease_data = load_disease_data()
        districts_meta = load_districts_metadata()
        
        # Professional System Status Section
        st.markdown("""
        <h3 style="
            color: #0f172a !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            margin-top: 0 !important;
            margin-bottom: 1.5rem !important;
            padding-bottom: 0.75rem !important;
            border-bottom: 2px solid #e2e8f0 !important;
        ">System Status</h3>
        """, unsafe_allow_html=True)
        # Professional Status Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div style="
                background: #ffffff;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border: 1px solid #e2e8f0;
                text-align: center;
            ">
                <div style="color: #0f172a; font-size: 1.25rem; font-weight: 700; margin-bottom: 0.25rem;">Ready</div>
                <div style="color: #64748b; font-size: 0.875rem; font-weight: 500;">Risk Index Generator</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: #ffffff;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border: 1px solid #e2e8f0;
                text-align: center;
            ">
                <div style="color: #0f172a; font-size: 1.25rem; font-weight: 700; margin-bottom: 0.25rem;">Ready</div>
                <div style="color: #64748b; font-size: 0.875rem; font-weight: 500;">GIS Visualization</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="
                background: #ffffff;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border: 1px solid #e2e8f0;
                text-align: center;
            ">
                <div style="color: #0f172a; font-size: 1.25rem; font-weight: 700; margin-bottom: 0.25rem;">Ready</div>
                <div style="color: #64748b; font-size: 0.875rem; font-weight: 500;">Alert System</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style="
                background: #ffffff;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border: 1px solid #e2e8f0;
                text-align: center;
            ">
                <div style="color: #0f172a; font-size: 1.25rem; font-weight: 700; margin-bottom: 0.25rem;">{len(disease_data):,}</div>
                <div style="color: #64748b; font-size: 0.875rem; font-weight: 500;">Data Records</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Professional Divider
        st.markdown("""
        <div style="height: 2px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); margin: 2rem 0;"></div>
        """, unsafe_allow_html=True)
        
        # Professional Data Summary Section
        st.markdown("""
        <h3 style="
            color: #0f172a !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            margin-top: 0 !important;
            margin-bottom: 1.5rem !important;
            padding-bottom: 0.75rem !important;
            border-bottom: 2px solid #e2e8f0 !important;
        ">Data Summary</h3>
        """, unsafe_allow_html=True)
        
        # Professional Summary Cards
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        
        with summary_col1:
            st.markdown(f"""
            <div style="
                background: #ffffff;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border: 1px solid #e2e8f0;
                text-align: center;
            ">
                <div style="color: #0f172a; font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">{len(disease_data):,}</div>
                <div style="color: #64748b; font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Total Records</div>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col2:
            st.markdown(f"""
            <div style="
                background: #ffffff;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border: 1px solid #e2e8f0;
                text-align: center;
            ">
                <div style="color: #0f172a; font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">{disease_data['district'].nunique()}</div>
                <div style="color: #64748b; font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Districts</div>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col3:
            st.markdown(f"""
            <div style="
                background: #ffffff;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border: 1px solid #e2e8f0;
                text-align: center;
            ">
                <div style="color: #0f172a; font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">{disease_data['disease'].nunique()}</div>
                <div style="color: #64748b; font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Diseases</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Detailed Summary in Expander
        with st.expander("View Detailed Information", expanded=False):
            st.markdown("""
            <div style="
                background: #f8fafc;
                padding: 1.5rem;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                margin-top: 1rem;
            ">
                <p style="color: #1e293b; margin: 0.75rem 0; font-size: 0.9375rem;">
                    <strong style="color: #0f172a;">Diseases:</strong> {}
                </p>
                <p style="color: #1e293b; margin: 0.75rem 0; font-size: 0.9375rem;">
                    <strong style="color: #0f172a;">Date Range:</strong> {} to {}
                </p>
            </div>
            """.format(
                ", ".join(sorted(disease_data['disease'].unique())),
                disease_data['date'].min().date(),
                disease_data['date'].max().date()
            ), unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please ensure data files exist in the data/ directory")

if __name__ == "__main__":
    auth_manager = AuthManager()
    if not st.session_state.get("authenticated", False):
        show_welcome_page(auth_manager)  # <-- Correct function from your imports
    else:
        user_role = st.session_state.get("user_role", "viewer").lower()  # Ensure lowercase
        main()  # <-- Actually call the main dashboard function
