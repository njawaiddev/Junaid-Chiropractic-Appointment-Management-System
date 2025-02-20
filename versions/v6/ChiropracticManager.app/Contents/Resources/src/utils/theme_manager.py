from datetime import datetime
import json
import os
from pathlib import Path
import customtkinter as ctk
from tkinter import ttk

# Dark Mode Color Palette
DARK_MODE = {
    # Primary Colors
    'PRIMARY_BG': '#1A1B1E',
    'SECONDARY_BG': '#2C2D31',
    'SURFACE_BG': '#373A40',
    
    # Text Colors
    'TEXT_PRIMARY': '#FFFFFF',
    'TEXT_SECONDARY': '#A6A7AB',
    'TEXT_MUTED': '#6C6D70',
    
    # Accent Colors
    'PRIMARY_BLUE': '#3B82F6',
    'PRIMARY_DARK': '#2563EB',
    'PRIMARY_LIGHT': '#1E3A8A',
    
    # Status Colors
    'SUCCESS_GREEN': '#059669',
    'WARNING_AMBER': '#D97706',
    'ERROR_RED': '#DC2626',
    
    # Border Colors
    'BORDER_LIGHT': '#373A40',
    'BORDER_FOCUS': '#3B82F6'
}

# Light Mode Color Palette
LIGHT_MODE = {
    'PRIMARY_BG': '#FFFFFF',
    'SECONDARY_BG': '#F8FAFC',
    'SURFACE_BG': '#F1F5F9',
    
    'TEXT_PRIMARY': '#1E293B',
    'TEXT_SECONDARY': '#475569',
    'TEXT_MUTED': '#94A3B8',
    
    'PRIMARY_BLUE': '#2196F3',
    'PRIMARY_DARK': '#1976D2',
    'PRIMARY_LIGHT': '#E3F2FD',
    
    'SUCCESS_GREEN': '#10B981',
    'WARNING_AMBER': '#F59E0B',
    'ERROR_RED': '#EF4444',
    
    'BORDER_LIGHT': '#E2E8F0',
    'BORDER_FOCUS': '#2196F3'
}

class ThemeManager:
    def __init__(self):
        self.config_path = Path.home() / '.chiropractic_app' / 'theme_config.json'
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.load_config()
        
    def load_config(self):
        """Load theme configuration from file"""
        default_config = {
            'theme_mode': 'light',
            'auto_switch': False,
            'day_start': '07:00',
            'night_start': '19:00',
            'follow_system': True,
            'transitions_enabled': True
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = {**default_config, **json.load(f)}
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save current theme configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def get_current_theme(self):
        """Get the current theme colors based on settings and time"""
        if self.config['auto_switch']:
            current_time = datetime.now().time()
            day_start = datetime.strptime(self.config['day_start'], '%H:%M').time()
            night_start = datetime.strptime(self.config['night_start'], '%H:%M').time()
            
            is_night = current_time >= night_start or current_time < day_start
            return DARK_MODE if is_night else LIGHT_MODE
        
        return DARK_MODE if self.config['theme_mode'] == 'dark' else LIGHT_MODE
    
    def toggle_theme(self):
        """Toggle between light and dark mode"""
        self.config['theme_mode'] = 'light' if self.config['theme_mode'] == 'dark' else 'dark'
        self.save_config()
        return self.get_current_theme()
    
    def set_auto_switch(self, enabled: bool, day_start: str = None, night_start: str = None):
        """Configure automatic theme switching"""
        self.config['auto_switch'] = enabled
        if day_start:
            self.config['day_start'] = day_start
        if night_start:
            self.config['night_start'] = night_start
        self.save_config()
    
    def set_follow_system(self, enabled: bool):
        """Configure system theme following"""
        self.config['follow_system'] = enabled
        self.save_config()
    
    def set_transitions(self, enabled: bool):
        """Configure theme transition animations"""
        self.config['transitions_enabled'] = enabled
        self.save_config()
    
    def apply_theme(self, root_widget):
        """Apply current theme to the application"""
        theme = self.get_current_theme()
        
        # Configure CustomTkinter appearance
        ctk.set_appearance_mode("dark" if theme == DARK_MODE else "light")
        
        # Apply theme colors to root widget
        root_widget.configure(fg_color=theme['PRIMARY_BG'])
        
        # Configure ttk styles
        style = ttk.Style()
        style.configure(
            "Treeview",
            background=theme['SURFACE_BG'],
            foreground=theme['TEXT_PRIMARY'],
            fieldbackground=theme['SURFACE_BG']
        )
        style.configure(
            "Treeview.Heading",
            background=theme['SECONDARY_BG'],
            foreground=theme['TEXT_PRIMARY']
        )
        style.map(
            "Treeview",
            background=[("selected", theme['PRIMARY_BLUE'])],
            foreground=[("selected", theme['TEXT_PRIMARY'])]
        ) 