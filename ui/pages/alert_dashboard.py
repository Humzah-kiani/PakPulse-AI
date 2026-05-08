"""
Alert System Dashboard Page
Configure alerts and view alert history
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
from src.alert_system import AlertSystem
from src.data_loader import DataLoader
from src.auth import AuthManager
from datetime import datetime

# Check authentication
auth = AuthManager()
if not auth.require_auth():
    st.cache_data.clear()
    st.warning("Please login to access this page")
    if "authenticated" in st.session_state:
        st.session_state["authenticated"] = False
    st.stop()

# Check role - Alert System is only for Admin and Officer
user_role = st.session_state.get('user_role', 'viewer')
if user_role not in ['admin', 'officer']:
    st.error("**Access Denied**")
    st.warning("Alert System is only available for Administrators and Health Officers.")
    st.info("You are logged in as a **Viewer**. Viewers can only access GIS Dashboard and Risk Dashboard.")
    if st.button("Go to Home", use_container_width=True):
        st.switch_page("app.py")
    st.stop()

st.set_page_config(
    page_title="Alert System - PakPulse AI",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add professional styling
from src.dashboard_styles import PROFESSIONAL_STYLES
st.markdown(PROFESSIONAL_STYLES, unsafe_allow_html=True)

# Ensure sidebar is visible
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    width: 21rem !important;
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}

/* Override any dark theme classes */
section[data-testid="stSidebar"] [class*="css-"],
section[data-testid="stSidebar"] [class*="st-"],
section[data-testid="stSidebar"] > div {
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)

# Enhanced Professional Styling for Alert Dashboard
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
    
    /* Buttons - Professional */
    .stButton > button[kind="primary"] {
        background: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #2563eb !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
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
    
    /* Tabs - Professional */
    .stTabs [data-baseweb="tab"] {
        color: #475569 !important;
        font-weight: 600 !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
        border-bottom: 3px solid #2563eb !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # Cache for 1 hour (refresh API data)
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
        
        if st.button("Risk Dashboard", use_container_width=True, type="secondary"):
            st.switch_page("pages/risk_dashboard.py")
        
        if st.button("Alert System", use_container_width=True, type="primary"):
            pass  # Already on this page
        
        st.markdown("---")
        
        if st.button("Logout", use_container_width=True):
            auth.logout()
            st.rerun()
        
        st.markdown("---")
    
    # Professional Header
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
        <h1 style="margin: 0; color: #1d4ed8; font-size: 2rem; font-weight: 700;">Alert System Dashboard</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.125rem; color: #475569; font-weight: 500;">Configure Alerts and Monitor Risk Thresholds</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Professional Breadcrumb
    st.markdown("""
    <div style="margin-bottom: 1.5rem; padding: 0.75rem 1rem; background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0;">
        <span style="color: #64748b; font-size: 0.875rem;">
            <a href="/" style="color: #2563eb; text-decoration: none;">Home</a> 
            <span style="color: #cbd5e1; margin: 0 0.5rem;">›</span> 
            <span style="color: #1e293b; font-weight: 600;">Alert System</span>
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize alert system
    alert_system = AlertSystem()
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "Current Alerts",
        "Alert Configuration",
        "Email Settings",
        "SMS Settings"
    ])
    
    with tab1:
        st.markdown("""
        <h3 style="
            color: #0f172a !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            margin-top: 0 !important;
            margin-bottom: 1.5rem !important;
            padding-bottom: 0.75rem !important;
            border-bottom: 2px solid #e2e8f0 !important;
        ">Current Risk Alerts</h3>
        """, unsafe_allow_html=True)
        
        try:
            disease_data = load_data()
            
            # Check for alerts
            alerts = alert_system.check_risk_thresholds(disease_data)
            
            if alerts:
                st.warning(f"**{len(alerts)} Active Alert(s) Detected**")
                
                # Display alerts
                alerts_df = pd.DataFrame(alerts)
                st.dataframe(
                    alerts_df[['district', 'disease', 'risk_index', 'threshold', 'date', 'status']],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Manual trigger button
                if st.button("Send Alerts Now", type="primary"):
                    with st.spinner("Processing alerts..."):
                        processed = alert_system.process_alerts(disease_data)
                        if processed:
                            # Check SMS status
                            sms_sent = any(alert.get('sms_sent', False) for alert in processed)
                            if sms_sent:
                                st.success(f"{len(processed)} alert(s) sent successfully! SMS notifications sent.")
                            else:
                                st.warning(f"{len(processed)} alert(s) processed, but SMS may not have been sent. Check SMS configuration.")
                            
                            # Show SMS errors if any
                            for alert in processed:
                                if 'sms_errors' in alert:
                                    st.error(f"SMS Errors: {', '.join(alert['sms_errors'])}")
                            
                            st.rerun()
                        else:
                            st.info("No new alerts to send (may have been sent recently)")
            else:
                st.success("No active alerts - All districts are within safe thresholds")
            
            # Professional Divider
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
            ">Alert History</h3>
            """, unsafe_allow_html=True)
            history = alert_system.get_alert_history(limit=20)
            
            if history:
                history_df = pd.DataFrame(history)
                # Sort by timestamp (most recent first)
                if 'timestamp' in history_df.columns:
                    history_df = history_df.sort_values('timestamp', ascending=False)
                
                st.dataframe(
                    history_df[['district', 'disease', 'risk_index', 'threshold', 'date', 'status', 'timestamp']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No alert history available")
        
        except Exception as e:
            st.error(f"**Error loading alerts:** {str(e)}")
            st.info("**Troubleshooting:**\n- Ensure data files exist in the `data/` directory\n- Check alert configuration file permissions")
            
            with st.expander("Technical Details"):
                st.code(str(e))
    
    with tab2:
        st.markdown("""
        <h3 style="
            color: #0f172a !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            margin-top: 0 !important;
            margin-bottom: 1.5rem !important;
            padding-bottom: 0.75rem !important;
            border-bottom: 2px solid #e2e8f0 !important;
        ">Risk Threshold Configuration</h3>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="
            background: #ffffff;
            border-left: 4px solid #2563eb;
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
            margin-bottom: 1.5rem;
        ">
            <p style="color: #1e293b; margin: 0; font-size: 0.9375rem; line-height: 1.6;">
                Set risk thresholds for each disease. Alerts will be triggered when risk exceeds these values.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        thresholds = alert_system.config.get("thresholds", {})
        loader = DataLoader()
        diseases = loader.get_all_diseases()
        
        # Threshold sliders
        new_thresholds = {}
        cols = st.columns(3)
        
        for idx, disease in enumerate(sorted(diseases)):
            with cols[idx % 3]:
                threshold = thresholds.get(disease, 70)
                new_threshold = st.slider(
                    f"{disease.title()} Threshold",
                    min_value=0,
                    max_value=100,
                    value=int(threshold),
                    key=f"threshold_{disease}",
                    help=f"Alert when {disease} risk exceeds this value"
                )
                new_thresholds[disease] = new_threshold
        
        # Alert frequency
        st.markdown("---")
        frequency = st.selectbox(
            "Alert Frequency",
            options=["immediate", "daily", "weekly"],
            index=["immediate", "daily", "weekly"].index(alert_system.config.get("alert_frequency", "daily")),
            help="How often to send alerts for the same risk"
        )
        
        # Save button
        if st.button("Save Configuration", type="primary"):
            for disease, threshold in new_thresholds.items():
                alert_system.update_threshold(disease, threshold)
            
            alert_system.config["alert_frequency"] = frequency
            alert_system.save_config()
            st.success("Configuration saved successfully!")
            st.rerun()
    
    with tab3:
        st.markdown("""
        <h3 style="
            color: #0f172a !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            margin-top: 0 !important;
            margin-bottom: 1.5rem !important;
            padding-bottom: 0.75rem !important;
            border-bottom: 2px solid #e2e8f0 !important;
        ">Email Alert Configuration</h3>
        """, unsafe_allow_html=True)
        
        email_config = alert_system.config.get("email", {})
        
        email_enabled = st.checkbox(
            "Enable Email Alerts",
            value=email_config.get("enabled", False),
            help="Enable/disable email alert notifications"
        )
        
        if email_enabled:
            col1, col2 = st.columns(2)
            
            with col1:
                smtp_server = st.text_input(
                    "SMTP Server",
                    value=email_config.get("smtp_server", "smtp.gmail.com"),
                    help="SMTP server address (e.g., smtp.gmail.com)"
                )
                smtp_port = st.number_input(
                    "SMTP Port",
                    min_value=1,
                    max_value=65535,
                    value=email_config.get("smtp_port", 587),
                    help="SMTP port (587 for TLS, 465 for SSL)"
                )
                sender_email = st.text_input(
                    "Sender Email",
                    value=email_config.get("sender_email", ""),
                    type="default",
                    help="Email address to send alerts from"
                )
            
            with col2:
                sender_password = st.text_input(
                    "Sender Password",
                    value=email_config.get("sender_password", ""),
                    type="password",
                    help="Password for sender email (use App Password for Gmail)"
                )
                recipients = st.text_area(
                    "Recipient Emails",
                    value="\n".join(email_config.get("recipients", [])),
                    help="Enter email addresses (one per line)"
                )
            
            if st.button("Save Email Configuration", type="primary"):
                recipient_list = [r.strip() for r in recipients.split('\n') if r.strip()]
                alert_system.update_email_config(
                    email_enabled, smtp_server, int(smtp_port),
                    sender_email, sender_password, recipient_list
                )
                st.success("Email configuration saved!")
                st.rerun()
            
            # Test Email button
            if email_enabled and smtp_server and sender_email and sender_password and recipients:
                st.markdown("---")
                st.markdown("""
                <h4 style="
                    color: #1e293b !important;
                    font-size: 1.25rem !important;
                    font-weight: 600 !important;
                    margin-top: 1.5rem !important;
                    margin-bottom: 1rem !important;
                ">Test Email</h4>
                """, unsafe_allow_html=True)
                if st.button("Send Test Email", type="secondary"):
                    try:
                        recipient_list = [r.strip() for r in recipients.split('\n') if r.strip()]
                        if recipient_list:
                            test_recipient = recipient_list[0]
                            
                            # Import email sending function
                            from src.alert_system import send_test_email
                            
                            # Send test email
                            test_subject = "PakPulse Test: Email Integration"
                            test_body = """
                            <html>
                                <body>
                                    <h2>PakPulse AI - Test Email</h2>
                                    <p>This is a test email to verify that the email integration is working correctly.</p>
                                    <p>If you received this email, your email configuration is set up properly.</p>
                                    <hr>
                                    <p style="color: #666; font-size: 0.9em;">PakPulse AI - Multi-Disease Early Warning System</p>
                                </body>
                            </html>
                            """
                            
                            success = send_test_email(
                                smtp_server=smtp_server,
                                smtp_port=int(smtp_port),
                                sender_email=sender_email,
                                sender_password=sender_password,
                                recipients=[test_recipient],
                                subject=test_subject,
                                body=test_body
                            )
                            
                            if success:
                                st.success(f"Test email sent to {test_recipient}!")
                            else:
                                st.error("Failed to send test email. Please check your email configuration.")
                        else:
                            st.warning("Please add at least one recipient email address.")
                    except Exception as e:
                        error_msg = str(e)
                        st.error(f"**Test email failed**: {error_msg}")
                        
                        # Show detailed error for debugging
                        with st.expander("Technical Error Details"):
                            import traceback
                            st.code(traceback.format_exc())
        else:
            st.info("Enable email alerts to configure email settings")
    
    with tab4:
        st.markdown("""
        <h3 style="
            color: #0f172a !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            margin-top: 0 !important;
            margin-bottom: 1.5rem !important;
            padding-bottom: 0.75rem !important;
            border-bottom: 2px solid #e2e8f0 !important;
        ">SMS Alert Configuration</h3>
        """, unsafe_allow_html=True)
        st.info("SMS alerts require a Twilio account. Configure your Twilio credentials below.")
        
        sms_config = alert_system.config.get("sms", {})
        
        sms_enabled = st.checkbox(
            "Enable SMS Alerts",
            value=sms_config.get("enabled", False),
            help="Enable/disable SMS alert notifications (requires Twilio)"
        )
        
        if sms_enabled:
            col1, col2 = st.columns(2)
            
            with col1:
                account_sid = st.text_input(
                    "Twilio Account SID",
                    value=sms_config.get("twilio_account_sid", ""),
                    type="default",
                    help="Your Twilio Account SID"
                )
                auth_token = st.text_input(
                    "Twilio Auth Token",
                    value=sms_config.get("twilio_auth_token", ""),
                    type="password",
                    help="Your Twilio Auth Token"
                )
            
            with col2:
                phone_number = st.text_input(
                    "Twilio Phone Number",
                    value=sms_config.get("twilio_phone_number", ""),
                    help="Your Twilio phone number (e.g., +1234567890)"
                )
                recipients = st.text_area(
                    "Recipient Phone Numbers",
                    value="\n".join(sms_config.get("recipients", [])),
                    help="Enter phone numbers (one per line, include country code)"
                )
            
            if st.button("Save SMS Configuration", type="primary"):
                recipient_list = [r.strip() for r in recipients.split('\n') if r.strip()]
                
                # Normalize phone numbers and show conversion
                from src.alert_system import normalize_phone_number
                normalized_recipients = [normalize_phone_number(r) for r in recipient_list]
                normalized_phone = normalize_phone_number(phone_number) if phone_number else phone_number
                
                # Show normalization info
                if recipient_list:
                    st.info("Phone numbers will be converted to E.164 format:")
                    for orig, norm in zip(recipient_list, normalized_recipients):
                        if orig != norm:
                            st.write(f"  `{orig}` → `{norm}`")
                        else:
                            st.write(f"  `{norm}`")
                
                alert_system.update_sms_config(
                    sms_enabled, account_sid, auth_token,
                    phone_number, recipient_list
                )
                st.success("SMS configuration saved!")
                st.rerun()
            
            # Test SMS button
            if sms_enabled and account_sid and auth_token and phone_number and recipients:
                st.markdown("---")
                st.markdown("""
                <h4 style="
                    color: #1e293b !important;
                    font-size: 1.25rem !important;
                    font-weight: 600 !important;
                    margin-top: 1.5rem !important;
                    margin-bottom: 1rem !important;
                ">Test SMS</h4>
                """, unsafe_allow_html=True)
                if st.button("Send Test SMS", type="secondary"):
                    from src.alert_system import normalize_phone_number
                    test_recipient = normalize_phone_number(recipients.split('\n')[0].strip())
                    
                    try:
                        from twilio.rest import Client
                        client = Client(account_sid, auth_token)
                        
                        test_message = "PakPulse Test: SMS integration is working correctly!"
                        message = client.messages.create(
                            body=test_message,
                            from_=normalize_phone_number(phone_number),
                            to=test_recipient
                        )
                        st.success(f"Test SMS sent to {test_recipient}!")
                        st.info(f"Message SID: {message.sid}\nStatus: {message.status}")
                    except Exception as e:
                        error_msg = str(e)
                        
                        # Check for common Twilio errors
                        if "unverified" in error_msg.lower() or "21608" in error_msg:
                            st.error("**SMS Failed: Phone Number Not Verified**")
                            st.warning("""
                            **Twilio Trial Account Limitation:**
                            
                            Your Twilio account is a trial account. Trial accounts can only send SMS to **verified phone numbers**.
                            
                            **Solution 1: Verify Phone Number (Free)**
                            1. Go to [Twilio Console - Verified Caller IDs](https://console.twilio.com/us1/develop/phone-numbers/manage/verified)
                            2. Click **"Add a new number"**
                            3. Enter your recipient number: `+923325519237`
                            4. Twilio will send a verification code via SMS
                            5. Enter the code to verify
                            6. Try sending SMS again
                            
                            **Solution 2: Upgrade Account (Paid)**
                            - Upgrade to a paid Twilio account
                            - Paid accounts can send to any number
                            - Go to [Twilio Console - Billing](https://console.twilio.com/us1/develop/billing/overview)
                            """)
                            
                            st.info("**Quick Link**: [Verify Phone Number](https://console.twilio.com/us1/develop/phone-numbers/manage/verified)")
                        elif "unauthorized" in error_msg.lower() or "20003" in error_msg:
                            st.error("**SMS Failed: Authentication Error**")
                            st.warning("Check your Twilio Account SID and Auth Token in SMS Settings.")
                        elif "insufficient" in error_msg.lower() or "balance" in error_msg.lower():
                            st.error("**SMS Failed: Insufficient Balance**")
                            st.warning("Add credits to your Twilio account to send SMS.")
                        else:
                            st.error(f"**Test SMS failed**: {error_msg}")
                        
                        # Show detailed error for debugging
                        with st.expander("Technical Error Details"):
                            import traceback
                            st.code(traceback.format_exc())
        else:
            st.info("Enable SMS alerts to configure SMS settings")

if __name__ == "__main__":
    main()

