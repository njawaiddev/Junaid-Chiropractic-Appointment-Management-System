import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime
import os
import shutil
import json
from utils.colors import *

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.backup_config_file = os.path.join(self.db._get_app_data_dir(), "backup_config.json")
        self.load_backup_config()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Configure colors
        self.configure(fg_color=BG_WHITE)
        
        self.setup_ui()
    
    def load_backup_config(self):
        """Load backup configuration from file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.backup_config_file), exist_ok=True)
            
            if os.path.exists(self.backup_config_file):
                with open(self.backup_config_file, 'r') as f:
                    self.backup_config = json.load(f)
            else:
                self.backup_config = {
                    'schedule': 'never',
                    'last_backup': None,
                    'backup_path': os.path.join(self.db._get_app_data_dir(), 'backups')
                }
                self.save_backup_config()
        except Exception as e:
            print(f"Error loading backup config: {str(e)}")
            self.backup_config = {
                'schedule': 'never',
                'last_backup': None,
                'backup_path': os.path.join(self.db._get_app_data_dir(), 'backups')
            }
    
    def save_backup_config(self):
        """Save backup configuration to file"""
        try:
            with open(self.backup_config_file, 'w') as f:
                json.dump(self.backup_config, f)
        except Exception as e:
            print(f"Error saving backup config: {str(e)}")
    
    def setup_ui(self):
        """Initialize settings UI components"""
        # Title
        title_frame = ctk.CTkFrame(self, fg_color=BG_WHITE)
        title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="Settings",
            font=("Helvetica", 24, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")
        
        # Main content
        content = ctk.CTkScrollableFrame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1)
        
        # Backup Section
        self.setup_backup_section(content)
    
    def setup_backup_section(self, parent):
        """Setup backup settings section"""
        # Backup header
        backup_header = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        backup_header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            backup_header,
            text="Database Backup",
            font=("Helvetica", 18, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")
        
        # Manual backup
        manual_frame = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        manual_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            manual_frame,
            text="Backup Now",
            command=self.manual_backup,
            font=("Helvetica", 12),
            height=36,
            corner_radius=18
        ).pack(side="left", padx=5)
        
        if self.backup_config['last_backup']:
            last_backup = datetime.fromisoformat(self.backup_config['last_backup'])
            last_backup_text = f"Last backup: {last_backup.strftime('%Y-%m-%d %H:%M')}"
        else:
            last_backup_text = "No previous backup"
        
        self.last_backup_label = ctk.CTkLabel(
            manual_frame,
            text=last_backup_text,
            font=("Helvetica", 12),
            text_color=TEXT_SECONDARY
        )
        self.last_backup_label.pack(side="left", padx=20)
        
        # Backup location
        location_frame = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        location_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            location_frame,
            text="Backup Location:",
            font=("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left", padx=5)
        
        self.location_entry = ctk.CTkEntry(
            location_frame,
            placeholder_text="Backup directory path",
            width=300,
            height=36
        )
        self.location_entry.pack(side="left", padx=10)
        self.location_entry.insert(0, self.backup_config['backup_path'])
        
        ctk.CTkButton(
            location_frame,
            text="Browse",
            command=self.browse_backup_location,
            width=100,
            height=36,
            corner_radius=18
        ).pack(side="left", padx=5)
        
        # Automatic backup schedule
        schedule_frame = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        schedule_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            schedule_frame,
            text="Automatic Backup Schedule:",
            font=("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=5, pady=(0, 10))
        
        self.schedule_var = tk.StringVar(value=self.backup_config['schedule'])
        
        schedules = [
            ("Never", "never"),
            ("Daily", "daily"),
            ("Weekly", "weekly"),
            ("Monthly", "monthly")
        ]
        
        for text, value in schedules:
            ctk.CTkRadioButton(
                schedule_frame,
                text=text,
                variable=self.schedule_var,
                value=value,
                command=self.update_schedule
            ).pack(anchor="w", padx=20, pady=2)
    
    def manual_backup(self):
        """Perform manual database backup"""
        try:
            # Create backup directory if it doesn't exist
            backup_dir = self.backup_config['backup_path']
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"chiropractic_backup_{timestamp}.db")
            
            # Close any existing database connections
            self.db.close()
            
            # Copy database file
            shutil.copy2(self.db.db_path, backup_file)
            
            # Update last backup time
            self.backup_config['last_backup'] = datetime.now().isoformat()
            self.save_backup_config()
            
            # Update last backup label
            self.last_backup_label.configure(
                text=f"Last backup: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            
            messagebox.showinfo(
                "Success",
                f"Database backed up successfully to:\n{backup_file}"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to backup database: {str(e)}"
            )
    
    def browse_backup_location(self):
        """Open directory browser to select backup location"""
        from tkinter import filedialog
        
        directory = filedialog.askdirectory(
            initialdir=self.backup_config['backup_path'],
            title="Select Backup Directory"
        )
        
        if directory:
            self.backup_config['backup_path'] = directory
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, directory)
            self.save_backup_config()
    
    def update_schedule(self):
        """Update backup schedule"""
        schedule = self.schedule_var.get()
        self.backup_config['schedule'] = schedule
        self.save_backup_config()
        
        if schedule != 'never':
            messagebox.showinfo(
                "Backup Schedule",
                f"Automatic backup has been scheduled to run {schedule}."
            ) 