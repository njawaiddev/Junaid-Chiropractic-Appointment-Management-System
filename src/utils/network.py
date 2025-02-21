import socket
import tkinter as tk
from tkinter import messagebox
import json
import os

def check_internet_connection(timeout=3):
    """
    Check if there is an active internet connection
    Returns: bool - True if connected, False otherwise
    """
    try:
        # Try to connect to a reliable host
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        return False

def show_offline_prompt():
    """
    Show a dialog asking if the user wants to continue without internet
    Returns: bool - True if user wants to continue, False otherwise
    """
    response = messagebox.askyesno(
        "No Internet Connection",
        "No internet connection detected. Some features like Google Calendar sync " +
        "and backups may not work.\n\nDo you want to continue anyway?",
        icon="warning"
    )
    return response

def should_attempt_gcal_sync(app_data_dir):
    """
    Check if Google Calendar sync should be attempted based on network status and user preference
    Returns: bool - True if sync should be attempted
    """
    try:
        # First check if we have internet
        if not check_internet_connection():
            return False
            
        # Check sync configuration
        sync_config_file = os.path.join(app_data_dir, "sync_config.json")
        if os.path.exists(sync_config_file):
            with open(sync_config_file, 'r') as f:
                sync_config = json.load(f)
                return sync_config.get('auto_sync', True)
        return True  # Default to True if no config exists
    except Exception:
        return False  # If any error occurs, don't attempt sync 