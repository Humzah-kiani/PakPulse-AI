"""
Authentication Module for PakPulse AI
- JSON-based user storage
- Admin/Officer quick login
- Welcome page with Login / Register tabs
"""

import streamlit as st
import hashlib
import re
import random
import string
from typing import Optional, Dict, Tuple
import json
from pathlib import Path
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -------------------------------------------------------------------
#  USER STORAGE (A1: JSON FILE)
# -------------------------------------------------------------------

USERS_FILE = Path("data/users.json")
OTP_STORAGE_FILE = Path("data/password_reset_otps.json")

# Validation functions
def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format using regex"""
    if not email:
        return False, "Email is required."
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Please enter a valid email address (e.g., user@example.com)."
    return True, ""

def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password: min 8 chars, uppercase, lowercase, digit, special char"""
    if not password:
        return False, "Password is required."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)."
    return True, ""

def validate_name(name: str) -> Tuple[bool, str]:
    """Validate name: no digits or special characters, only letters and spaces"""
    if not name:
        return False, "Name is required."
    if not re.match(r'^[a-zA-Z\s]+$', name):
        return False, "Name can only contain letters and spaces. No digits or special characters allowed."
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long."
    return True, ""

# Built-in accounts (do NOT require registration)
DEFAULT_USERS = {
    "admin": {
        "password": "admin123",        # plain for demo (change in production)
        "role": "admin",
        "name": "Administrator",
        "email": "admin@pakpulse.ai",
    },
    "officer": {
        "password": "officer123",
        "role": "officer",
        "name": "Health Officer",
        "email": "officer@pakpulse.ai",
    },
}


