"""
Error Handling Module for PakPulse AI
Provides consistent error handling across the application
"""

import streamlit as st
from typing import Optional, Callable
import traceback

def handle_error(error: Exception, context: str = "", show_traceback: bool = False) -> None:
    """
    Display error message in Streamlit
    
    Args:
        error: Exception object
        context: Context where error occurred
        show_traceback: Whether to show full traceback
    """
    error_msg = f"**Error{': ' + context if context else ''}**\n\n{str(error)}"
    
    if show_traceback:
        error_msg += f"\n\n**Traceback:**\n```\n{traceback.format_exc()}\n```"
    
    st.error(error_msg)
    
    # Also log to console for debugging
    print(f"ERROR [{context}]: {str(error)}")
    if show_traceback:
        print(traceback.format_exc())

def safe_execute(func: Callable, context: str = "", default_return=None, show_traceback: bool = False):
    """
    Safely execute a function with error handling
    
    Args:
        func: Function to execute
        context: Context description
        default_return: Value to return on error
        show_traceback: Whether to show traceback
        
    Returns:
        Function result or default_return on error
    """
    try:
        return func()
    except Exception as e:
        handle_error(e, context, show_traceback)
        return default_return

def show_loading_state(message: str = "Loading..."):
    """
    Context manager for showing loading state
    
    Usage:
        with show_loading_state("Loading data..."):
            # code here
    """
    return st.spinner(message)

def handle_api_error(error: Exception, api_name: str = "API", fallback_message: str = "") -> None:
    """
    Handle API-specific errors with helpful messages
    
    Args:
        error: Exception object
        api_name: Name of the API
        fallback_message: Message to show if API fails
    """
    error_type = type(error).__name__
    
    if "ConnectionError" in error_type or "Timeout" in error_type:
        error_msg = f"**{api_name} Connection Error**\n\n"
        error_msg += "Could not connect to the API. Please check:\n"
        error_msg += "- API server is running\n"
        error_msg += "- Network connection is active\n"
        error_msg += "- API URL is correct\n"
        if fallback_message:
            error_msg += f"\n{fallback_message}"
    elif "HTTPError" in error_type or "401" in str(error) or "403" in str(error):
        error_msg = f"**{api_name} Authentication Error**\n\n"
        error_msg += "Authentication failed. Please check:\n"
        error_msg += "- API credentials are correct\n"
        error_msg += "- API key/token is valid\n"
        error_msg += "- Authentication method is correct\n"
    elif "404" in str(error):
        error_msg = f"**{api_name} Not Found**\n\n"
        error_msg += "API endpoint not found. Please check:\n"
        error_msg += "- API endpoint URL is correct\n"
        error_msg += "- API server is configured properly\n"
    else:
        error_msg = f"**{api_name} Error**\n\n{str(error)}"
        if fallback_message:
            error_msg += f"\n\n{fallback_message}"
    
    st.error(error_msg)
    print(f"API ERROR [{api_name}]: {str(error)}")

