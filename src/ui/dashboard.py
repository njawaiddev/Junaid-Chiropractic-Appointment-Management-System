import customtkinter as ctk
from tkcalendar import Calendar
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
from utils.helpers import (
    format_date,
    parse_date,
    time_slots,
    get_week_dates,
    format_time,
    format_time_12hr
)
from utils.colors import *
import calendar
from utils.google_calendar import GoogleCalendarManager
import os
import json
from utils.network import should_attempt_gcal_sync

# Add hover color constants if not defined in colors.py
WARNING_AMBER_HOVER = "#F59E0B"  # Darker amber for hover
SUCCESS_GREEN_HOVER = "#059669"  # Darker green for hover
ERROR_RED_HOVER = "#DC2626"    # Darker red for hover

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.selected_date = datetime.now()
        self.selected_appointment = None
        self.appointment_list = None
        self.calendar = None
        self.search_var = None
        self.status_var = None
        self.view_var = tk.StringVar(value="daily")  # Initialize view variable
        
        # Initialize Google Calendar
        self.gcal = None
        if self.try_init_gcal():
            # Perform initial sync of today's appointments
            self.after(1000, self.initial_sync)  # Schedule initial sync after 1 second
        
        self.setup_ui()
        
    def initial_sync(self):
        """Perform initial sync of appointments when app starts"""
        try:
            # Get today's appointments
            today = datetime.now()
            appointments = self.db.get_appointments_by_date(today.strftime("%Y-%m-%d"))
            if appointments:
                print(f"Performing initial sync of {len(appointments)} appointments...")
                self.sync_with_google_calendar(appointments)
        except Exception as e:
            print(f"Error during initial sync: {str(e)}")

    def try_init_gcal(self):
        """Initialize Google Calendar if credentials exist and internet is available"""
        try:
            # Check if we should attempt sync
            if not should_attempt_gcal_sync(self.db._get_app_data_dir()):
                print("Skipping Google Calendar sync - offline mode or sync disabled")
                self.gcal = None
                return False
                
            # Load sync config
            sync_config_file = os.path.join(self.db._get_app_data_dir(), "sync_config.json")
            if os.path.exists(sync_config_file):
                with open(sync_config_file, 'r') as f:
                    sync_config = json.load(f)
                    
                if sync_config.get('auto_sync', True):  # Default to True if not set
                    self.gcal = GoogleCalendarManager()
                    try:
                        if self.gcal.authenticate(silent=True):
                            print("Successfully authenticated with Google Calendar")
                            return True
                        else:
                            print("Failed to authenticate with Google Calendar")
                            self.gcal = None
                            return False
                    except Exception as auth_error:
                        print(f"Google Calendar authentication error: {str(auth_error)}")
                        self.gcal = None
                        return False
            else:
                # Create default config with auto-sync enabled
                sync_config = {
                    'auto_sync': True,
                    'last_sync': None,
                    'credentials_path': None
                }
                os.makedirs(os.path.dirname(sync_config_file), exist_ok=True)
                with open(sync_config_file, 'w') as f:
                    json.dump(sync_config, f)
                
                return False  # Don't try to authenticate without credentials
                
        except Exception as e:
            print(f"Google Calendar initialization failed: {str(e)}")
            self.gcal = None
            return False

    def get_current_appointments(self):
        """Get appointments for the current selected date"""
        try:
            return self.db.get_appointments_by_date(self.selected_date.strftime("%Y-%m-%d"))
        except Exception as e:
            print(f"Error getting appointments: {str(e)}")
            return []

    def sync_with_google_calendar(self, appointments=None):
        """Sync appointments with Google Calendar"""
        if not self.gcal:
            return False
            
        if not appointments:
            appointments = self.get_current_appointments()
            
        if not appointments:
            return False
            
        try:
            # Initialize last sync times if not exists
            if not hasattr(self, '_last_sync_times'):
                self._last_sync_times = {}
            
            # Filter out recently synced appointments that haven't changed
            current_time = datetime.now()
            appointments_to_sync = []
            for appt in appointments:
                appt_id = str(appt['id'])
                should_sync = False
                
                # Check if appointment was recently synced
                if appt_id not in self._last_sync_times:
                    should_sync = True
                else:
                    last_sync = self._last_sync_times[appt_id]
                    # Only sync if:
                    # 1. It's been more than 5 minutes since last sync
                    # 2. OR the appointment status has changed
                    if (current_time - last_sync).total_seconds() >= 300:  # 5 minutes
                        should_sync = True
                    else:
                        # Check if status has changed
                        try:
                            existing_appts = self.db.get_appointments_by_date(appt['appointment_date'])
                            existing_appt = next((a for a in existing_appts if str(a['id']) == appt_id), None)
                            if existing_appt and existing_appt.get('status') != appt.get('status'):
                                should_sync = True
                        except Exception:
                            pass  # If we can't check status, don't sync
                
                if should_sync:
                    appointments_to_sync.append(appt)
                    self._last_sync_times[appt_id] = current_time
            
            if not appointments_to_sync:
                return True  # Nothing to sync
            
            def sync_task():
                try:
                    # Perform sync in batches of 10
                    batch_size = 10
                    success = True
                    for i in range(0, len(appointments_to_sync), batch_size):
                        batch = appointments_to_sync[i:i + batch_size]
                        if self.gcal.sync_appointments(batch):
                            print(f"Successfully synced batch of {len(batch)} appointments")
                        else:
                            print(f"Failed to sync batch of {len(batch)} appointments")
                            success = False
                    
                    if success:
                        print(f"Successfully synced all {len(appointments_to_sync)} appointments")
                    else:
                        print("Some appointments failed to sync")
                    
                except Exception as e:
                    print(f"Error in sync task: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            # Schedule sync task
            self.after(100, sync_task)
            return True
            
        except Exception as e:
            print(f"Error in sync_with_google_calendar: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def refresh_appointments(self, skip_sync=False):
        """Refresh appointments list"""
        try:
            # Get appointments for selected date
            appointments = self.db.get_appointments_by_date(self.selected_date.strftime("%Y-%m-%d"))
            
            # Update the appointment list
            self.update_appointment_list(appointments)
            
            # Only sync if:
            # 1. Not explicitly skipped
            # 2. We have appointments to sync
            # 3. Google Calendar is initialized
            # 4. It's been at least 5 minutes since last full sync of this date
            if not skip_sync and appointments and self.gcal:
                date_key = self.selected_date.strftime("%Y-%m-%d")
                current_time = datetime.now()
                
                # Initialize last full sync times if not exists
                if not hasattr(self, '_last_full_sync_times'):
                    self._last_full_sync_times = {}
                
                needs_sync = False
                if date_key not in self._last_full_sync_times:
                    needs_sync = True
                else:
                    last_sync = self._last_full_sync_times[date_key]
                    if (current_time - last_sync).total_seconds() >= 300:  # 5 minutes
                        needs_sync = True
                
                if needs_sync:
                    if self.sync_with_google_calendar(appointments):
                        self._last_full_sync_times[date_key] = current_time
        
        except Exception as e:
            print(f"Error refreshing appointments: {str(e)}")
            messagebox.showerror(
                "Error",
                "Failed to refresh appointments. Please try again."
            )

    def setup_ui(self):
        """Initialize dashboard UI components"""
        # Configure main frame to use full space
        self.pack(fill="both", expand=True)
        
        # Left panel - Calendar (40% width)
        left_panel = ctk.CTkFrame(self)
        left_panel.pack(side="left", fill="both", padx=(10, 5), pady=10, expand=True)
        
        # Configure left panel grid
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(1, weight=1)
        
        # Calendar frame
        self.setup_calendar(left_panel)
        
        # Right panel - Appointment list (60% width)
        right_panel = ctk.CTkFrame(self)
        right_panel.pack(side="left", fill="both", padx=(5, 10), pady=10, expand=True)
        
        # Configure right panel grid
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(2, weight=1)
        
        # Add search box at the top
        search_frame = ctk.CTkFrame(right_panel)
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 0))
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_appointments)
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search appointments by patient name...",
            textvariable=self.search_var,
            height=35,
            font=("Helvetica", 12)
        )
        search_entry.pack(fill="x", padx=5, pady=5)
        
        # Add status filter buttons
        status_filter_frame = ctk.CTkFrame(search_frame)
        status_filter_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        # Initialize status filter variable
        self.status_filter = tk.StringVar(value="all")
        
        # Create small filter buttons
        ctk.CTkButton(
            status_filter_frame,
            text="Pending",
            command=lambda: self.filter_by_status("pending"),
            width=80,
            height=25,
            corner_radius=12,
            fg_color=WARNING_AMBER,
            hover_color=WARNING_AMBER_HOVER,
            text_color=TEXT_WHITE
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            status_filter_frame,
            text="Done",
            command=lambda: self.filter_by_status("done"),
            width=80,
            height=25,
            corner_radius=12,
            fg_color=SUCCESS_GREEN,
            hover_color=SUCCESS_GREEN_HOVER,
            text_color=TEXT_WHITE
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            status_filter_frame,
            text="Cancelled",
            command=lambda: self.filter_by_status("cancelled"),
            width=80,
            height=25,
            corner_radius=12,
            fg_color=ERROR_RED,
            hover_color=ERROR_RED_HOVER,
            text_color=TEXT_WHITE
        ).pack(side="left", padx=2)
        
        # Clear filter button
        ctk.CTkButton(
            status_filter_frame,
            text="All",
            command=lambda: self.filter_by_status("all"),
            width=80,
            height=25,
            corner_radius=12,
            fg_color=BG_LIGHT,
            hover_color=PRIMARY_BLUE,
            text_color=TEXT_PRIMARY
        ).pack(side="left", padx=2)
        
        # Schedule header
        header_frame = ctk.CTkFrame(right_panel)
        header_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            header_frame,
            text="Schedule",
            font=("Helvetica", 20, "bold"),
            text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, sticky="w", padx=5)
        
        # View options
        self.view_frame = ctk.CTkFrame(header_frame)
        self.view_frame.grid(row=0, column=1, sticky="e", padx=5)
        
        for view_type in ["Today", "Weekly", "Monthly"]:
            btn = ctk.CTkButton(
                self.view_frame,
                text=view_type,
                command=lambda t=view_type.lower(): self.change_view(t),
                width=80,
                height=32,
                corner_radius=16
            )
            btn.pack(side="left", padx=2)
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(header_frame)
        nav_frame.grid(row=0, column=2, sticky="e", padx=5)
        
        self.date_label = ctk.CTkLabel(
            nav_frame,
            text=datetime.now().strftime("%Y-%m-%d"),
            font=("Helvetica", 14),
            text_color=TEXT_PRIMARY
        )
        self.date_label.pack(side="left", padx=10)
        
        ctk.CTkButton(
            nav_frame,
            text="Previous",
            command=self.previous_day,
            width=80,
            height=32,
            corner_radius=16
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            nav_frame,
            text="Today",
            command=self.go_to_today,
            width=80,
            height=32,
            corner_radius=16
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            nav_frame,
            text="Next",
            command=self.next_day,
            width=80,
            height=32,
            corner_radius=16
        ).pack(side="left", padx=2)
        
        # Setup appointment list
        self.setup_appointment_list(right_panel)
        
        # Action buttons
        action_frame = ctk.CTkFrame(right_panel)
        action_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        
        ctk.CTkButton(
            action_frame,
            text="+ Add Appointment",
            command=self.add_appointment,
            height=40,
            corner_radius=20
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            action_frame,
            text="Edit",
            command=self.edit_appointment,
            height=40,
            corner_radius=20
        ).pack(side="left", padx=5)

    def filter_appointments(self, *args):
        """Filter appointments based on search text"""
        search_text = self.search_var.get().lower()
        
        if not search_text:
            # If search is cleared, refresh all appointments
            self.refresh_appointments()
            return
            
        # Hide items that don't match the search
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            patient_name = values[1].lower() if values and len(values) > 1 else ""
            if search_text not in patient_name:
                self.tree.detach(item)

    def filter_by_status(self, status):
        """Filter appointments by status"""
        self.status_filter.set(status)
        
        # Show all items first
        for item in self.tree.get_children():
            self.tree.reattach(item, "", "end")
        
        if status == "all":
            return
            
        # Hide items that don't match the status
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            item_status = values[2].lower() if values and len(values) > 2 else ""
            if item_status != status:
                self.tree.detach(item)

    def setup_calendar(self, parent):
        """Initialize the calendar"""
        # Calendar container with shadow effect
        calendar_container = ctk.CTkFrame(
            parent,
            fg_color=BG_WHITE,
            border_width=1,
            border_color=BORDER_LIGHT,
            corner_radius=10,
            width=480,  # Slightly smaller than parent to allow padding
            height=480
        )
        calendar_container.pack(fill="both", expand=True, padx=10, pady=10)
        calendar_container.pack_propagate(False)  # Prevent size from changing
        
        # Calendar header with month/year
        header_frame = ctk.CTkFrame(calendar_container, fg_color=BG_WHITE)
        header_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        # Month navigation buttons
        prev_month_btn = ctk.CTkButton(
            header_frame,
            text="<",
            width=30,
            height=30,
            corner_radius=15,
            fg_color=BG_WHITE,
            text_color=TEXT_PRIMARY,
            hover_color=BG_LIGHT,
            border_width=1,
            border_color=BORDER_LIGHT
        )
        prev_month_btn.pack(side="left", padx=(0, 10))
        
        calendar_title = ctk.CTkLabel(
            header_frame,
            text="Calendar",
            font=("Helvetica", 16, "bold"),
            text_color=TEXT_PRIMARY
        )
        calendar_title.pack(side="left", expand=True)
        
        next_month_btn = ctk.CTkButton(
            header_frame,
            text=">",
            width=30,
            height=30,
            corner_radius=15,
            fg_color=BG_WHITE,
            text_color=TEXT_PRIMARY,
            hover_color=BG_LIGHT,
            border_width=1,
            border_color=BORDER_LIGHT
        )
        next_month_btn.pack(side="right", padx=(10, 0))
        
        # Separator between header and calendar
        separator = ttk.Separator(calendar_container, orient="horizontal")
        separator.pack(fill="x", padx=15, pady=(5, 0))
        
        # Calendar widget with modern medical colors
        style = ttk.Style()
        
        # Reset and configure the style
        style.theme_use('default')
        
        # Configure the main calendar style
        style.configure(
            "Calendar.Treeview",
            background="#1E1E1E",
            fieldbackground="#1E1E1E",
            foreground="#FFFFFF",
            borderwidth=0,
            font=("Helvetica", 10),
            rowheight=25,  # Reduced row height
            relief="flat"
        )
        
        # Configure selection colors and hover effect
        style.map(
            "Calendar.Treeview",
            background=[
                ("selected", "#3B82F6"),
                ("hover", "#2D2D2D")
            ],
            foreground=[
                ("selected", "#FFFFFF"),
                ("hover", "#FFFFFF")
            ]
        )
        
        # Configure header style for smaller size
        style.configure(
            "Calendar.Treeview.Heading",
            background="#1E1E1E",
            foreground="#FFFFFF",
            borderwidth=0,
            font=("Helvetica", 10),
            relief="flat"
        )
        
        # Remove all borders
        style.layout("Calendar.Treeview", [
            ('Calendar.Treeview.treearea', {'sticky': 'nswe'})
        ])
        
        # Calendar widget with modern styling
        self.calendar = Calendar(
            calendar_container,
            selectmode="day",
            date_pattern="y-mm-dd",
            showweeknumbers=False,
            firstweekday="sunday",
            style="Calendar.Treeview",
            background="#1E1E1E",  # Dark background
            foreground="#FFFFFF",  # White text
            headersbackground="#1E1E1E",  # Dark header background
            headersforeground="#FFFFFF",  # White header text
            selectbackground="#3B82F6",  # Blue selection
            selectforeground="#FFFFFF",  # White text for selected
            normalbackground="#1E1E1E",  # Dark background for normal days
            normalforeground="#FFFFFF",  # White text for normal days
            weekendbackground="#2D2D2D",  # Slightly lighter dark for weekends
            weekendforeground="#FFFFFF",  # White text for weekends
            othermonthbackground="#1E1E1E",  # Dark background for other month days
            othermonthforeground="#666666",  # Gray text for other month days
            othermonthwebackground="#2D2D2D",  # Slightly lighter dark for other month weekends
            othermonthweforeground="#666666",  # Gray text for other month weekends
            font=("Helvetica", 10),  # Smaller font size
            borderwidth=0,
            disableddaybackground="#1E1E1E",
            disableddayforeground="#666666",
            cursor="hand2",  # Hand cursor for better UX
            width=460,  # Fixed width for calendar
            height=400  # Fixed height for calendar
        )
        
        # Force update the calendar's internal widgets
        for widget in self.calendar.winfo_children():
            if isinstance(widget, ttk.Treeview):
                widget.configure(style="Calendar.Treeview")
                widget.tag_configure('focus', background="#3B82F6", foreground="#FFFFFF")
                widget.tag_configure('weekend', background="#2D2D2D", foreground="#FFFFFF")
                widget.tag_configure('normal', background="#1E1E1E", foreground="#FFFFFF")
                widget.tag_configure('today', background="#3B82F6", foreground="#FFFFFF")
                widget.tag_configure('hover', background="#2D2D2D", foreground="#FFFFFF")
                
                # Bind hover events
                widget.bind('<Enter>', lambda e: e.widget.state(['hover']))
                widget.bind('<Leave>', lambda e: e.widget.state(['!hover']))
            elif isinstance(widget, ttk.Frame):
                widget.configure(style="Calendar.TFrame")
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label):
                        child.configure(
                            background="#1E1E1E",
                            foreground="#FFFFFF",
                            font=("Helvetica", 10)
                        )
        
        self.calendar.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Configure calendar header
        header_frame.configure(fg_color="#1E1E1E", corner_radius=0)
        calendar_title.configure(
            text=f"{self.selected_date.strftime('%B')} {self.selected_date.year}",
            font=("Helvetica", 16, "bold"),
            text_color="#FFFFFF"
        )
        
        # Update navigation buttons
        prev_month_btn.configure(
            fg_color="#2D2D2D",
            text_color="#FFFFFF",
            hover_color="#3D3D3D",
            border_width=0
        )
        
        next_month_btn.configure(
            fg_color="#2D2D2D",
            text_color="#FFFFFF",
            hover_color="#3D3D3D",
            border_width=0
        )
        
        # Add subtle shadow to calendar container
        calendar_container.configure(
            fg_color="#1E1E1E",
            border_width=1,
            border_color="#333333",
            corner_radius=12
        )
        
        # Force a complete redraw
        self.calendar.update_idletasks()
        self.calendar.update()
        
        # Update the calendar title when month changes
        def update_calendar_title(event=None):
            calendar_title.configure(
                text=f"{self.selected_date.strftime('%B')} {self.selected_date.year}"
            )

        self.calendar.bind("<<CalendarSelected>>", lambda e: (self.on_date_select(e), update_calendar_title()))
        prev_month_btn.configure(command=lambda: (self.calendar._prev_month(), update_calendar_title()))
        next_month_btn.configure(command=lambda: (self.calendar._next_month(), update_calendar_title()))
        
        self.calendar.selection_set(self.selected_date)
        
    def setup_appointment_list(self, parent):
        """Set up the appointments treeview with modern style"""
        tree_frame = ctk.CTkFrame(parent)
        tree_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")  # Increased padding
        tree_frame.configure(fg_color=BG_WHITE)
        
        # Modern treeview style
        style = ttk.Style()
        style.configure(
            "Treeview",
            background=BG_WHITE,
            fieldbackground=BG_WHITE,
            foreground=TEXT_PRIMARY,
            rowheight=45,  # Increased row height
            font=("Helvetica", 12)  # Slightly larger font
        )
        style.configure(
            "Treeview.Heading",
            background=BG_LIGHT,
            foreground=TEXT_PRIMARY,
            font=("Helvetica", 13, "bold"),  # Larger header font
            padding=[10, 5]  # Added padding to headers
        )
        
        # Configure selection colors
        style.map(
            "Treeview",
            background=[("selected", PRIMARY_LIGHT)],
            foreground=[("selected", TEXT_PRIMARY)]
        )
        
        # Create treeview with modern columns
        columns = ("Time", "Patient", "Status", "Actions")  # Removed Notes column
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Treeview"
        )
        
        # Configure columns with improved proportions
        column_widths = {
            "Time": 120,      # Wider for time with AM/PM
            "Patient": 250,   # Wider for full names
            "Status": 120,    # Width for status
            "Actions": 120    # Width for action buttons
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[col], minwidth=column_widths[col]//2, anchor="w")
        
        # Modern scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack with modern padding
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Modern status colors with better visibility
        self.tree.tag_configure("pending", foreground=WARNING_AMBER)
        self.tree.tag_configure("done", foreground=SUCCESS_GREEN)
        self.tree.tag_configure("cancelled", foreground=ERROR_RED)
        
        # Configure alternating row colors for better readability
        self.tree.tag_configure("oddrow", background="#F8F9FA")
        self.tree.tag_configure("evenrow", background=BG_WHITE)
        
        # Bind double-click event for viewing notes
        self.tree.bind('<Double-1>', self.view_notes)
        
        # Load appointments
        self.refresh_appointments()
        
    def on_date_select(self, event):
        """Handle date selection in calendar"""
        try:
            selected = self.calendar.get_date()
            self.selected_date = datetime.strptime(selected, "%Y-%m-%d")
            self.date_label.configure(text=format_date(self.selected_date))
            self.refresh_appointments()
        except ValueError as e:
            messagebox.showerror("Error", "Invalid date selection")
            # Reset to today's date
            self.go_to_today()
    
    def previous_day(self):
        """Go to previous day"""
        self.selected_date -= timedelta(days=1)
        self.calendar.selection_set(self.selected_date)
        self.date_label.configure(text=format_date(self.selected_date))
        self.refresh_appointments()
    
    def next_day(self):
        """Go to next day"""
        self.selected_date += timedelta(days=1)
        self.calendar.selection_set(self.selected_date)
        self.date_label.configure(text=format_date(self.selected_date))
        self.refresh_appointments()
    
    def go_to_today(self):
        """Go to current date"""
        self.selected_date = datetime.now()
        self.calendar.selection_set(self.selected_date)
        self.date_label.configure(text=format_date(self.selected_date))
        self.refresh_appointments()
    
    def add_appointment(self):
        """Open dialog to add new appointment"""
        dialog = AppointmentDialog(self, self.db, self.selected_date)
        self.wait_window(dialog)
        self.refresh_appointments()
    
    def edit_appointment(self):
        """Edit selected appointment"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an appointment to edit.")
            return
        
        try:
            # Get the selected appointment's values
            item = selected[0]
            values = self.tree.item(item)["values"]
            tags = self.tree.item(item)["tags"]
            
            # Skip if this is a message row
            if not tags:
                messagebox.showwarning("Invalid Selection", "Please select a valid appointment to edit.")
                return
            
            # The first tag that's not a status should be the appointment ID
            appointment_id = None
            for tag in tags:
                if tag not in ['pending', 'done', 'cancelled']:
                    appointment_id = int(tag)
                    break
                
            if not appointment_id:
                messagebox.showwarning("Invalid Selection", "Could not find appointment ID.")
                return
            
            # Get the appointment details from the database
            date_obj = datetime.strptime(self.selected_date.strftime("%Y-%m-%d"), "%Y-%m-%d")
            month_year = date_obj.strftime("%Y_%m")
            
            self.db.connect()
            try:
                # Get full appointment details
                query = f"""
                SELECT a.*, p.first_name || ' ' || p.last_name as patient_name, p.id as patient_id
                FROM appointments_{month_year} a
                JOIN patients p ON a.patient_id = p.id
                WHERE a.id = ?
                """
                appointment = self.db.cursor.execute(query, (appointment_id,)).fetchone()
                
                if not appointment:
                    raise ValueError(f"Appointment with ID {appointment_id} not found")
                
                # Convert appointment to dictionary if it's a sqlite3.Row
                appointment_dict = dict(appointment)
                
                # Create initial values dictionary
                initial_values = {
                    'id': appointment_id,
                    'patient_id': appointment_dict['patient_id'],
                    'patient_name': appointment_dict['patient_name'],
                    'date': appointment_dict['appointment_date'],
                    'time': appointment_dict['appointment_time'],
                    'status': appointment_dict['status'],
                    'notes': appointment_dict['notes'] if appointment_dict['notes'] else ""
                }
                
                # Open appointment dialog in edit mode
                dialog = AppointmentDialog(
                    self,
                    self.db,
                    self.selected_date,
                    edit_mode=True,
                    initial_values=initial_values
                )
                
                # Wait for the dialog to close and refresh appointments
                self.wait_window(dialog)
                self.refresh_appointments()
                
            finally:
                self.db.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit appointment: {str(e)}")
            print(f"Error editing appointment: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def change_view(self, view_type):
        """Change the view type (today/weekly/monthly)"""
        self.view_var.set(view_type)
        
        # Update button appearances
        for button in self.view_frame.winfo_children():
            if isinstance(button, ctk.CTkButton):
                button_text = button.cget("text").lower()
                if button_text == view_type:
                    button.configure(
                        fg_color=PRIMARY_BLUE,
                        text_color=TEXT_WHITE
                    )
                else:
                    button.configure(
                        fg_color=BG_WHITE,
                        text_color=TEXT_PRIMARY
                    )
        
        # Update the appointments display based on view type
        if view_type == "today":
            self.refresh_appointments()
        elif view_type == "weekly":
            self.show_weekly_view()
        else:  # monthly
            self.show_monthly_view()

    def show_weekly_view(self):
        """Display weekly appointments"""
        # Get the start of the week (Monday)
        week_start = self.selected_date - timedelta(days=self.selected_date.weekday())
        week_dates = [week_start + timedelta(days=i) for i in range(7)]
        
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get appointments for each day
        for date in week_dates:
            appointments = self.db.get_appointments_by_date(format_date(date))
            if appointments:
                # Add date header
                date_str = date.strftime("%A, %B %d")
                self.tree.insert("", "end", values=(date_str, "", "", ""), tags=("date_header",))
                
                # Add appointments
                for appt in appointments:
                    status = appt["status"].lower()
                    # Convert time to 12-hour format
                    time_obj = datetime.strptime(appt["appointment_time"], '%H:%M')
                    time_12h = time_obj.strftime('%I:%M %p')
                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            time_12h,  # Use 12-hour format
                            appt["patient_name"],
                            status.capitalize(),
                            "View Notes" if appt["notes"] else ""
                        ),
                        tags=(str(appt["id"]), status)
                    )

    def show_monthly_view(self):
        """Display monthly appointments"""
        # Get all dates for the current month
        year = self.selected_date.year
        month = self.selected_date.month
        _, last_day = calendar.monthrange(year, month)
        month_dates = [
            datetime(year, month, day) for day in range(1, last_day + 1)
        ]
        
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get appointments for each day
        for date in month_dates:
            appointments = self.db.get_appointments_by_date(format_date(date))
            if appointments:
                # Add date header
                date_str = date.strftime("%A, %B %d")
                self.tree.insert("", "end", values=(date_str, "", "", ""), tags=("date_header",))
                
                # Add appointments
                for appt in appointments:
                    status = appt["status"].lower()
                    # Convert time to 12-hour format
                    time_obj = datetime.strptime(appt["appointment_time"], '%H:%M')
                    time_12h = time_obj.strftime('%I:%M %p')
                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            time_12h,  # Use 12-hour format
                            appt["patient_name"],
                            status.capitalize(),
                            "View Notes" if appt["notes"] else ""
                        ),
                        tags=(str(appt["id"]), status)
                    )

    def view_notes(self, event):
        """Handle double-click event to view notes"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            try:
                item = self.tree.selection()[0]
                column = self.tree.identify_column(event.x)
                values = self.tree.item(item)["values"]
                
                # Get appointment ID from tags
                tags = self.tree.item(item)["tags"]
                if not tags or tags[0] == 'message' or tags[0] == 'date_header':
                    return
                
                # If clicked on Actions column and it shows "View Notes"
                if column == "#4" and values[3] == "View Notes":
                    # Get the full appointment details
                    time_12h = values[0]
                    patient_name = values[1]
                    
                    appointments = self.db.get_appointments_by_date(format_date(self.selected_date))
                    for appt in appointments:
                        # Convert appointment time to 12-hour format for comparison
                        time_24h = datetime.strptime(appt['appointment_time'], "%H:%M")
                        appt_time_12h = time_24h.strftime("%I:%M %p")  # This will show like "09:30 AM"
                        
                        if appt_time_12h == time_12h and appt['patient_name'] == patient_name:
                            # Show notes in dialog
                            dialog = NotesDialog(
                                self,
                                f"Notes for {patient_name} - {time_12h}",
                                appt.get('notes', 'No notes available')
                            )
                            break
            except Exception as e:
                print(f"Error viewing notes: {str(e)}")
                import traceback
                traceback.print_exc()

    def update_appointment_list(self, appointments):
        """Update the appointment list with new appointments"""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Group appointments by date for better organization
            current_date = None
            row_count = 0  # Counter for alternating colors
            
            # Insert new appointments
            for appt in appointments:
                # Convert time to 12-hour format with AM/PM
                time_obj = datetime.strptime(appt['appointment_time'], '%H:%M')
                time_12h = time_obj.strftime('%I:%M %p')  # This will show like "09:30 AM"
                
                # Get status color
                status = appt['status'].lower() if appt['status'] else 'pending'
                
                # Determine row color
                row_tags = [str(appt['id']), status]
                if row_count % 2 == 0:
                    row_tags.append('evenrow')
                else:
                    row_tags.append('oddrow')
                row_count += 1
                
                # Insert the appointment with all tags
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        time_12h,
                        appt['patient_name'],
                        status.capitalize(),
                        "View Notes" if appt['notes'] else ""
                    ),
                    tags=tuple(row_tags)
                )
            
            # If no appointments, show message
            if not appointments:
                self.tree.insert(
                    "",
                    "end",
                    values=("No appointments scheduled for this day", "", "", ""),
                    tags=('message',)
                )
            
        except Exception as e:
            print(f"Error updating appointment list: {str(e)}")
            import traceback
            traceback.print_exc()

    def save_appointment(self, appointment_data):
        """Save appointment data to database"""
        try:
            # Validate appointment data
            if not appointment_data.get('patient_id'):
                messagebox.showerror("Error", "Please select a patient")
                return False
            
            # Check if timeslot is available
            if not self.db.is_timeslot_available(
                appointment_data['appointment_date'],
                appointment_data['appointment_time'],
                appointment_data.get('id')  # Pass ID for updates
            ):
                messagebox.showerror(
                    "Error",
                    "This timeslot is already booked. Please select another time."
                )
                return False
            
            # Use transaction context manager for database operations
            with self.db.transaction() as db:
                if 'id' in appointment_data:  # Update existing appointment
                    db.update_appointment(
                        appointment_data['id'],
                        appointment_data['patient_id'],
                        appointment_data['appointment_date'],
                        appointment_data['appointment_time'],
                        appointment_data.get('notes', ''),
                        appointment_data.get('status', 'scheduled')
                    )
                else:  # Add new appointment
                    appointment_data['id'] = db.add_appointment(appointment_data)
                
                # Trigger sync if auto-sync is enabled
                try:
                    # Load sync configuration
                    sync_config_file = os.path.join(self._get_app_data_dir(), "sync_config.json")
                    if os.path.exists(sync_config_file):
                        with open(sync_config_file, 'r') as f:
                            sync_config = json.load(f)
                            if sync_config.get('auto_sync', True):
                                # Get the appointment with patient name for sync
                                appointments = db.get_appointments_by_date(appointment_data['appointment_date'])
                                appointment = next(
                                    (a for a in appointments if str(a['id']) == str(appointment_data['id'])),
                                    None
                                )
                                if appointment:
                                    # Import here to avoid circular imports
                                    from utils.google_calendar import GoogleCalendarManager
                                    gcal = GoogleCalendarManager()
                                    if gcal.is_authenticated():
                                        gcal.sync_appointments([appointment])
                except Exception as e:
                    print(f"Error during auto-sync: {str(e)}")
                    # Don't show error to user, just log it
                    
            # Refresh the appointment list
            self.refresh_appointments()
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving appointment: {str(e)}")
            print(f"Error saving appointment: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

class AppointmentDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, date, edit_mode=False, initial_values=None):
        super().__init__(parent)
        
        # Set initial window size
        self.geometry("500x700")  # Set a fixed initial size that fits all content
        
        # Initialize constants
        self.APPOINTMENT_DURATION = 45  # Duration in minutes
        
        # Store parameters
        self.parent = parent
        self.db = db
        self.date = date
        self.edit_mode = edit_mode
        self.initial_values = initial_values or {}
        
        # Set window title
        self.title("Edit Appointment" if edit_mode else "Add Appointment")
        
        # Initialize variables
        self.selected_patient_id = None
        self.appointment_id = None
        self.calendar = parent.calendar  # Get calendar reference from parent
        
        # Setup UI
        self.setup_ui()
        
        # Set initial values if in edit mode
        if edit_mode and initial_values:
            self.set_initial_values()
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center the window
        self.center_window()
        
        # Bind escape key to close
        self.bind("<Escape>", lambda e: self.destroy())

    def setup_ui(self):
        """Initialize UI components"""
        # Main container using grid
        self.main_container = ctk.CTkFrame(self)
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Configure grid weights for main window
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Configure grid weights for main container
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Setup sections using grid
        self.setup_patient_section()
        self.setup_datetime_section()
        self.setup_status_section()
        self.setup_notes_section()
        self.setup_buttons()
        
        # Create status label for availability
        self.status_label = ctk.CTkLabel(
            self.main_container,
            text="",
            font=("Helvetica", 12)
        )
        self.status_label.grid(row=5, column=0, sticky="ew", pady=5)
        
        # Create cancel frame (hidden by default)
        self.cancel_frame = ctk.CTkFrame(self.main_container)
        self.cancel_frame.grid(row=6, column=0, sticky="ew", pady=5)
        self.cancel_frame.grid_remove()  # Hide initially

    def setup_patient_section(self):
        """Setup patient selection section"""
        # Patient section frame
        patient_frame = ctk.CTkFrame(self.main_container)
        patient_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        patient_frame.grid_columnconfigure(1, weight=1)
        
        # Patient label
        ctk.CTkLabel(
            patient_frame,
            text="Patient:",
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Patient search entry
        self.patient_search = ctk.CTkEntry(
            patient_frame,
            placeholder_text="Search patient by name or phone"
        )
        self.patient_search.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Patient listbox
        self.patient_listbox = tk.Listbox(
            patient_frame,
            height=5,
            selectmode="single"
        )
        self.patient_listbox.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Bind events
        self.patient_search.bind('<KeyRelease>', self.on_patient_search)
        self.patient_listbox.bind('<<ListboxSelect>>', self.on_patient_select)

    def setup_datetime_section(self):
        """Setup date and time selection section"""
        # Date and time frame
        datetime_frame = ctk.CTkFrame(self.main_container)
        datetime_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        datetime_frame.grid_columnconfigure(1, weight=1)
        
        # Date label
        ctk.CTkLabel(
            datetime_frame,
            text="Date:",
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Date display
        date_str = self.date.strftime("%Y-%m-%d")
        ctk.CTkLabel(
            datetime_frame,
            text=date_str
        ).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Time label
        ctk.CTkLabel(
            datetime_frame,
            text="Time:",
            font=("Helvetica", 12, "bold")
        ).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        # Time selection combobox
        self.time_var = tk.StringVar()
        self.time_combo = ctk.CTkComboBox(
            datetime_frame,
            values=self.get_time_slots(),
            variable=self.time_var,
            state="readonly",
            width=120,
            height=32
        )
        self.time_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # End time label
        ctk.CTkLabel(
            datetime_frame,
            text="End Time:",
            font=("Helvetica", 12, "bold")
        ).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        # End time display
        self.end_time_label = ctk.CTkLabel(datetime_frame, text="")
        self.end_time_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Bind time selection event
        self.time_var.trace_add("write", self.on_time_change)

    def setup_status_section(self):
        """Setup status selection section"""
        # Status frame
        status_frame = ctk.CTkFrame(self.main_container)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        status_frame.grid_columnconfigure(1, weight=1)
        
        # Status label
        ctk.CTkLabel(
            status_frame,
            text="Status:",
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Status selection
        self.status_var = tk.StringVar(value="confirmed")  # Set default to confirmed
        statuses = ["confirmed", "pending", "done", "cancelled"]
        self.status_combo = ctk.CTkComboBox(
            status_frame,
            values=statuses,
            variable=self.status_var,
            state="readonly",
            width=120,
            height=32
        )
        self.status_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Bind status change event
        self.status_var.trace_add("write", self.on_status_change)

    def setup_notes_section(self):
        """Setup notes section"""
        # Notes frame
        notes_frame = ctk.CTkFrame(self.main_container)
        notes_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        notes_frame.grid_columnconfigure(0, weight=1)
        
        # Notes label
        ctk.CTkLabel(
            notes_frame,
            text="Notes:",
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, padx=5, pady=(5,0), sticky="w")
        
        # Notes textbox
        self.notes_text = ctk.CTkTextbox(
            notes_frame,
            height=100
        )
        self.notes_text.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    def setup_buttons(self):
        """Setup action buttons"""
        # Buttons frame
        button_frame = ctk.CTkFrame(self.main_container)
        button_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Save button
        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save
        ).grid(row=0, column=0, padx=5, pady=5)
        
        # Cancel button
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy
        ).grid(row=0, column=1, padx=5, pady=5)

    def set_initial_values(self):
        """Set initial values when editing an appointment"""
        if not hasattr(self, 'initial_values') or not self.initial_values:
            return
            
        try:
            # Set patient
            if self.initial_values.get('patient_name'):
                self.patient_search.delete(0, tk.END)
                self.patient_search.insert(0, self.initial_values['patient_name'])
                # Hide the patient list since we already have a selection
                self.patient_listbox.grid_remove()
            
            # Set time
            if self.initial_values.get('time'):
                time_str = self.initial_values['time']
                # Convert to 12-hour format if needed
                try:
                    time_obj = datetime.strptime(time_str, "%H:%M")
                    time_12h = time_obj.strftime("%I:%M %p").lstrip("0")
                except ValueError:
                    time_12h = time_str
                self.time_combo.set(time_12h)
            
            # Set status
            if self.initial_values.get('status'):
                self.status_var.set(self.initial_values['status'].capitalize())
            
            # Set notes
            if self.initial_values.get('notes'):
                self.notes_text.delete("1.0", tk.END)
                self.notes_text.insert("1.0", self.initial_values['notes'])
            
            # Store appointment ID and patient ID for saving
            self.appointment_id = self.initial_values.get('id')
            self.selected_patient_id = self.initial_values.get('patient_id')
            
        except Exception as e:
            print(f"Error setting initial values: {str(e)}")
            import traceback
            traceback.print_exc()

    def on_time_change(self, *args):
        """Handle time selection change"""
        selected_time = self.time_var.get()
        if selected_time:
            # Update end time
            try:
                start_time = datetime.strptime(selected_time, "%I:%M %p")
                end_time = start_time + timedelta(minutes=self.APPOINTMENT_DURATION)
                self.end_time_label.configure(
                    text=f"End: {end_time.strftime('%I:%M %p').lstrip('0')} ({self.APPOINTMENT_DURATION} min)"
                )
            except ValueError:
                self.end_time_label.configure(text="")
            
            # Check availability
            self.check_timeslot_availability(selected_time)

    def get_time_slots(self):
        """Generate time slots for the combobox"""
        slots = []
        
        # Start at 9:00 AM today
        start = datetime.strptime("09:00", "%H:%M")
        # End at 8:00 AM next day
        end = datetime.strptime("08:00", "%H:%M") + timedelta(days=1)
        current = start
        
        while current <= end:
            # Format in 12-hour with AM/PM
            time_12h = current.strftime("%I:%M %p").lstrip("0")
            slots.append(time_12h)
            # Use 15-minute intervals
            current += timedelta(minutes=15)
        
        return slots

    def check_timeslot_availability(self, selected_time):
        """Check if selected timeslot is available"""
        if not selected_time:
            return
        
        try:
            # Convert 12h time to 24h format for database
            time_12h = datetime.strptime(selected_time, "%I:%M %p")
            time_24h = time_12h.strftime("%H:%M")
            
            # Get appointment date
            appointment_date = self.calendar.get_date()
            
            # Check availability
            is_available = self.db.is_timeslot_available(
                appointment_date,
                time_24h,
                self.initial_values.get('id') if self.edit_mode else None
            )
            
            if is_available:
                self.status_label.configure(
                    text="Available",
                    text_color=SUCCESS_GREEN
                )
            else:
                self.status_label.configure(
                    text="Not Available",
                    text_color=ERROR_RED
                )
            
            return is_available
            
        except Exception as e:
            print(f"Error checking timeslot availability: {str(e)}")
            return False
    
    def on_status_change(self, *args):
        """Handle status change"""
        if self.status_var.get().lower() == "cancelled":
            self.cancel_frame.grid()  # Show the frame
        else:
            self.cancel_frame.grid_remove()  # Hide the frame
    
    def on_patient_search(self, *args):
        """Handle patient search input changes"""
        search_text = self.patient_search.get().strip()
        
        # Clear listbox
        self.patient_listbox.delete(0, tk.END)
        
        if search_text:
            # Show listbox when searching
            self.patient_listbox.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
            
            # Search patients
            matching_patients = self.db.search_patients(search_text)
            
            # Add matching patients to listbox with formatted display
            for patient in matching_patients[:10]:  # Limit to 10 results
                try:
                    # Format display text with patient details in a clear, organized way
                    display_text = (
                        f"ID: {patient['id']} | "
                        f"{patient['first_name']} {patient['last_name']} | "
                        f"Age: {patient.get('age', 'N/A')} | "
                        f"📞 {patient.get('phone', 'N/A')}"
                    )
                    
                    self.patient_listbox.insert(tk.END, display_text)
                except Exception as e:
                    print(f"Error formatting patient details: {str(e)}")
                    continue
            
            # Configure listbox height based on results
            self.patient_listbox.configure(height=min(5, len(matching_patients)))
            
            # Configure listbox appearance for better readability
            self.patient_listbox.configure(
                font=("Helvetica", 11),
                selectmode="single",
                activestyle="none"
            )
        else:
            # Hide listbox when search is empty
            self.patient_listbox.grid_remove()
    
    def on_patient_select(self, event):
        """Handle patient selection from listbox"""
        selection = self.patient_listbox.curselection()
        if selection:
            selected_text = self.patient_listbox.get(selection[0])
            try:
                # Extract patient ID from the selection
                patient_id = selected_text.split("ID: ")[-1].split()[0]
                self.selected_patient_id = int(patient_id)
                
                # Update entry with patient name
                patient_name = selected_text.split(" |")[0]
                self.patient_search.delete(0, tk.END)
                self.patient_search.insert(0, patient_name)
                
                # Hide the listbox after selection
                self.patient_listbox.grid_remove()
            except (IndexError, ValueError) as e:
                print(f"Error parsing patient selection: {str(e)}")
                messagebox.showerror(
                    "Error",
                    "Could not process patient selection. Please try again."
                )
    
    def save(self):
        """Save the appointment"""
        try:
            # Validate required fields
            if not self.patient_search.get().strip():
                messagebox.showerror("Error", "Please select a patient")
                return
                
            if not self.time_combo.get():
                messagebox.showerror("Error", "Please select a time")
                return
            
            # Get the values
            patient_name = self.patient_search.get().strip()
            time_str = self.time_combo.get()
            status = self.status_var.get().lower()  # Get the actual selected status
            notes = self.notes_text.get("1.0", tk.END).strip()
            
            # Get the selected date from calendar
            selected_date = self.calendar.get_date()
            
            # Convert time to 24-hour format for database
            try:
                time_obj = datetime.strptime(time_str, "%I:%M %p")
                time_24h = time_obj.strftime("%H:%M")
            except ValueError:
                messagebox.showerror("Error", "Invalid time format")
                return
            
            # Get patient ID - first try from stored value
            patient_id = None
            if hasattr(self, 'selected_patient_id'):
                patient_id = self.selected_patient_id
            elif hasattr(self, 'initial_values') and self.initial_values.get('patient_id'):
                patient_id = self.initial_values['patient_id']
            
            # If no patient ID stored, try to get it from the database
            if not patient_id:
                self.db.connect()
                try:
                    query = "SELECT id FROM patients WHERE first_name || ' ' || last_name = ?"
                    result = self.db.cursor.execute(query, (patient_name,)).fetchone()
                    if result:
                        patient_id = result[0]
                    else:
                        raise ValueError(f"Patient {patient_name} not found")
                finally:
                    self.db.close()
                
            if not patient_id:
                raise ValueError("No patient selected or patient not found")
            
            # Save to database
            if self.edit_mode and hasattr(self, 'initial_values') and self.initial_values.get('id'):
                # Update existing appointment
                appointment_id = int(self.initial_values['id'])  # Ensure ID is an integer
                self.db.update_appointment(
                    appointment_id,
                    patient_id,
                    selected_date,
                    time_24h,
                    notes,
                    status  # Pass the actual selected status
                )
                messagebox.showinfo("Success", "Appointment updated successfully")
            else:
                # Create new appointment with status
                appointment_data = {
                    'patient_id': patient_id,
                    'appointment_date': selected_date,
                    'appointment_time': time_24h,
                    'notes': notes,
                    'status': status
                }
                appointment_id = self.db.add_appointment(appointment_data)
                messagebox.showinfo("Success", "Appointment added successfully")
            
            # Close dialog
            self.destroy()
            
            # Refresh the appointment list in the dashboard
            if hasattr(self.parent, 'refresh_appointments'):
                self.parent.refresh_appointments()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save appointment: {str(e)}")
            print(f"Error saving appointment: {str(e)}")
            import traceback
            traceback.print_exc()

    def center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        # Ensure minimum size
        width = max(500, self.winfo_width())
        height = max(700, self.winfo_height())
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

class NotesDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, notes):
        super().__init__(parent)
        self.title(title)
        
        # Set size and position
        window_width = 500
        window_height = 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=BG_WHITE)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Notes text area
        self.notes_text = ctk.CTkTextbox(
            main_frame,
            height=300,
            fg_color="white",
            border_color=BORDER_LIGHT,
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12)
        )
        self.notes_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.notes_text.insert("1.0", notes)
        self.notes_text.configure(state="disabled")  # Make read-only
        
        # Close button
        ctk.CTkButton(
            main_frame,
            text="Close",
            command=self.destroy,
            width=100,
            height=32,
            corner_radius=16
        ).pack(pady=(10, 0)) 