"""
API Configuration Module for PakPulse AI
Manages API settings and authentication for disease data API
"""

import json
from pathlib import Path
from typing import Dict, Optional
from enum import Enum

# Configuration file path
CONFIG_DIR = Path(__file__).parent.parent / "data"
CONFIG_FILE = CONFIG_DIR / "api_config.json"


class AuthMethod(str, Enum):
    """Authentication methods"""
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"


class APIConfig:
    """Class to manage API configuration"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize APIConfig
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file or CONFIG_FILE
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """
        Load API configuration from file
        
        Returns:
            Dictionary with API configuration
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return config
            except Exception as e:
                print(f"Warning: Could not load API config: {e}")
                return self.get_default_config()
        else:
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """
        Get default API configuration
        
        Returns:
            Default configuration dictionary
        """
        return {
            "enabled": False,
            "base_url": "",
            "endpoints": {
                "disease_risk_data": "/api/disease-risk-data",
                "districts": "/api/districts"
            },
            "authentication": {
                "method": "none",  # none, api_key, bearer_token, basic_auth
                "api_key": "",
                "bearer_token": "",
                "username": "",
                "password": ""
            },
            "timeout": 30,  # seconds
            "retry_attempts": 3,
            "cache_duration": 300,  # seconds (5 minutes)
            "rate_limit": {
                "enabled": False,
                "requests_per_minute": 60
            }
        }
    
    def save_config(self) -> None:
        """Save API configuration to file"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def is_enabled(self) -> bool:
        """Check if API is enabled"""
        return self.config.get("enabled", False) and bool(self.config.get("base_url"))
    
    def get_base_url(self) -> str:
        """Get API base URL"""
        return self.config.get("base_url", "")
    
    def get_endpoint(self, endpoint_name: str) -> str:
        """
        Get full endpoint URL
        
        Args:
            endpoint_name: Name of endpoint (disease_risk_data, districts)
            
        Returns:
            Full endpoint URL
        """
        base_url = self.get_base_url().rstrip('/')
        endpoint_path = self.config.get("endpoints", {}).get(endpoint_name, "")
        return f"{base_url}{endpoint_path}"
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers based on configured method
        
        Returns:
            Dictionary with authentication headers
        """
        auth_config = self.config.get("authentication", {})
        method = auth_config.get("method", "none")
        headers = {}
        
        if method == "api_key":
            api_key = auth_config.get("api_key", "")
            if api_key:
                # Try common API key header formats
                headers["X-API-Key"] = api_key
                headers["Authorization"] = f"ApiKey {api_key}"
        elif method == "bearer_token":
            token = auth_config.get("bearer_token", "")
            if token:
                headers["Authorization"] = f"Bearer {token}"
        elif method == "basic_auth":
            # Basic auth is handled in requests.get() with auth parameter
            pass
        
        return headers
    
    def get_auth_credentials(self) -> Optional[tuple]:
        """
        Get basic auth credentials if configured
        
        Returns:
            Tuple of (username, password) or None
        """
        auth_config = self.config.get("authentication", {})
        if auth_config.get("method") == "basic_auth":
            username = auth_config.get("username", "")
            password = auth_config.get("password", "")
            if username and password:
                return (username, password)
        return None
    
    def get_timeout(self) -> int:
        """Get request timeout in seconds"""
        return self.config.get("timeout", 30)
    
    def get_retry_attempts(self) -> int:
        """Get number of retry attempts"""
        return self.config.get("retry_attempts", 3)
    
    def get_cache_duration(self) -> int:
        """Get cache duration in seconds"""
        return self.config.get("cache_duration", 300)
    
    def update_config(self, **kwargs) -> None:
        """
        Update configuration values
        
        Args:
            **kwargs: Configuration key-value pairs to update
        """
        for key, value in kwargs.items():
            if '.' in key:
                # Handle nested keys (e.g., "authentication.method")
                keys = key.split('.')
                config = self.config
                for k in keys[:-1]:
                    if k not in config:
                        config[k] = {}
                    config = config[k]
                config[keys[-1]] = value
            else:
                self.config[key] = value
        self.save_config()
    
    def set_api_details(self, base_url: str, auth_method: str = "none", 
                       api_key: Optional[str] = None,
                       bearer_token: Optional[str] = None,
                       username: Optional[str] = None,
                       password: Optional[str] = None) -> None:
        """
        Set API details and enable API
        
        Args:
            base_url: API base URL
            auth_method: Authentication method (none, api_key, bearer_token, basic_auth)
            api_key: API key (if using api_key method)
            bearer_token: Bearer token (if using bearer_token method)
            username: Username (if using basic_auth method)
            password: Password (if using basic_auth method)
        """
        self.config["enabled"] = True
        self.config["base_url"] = base_url.rstrip('/')
        self.config["authentication"]["method"] = auth_method
        
        if auth_method == "api_key" and api_key:
            self.config["authentication"]["api_key"] = api_key
        elif auth_method == "bearer_token" and bearer_token:
            self.config["authentication"]["bearer_token"] = bearer_token
        elif auth_method == "basic_auth" and username and password:
            self.config["authentication"]["username"] = username
            self.config["authentication"]["password"] = password
        
        self.save_config()

