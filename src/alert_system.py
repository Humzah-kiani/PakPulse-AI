"""
Alert System Module for PakPulse AI
Handles email/SMS alerts when disease risk thresholds are crossed
"""

import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from src.data_loader import DataLoader
from src.risk_calculator import RiskCalculator

# Load environment variables
load_dotenv()

def normalize_phone_number(phone: str) -> str:
    """
    Convert phone number to E.164 format for Twilio
    
    Args:
        phone: Phone number in any format
        
    Returns:
        Phone number in E.164 format (e.g., +923125110768)
    """
    if not phone:
        return ""
    
    # Remove all spaces, dashes, and parentheses
    phone = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # If already in E.164 format, return as is
    if phone.startswith("+"):
        return phone
    
    # Handle Pakistani numbers (starting with 0)
    if phone.startswith("0"):
        # Remove leading 0 and add +92
        return "+92" + phone[1:]
    
    # Handle numbers without country code (assume Pakistan)
    if len(phone) == 10 and phone[0] in ["3", "4", "5"]:
        return "+92" + phone
    
    # If it's 11 digits starting with 92, add +
    if len(phone) == 11 and phone.startswith("92"):
        return "+" + phone
    
    # If it's 12 digits starting with 923, add +
    if len(phone) == 12 and phone.startswith("923"):
        return "+" + phone
    
    # Return as is if we can't determine format
    return phone