class AuthManager:
    """Class to handle authentication + user storage"""

    def __init__(self):
        self.users_file = USERS_FILE
        self._users_cache: Dict[str, Dict] = {}
        self._load_users_into_cache()

    # ----------------- Internal helpers -----------------

    def _load_users_into_cache(self) -> None:
        """Load users from JSON and ensure default admin/officer exist."""
        data: Dict[str, Dict] = {}

        if self.users_file.exists():
            try:
                with open(self.users_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}

        # Always ensure built-in admin/officer accounts exist
        for username, info in DEFAULT_USERS.items():
            if username not in data:
                data[username] = info

        self._users_cache = data
        self._save_users_to_disk()

    def _save_users_to_disk(self) -> None:
        """Persist cache to disk."""
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(self._users_cache, f, indent=2)

    # ----------------- Public helpers -----------------

    def load_users(self) -> Dict[str, Dict]:
        return self._users_cache

    def save_users(self, users: Dict[str, Dict]) -> None:
        self._users_cache = users
        self._save_users_to_disk()

    # -------- Password helpers (optional hashing) --------

    def hash_password(self, password: str) -> str:
        """Simple SHA256 hash (for demo)."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def verify_password(self, password: str, stored: str, is_hashed: bool) -> bool:
        if is_hashed:
            return self.hash_password(password) == stored
        return password == stored

    # ----------------- Core auth logic -----------------

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user with case-insensitive username lookup."""
        users = self.load_users()
        # Case-insensitive username lookup
        username_lower = username.lower()
        user = None
        for key, value in users.items():
            if key.lower() == username_lower:
                user = value
                break
        
        if not user:
            return False

        stored_pw = user.get("password", "")
        is_hashed = user.get("hashed", False)
        return self.verify_password(password, stored_pw, is_hashed)

    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user info with case-insensitive lookup."""
        users = self.load_users()
        username_lower = username.lower()
        for key, value in users.items():
            if key.lower() == username_lower:
                return value
        return None
    
    def _get_actual_username(self, username: str) -> Optional[str]:
        """Get the actual username key from users dict (case-insensitive lookup)."""
        users = self.load_users()
        username_lower = username.lower()
        for key in users.keys():
            if key.lower() == username_lower:
                return key
        return None

    def login(self, username: str, password: str) -> bool:
        """Normal login using username + password (case-insensitive username)."""
        if self.authenticate(username, password):
            # Get the actual username key (preserves original case from storage)
            actual_username = self._get_actual_username(username)
            if actual_username:
                self._set_session(actual_username)
                return True
        return False

    def quick_login(self, username: str) -> bool:
        """
        Direct login without entering password.
        Used for built-in admin/officer quick buttons.
        """
        users = self.load_users()
        if username not in users:
            return False
        self._set_session(username)
        return True

    def _set_session(self, username: str) -> None:
        user = self.get_user_info(username) or {}
        st.session_state["authenticated"] = True
        st.session_state["username"] = username
        st.session_state["user_role"] = user.get("role", "viewer")
        st.session_state["user_name"] = user.get("name", username)
        # Also set compatibility variables
        st.session_state["role"] = user.get("role", "viewer")
        st.session_state["name"] = user.get("name", username)

    def logout(self) -> None:
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.session_state["user_role"] = None
        st.session_state["user_name"] = None
        # Also clear compatibility variables
        st.session_state["role"] = None
        st.session_state["name"] = None

    def is_authenticated(self) -> bool:
        return st.session_state.get("authenticated", False)

    def require_auth(self) -> bool:
        return self.is_authenticated()

    # ----------------- Registration -----------------

    def register(
        self,
        name: str,
        email: str,
        username: str,
        password: str,
        role: str = "viewer",
    ) -> Tuple[bool, str]:
        """
        Register a new *normal* user (not admin/officer).
        """
        users = self.load_users()

        if username in users:
            return False, "Username already exists. Please choose another."

        # Validate name
        name_valid, name_error = validate_name(name)
        if not name_valid:
            return False, name_error

        # Validate email
        email_valid, email_error = validate_email(email)
        if not email_valid:
            return False, email_error

        # Validate password
        password_valid, password_error = validate_password(password)
        if not password_valid:
            return False, password_error

        # Only allow regular roles for registration
        if role not in ["viewer"]:
            role = "viewer"

        users[username] = {
            "password": password,      # plain for demo; use hash_password in prod
            "hashed": False,
            "role": role,
            "name": name,
            "email": email,
        }

        self.save_users(users)
        return True, "Registration successful! You can now log in."

    # Compatibility method for existing code
    def register_user(self, name: str, email: str, username: str, password: str) -> Tuple[bool, str]:
        """Compatibility wrapper for register method."""
        return self.register(name, email, username, password, role="viewer")
    
    # ----------------- Password Reset / Forgot Password -----------------
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP"""
        return ''.join(random.choices(string.digits, k=length))
    
    def save_otp(self, email: str, otp: str, username: str) -> None:
        """Save OTP with expiration time (10 minutes)"""
        otp_data = {}
        if OTP_STORAGE_FILE.exists():
            try:
                with open(OTP_STORAGE_FILE, 'r', encoding='utf-8') as f:
                    otp_data = json.load(f)
            except:
                otp_data = {}
        
        otp_data[email.lower()] = {
            'otp': otp,
            'username': username,
            'expires_at': (datetime.now() + timedelta(minutes=10)).isoformat(),
            'created_at': datetime.now().isoformat()
        }
        
        OTP_STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OTP_STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(otp_data, f, indent=2)
    
    def verify_otp(self, email: str, otp: str) -> Tuple[bool, Optional[str]]:
        """
        Verify OTP for password reset
        
        Returns:
            (is_valid, username_or_error_message)
        """
        if not OTP_STORAGE_FILE.exists():
            return False, "No OTP found. Please request a new one."
        
        try:
            with open(OTP_STORAGE_FILE, 'r', encoding='utf-8') as f:
                otp_data = json.load(f)
        except:
            return False, "Error reading OTP data."
        
        email_lower = email.lower()
        if email_lower not in otp_data:
            return False, "No OTP found for this email. Please request a new one."
        
        stored_otp_info = otp_data[email_lower]
        stored_otp = stored_otp_info.get('otp', '')
        expires_at = datetime.fromisoformat(stored_otp_info.get('expires_at', ''))
        
        # Check if OTP expired
        if datetime.now() > expires_at:
            # Remove expired OTP
            del otp_data[email_lower]
            with open(OTP_STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump(otp_data, f, indent=2)
            return False, "OTP has expired. Please request a new one."
        
        # Verify OTP
        if stored_otp == otp:
            username = stored_otp_info.get('username', '')
            # Remove used OTP
            del otp_data[email_lower]
            with open(OTP_STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump(otp_data, f, indent=2)
            return True, username
        else:
            return False, "Invalid OTP. Please check and try again."
    
    def find_user_by_email(self, email: str) -> Optional[Dict]:
        """Find user by email address (case-insensitive)"""
        users = self.load_users()
        email_lower = email.lower()
        
        for username, user_info in users.items():
            user_email = user_info.get('email', '').lower()
            if user_email == email_lower:
                return {'username': username, **user_info}
        
        return None
    
    def send_otp_email(self, email: str, otp: str, username: str) -> Tuple[bool, str]:
        """
        Send OTP email for password reset
        
        Returns:
            (success, message)
        """
        try:
            # Try to get email config from alert system or use defaults
            email_config = self._get_email_config()
            
            if not email_config.get('enabled', False):
                # If email not configured, show OTP in UI (for development)
                return False, "Email not configured. Please contact administrator."
            
            sender_email = email_config.get('sender_email', '')
            sender_password = email_config.get('sender_password', '')
            smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = email_config.get('smtp_port', 587)
            
            if not sender_email or not sender_password:
                return False, "Email service not configured. Please contact administrator."
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = "PakPulse AI - Password Reset OTP"
            
            # Email body
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                    <h2 style="color: #1e40af; text-align: center;">PakPulse AI</h2>
                    <h3 style="color: #1e293b;">Password Reset Request</h3>
                    
                    <p>Hello {username},</p>
                    
                    <p>You have requested to reset your password for your PakPulse AI account.</p>
                    
                    <div style="background: #ffffff; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; border: 2px solid #3b82f6;">
                        <p style="margin: 0; font-size: 14px; color: #64748b; margin-bottom: 10px;">Your OTP Code:</p>
                        <p style="margin: 0; font-size: 32px; font-weight: 700; color: #1e40af; letter-spacing: 5px;">{otp}</p>
                    </div>
                    
                    <p style="color: #ef4444; font-weight: 600;">This OTP will expire in 10 minutes.</p>
                    
                    <p>If you did not request this password reset, please ignore this email.</p>
                    
                    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                    <p style="font-size: 12px; color: #64748b; text-align: center;">
                        PakPulse AI - Multi-Disease Early Warning System<br>
                        This is an automated message. Please do not reply.
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, [email], text)
            server.quit()
            
            return True, "OTP sent successfully to your email!"
            
        except Exception as e:
            error_msg = str(e)
            # For development: if email fails, we can still show OTP in UI
            return False, f"Email sending failed: {error_msg}"
    
    def _get_email_config(self) -> Dict:
        """Get email configuration from alert system or environment"""
        # Try to load from alert config
        alert_config_file = Path("data/alert_config.json")
        if alert_config_file.exists():
            try:
                with open(alert_config_file, 'r') as f:
                    alert_config = json.load(f)
                    email_config = alert_config.get('email', {})
                    if email_config.get('enabled', False):
                        return email_config
            except:
                pass
        
        # Try environment variables
        sender_email = os.getenv('SMTP_SENDER_EMAIL', '')
        sender_password = os.getenv('SMTP_SENDER_PASSWORD', '')
        
        if sender_email and sender_password:
            return {
                'enabled': True,
                'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                'smtp_port': int(os.getenv('SMTP_PORT', '587')),
                'sender_email': sender_email,
                'sender_password': sender_password
            }
        
        return {'enabled': False}
    
    def reset_password(self, username: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset user password
        
        Args:
            username: Username
            new_password: New password
            
        Returns:
            (success, message)
        """
        # Validate password
        password_valid, password_error = validate_password(new_password)
        if not password_valid:
            return False, password_error
        
        users = self.load_users()
        
        # Case-insensitive username lookup
        username_lower = username.lower()
        actual_username = None
        for key in users.keys():
            if key.lower() == username_lower:
                actual_username = key
                break
        
        if not actual_username or actual_username not in users:
            return False, "User not found."
        
        # Don't allow resetting admin/officer passwords via this method
        user = users[actual_username]
        if user.get('role') in ['admin', 'officer']:
            return False, "Admin and Officer passwords cannot be reset through this method. Please contact system administrator."
        
        # Update password
        users[actual_username]['password'] = new_password
        users[actual_username]['hashed'] = False  # Keep plain for now (can hash in production)
        
        self.save_users(users)
        return True, "Password reset successfully! You can now login with your new password."


# -------------------------------------------------------------------
#  WELCOME PAGE (Login + Register + Admin/Officer quick login)
# -------------------------------------------------------------------

def show_welcome_page(auth: AuthManager) -> None:
    # Initialize page state
    if "welcome_page" not in st.session_state:
        st.session_state.welcome_page = "welcome"

    # Hide sidebar for login page
    st.markdown("""
    <style>
    [data-testid="collapsedControl"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

    # ---------------------------- PROFESSIONAL MODERN STYLE ----------------------------
    page_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    [data-testid="stToolbar"] {display: none !important;}
    section[data-testid="stSidebar"] {display: none !important;}
    div[data-testid="collapsedControl"] {display: none !important;}
    
    /* Full viewport background */
    .stApp, div[data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%) !important;
        background-image: 
            radial-gradient(circle at 50% 20%, rgba(255,255,255,0.6) 0%, transparent 60%),
            linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%) !important;
        background-attachment: fixed !important;
        font-family: 'Inter', sans-serif !important;
        min-height: 100vh !important;
    }

    .stApp > header {
        background-color: transparent !important;
    }

    /* Centers the main block */
    .block-container {
        padding: 0 !important;
        max-width: 900px !important;
        margin: 0 auto !important;
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    div[data-testid="stAppViewContainer"] > section > div {
        background: transparent !important;
    }

    /* Login UI container */
    .login-ui-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 2rem;
        margin-top: 1rem;
    }

    /* Form Buttons inside streamlit */
    .stButton > button {
        height: 45px !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        text-transform: uppercase !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.5px !important;
    }
    
    /* LOGIN button style (Primary) */
    .btn-login .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    .btn-login .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        box-shadow: 0 6px 15px rgba(37, 99, 235, 0.3) !important;
        transform: translateY(-2px) !important;
    }

    /* REGISTER button style (Secondary) */
    .btn-register .stButton > button {
        background: #ffffff !important;
        color: #2563eb !important;
        border: 1px solid #cbd5e1 !important;
    }
    
    .btn-register .stButton > button:hover {
        background: #f8fafc !important;
        border-color: #94a3b8 !important;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.05) !important;
        transform: translateY(-2px) !important;
    }
    </style>
    """
    st.markdown(page_style, unsafe_allow_html=True)

    # ---------------------------- PAGE SWITCHER ----------------------------
    def goto(page):
        st.session_state.welcome_page = page
        st.rerun()

    # ---------------------------- WELCOME PAGE ----------------------------
    if st.session_state.welcome_page == "welcome":
        # Top Bar
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.2rem 2rem; position: fixed; top: 0; left: 0; right: 0; z-index: 100;">
            <div style="font-weight: 700; font-size: 1.25rem; color: #0f172a; font-family: 'Inter', sans-serif;">
                PakPulse-AI
            </div>
            <div style="display: flex; gap: 1rem; color: #64748b; font-size: 1.1rem; background: rgba(255,255,255,0.7); padding: 0.4rem 0.8rem; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                <span title="Settings" style="cursor: pointer; opacity: 0.8;">⚙️</span>
                <span title="Share" style="cursor: pointer; opacity: 0.8;">📤</span>
                <span title="Profile" style="cursor: pointer; opacity: 0.8;">👤</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # SVG Logo
        logo_svg = '<svg width="140" height="140" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M50 8 V92 M8 50 H92" stroke="#1d4ed8" stroke-width="1.5" stroke-dasharray="3 3" /><path d="M25 25 L75 75 M25 75 L75 25" stroke="#3b82f6" stroke-width="1.2" stroke-dasharray="2 3" /><rect x="36" y="15" width="28" height="70" rx="3" fill="none" stroke="#1d4ed8" stroke-width="3" /><rect x="15" y="36" width="70" height="28" rx="3" fill="none" stroke="#1d4ed8" stroke-width="3" /><rect x="37.5" y="37.5" width="25" height="25" fill="#eff6ff" /><circle cx="50" cy="50" r="10" fill="#ffffff" stroke="#2563eb" stroke-width="2.5" /><path d="M45 45 L55 55 M45 55 L55 45" stroke="#2563eb" stroke-width="1.5" /><circle cx="50" cy="15" r="3.5" fill="#1e40af" /><circle cx="50" cy="85" r="3.5" fill="#1e40af" /><circle cx="15" cy="50" r="3.5" fill="#1e40af" /><circle cx="85" cy="50" r="3.5" fill="#1e40af" /><circle cx="36" cy="36" r="3.5" fill="#2563eb" /><circle cx="64" cy="64" r="3.5" fill="#2563eb" /><circle cx="36" cy="64" r="3.5" fill="#2563eb" /><circle cx="64" cy="36" r="3.5" fill="#2563eb" /></svg>'

        # Flat HTML string to avoid Streamlit Markdown parser issues
        welcome_html = f'''<div class="login-ui-wrapper" style="margin-top: 0rem; padding-top: 0rem;"><div style="width: 150px; height: 150px; background: radial-gradient(circle, rgba(255,255,255,1) 0%, rgba(220,240,255,0.6) 45%, transparent 75%); border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; margin-bottom: 0rem; pointer-events: none;"><div style="position: absolute; width: 200px; height: 200px; background: radial-gradient(circle, rgba(255,255,255,0.5) 0%, rgba(230,245,255,0.1) 60%, transparent 100%); border-radius: 50%; z-index: -1;"></div><div style="z-index: 1; display: flex; flex-direction: column; align-items: center;">{logo_svg}<div style="color: #0f4c8a; font-size: 1.3rem; font-weight: 700; margin-top: 2px; letter-spacing: -0.5px;">PakPulse.AI</div><div style="color: #0c3e75; font-size: 0.5rem; font-weight: 700; letter-spacing: 1px; margin-top: 0px;">DISEASE EARLY WARNING SYSTEM</div></div></div><h1 style="color: #1e293b; font-size: 1.8rem; font-weight: 600; margin-top: 0.5rem; margin-bottom: 0.2rem; text-align: center; letter-spacing: -0.5px;">Welcome Back</h1><div style="max-width: 620px; text-align: center; color: #475569; font-size: 0.8rem; line-height: 1.3; margin-bottom: 0.5rem;">PakPulse AI is a comprehensive outbreak prediction and health surveillance ecosystem. Leveraging advanced AI models, real-time climate telemetry, and national epidemiological reports, we dynamically predict potential outbreaks and visualize disease risk levels across all districts. Our analytical platform empowers healthcare officers with proactive early warning signals to safeguard public wellness.</div><div style="color: #334155; font-size: 0.8rem; margin-bottom: 0.2rem; text-align: center; font-weight: 400;">Enter your personal details to use all of site features</div></div>'''
        st.markdown(welcome_html, unsafe_allow_html=True)

        # Buttons side by side
        col1, col2, col3, col4 = st.columns([1, 1.8, 1.8, 1])
        
        with col2:
            st.markdown('<div class="btn-login" style="width: 100%;">', unsafe_allow_html=True)
            if st.button("LOGIN", use_container_width=True):
                goto("login")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="btn-register" style="width: 100%;">', unsafe_allow_html=True)
            if st.button("REGISTER", use_container_width=True):
                goto("register")
            st.markdown('</div>', unsafe_allow_html=True)

        # Quick Admin & Officer Logins
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 0.2rem; margin-bottom: 0.2rem;'>Or continue directly as</p>", unsafe_allow_html=True)
        col_q1, col_q2, col_q3, col_q4 = st.columns([1, 1.8, 1.8, 1])
        
        with col_q2:
            st.markdown('<div class="btn-register" style="width: 100%;">', unsafe_allow_html=True)
            if st.button("ADMIN", key="btn_admin", use_container_width=True):
                if auth.quick_login("admin"):
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_q3:
            st.markdown('<div class="btn-register" style="width: 100%;">', unsafe_allow_html=True)
            if st.button("HEALTH OFFICER", key="btn_officer", use_container_width=True):
                if auth.quick_login("officer"):
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Footer Links and Copyright
        st.markdown("""
        <div style="width: 100%; display: flex; flex-direction: column; align-items: center; margin-top: 0.2rem; margin-bottom: 0.2rem;">
            <div style="color: #64748b; font-size: 0.85rem; display: flex; align-items: center; gap: 0.5rem; justify-content: center;">
                <span style="cursor: pointer; text-decoration: none;" onmouseover="this.style.color='#2563eb'" onmouseout="this.style.color='#64748b'">Privacy Policy</span> 
                <span style="color: #cbd5e1;">|</span> 
                <span style="cursor: pointer; text-decoration: none;" onmouseover="this.style.color='#2563eb'" onmouseout="this.style.color='#64748b'">Terms of Service</span> 
                <span style="color: #cbd5e1;">|</span> 
                <span style="cursor: pointer; text-decoration: none;" onmouseover="this.style.color='#2563eb'" onmouseout="this.style.color='#64748b'">Contact Us</span>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; position: fixed; bottom: 15px; left: 20px; right: 20px; color: #94a3b8; font-size: 0.8rem; pointer-events: none;">
            <span>© 2026 PakPulse AI. All rights reserved.</span>
            <span>© 2026 PakPulse AI. All rights reserved.</span>
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------- LOGIN PAGE ----------------------------
    elif st.session_state.welcome_page == "login":
        st.markdown("<h1 class='title'>Login</h1>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle'>Access your dashboard</p>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

        st.markdown(
            "<h3>Login Required</h3>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            "<p style='color:#666; font-size:0.9rem; margin-bottom:1.5rem;'>Please enter your username and password to access the system. Admin and Health Officer accounts require valid credentials.</p>",
            unsafe_allow_html=True
        )

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username (admin/officer/your_username)")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            # Forgot Password Link
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("")
            with col2:
                if st.form_submit_button("Forgot Password?", use_container_width=True, type="secondary"):
                    goto("forgot_password")
            
            submit = st.form_submit_button("Sign In", use_container_width=True)

        if submit:
            # Validate that both fields are provided
            if not username or not username.strip():
                st.error("Username is required. Please enter your username.")
            elif not password or not password.strip():
                st.error("Password is required. Please enter your password.")
            else:
                # Use the authenticate method which handles all user types (admin, officer, regular users)
                if auth.login(username.strip(), password):
                    user_info = auth.get_user_info(username.strip())
                    user_role = user_info.get("role", "viewer") if user_info else "viewer"
                    user_name = user_info.get("name", username.strip()) if user_info else username.strip()
                    
                    # Show role-specific welcome message
                    if user_role == "admin":
                        st.success(f"Welcome Admin, {user_name}!")
                    elif user_role == "officer":
                        st.success(f"Welcome Health Officer, {user_name}!")
                    else:
                        st.success(f"Welcome, {user_name}!")
                    
                    st.rerun()
                else:
                    st.error("Invalid username or password. Please check your credentials and try again.")

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Back to Home", use_container_width=True):
            goto("welcome")
    
    # ---------------------------- FORGOT PASSWORD PAGE ----------------------------
    elif st.session_state.welcome_page == "forgot_password":
        st.markdown("<h1 class='title'>Forgot Password</h1>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle'>Reset your password with OTP verification</p>", unsafe_allow_html=True)
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        
        # Initialize forgot password state
        if "forgot_password_step" not in st.session_state:
            st.session_state.forgot_password_step = "enter_email"
        if "forgot_password_email" not in st.session_state:
            st.session_state.forgot_password_email = ""
        if "forgot_password_username" not in st.session_state:
            st.session_state.forgot_password_username = ""
        if "forgot_password_otp" not in st.session_state:
            st.session_state.forgot_password_otp = ""
        
        # Step 1: Enter Email
        if st.session_state.forgot_password_step == "enter_email":
            st.markdown("<h3>Enter Your Email</h3>", unsafe_allow_html=True)
            st.markdown(
                "<p style='color:#666; font-size:0.9rem; margin-bottom:1.5rem;'>Enter the email address associated with your account. We'll send you an OTP to verify your identity.</p>",
                unsafe_allow_html=True
            )
            
            with st.form("forgot_password_email_form", clear_on_submit=False):
                email = st.text_input("Email Address", placeholder="Enter your registered email address")
                submit = st.form_submit_button("Send OTP", use_container_width=True)
            
            if submit:
                if not email or not email.strip():
                    st.error("Email is required. Please enter your email address.")
                else:
                    email_valid, email_error = validate_email(email.strip())
                    if not email_valid:
                        st.error(f"{email_error}")
                    else:
                        # Find user by email
                        user_info = auth.find_user_by_email(email.strip())
                        if not user_info:
                            st.error("No account found with this email address. Please check your email and try again.")
                        else:
                            # Generate and send OTP
                            otp = auth.generate_otp()
                            username = user_info['username']
                            auth.save_otp(email.strip(), otp, username)
                            
                            # Try to send email
                            email_sent, email_msg = auth.send_otp_email(email.strip(), otp, username)
                            
                            if email_sent:
                                st.success(f"{email_msg}")
                                st.session_state.forgot_password_step = "verify_otp"
                                st.session_state.forgot_password_email = email.strip()
                                st.session_state.forgot_password_username = username
                                st.rerun()
                            else:
                                # If email fails, show OTP in UI for development
                                st.warning(f"{email_msg}")
                                st.info(f"**Development Mode:** Since email is not configured, here is your OTP: **{otp}**\n\nThis OTP is valid for 10 minutes.")
                                st.session_state.forgot_password_step = "verify_otp"
                                st.session_state.forgot_password_email = email.strip()
                                st.session_state.forgot_password_username = username
                                st.session_state.forgot_password_otp = otp
                                st.rerun()
        
        # Step 2: Verify OTP
        elif st.session_state.forgot_password_step == "verify_otp":
            st.markdown("<h3>Verify OTP</h3>", unsafe_allow_html=True)
            st.markdown(
                f"<p style='color:#666; font-size:0.9rem; margin-bottom:1.5rem;'>We've sent an OTP to <strong>{st.session_state.forgot_password_email}</strong>. Please enter the 6-digit code you received.</p>",
                unsafe_allow_html=True
            )
            
            with st.form("forgot_password_otp_form", clear_on_submit=False):
                otp = st.text_input("Enter OTP", placeholder="Enter 6-digit OTP code", max_chars=6)
                submit = st.form_submit_button("Verify OTP", use_container_width=True)
            
            if submit:
                if not otp or len(otp) != 6:
                    st.error("Please enter a valid 6-digit OTP code.")
                else:
                    # Verify OTP
                    is_valid, result = auth.verify_otp(st.session_state.forgot_password_email, otp.strip())
                    if is_valid:
                        st.success("OTP verified successfully!")
                        st.session_state.forgot_password_step = "reset_password"
                        st.rerun()
                    else:
                        st.error(f"{result}")
        
        # Step 3: Reset Password
        elif st.session_state.forgot_password_step == "reset_password":
            st.markdown("<h3>Create New Password</h3>", unsafe_allow_html=True)
            st.markdown(
                "<p style='color:#666; font-size:0.9rem; margin-bottom:1.5rem;'>Please create a new strong password for your account.</p>",
                unsafe_allow_html=True
            )
            
            with st.form("forgot_password_reset_form", clear_on_submit=False):
                new_password = st.text_input("New Password", type="password", placeholder="Enter your new password")
                confirm_password = st.text_input("Confirm New Password", type="password", placeholder="Re-enter your new password")
                
                st.caption("Password Requirements: Minimum 8 characters, at least one uppercase letter, one lowercase letter, one digit, and one special character (!@#$%^&*(),.?\":{}|<>)")
                
                submit = st.form_submit_button("Reset Password", use_container_width=True)
            
            if submit:
                validation_errors = []
                
                # Validate password
                if not new_password:
                    validation_errors.append("New password is required.")
                else:
                    password_valid, password_error = validate_password(new_password)
                    if not password_valid:
                        validation_errors.append(f"{password_error}")
                
                # Check password confirmation
                if new_password and confirm_password and new_password != confirm_password:
                    validation_errors.append("Passwords do not match!")
                
                if validation_errors:
                    for error in validation_errors:
                        st.error(error)
                else:
                    # Reset password
                    success, msg = auth.reset_password(st.session_state.forgot_password_username, new_password)
                    if success:
                        st.success(f"{msg}")
                        st.info("Redirecting to login page...")
                        # Clear forgot password state
                        st.session_state.forgot_password_step = "enter_email"
                        st.session_state.forgot_password_email = ""
                        st.session_state.forgot_password_username = ""
                        st.session_state.forgot_password_otp = ""
                        # Wait a moment then redirect
                        import time
                        time.sleep(2)
                        goto("login")
                    else:
                        st.error(f"{msg}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("Back to Login", use_container_width=True):
            # Clear forgot password state
            st.session_state.forgot_password_step = "enter_email"
            st.session_state.forgot_password_email = ""
            st.session_state.forgot_password_username = ""
            st.session_state.forgot_password_otp = ""
            goto("login")

    # ---------------------------- REGISTER PAGE ----------------------------
    elif st.session_state.welcome_page == "register":
        st.markdown("<h1 class='title'>Create Account</h1>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle'>Join PakPulse AI today</p>", unsafe_allow_html=True)

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

        st.markdown(
            "<h3>Get Started</h3>",
            unsafe_allow_html=True
        )

        with st.form("register_form", clear_on_submit=False):
            full_name = st.text_input("Full Name", placeholder="Enter your full name (letters and spaces only)")
            email = st.text_input("Email", placeholder="Enter a valid email address (e.g., user@example.com)")
            new_username = st.text_input("Choose Username", placeholder="Pick a unique username")
            new_password = st.text_input("Choose Password", type="password", placeholder="Create a strong password")
            confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
            
            st.caption("Password Requirements: Minimum 8 characters, at least one uppercase letter, one lowercase letter, one digit, and one special character (!@#$%^&*(),.?\":{}|<>)")
            
            submit = st.form_submit_button("Create Account", use_container_width=True)

        if submit:
            # Validate all fields
            validation_errors = []
            
            # Validate name
            if not full_name:
                validation_errors.append("Full Name is required.")
            else:
                name_valid, name_error = validate_name(full_name)
                if not name_valid:
                    validation_errors.append(f"{name_error}")
            
            # Validate email
            if not email:
                validation_errors.append("Email is required.")
            else:
                email_valid, email_error = validate_email(email)
                if not email_valid:
                    validation_errors.append(f"{email_error}")
            
            # Validate username
            if not new_username:
                validation_errors.append("Username is required.")
            elif new_username.lower() in ["admin", "officer"]:
                validation_errors.append("Username is reserved! Please choose another.")
            
            # Validate password
            if not new_password:
                validation_errors.append("Password is required.")
            else:
                password_valid, password_error = validate_password(new_password)
                if not password_valid:
                    validation_errors.append(f"{password_error}")
            
            # Check password confirmation
            if new_password and confirm and new_password != confirm:
                validation_errors.append("Passwords do not match!")
            
            # Show all validation errors or proceed with registration
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            else:
                success, msg = auth.register(
                    name=full_name,
                    email=email,
                    username=new_username,
                    password=new_password,
                    role="viewer",
                )
                if success:
                    st.success("Account created successfully! Redirecting to login...")
                    goto("login")
                else:
                    st.error(f"{msg}")

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Back to Home", use_container_width=True):
            goto("welcome")


# -------------------------------------------------------------------
#  OPTIONAL: small helper if you want to call from app.py
# -------------------------------------------------------------------

def ensure_authenticated_page(auth: AuthManager):
    """
    Call this from app.py:
        auth = AuthManager()
        if not auth.is_authenticated():
            show_welcome_page(auth)
            st.stop()
    """
    if not auth.is_authenticated():
        show_welcome_page(auth)
        st.stop()
