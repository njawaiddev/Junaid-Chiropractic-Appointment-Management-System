import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime
import os
import shutil
import json
import webbrowser
from utils.colors import *
from utils.google_calendar import GoogleCalendarManager

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.backup_config_file = os.path.join(self.db._get_app_data_dir(), "backup_config.json")
        self.sync_config_file = os.path.join(self.db._get_app_data_dir(), "sync_config.json")
        self.load_backup_config()
        self.load_sync_config()
        
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
    
    def load_sync_config(self):
        """Load Google Calendar sync configuration"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.sync_config_file), exist_ok=True)
            
            if os.path.exists(self.sync_config_file):
                with open(self.sync_config_file, 'r') as f:
                    self.sync_config = json.load(f)
            else:
                self.sync_config = {
                    'auto_sync': True,  # Enable by default
                    'last_sync': None,
                    'credentials_path': None
                }
                self.save_sync_config()
        except Exception as e:
            print(f"Error loading sync config: {str(e)}")
            self.sync_config = {
                'auto_sync': True,  # Enable by default
                'last_sync': None,
                'credentials_path': None
            }
    
    def save_sync_config(self):
        """Save Google Calendar sync configuration"""
        try:
            with open(self.sync_config_file, 'w') as f:
                json.dump(self.sync_config, f)
        except Exception as e:
            print(f"Error saving sync config: {str(e)}")
    
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
        
        # Google Calendar Section
        self.setup_google_calendar_section(content)
    
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
    
    def setup_google_calendar_section(self, parent):
        """Setup Google Calendar settings section"""
        # Google Calendar header
        calendar_header = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        calendar_header.pack(fill="x", pady=(20, 10))
        
        ctk.CTkLabel(
            calendar_header,
            text="Google Calendar Integration",
            font=("Helvetica", 18, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")
        
        # Authorization section
        auth_frame = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        auth_frame.pack(fill="x", pady=5)
        
        # Authorization status and email
        status_frame = ctk.CTkFrame(auth_frame, fg_color=BG_WHITE)
        status_frame.pack(fill="x", padx=5, pady=5)
        
        self.auth_status_label = ctk.CTkLabel(
            status_frame,
            text="Not authenticated with Google Calendar",
            font=("Helvetica", 12),
            text_color=WARNING_AMBER
        )
        self.auth_status_label.pack(side="left", padx=5)
        
        self.email_label = ctk.CTkLabel(
            status_frame,
            text="",
            font=("Helvetica", 12),
            text_color=TEXT_SECONDARY
        )
        self.email_label.pack(side="right", padx=5)
        
        # Authorization and sync buttons
        button_frame = ctk.CTkFrame(auth_frame, fg_color=BG_WHITE)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        self.auth_button = ctk.CTkButton(
            button_frame,
            text="Authorize Google Calendar",
            command=self.authorize_google_calendar,
            height=36,
            corner_radius=18,
            fg_color=PRIMARY_BLUE,
            hover_color=PRIMARY_DARK
        )
        self.auth_button.pack(side="left", padx=5)
        
        self.sync_button = ctk.CTkButton(
            button_frame,
            text="Sync All Appointments",
            command=self.sync_all_appointments,
            height=36,
            corner_radius=18,
            fg_color=SUCCESS_GREEN,
            hover_color=SUCCESS_GREEN_HOVER,
            state="disabled"
        )
        self.sync_button.pack(side="left", padx=5)
        
        # Check current auth status
        self.check_auth_status()
        
        # Credentials section
        creds_frame = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        creds_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            creds_frame,
            text="Google Calendar Credentials:",
            font=("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=5, pady=(0, 10))
        
        # Credentials file selection
        creds_path_frame = ctk.CTkFrame(creds_frame, fg_color=BG_WHITE)
        creds_path_frame.pack(fill="x", pady=5)
        
        self.creds_entry = ctk.CTkEntry(
            creds_path_frame,
            placeholder_text="Path to credentials.json",
            width=300,
            height=36
        )
        self.creds_entry.pack(side="left", padx=10)
        
        # Set credentials path if exists
        if self.sync_config['credentials_path']:
            self.creds_entry.insert(0, self.sync_config['credentials_path'])
        
        ctk.CTkButton(
            creds_path_frame,
            text="Browse",
            command=self.browse_credentials,
            width=100,
            height=36,
            corner_radius=18
        ).pack(side="left", padx=5)
        
        # Help text
        help_text = """
        To use Google Calendar integration:
        1. Go to Google Cloud Console
        2. Create a new project or select existing one
        3. Enable Google Calendar API
        4. Create OAuth 2.0 credentials
        5. Download credentials.json file
        6. Select the file using the Browse button above
        """
        
        help_label = ctk.CTkLabel(
            creds_frame,
            text=help_text,
            font=("Helvetica", 12),
            text_color=TEXT_SECONDARY,
            justify="left"
        )
        help_label.pack(anchor="w", padx=10, pady=10)
        
        # Sync settings
        sync_frame = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        sync_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            sync_frame,
            text="Sync Settings:",
            font=("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=5, pady=(0, 10))
        
        # Auto-sync toggle
        self.auto_sync_var = tk.BooleanVar(value=self.sync_config['auto_sync'])
        auto_sync = ctk.CTkCheckBox(
            sync_frame,
            text="Enable automatic sync",
            variable=self.auto_sync_var,
            command=self.toggle_auto_sync
        )
        auto_sync.pack(anchor="w", padx=20, pady=2)
        
        # Manual sync button
        ctk.CTkButton(
            sync_frame,
            text="Sync Now",
            command=self.manual_sync,
            height=36,
            corner_radius=18
        ).pack(anchor="w", padx=20, pady=10)
    
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
    
    def browse_credentials(self):
        """Open file browser to select Google Calendar credentials"""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            initialdir=os.path.expanduser("~"),
            title="Select Google Calendar Credentials",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        
        if filename:
            # Copy credentials to app data directory
            app_data = self.db._get_app_data_dir()
            os.makedirs(app_data, exist_ok=True)
            target_path = os.path.join(app_data, "google_credentials.json")
            
            try:
                import shutil
                shutil.copy2(filename, target_path)
                self.creds_entry.delete(0, tk.END)
                self.creds_entry.insert(0, target_path)
                
                # Update sync config
                self.sync_config['credentials_path'] = target_path
                self.save_sync_config()
                
                messagebox.showinfo(
                    "Success",
                    "Google Calendar credentials imported successfully!"
                )
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to import credentials: {str(e)}"
                )
        
    def toggle_auto_sync(self):
        """Handle auto-sync toggle"""
        is_enabled = self.auto_sync_var.get()
        self.sync_config['auto_sync'] = is_enabled
        self.save_sync_config()
        
        if is_enabled:
            messagebox.showinfo(
                "Auto-sync Enabled",
                "Appointments will automatically sync with Google Calendar"
            )
    
    def manual_sync(self):
        """Manually sync appointments with Google Calendar"""
        try:
            from utils.google_calendar import GoogleCalendarManager
            
            # Initialize Google Calendar manager
            gcal = GoogleCalendarManager()
            
            # Get today's appointments
            today = datetime.now().strftime("%Y-%m-%d")
            appointments = self.db.get_appointments_by_date(today)
            
            # Sync appointments
            if gcal.sync_appointments(appointments):
                messagebox.showinfo(
                    "Success",
                    "Appointments synced with Google Calendar successfully!"
                )
            else:
                messagebox.showerror(
                    "Error",
                    "Failed to sync appointments with Google Calendar"
                )
                
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to sync with Google Calendar: {str(e)}"
            )
    
    def check_auth_status(self):
        """Check Google Calendar authorization status"""
        try:
            gcal = GoogleCalendarManager()
            if gcal.is_authenticated():
                email = gcal.get_connected_email()
                email_text = f" - {email}" if email else ""
                
                self.auth_status_label.configure(
                    text=f"Successfully authenticated with Google Calendar{email_text}",
                    text_color=SUCCESS_GREEN
                )
                self.auth_button.configure(
                    text="Re-authorize Google Calendar",
                    fg_color=SUCCESS_GREEN,
                    hover_color=SUCCESS_GREEN_HOVER
                )
                self.sync_button.configure(state="normal")
            else:
                self.auth_status_label.configure(
                    text="Not authenticated with Google Calendar",
                    text_color=WARNING_AMBER
                )
                self.auth_button.configure(
                    text="Authorize Google Calendar",
                    fg_color=PRIMARY_BLUE,
                    hover_color=PRIMARY_DARK
                )
                self.sync_button.configure(state="disabled")
                self.email_label.configure(text="")
        except Exception as e:
            self.auth_status_label.configure(
                text=f"Error checking auth status: {str(e)}",
                text_color=ERROR_RED
            )
            self.sync_button.configure(state="disabled")
            self.email_label.configure(text="")
    
    def authorize_google_calendar(self):
        """Start Google Calendar authorization process"""
        try:
            # First check if credentials file exists
            if not self.sync_config['credentials_path'] or not os.path.exists(self.sync_config['credentials_path']):
                messagebox.showerror(
                    "Missing Credentials",
                    "Please select your Google Calendar credentials file first.\n\n"
                    "To get credentials:\n"
                    "1. Go to Google Cloud Console\n"
                    "2. Create a project or select existing one\n"
                    "3. Enable Google Calendar API\n"
                    "4. Create OAuth 2.0 credentials (Desktop application)\n"
                    "5. Download the credentials file\n"
                    "6. Select it using the Browse button below"
                )
                return
            
            gcal = GoogleCalendarManager(credentials_path=self.sync_config['credentials_path'])
            auth_url = gcal.get_authorization_url()
            
            if auth_url:
                # Open the authorization URL in default browser
                webbrowser.open(auth_url)
                
                # Show instructions to user
                messagebox.showinfo(
                    "Google Calendar Authorization",
                    "A browser window has been opened for Google Calendar authorization.\n\n"
                    "Please:\n"
                    "1. Sign in with your Google account\n"
                    "2. Grant the requested permissions\n"
                    "3. Copy the authorization code shown\n"
                    "4. Return to this window and click OK to proceed\n\n"
                    "Note: If you see a warning about unverified app, click 'Continue' as this is your own app instance."
                )
                
                # Get authorization code from user
                from tkinter import simpledialog
                auth_code = simpledialog.askstring(
                    "Authorization Code",
                    "Please enter the authorization code from Google:",
                    parent=self
                )
                
                if auth_code:
                    # Complete authorization with the code
                    if gcal.complete_authorization(auth_code):
                        messagebox.showinfo(
                            "Success",
                            "Successfully authorized with Google Calendar!"
                        )
                        self.check_auth_status()
                    else:
                        messagebox.showerror(
                            "Error",
                            "Failed to complete authorization. Please ensure you copied the entire code correctly and try again."
                        )
            else:
                messagebox.showerror(
                    "Error",
                    "Failed to generate authorization URL. Please ensure your credentials file is valid."
                )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to start authorization process: {str(e)}"
            )
    
    def sync_all_appointments(self):
        """Sync all appointments with Google Calendar"""
        try:
            # Show confirmation dialog
            if not messagebox.askyesno(
                "Sync All Appointments",
                "This will sync all appointments with Google Calendar.\n"
                "It may take a few minutes depending on the number of appointments.\n\n"
                "Do you want to continue?"
            ):
                return
            
            # Initialize Google Calendar manager
            gcal = GoogleCalendarManager(credentials_path=self.sync_config['credentials_path'])
            
            # Show progress dialog
            progress = ctk.CTkToplevel(self)
            progress.title("Syncing Appointments")
            progress.geometry("300x150")
            progress.transient(self)
            progress.grab_set()
            
            # Center the dialog
            progress.update_idletasks()
            x = self.winfo_rootx() + (self.winfo_width() - progress.winfo_width()) // 2
            y = self.winfo_rooty() + (self.winfo_height() - progress.winfo_height()) // 2
            progress.geometry(f"+{x}+{y}")
            
            # Add progress message
            message = ctk.CTkLabel(
                progress,
                text="Syncing appointments with Google Calendar...\nPlease wait...",
                font=("Helvetica", 12),
                text_color=TEXT_PRIMARY
            )
            message.pack(pady=20)
            
            # Add progress bar
            progress_bar = ctk.CTkProgressBar(progress)
            progress_bar.pack(pady=10)
            progress_bar.start()
            
            # Update UI
            progress.update()
            
            # Perform sync
            total_synced = gcal.sync_all_appointments(self.db)
            
            # Close progress dialog
            progress.destroy()
            
            if total_synced > 0:
                messagebox.showinfo(
                    "Success",
                    f"Successfully synced {total_synced} appointments with Google Calendar!"
                )
            else:
                messagebox.showinfo(
                    "No Changes",
                    "No appointments needed to be synced."
                )
                
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to sync appointments: {str(e)}"
            ) 