class AlertSystem:
    """Class to handle alert system functionality"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize AlertSystem
        
        Args:
            config_file: Path to alert configuration file
        """
        self.config_file = config_file or Path("data/alert_config.json")
        self.loader = DataLoader()
        self.calculator = RiskCalculator()
        self.alert_history_file = Path("data/alert_history.json")
        self.load_config()
        self.load_alert_history()
    
    def load_config(self) -> Dict:
        """Load alert configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except:
                self.config = self.get_default_config()
                self.save_config()
        else:
            self.config = self.get_default_config()
            self.save_config()
        return self.config
    
    def get_default_config(self) -> Dict:
        """Get default alert configuration"""
        # Load Twilio credentials from environment or use provided defaults
        default_account_sid = os.getenv("TWILIO_ACCOUNT_SID", "ACfca66b2a92904ef1db572a6955c9ceae")
        default_auth_token = os.getenv("TWILIO_AUTH_TOKEN", "f216e55b110a40e18580e0248747ccdf")
        
        return {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "",
                "sender_password": "",
                "recipients": []
            },
            "sms": {
                "enabled": True,  # Enable by default if credentials are provided
                "twilio_account_sid": default_account_sid,
                "twilio_auth_token": default_auth_token,
                "twilio_phone_number": os.getenv("TWILIO_PHONE_NUMBER", "+12055551234"),
                "recipients": ["+923125110768"]  # Default recipient (converted from 03125110768)
            },
            "thresholds": {
                "covid19": 70,       # Disease.sh API
                "dengue": 70,        # Epidemic Forecasting API
                "influenza": 70,     # WHO GHO API
                "malaria": 70,       # WHO GHO API
                "cholera": 70,       # WHO GHO API
                "pneumonia": 70,     # Local CSV
                "tuberculosis": 75,  # Local CSV - Higher threshold due to chronic nature
                "typhoid": 70,       # Local CSV
                "hepatitis_a": 65    # Local CSV
            },
            "alert_frequency": "daily"  # daily, weekly, immediate
        }
    
    def save_config(self) -> None:
        """Save alert configuration"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def load_alert_history(self) -> List[Dict]:
        """Load alert history"""
        if self.alert_history_file.exists():
            try:
                with open(self.alert_history_file, 'r') as f:
                    self.alert_history = json.load(f)
            except:
                self.alert_history = []
        else:
            self.alert_history = []
        return self.alert_history
    
    def save_alert_history(self) -> None:
        """Save alert history"""
        self.alert_history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.alert_history_file, 'w') as f:
            json.dump(self.alert_history, f, indent=2)
    
    def check_risk_thresholds(self, disease_data: pd.DataFrame) -> List[Dict]:
        """
        Check if any districts exceed risk thresholds
        
        Args:
            disease_data: DataFrame with disease risk data
            
        Returns:
            List of alerts that should be triggered
        """
        alerts = []
        thresholds = self.config.get("thresholds", {})
        
        # Get latest data for each district-disease combination
        # Use as_index=False and include_groups=False to avoid FutureWarning
        latest_data = disease_data.groupby(['district', 'disease'], as_index=False, group_keys=False).apply(
            lambda x: x.loc[x['date'].idxmax()], include_groups=False
        ).reset_index(drop=True)
        
        for _, row in latest_data.iterrows():
            district = row['district']
            disease = row['disease']
            risk_index = row['risk_index']
            threshold = thresholds.get(disease, 70)
            
            if risk_index >= threshold:
                alerts.append({
                    "district": district,
                    "disease": disease,
                    "risk_index": float(risk_index),
                    "threshold": threshold,
                    "date": row['date'].strftime('%Y-%m-%d') if 'date' in row else datetime.now().strftime('%Y-%m-%d'),
                    "status": "pending"
                })
        
        return alerts
    
    def send_email_alert(self, alert: Dict) -> bool:
        """
        Send email alert
        
        Args:
            alert: Alert dictionary with district, disease, risk_index, etc.
            
        Returns:
            True if sent successfully, False otherwise
        """
        email_config = self.config.get("email", {})
        
        if not email_config.get("enabled", False):
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config.get("sender_email", "")
            msg['To'] = ", ".join(email_config.get("recipients", []))
            msg['Subject'] = f"Alert: {alert['disease'].title()} Risk Alert - {alert['district']}"
            
            # Create email body
            body = f"""
            <html>
            <body style='font-family: Arial, sans-serif;'>
                <h2 style='color: #F44336;'>Disease Risk Alert</h2>
                <div style='background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;'>
                    <h3>Alert Details</h3>
                    <p><strong>District:</strong> {alert['district']}</p>
                    <p><strong>Disease:</strong> {alert['disease'].title()}</p>
                    <p><strong>Risk Index:</strong> {alert['risk_index']:.1f}/100</p>
                    <p><strong>Threshold:</strong> {alert['threshold']}/100</p>
                    <p><strong>Date:</strong> {alert['date']}</p>
                </div>
                <div style='background: #e3f2fd; padding: 15px; margin: 20px 0;'>
                    <h3>Recommended Actions</h3>
                    <ul>
                        <li>Review current surveillance data for {alert['district']}</li>
                        <li>Consider increasing monitoring and preventive measures</li>
                        <li>Alert local health authorities if risk continues to rise</li>
                        <li>Prepare response resources if needed</li>
                    </ul>
                </div>
                <p style='color: #666; font-size: 0.9em;'>
                    This is an automated alert from PakPulse AI - Disease Early Warning System
                </p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(email_config.get("smtp_server", "smtp.gmail.com"), 
                                 email_config.get("smtp_port", 587))
            server.starttls()
            server.login(email_config.get("sender_email", ""), 
                        email_config.get("sender_password", ""))
            text = msg.as_string()
            server.sendmail(email_config.get("sender_email", ""), 
                          email_config.get("recipients", []), text)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def send_sms_alert(self, alert: Dict) -> bool:
        """
        Send SMS alert using Twilio API
        
        Args:
            alert: Alert dictionary with disease, district, risk_index, etc.
            
        Returns:
            True if sent successfully, False otherwise
        """
        sms_config = self.config.get("sms", {})
        
        if not sms_config.get("enabled", False):
            return False
        
        # Get credentials from config or environment variables
        account_sid = sms_config.get("twilio_account_sid", "") or os.getenv("TWILIO_ACCOUNT_SID", "")
        auth_token = sms_config.get("twilio_auth_token", "") or os.getenv("TWILIO_AUTH_TOKEN", "")
        twilio_phone = sms_config.get("twilio_phone_number", "") or os.getenv("TWILIO_PHONE_NUMBER", "")
        recipients = sms_config.get("recipients", [])
        
        if not account_sid or not auth_token or not twilio_phone:
            print("Warning: Twilio credentials not configured")
            return False
        
        if not recipients:
            print("Warning: No SMS recipients configured")
            return False
        
        try:
            from twilio.rest import Client
            
            # Initialize Twilio client
            client = Client(account_sid, auth_token)
            
            # Create alert message
            disease = alert.get('disease', 'Unknown').title()
            district = alert.get('district', 'Unknown')
            risk_index = alert.get('risk_index', 0)
            risk_level = alert.get('risk_level', 'Unknown')
            cases = alert.get('cases_reported', 0)
            
            message_body = (
                f"PakPulse Alert: {disease} outbreak detected!\n"
                f"District: {district}\n"
                f"Risk Level: {risk_level} ({risk_index:.1f}/100)\n"
                f"Cases: {cases}\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"Take necessary precautions!"
            )
            
            # Send SMS to all recipients
            success_count = 0
            error_details = []
            
            for recipient in recipients:
                try:
                    # Normalize phone number to E.164 format
                    normalized_recipient = normalize_phone_number(recipient)
                    
                    if not normalized_recipient.startswith("+"):
                        error_msg = f"Invalid phone number format: {recipient} (normalized: {normalized_recipient})"
                        print(f"âœ— {error_msg}")
                        error_details.append(error_msg)
                        continue
                    
                    # Send SMS
                    message = client.messages.create(
                        body=message_body,
                        from_=twilio_phone,
                        to=normalized_recipient
                    )
                    
                    print(f"âœ“ SMS sent to {normalized_recipient} (SID: {message.sid})")
                    print(f"  Status: {message.status}, Price: {message.price}")
                    success_count += 1
                    
                except Exception as e:
                    error_msg = str(e)
                    
                    # Provide helpful error messages
                    if "unverified" in error_msg.lower() or "21608" in error_msg:
                        detailed_msg = f"Phone number {normalized_recipient} is not verified. Verify it at: https://console.twilio.com/us1/develop/phone-numbers/manage/verified"
                    elif "unauthorized" in error_msg.lower() or "20003" in error_msg:
                        detailed_msg = "Authentication failed. Check Account SID and Auth Token."
                    elif "insufficient" in error_msg.lower() or "balance" in error_msg.lower():
                        detailed_msg = "Insufficient Twilio account balance. Add credits to send SMS."
                    else:
                        detailed_msg = error_msg
                    
                    full_error = f"Failed to send SMS to {normalized_recipient}: {detailed_msg}"
                    print(f"âœ— {full_error}")
                    error_details.append(full_error)
                    # Log detailed error for debugging
                    import traceback
                    traceback.print_exc()
            
            # Store error details in alert for debugging
            if error_details:
                alert['sms_errors'] = error_details
            
            return success_count > 0
            
        except ImportError:
            print("Error: Twilio library not installed. Run: pip install twilio")
            return False
        except Exception as e:
            print(f"Error sending SMS: {str(e)}")
            return False
    
    def process_alerts(self, disease_data: pd.DataFrame) -> List[Dict]:
        """
        Process all alerts and send notifications
        
        Args:
            disease_data: DataFrame with disease risk data
            
        Returns:
            List of processed alerts with status
        """
        alerts = self.check_risk_thresholds(disease_data)
        processed_alerts = []
        
        for alert in alerts:
            alert_id = f"{alert['district']}_{alert['disease']}_{alert['date']}"
            
            # Check if alert was already sent (based on frequency setting)
            if self.should_send_alert(alert_id):
                # Send email
                email_sent = self.send_email_alert(alert)
                
                # Send SMS
                sms_sent = self.send_sms_alert(alert)
                
                alert['status'] = 'sent' if (email_sent or sms_sent) else 'failed'
                alert['email_sent'] = email_sent
                alert['sms_sent'] = sms_sent
                alert['alert_id'] = alert_id
                alert['timestamp'] = datetime.now().isoformat()
                
                # Add to history
                self.alert_history.append(alert)
                processed_alerts.append(alert)
        
        # Save history
        if processed_alerts:
            self.save_alert_history()
        
        return processed_alerts
    
    def should_send_alert(self, alert_id: str) -> bool:
        """
        Check if alert should be sent based on frequency setting
        
        Args:
            alert_id: Unique alert identifier
            
        Returns:
            True if alert should be sent
        """
        frequency = self.config.get("alert_frequency", "daily")
        
        # Check if this alert was already sent today
        today = datetime.now().strftime('%Y-%m-%d')
        recent_alerts = [
            a for a in self.alert_history 
            if a.get('alert_id') == alert_id and 
            a.get('timestamp', '').startswith(today)
        ]
        
        if frequency == "immediate":
            return len(recent_alerts) == 0
        elif frequency == "daily":
            return len(recent_alerts) == 0
        elif frequency == "weekly":
            # Check if sent in last 7 days
            from datetime import timedelta
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            recent_alerts = [
                a for a in self.alert_history 
                if a.get('alert_id') == alert_id and 
                a.get('timestamp', '') > week_ago
            ]
            return len(recent_alerts) == 0
        
        return True
    
    def get_alert_history(self, limit: int = 50) -> List[Dict]:
        """
        Get recent alert history
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        return self.alert_history[-limit:]
    
    def update_threshold(self, disease: str, threshold: int) -> None:
        """
        Update risk threshold for a disease
        
        Args:
            disease: Disease name
            threshold: New threshold value (0-100)
        """
        if "thresholds" not in self.config:
            self.config["thresholds"] = {}
        
        self.config["thresholds"][disease] = max(0, min(100, threshold))
        self.save_config()
    
    def update_email_config(self, enabled: bool, smtp_server: str, smtp_port: int,
                           sender_email: str, sender_password: str, recipients: List[str]) -> None:
        """
        Update email configuration
        
        Args:
            enabled: Enable/disable email alerts
            smtp_server: SMTP server address
            smtp_port: SMTP port
            sender_email: Sender email address
            sender_password: Sender password
            recipients: List of recipient email addresses
        """
        self.config["email"] = {
            "enabled": enabled,
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "sender_email": sender_email,
            "sender_password": sender_password,
            "recipients": recipients
        }
        self.save_config()
    
    def update_sms_config(self, enabled: bool, account_sid: str, auth_token: str,
                         phone_number: str, recipients: List[str]) -> None:
        """
        Update SMS configuration
        
        Args:
            enabled: Enable/disable SMS alerts
            account_sid: Twilio account SID
            auth_token: Twilio auth token
            phone_number: Twilio phone number
            recipients: List of recipient phone numbers (will be normalized to E.164)
        """
        # Normalize all phone numbers to E.164 format
        normalized_recipients = [normalize_phone_number(r) for r in recipients if r.strip()]
        normalized_phone = normalize_phone_number(phone_number) if phone_number else phone_number
        
        self.config["sms"] = {
            "enabled": enabled,
            "twilio_account_sid": account_sid,
            "twilio_auth_token": auth_token,
            "twilio_phone_number": normalized_phone,
            "recipients": normalized_recipients
        }
        self.save_config()
        
        # Print normalized numbers for verification
        if normalized_recipients:
            print(f"âœ“ SMS recipients normalized to E.164 format:")
            for orig, norm in zip(recipients, normalized_recipients):
                if orig != norm:
                    print(f"  {orig} â†’ {norm}")
                else:
                    print(f"  {norm}")


def send_test_email(smtp_server: str, smtp_port: int, sender_email: str, 
                   sender_password: str, recipients: List[str], 
                   subject: str, body: str) -> bool:
    """
    Standalone function to send a test email
    
    Args:
        smtp_server: SMTP server address
        smtp_port: SMTP port number
        sender_email: Sender email address
        sender_password: Sender password
        recipients: List of recipient email addresses
        subject: Email subject
        body: Email body (HTML format)
        
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject
        
        # Attach HTML body
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipients, text)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error sending test email: {str(e)}")
        return False

