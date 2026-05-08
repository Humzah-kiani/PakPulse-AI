"""
PakPulse AI - Multi-Disease Early Warning System
Main Streamlit Application Entry Point
"""

import sys
import os
from pathlib import Path

# Add parent directory to path so we can import src module
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import streamlit as st
from src.auth import AuthManager, show_welcome_page

# PAGE CONFIGURATION (Set before other operations)
st.set_page_config(
    page_title="PakPulse AI - Disease Early Warning System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["user_role"] = None
    st.session_state["user_name"] = None

# Initialize auth manager
auth_manager = AuthManager()

# ============================================================================
#  ROLE-BASED ACCESS CONTROL
# ============================================================================

# Show login page if not authenticated
if not st.session_state.get("authenticated", False):
    st.session_state["authenticated"] = False
    show_welcome_page(auth_manager)
    st.stop()

# User is authenticated - proceed with dashboard
user_role = st.session_state.get("user_role", "viewer")
username = st.session_state.get("username", "Unknown")
user_name = st.session_state.get("user_name", username)

# Add professional styling
try:
    from src.dashboard_styles import PROFESSIONAL_STYLES
    st.markdown(PROFESSIONAL_STYLES, unsafe_allow_html=True)
except:
    pass

@st.cache_data(ttl=3600)  # Cache for 1 hour (refresh API data)
def load_disease_data():
    """Load disease data from ALL LIVE APIs (no local files)
    
    Returns:
        DataFrame with combined disease data from WHO, HealthMap, and GDELT APIs
    """
    from src.data_loader import load_combined_api_data
    return load_combined_api_data()

@st.cache_data
def load_districts_metadata():
    """Load districts metadata (cached for performance)"""
    loader = DataLoader()
    return loader.load_districts_metadata()

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
    
    /* Main content area - Light grey/off-white background */
    .main {
        background: #f8fafc !important;
    }
    
    div[data-testid="stAppViewContainer"] {
        background: #f8fafc !important;
    }
    
    div[data-testid="stAppViewContainer"] > div:first-child {
        background: #f8fafc !important;
    }
    
    /* Remove any white containers */
    div[data-testid="stAppViewContainer"] > div > div {
        background: transparent !important;
    }
    
    /* Ensure main content wrapper is light grey */
    [data-testid="stAppViewContainer"] > div[class*="main"] {
        background: #f8fafc !important;
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
        color: #1e293b !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #475569 !important;
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
    
    /* Search input on white background */
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] input {
        background: #f8fafc !important;
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
    
    /* Ensure all buttons are visible and have proper spacing */
    section[data-testid="stSidebar"] .stButton {
        margin-bottom: 0.5rem;
    }
    
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        transition: all 0.2s ease;
        font-size: 0.9375rem;
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
    /* Force sidebar to be visible and expanded with light background */
    section[data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        width: 21rem !important;
        min-width: 21rem !important;
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%) !important;
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
        # Branding section - Promotion bar
        st.markdown("""
        <div class="sidebar-branding">
            <h2>PakPulse AI</h2>
            <p>Multi-Disease Early Warning System</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User Information section
        user_name = st.session_state.get('user_name', 'Unknown')
        user_role = st.session_state.get('user_role', 'viewer').title()
        
        st.markdown("""
        <div class="sidebar-user-info">
            <h3>User Information</h3>
            <p><strong>Name:</strong> {}</p>
            <p><strong>Role:</strong> {}</p>
        </div>
        """.format(user_name, user_role), unsafe_allow_html=True)
        
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
        
        # Navigation buttons - Home is primary (blue), others are secondary
        # Home button - primary (blue) when on home page
        home_type = "primary" if current_page == "Home" else "secondary"
        if st.button("Home", use_container_width=True, type=home_type):
            # For multi-page apps, navigate to main app
            try:
                st.switch_page("app.py")
            except:
                pass  # Already on home page
        
        # Other navigation buttons
        if st.button("GIS Dashboard", use_container_width=True, type="secondary"):
            st.switch_page("pages/gis_dashboard.py")
        
        if st.button("Risk Dashboard", use_container_width=True, type="secondary"):
            st.switch_page("pages/risk_dashboard.py")
        
        # Alert System - Only visible to Admin and Officer
        user_role = st.session_state.get('user_role', 'viewer')
        if user_role in ['admin', 'officer']:
            if st.button("Alert System", use_container_width=True, type="secondary"):
                st.switch_page("pages/alert_dashboard.py")
        
        st.markdown("---")
        
        if st.button("Logout", use_container_width=True, type="secondary"):
            auth_manager = AuthManager()
            auth_manager.logout()
            st.rerun()
    
    # Professional Main Header - Light Theme
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #eff6ff 0%, #dfe8ff 100%);
        color: #1e293b;
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
        border: 1px solid #bfdbfe;
    ">
        <h1 style="color: #1d4ed8; margin: 0; font-size: 2rem; font-weight: 700;">PakPulse AI</h1>
        <p style="color: #475569; margin: 0.5rem 0 0 0; font-size: 1rem; font-weight: 500;">Multi-Disease Early Warning System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Professional Welcome Banner - Light Theme
    user_name = st.session_state.get('user_name', 'User')
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #eff6ff 0%, #dfe8ff 100%);
        color: #1e293b;
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
        border: 1px solid #bfdbfe;
    ">
        <h2 style="color: #1d4ed8; margin: 0 0 0.5rem 0; font-size: 1.75rem; font-weight: 700;">Welcome, {user_name}!</h2>
        <p style="color: #475569; margin: 0; font-size: 1rem; font-weight: 500;">You are successfully logged into the PakPulse AI Dashboard.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Professional Divider
    st.markdown("""
    <div style="height: 2px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); margin: 2rem 0;"></div>
    """, unsafe_allow_html=True)
    
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
    main()

