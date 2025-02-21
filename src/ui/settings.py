import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime
import os
import shutil
import json
import webbrowser
import csv
from utils.colors import *
from utils.google_calendar import GoogleCalendarManager
from utils.network import check_internet_connection

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
        
        # Database Management Section
        self.setup_database_section(content)
        
        # Database Backup Section
        self.setup_backup_section(content)
        
        # Google Contact Import Section
        self.setup_google_contact_section(content)
        
        # Google Calendar Section
        self.setup_google_calendar_section(content)
    
    def setup_database_section(self, parent):
        """Setup database management section"""
        # Database header
        db_header = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        db_header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            db_header,
            text="Database Management",
            font=("Helvetica", 18, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")
        
        # Current database info
        info_frame = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        info_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            info_frame,
            text="Current Database:",
            font=("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left", padx=5)
        
        self.db_path_label = ctk.CTkLabel(
            info_frame,
            text=self.db.db_path,
            font=("Helvetica", 12),
            text_color=TEXT_SECONDARY
        )
        self.db_path_label.pack(side="left", padx=20)
        
        # Button frame for database actions
        button_frame = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        button_frame.pack(fill="x", pady=10)
        
        # Import database button
        ctk.CTkButton(
            button_frame,
            text="Import Database",
            command=self.import_database,
            font=("Helvetica", 12),
            height=36,
            corner_radius=18,
            fg_color=PRIMARY_BLUE,
            hover_color=PRIMARY_DARK
        ).pack(side="left", padx=5)
        
        # Clear appointments button
        ctk.CTkButton(
            button_frame,
            text="Clear All Appointments",
            command=self.clear_all_appointments,
            font=("Helvetica", 12),
            height=36,
            corner_radius=18,
            fg_color=ERROR_RED,
            hover_color=ERROR_RED_HOVER
        ).pack(side="left", padx=5)

        # Clear patients button
        ctk.CTkButton(
            button_frame,
            text="Clear All Patients",
            command=self.clear_all_patients,
            font=("Helvetica", 12),
            height=36,
            corner_radius=18,
            fg_color=ERROR_RED,
            hover_color=ERROR_RED_HOVER
        ).pack(side="left", padx=5)
        
        # Add a warning label
        warning_frame = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        warning_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            warning_frame,
            text="Warning: Importing a database will replace the current database.",
            font=("Helvetica", 12),
            text_color=WARNING_AMBER
        ).pack(anchor="w", padx=5)
        
        # Add separator
        separator = ctk.CTkFrame(parent, height=2, fg_color=BORDER_LIGHT)
        separator.pack(fill="x", pady=20)
    
    def import_database(self):
        """Handle database import"""
        try:
            from tkinter import filedialog
            
            # Show file dialog
            file_path = filedialog.askopenfilename(
                title="Select Database File",
                filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
                initialdir=os.path.expanduser("~")
            )
            
            if not file_path:
                return
                
            # Confirm import
            if not messagebox.askyesno(
                "Confirm Import",
                "This will replace your current database. Are you sure you want to continue?\n\n"
                "It's recommended to backup your current database first."
            ):
                return
            
            # Close current database connections
            self.db.close()
            
            # Backup current database
            backup_path = f"{self.db.db_path}.bak"
            shutil.copy2(self.db.db_path, backup_path)
            
            try:
                # Copy new database
                shutil.copy2(file_path, self.db.db_path)
                
                # Try to connect to new database
                self.db.connect()
                self.db.close()
                
                # Update path label
                self.db_path_label.configure(text=self.db.db_path)
                
                messagebox.showinfo(
                    "Success",
                    f"Database imported successfully!\n\n"
                    f"A backup of your previous database was saved to:\n{backup_path}"
                )
                
                # Prompt for restart
                if messagebox.askyesno(
                    "Restart Required",
                    "The application needs to restart to use the new database.\n\n"
                    "Would you like to restart now?"
                ):
                    self.master.master.master.destroy()  # Close the application
                    
            except Exception as e:
                # Restore backup on error
                shutil.copy2(backup_path, self.db.db_path)
                messagebox.showerror(
                    "Error",
                    f"Failed to import database: {str(e)}\n\n"
                    "Your previous database has been restored."
                )
                
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error importing database: {str(e)}"
            )
    
    def setup_google_contact_section(self, parent):
        """Setup Google Contact import section"""
        # Google Contact header
        contact_header = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        contact_header.pack(fill="x", pady=(20, 10))
        
        ctk.CTkLabel(
            contact_header,
            text="Google Contact Import",
            font=("Helvetica", 18, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")
        
        # Import frame
        import_frame = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        import_frame.pack(fill="x", pady=5)
        
        # Import button
        ctk.CTkButton(
            import_frame,
            text="Import Google Contacts",
            command=self.import_google_contacts,
            font=("Helvetica", 12),
            height=36,
            corner_radius=18,
            fg_color=PRIMARY_BLUE,
            hover_color=PRIMARY_DARK
        ).pack(side="left", padx=5)
        
        # Help text
        help_text = """
        To import contacts from Google:
        1. Go to Google Contacts (contacts.google.com)
        2. Click Export from the left sidebar
        3. Choose 'Google CSV' as the export format
        4. Download the file
        5. Click the Import button above and select the downloaded file
        """
        
        help_label = ctk.CTkLabel(
            import_frame,
            text=help_text,
            font=("Helvetica", 12),
            text_color=TEXT_SECONDARY,
            justify="left"
        )
        help_label.pack(anchor="w", padx=10, pady=10)
        
        # Add separator
        separator = ctk.CTkFrame(parent, height=2, fg_color=BORDER_LIGHT)
        separator.pack(fill="x", pady=20)
    
    def import_google_contacts(self):
        """Handle Google Contacts CSV import"""
        try:
            from tkinter import filedialog
            
            # Show file dialog
            file_path = filedialog.askopenfilename(
                title="Select Google Contacts CSV File",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                initialdir=os.path.expanduser("~")
            )
            
            if not file_path:
                return
            
            # Read and process the CSV file
            imported_count = 0
            skipped_count = 0
            error_count = 0
            skipped_reasons = {
                'no_name': 0,
                'no_phone': 0,
                'invalid_phone': 0,
                'duplicate': 0
            }
            
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    try:
                        # Get name fields
                        first_name = row.get('First Name', '').strip()
                        middle_name = row.get('Middle Name', '').strip()
                        last_name = row.get('Last Name', '').strip()
                        
                        # If no first name, skip this contact
                        if not first_name:
                            skipped_reasons['no_name'] += 1
                            skipped_count += 1
                            continue
                        
                        # Extract phone number (try all phone fields)
                        phone = None
                        for i in range(1, 4):  # Check Phone 1, 2, and 3
                            phone_value = row.get(f'Phone {i} - Value', '').strip()
                            if phone_value:
                                # Clean up phone number
                                cleaned_phone = '+' + ''.join(filter(str.isdigit, phone_value[1:])) if phone_value.startswith('+') else ''.join(filter(str.isdigit, phone_value))
                                if len(cleaned_phone.replace('+', '')) >= 10:  # Valid phone number
                                    phone = cleaned_phone
                                    break
                        
                        # Skip if no valid phone number found
                        if not phone:
                            skipped_reasons['no_phone'] += 1
                            skipped_count += 1
                            continue
                        
                        # Create patient data with mandatory fields
                        patient_data = {
                            'first_name': first_name,
                            'last_name': last_name or '',  # Use empty string if last_name is empty
                            'phone': phone,
                            'age': 0,  # Default value to satisfy constraint
                            'gender': 'Other',  # Default value to satisfy constraint
                        }
                        
                        # Add middle name if present
                        if middle_name:
                            patient_data['middle_name'] = middle_name
                        
                        # Add name prefix and suffix if present
                        name_prefix = row.get('Name Prefix', '').strip()
                        if name_prefix:
                            patient_data['title'] = name_prefix
                        
                        # Add organization info if present
                        org_name = row.get('Organization Name', '').strip()
                        org_title = row.get('Organization Title', '').strip()
                        if org_name:
                            patient_data['organization'] = org_name
                        if org_title:
                            patient_data['job_title'] = org_title
                        
                        # Add email if present
                        email = row.get('E-mail 1 - Value', '').strip()
                        if email:
                            patient_data['email'] = email
                        
                        # Add address if present
                        address_fields = {
                            'address_street': row.get('Address 1 - Street', '').strip(),
                            'address_city': row.get('Address 1 - City', '').strip(),
                            'address_state': row.get('Address 1 - Region', '').strip(),
                            'address_zip': row.get('Address 1 - Postal Code', '').strip()
                        }
                        
                        # Add address fields only if they have values
                        for key, value in address_fields.items():
                            if value:
                                patient_data[key] = value
                        
                        # Add notes if present
                        notes = row.get('Notes', '').strip()
                        if notes:
                            patient_data['remarks'] = notes
                        
                        # Check for duplicate before adding
                        try:
                            existing = self.db.search_patients(patient_data['phone'])
                            if existing:
                                skipped_reasons['duplicate'] += 1
                                skipped_count += 1
                                continue
                            
                            # Add patient to database
                            self.db.add_patient(patient_data)
                            imported_count += 1
                            
                        except Exception as e:
                            print(f"Error checking for duplicate or adding patient: {str(e)}")
                            error_count += 1
                            continue
                        
                    except Exception as e:
                        print(f"Error importing contact: {str(e)}")
                        error_count += 1
            
            # Show import results with detailed breakdown
            message = f"Import completed:\n\n"
            message += f"Successfully imported: {imported_count} contacts\n"
            message += f"Skipped (duplicates/invalid): {skipped_count} contacts\n"
            message += f"Errors: {error_count} contacts\n\n"
            message += "Skipped contacts breakdown:\n"
            message += f"- Missing name: {skipped_reasons['no_name']}\n"
            message += f"- Missing phone: {skipped_reasons['no_phone']}\n"
            message += f"- Invalid phone: {skipped_reasons['invalid_phone']}\n"
            message += f"- Duplicates: {skipped_reasons['duplicate']}\n\n"
            message += "Note: Imported contacts will need age and gender information updated."
            
            messagebox.showinfo("Import Results", message)
            
        except Exception as e:
            messagebox.showerror(
                "Import Error",
                f"Error importing contacts: {str(e)}"
            )
    
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

        # Add Calendar Import section
        import_frame = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        import_frame.pack(fill="x", pady=5)

        # Import header
        ctk.CTkLabel(
            import_frame,
            text="Import Calendar Events",
            font=("Helvetica", 14, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=5, pady=(5, 10))

        # Import button
        ctk.CTkButton(
            import_frame,
            text="Import Calendar File (.ics)",
            command=self.import_calendar_file,
            height=36,
            corner_radius=18,
            fg_color=PRIMARY_BLUE,
            hover_color=PRIMARY_DARK
        ).pack(side="left", padx=5)

        # Help text for calendar import
        calendar_help_text = """
        To import events from Google Calendar:
        1. Go to Google Calendar
        2. Click the gear icon (Settings)
        3. Select 'Export calendar'
        4. Download the .ics file
        5. Click the Import button above and select the downloaded file
        """

        calendar_help_label = ctk.CTkLabel(
            import_frame,
            text=calendar_help_text,
            font=("Helvetica", 12),
            text_color=TEXT_SECONDARY,
            justify="left"
        )
        calendar_help_label.pack(anchor="w", padx=10, pady=10)

        # Add separator
        separator = ctk.CTkFrame(parent, height=2, fg_color=BORDER_LIGHT)
        separator.pack(fill="x", pady=10)

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
            # First check internet connection
            if not check_internet_connection():
                messagebox.showwarning(
                    "No Internet Connection",
                    "Internet connection is not available. Please check your connection and try again."
                )
                return
            
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
            # First check internet connection
            if not check_internet_connection():
                self.auth_status_label.configure(
                    text="Internet connection not available",
                    text_color=WARNING_AMBER
                )
                self.auth_button.configure(
                    text="Check Connection",
                    fg_color=WARNING_AMBER,
                    hover_color="#F59E0B",  # Darker amber
                    command=self.check_auth_status  # Will recheck when clicked
                )
                self.sync_button.configure(state="disabled")
                self.email_label.configure(text="")
                return
            
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
        except Exception as e:
            self.auth_status_label.configure(
                text=f"Error checking auth status: {str(e)}",
                text_color=ERROR_RED
            )
            self.sync_button.configure(state="disabled")
    
    def authorize_google_calendar(self):
        """Start Google Calendar authorization process"""
        try:
            # First check internet connection
            if not check_internet_connection():
                messagebox.showwarning(
                    "No Internet Connection",
                    "Internet connection is required to authorize Google Calendar. " +
                    "Please check your connection and try again."
                )
                return
            
            gcal = GoogleCalendarManager()
            
            if gcal.authenticate():
                # Force a refresh of the auth status
                self.check_auth_status()
                
                # Update UI elements directly
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
                
                messagebox.showinfo(
                    "Success",
                    "Successfully authenticated with Google Calendar!"
                )
            else:
                messagebox.showerror(
                    "Error",
                    "Failed to authenticate with Google Calendar"
                )
                # Reset UI to unauthenticated state
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
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to authenticate: {str(e)}"
            )
            # Reset UI to error state
            self.auth_status_label.configure(
                text=f"Error checking auth status: {str(e)}",
                text_color=ERROR_RED
            )
            self.sync_button.configure(state="disabled")
    
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
    
    def extract_patient_info(self, summary, description):
        """Extract patient information from event summary and description
        Returns a dictionary with name and any other identifiable information
        """
        patient_info = {}
        
        # Clean and normalize the summary/title
        if summary:
            # Remove common prefixes and emojis
            prefixes = ['🏥 Chiropractic:', 'Appointment with ', 'Meeting with ', 'Consultation with ', 'Appointment: ', 'Patient: ']
            cleaned_summary = summary
            for prefix in prefixes:
                if cleaned_summary.strip().startswith(prefix):
                    cleaned_summary = cleaned_summary[len(prefix):].strip()
                    break
            
            # Store the full name
            cleaned_name = cleaned_summary.strip()
            patient_info['full_name'] = cleaned_name
            
            # Try to split into first and last name
            name_parts = cleaned_name.split()
            if len(name_parts) >= 2:
                # For names with more than 2 parts, combine all middle parts into the last name
                patient_info['first_name'] = name_parts[0]
                patient_info['last_name'] = ' '.join(name_parts[1:])  # Combine remaining parts as last name
        
        # Extract additional info from description
        if description:
            lines = description.lower().split('\n')
            for line in lines:
                line = line.strip()
                # Look for phone numbers
                if any(key in line for key in ['phone:', 'tel:', 'mobile:', 'contact:']):
                    phone = ''.join(filter(str.isdigit, line.split(':', 1)[1]))
                    if phone:
                        patient_info['phone'] = phone
                
                # Look for email
                elif 'email:' in line:
                    email = line.split(':', 1)[1].strip()
                    if email:
                        patient_info['email'] = email
        
        return patient_info if patient_info else None

    def find_matching_patient(self, patient_info):
        """Find matching patient in database using available information"""
        if not patient_info:
            return None
            
        self.db.connect()
        try:
            # Try exact full name match first
            if 'full_name' in patient_info:
                query = """
                SELECT id FROM patients 
                WHERE LOWER(first_name || ' ' || last_name) = ?
                """
                full_name = patient_info['full_name'].lower()
                self.db.cursor.execute(query, (full_name,))
                result = self.db.cursor.fetchone()
                if result:
                    return result[0]
            
            # Try first and last name match
            if 'first_name' in patient_info and 'last_name' in patient_info:
                query = """
                SELECT id FROM patients 
                WHERE LOWER(first_name) = ? AND LOWER(last_name) = ?
                """
                self.db.cursor.execute(
                    query, 
                    (patient_info['first_name'].lower(), patient_info['last_name'].lower())
                )
                result = self.db.cursor.fetchone()
                if result:
                    return result[0]
            
            # Try phone number match if available
            if 'phone' in patient_info:
                patients = self.db.search_patients(patient_info['phone'])
                if patients:
                    return patients[0]['id']
            
            # Try email match if available
            if 'email' in patient_info:
                patients = self.db.search_patients(patient_info['email'])
                if patients:
                    return patients[0]['id']
            
            # Try partial name match as last resort
            if 'full_name' in patient_info:
                query = """
                SELECT id FROM patients 
                WHERE LOWER(first_name) LIKE ? OR LOWER(last_name) LIKE ?
                """
                search_term = f"%{patient_info['full_name'].lower()}%"
                self.db.cursor.execute(query, (search_term, search_term))
                result = self.db.cursor.fetchone()
                if result:
                    return result[0]
            
            return None
        finally:
            self.db.close()

    def import_calendar_file(self):
        """Handle Google Calendar .ics file import"""
        try:
            from tkinter import filedialog
            from icalendar import Calendar
            from datetime import datetime, timezone
            
            # Show file dialog
            file_path = filedialog.askopenfilename(
                title="Select Calendar File",
                filetypes=[("iCalendar Files", "*.ics"), ("All Files", "*.*")],
                initialdir=os.path.expanduser("~")
            )
            
            if not file_path:
                return
            
            # Read and process the .ics file
            imported_count = 0
            skipped_count = 0
            error_count = 0
            matched_count = 0
            new_patient_count = 0
            error_details = []  # Store detailed error information
            
            print(f"\nStarting calendar import from: {file_path}")
            
            with open(file_path, 'rb') as file:
                cal = Calendar.from_ical(file.read())
                
                # Process each event in the calendar
                for component in cal.walk('VEVENT'):
                    try:
                        # Get event details
                        start = component.get('dtstart').dt
                        summary = str(component.get('summary', ''))
                        description = str(component.get('description', ''))
                        
                        print(f"\nProcessing event: {summary}")
                        print(f"Date/Time: {start}")
                        
                        # Convert to local timezone if datetime is aware
                        if hasattr(start, 'tzinfo') and start.tzinfo is not None:
                            start = start.astimezone(timezone.utc).replace(tzinfo=None)
                        
                        # Format date and time
                        appointment_date = start.strftime("%Y-%m-%d")
                        appointment_time = start.strftime("%H:%M")
                        
                        print(f"Extracting patient info from summary: {summary}")
                        # Extract patient info and try to match with existing patient
                        patient_info = self.extract_patient_info(summary, description)
                        print(f"Extracted patient info: {patient_info}")
                        
                        if not patient_info:
                            print("No patient info extracted, skipping event")
                            skipped_count += 1
                            continue
                        
                        # Try to find matching patient
                        print("Attempting to find matching patient...")
                        patient_id = self.find_matching_patient(patient_info)
                        print(f"Matching patient ID: {patient_id}")
                        
                        if patient_id:
                            matched_count += 1
                            print(f"Matched with existing patient ID: {patient_id}")
                        else:
                            print("No match found, creating new patient...")
                            # Create new patient with available info
                            patient_data = {
                                'first_name': patient_info.get('first_name', patient_info['full_name'].split()[0]),
                                'last_name': patient_info.get('last_name', 'Unknown'),
                                'phone': patient_info.get('phone', ''),
                                'email': patient_info.get('email', ''),
                                'gender': 'Other',  # Default value
                                'age': 1  # Default value
                            }
                            print(f"New patient data: {patient_data}")
                            try:
                                patient_id = self.db.add_patient(patient_data)
                                new_patient_count += 1
                                print(f"Created new patient with ID: {patient_id}")
                            except Exception as e:
                                error_count += 1
                                error_msg = f"Error creating patient for event '{summary}': {str(e)}"
                                print(f"ERROR: {error_msg}")
                                error_details.append(error_msg)
                                continue
                        
                        # Check for duplicate appointment
                        if self.db.check_appointment_exists(patient_id, appointment_date, appointment_time):
                            print("Skipped - duplicate appointment")
                            skipped_count += 1
                            continue
                        
                        # Add appointment
                        try:
                            # Create appointment data dictionary
                            appointment_data = {
                                'patient_id': patient_id,
                                'appointment_date': appointment_date,
                                'appointment_time': appointment_time,
                                'notes': description,
                                'status': 'scheduled'
                            }
                            
                            # Add the appointment
                            self.db.add_appointment(appointment_data)
                            imported_count += 1
                            print("Appointment added successfully")
                            
                        except Exception as e:
                            error_count += 1
                            error_msg = f"Error saving appointment for event '{summary}': {str(e)}"
                            print(f"ERROR: {error_msg}")
                            error_details.append(error_msg)
                            import traceback
                            traceback.print_exc()
                            
                    except Exception as e:
                        error_count += 1
                        error_msg = f"Error processing event '{summary}': {str(e)}"
                        print(f"ERROR: {error_msg}")
                        error_details.append(error_msg)
                        import traceback
                        traceback.print_exc()
            
            # Show import results with detailed breakdown
            message = f"Import completed:\n\n"
            message += f"Successfully imported: {imported_count} appointments\n"
            message += f"- Matched with existing patients: {matched_count}\n"
            message += f"- Created new patients: {new_patient_count}\n"
            message += f"Skipped (duplicates/invalid): {skipped_count} appointments\n"
            message += f"Errors: {error_count} appointments\n\n"
            
            if error_details:
                message += "Error details:\n"
                for i, error in enumerate(error_details, 1):
                    message += f"{i}. {error}\n"
                message += "\n"
            
            message += "Note: New patients were created with minimal information.\n"
            message += "Please update their details in the patient view."
            
            print("\nFinal import results:")
            print(message)
            
            messagebox.showinfo("Import Results", message)
            
        except Exception as e:
            error_msg = f"Error importing calendar: {str(e)}"
            print(f"CRITICAL ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Import Error",
                error_msg
            )
    
    def clear_all_appointments(self):
        """Clear all appointments from the database"""
        try:
            # Show warning dialog
            if not messagebox.askyesno(
                "Clear All Appointments",
                "WARNING: This will permanently delete ALL appointments from the database.\n\n"
                "This action cannot be undone.\n"
                "Are you absolutely sure you want to continue?",
                icon="warning"
            ):
                return

            # Double confirm for safety
            if not messagebox.askyesno(
                "Final Confirmation",
                "Please confirm one more time:\n\n"
                "ALL appointments will be permanently deleted.\n"
                "This includes past, present, and future appointments.\n\n"
                "Do you want to proceed?",
                icon="warning"
            ):
                return

            # Get all appointment tables
            self.db.connect()
            try:
                # Get list of all appointment tables
                tables = self.db.cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'appointments_%'"
                ).fetchall()

                # Clear each appointment table
                for table in tables:
                    self.db.cursor.execute(f"DELETE FROM {table[0]}")

                self.db.conn.commit()

                # Show success message
                messagebox.showinfo(
                    "Success",
                    f"Successfully cleared all appointments from {len(tables)} tables."
                )

            finally:
                self.db.close()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to clear appointments: {str(e)}"
            )

    def clear_all_patients(self):
        """Clear all patients from the database"""
        try:
            # Show warning dialog
            if not messagebox.askyesno(
                "Clear All Patients",
                "WARNING: This will permanently delete ALL patients from the database.\n\n"
                "This action cannot be undone.\n"
                "Are you absolutely sure you want to continue?",
                icon="warning"
            ):
                return

            # Double confirm for safety
            if not messagebox.askyesno(
                "Final Confirmation",
                "Please confirm one more time:\n\n"
                "ALL patients and their related data will be permanently deleted.\n"
                "This includes appointments, session history, and all patient records.\n\n"
                "Do you want to proceed?",
                icon="warning"
            ):
                return

            # Clear all patients
            self.db.connect()
            try:
                # First clear all appointment tables
                tables = self.db.cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'appointments_%'"
                ).fetchall()

                for table in tables:
                    self.db.cursor.execute(f"DELETE FROM {table[0]}")

                # Clear session history
                self.db.cursor.execute("DELETE FROM session_history")
                
                # Clear patient history
                self.db.cursor.execute("DELETE FROM patient_history")
                
                # Finally clear patients table
                self.db.cursor.execute("DELETE FROM patients")
                
                # Reset the auto-increment counter
                self.db.cursor.execute("DELETE FROM sqlite_sequence WHERE name='patients'")

                self.db.conn.commit()

                # Show success message
                messagebox.showinfo(
                    "Success",
                    "Successfully cleared all patients and related data from the database."
                )

            finally:
                self.db.close()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to clear patients: {str(e)}"
            ) 