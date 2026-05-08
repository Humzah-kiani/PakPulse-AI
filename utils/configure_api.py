"""
Utility script to configure API settings for PakPulse AI
Run this script to set up your disease data API
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.api_config import APIConfig, AuthMethod

def configure_api_interactive():
    """Interactive API configuration"""
    print("=" * 60)
    print("PakPulse AI - API Configuration")
    print("=" * 60)
    print()
    
    config = APIConfig()
    
    # Check if already configured
    if config.is_enabled():
        print(f"Current API Configuration:")
        print(f"  Base URL: {config.get_base_url()}")
        print(f"  Enabled: {config.is_enabled()}")
        print()
        response = input("API is already configured. Update? (y/n): ").strip().lower()
        if response != 'y':
            print("Configuration cancelled.")
            return
    
    print("Enter API details (press Enter to skip):")
    print()
    
    # Base URL
    base_url = input("API Base URL (e.g., https://api.example.com): ").strip()
    if not base_url:
        print("Base URL is required. Configuration cancelled.")
        return
    
    # Authentication method
    print("\nAuthentication Method:")
    print("  1. None (no authentication)")
    print("  2. API Key")
    print("  3. Bearer Token")
    print("  4. Basic Auth (username/password)")
    
    auth_choice = input("Select method (1-4): ").strip()
    
    auth_method = "none"
    api_key = None
    bearer_token = None
    username = None
    password = None
    
    if auth_choice == "2":
        auth_method = "api_key"
        api_key = input("API Key: ").strip()
    elif auth_choice == "3":
        auth_method = "bearer_token"
        bearer_token = input("Bearer Token: ").strip()
    elif auth_choice == "4":
        auth_method = "basic_auth"
        username = input("Username: ").strip()
        password = input("Password: ").strip()
    
    # Optional settings
    print("\nOptional Settings (press Enter for defaults):")
    timeout = input("Request timeout in seconds (default: 30): ").strip()
    timeout = int(timeout) if timeout else 30
    
    retry_attempts = input("Retry attempts (default: 3): ").strip()
    retry_attempts = int(retry_attempts) if retry_attempts else 3
    
    cache_duration = input("Cache duration in seconds (default: 300): ").strip()
    cache_duration = int(cache_duration) if cache_duration else 300
    
    # Set configuration
    config.set_api_details(
        base_url=base_url,
        auth_method=auth_method,
        api_key=api_key,
        bearer_token=bearer_token,
        username=username,
        password=password
    )
    
    config.update_config(
        timeout=timeout,
        retry_attempts=retry_attempts,
        cache_duration=cache_duration
    )
    
    print("\n" + "=" * 60)
    print("API Configuration Saved Successfully!")
    print("=" * 60)
    print(f"Base URL: {config.get_base_url()}")
    print(f"Authentication: {auth_method}")
    print(f"Timeout: {timeout}s")
    print(f"Retry Attempts: {retry_attempts}")
    print(f"Cache Duration: {cache_duration}s")
    print("\nConfiguration file: data/api_config.json")
    print("\nYou can now use the API by enabling it in your application.")


if __name__ == "__main__":
    try:
        configure_api_interactive()
    except KeyboardInterrupt:
        print("\n\nConfiguration cancelled by user.")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)

