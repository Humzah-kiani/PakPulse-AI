import sys
import os
from pathlib import Path
import streamlit as st
import pandas as pd

parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.auth import AuthManager, show_welcome_page

st.set_page_config(
    page_title="PakPulse AI - Disease Early Warning System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["user_role"] = None
    st.session_state["user_name"] = None

auth_manager = AuthManager()

if not st.session_state.get("authenticated", False):
    st.session_state["authenticated"] = False
    show_welcome_page(auth_manager)
    st.stop()

user_role = st.session_state.get("user_role", "viewer")
username = st.session_state.get("username", "Unknown")
user_name = st.session_state.get("user_name", username)

st.markdown("""
<style>
[data-testid="stSidebar"] {background-color: #f8f9fa;}
.stMetric {background-color: #ffffff; padding: 1rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🏥 PakPulse AI")
    st.markdown(f"**Logged in as:** {user_name}")
    st.markdown(f"**Role:** {user_role.upper()}")
    st.divider()
    
    if st.button("🚪 Logout", use_container_width=True):
        auth_manager.logout()
        st.session_state["authenticated"] = False
        st.rerun()

st.title("🏥 PakPulse AI - Disease Early Warning System")
st.markdown(f"Welcome **{user_name}** | Role: **{user_role.upper()}**")
st.divider()

if user_role == "admin":
    st.header("📊 Admin Dashboard")
    st.info("🔐 Admin Access: Full system control and monitoring")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Districts", "50", "✓")
    with col2:
        st.metric("Total Diseases", "20", "✓")
    with col3:
        st.metric("Active Users", "125", "+5")
    with col4:
        st.metric("System Status", "Operational", "✓")
    
    st.subheader("System Management")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("👥 Manage Users"):
            st.success("User Management Module")
    with col2:
        if st.button("⚙️ System Settings"):
            st.success("System Settings Module")
    with col3:
        if st.button("📈 Analytics"):
            st.success("Analytics Module")
    
    st.subheader("Recent Activity")
    activity_data = {
        "Timestamp": ["2026-03-15 10:30", "2026-03-15 10:25", "2026-03-15 10:20"],
        "Action": ["User Login", "Data Updated", "Report Generated"],
        "User": ["officer1", "system", "admin"]
    }
    st.dataframe(pd.DataFrame(activity_data), use_container_width=True)

elif user_role == "officer":
    st.header("📋 Health Officer Dashboard")
    st.warning("🔒 Officer Access: View and manage district health data")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("My Districts", "10", "")
    with col2:
        st.metric("Active Cases", "345", "+12")
    with col3:
        st.metric("Alerts", "3", "🔴")
    
    st.subheader("District Management")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📍 View Districts"):
            st.success("District Monitoring Module")
    with col2:
        if st.button("📊 Disease Cases"):
            st.success("Disease Cases Module")
    
    st.subheader("Active Alerts")
    alerts_data = {
        "District": ["Lahore", "Karachi", "Islamabad"],
        "Disease": ["Dengue", "Cholera", "COVID-19"],
        "Cases": [45, 23, 12],
        "Risk Level": ["🔴 High", "🟠 Medium", "🟡 Low"]
    }
    st.dataframe(pd.DataFrame(alerts_data), use_container_width=True)

else:
    st.header("👁️ Viewer Dashboard")
    st.info("👤 Viewer Access: View-only access to public health data")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Cases", "12,450", "+234")
    with col2:
        st.metric("Recovery Rate", "85.2%", "+2.1%")
    
    st.subheader("Public Health Information")
    if st.button("📊 View Statistics"):
        st.success("Public Health Statistics Module")
    
    st.subheader("Disease Overview")
    diseases_data = {
        "Disease": ["COVID-19", "Dengue", "Cholera", "Malaria"],
        "National Cases": [234, 567, 89, 456],
        "Trend": ["📈", "📉", "➡️", "📈"]
    }
    st.dataframe(pd.DataFrame(diseases_data), use_container_width=True)

st.divider()
st.markdown(f"""
### 📋 Session Information
- **Username:** {username}
- **Full Name:** {user_name}
- **Role:** {user_role.upper()}
- **Authenticated:** ✅ Yes
""")
