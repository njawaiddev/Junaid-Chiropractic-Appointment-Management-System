import customtkinter as ctk
from tkcalendar import Calendar
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
from utils.helpers import (
    format_date,
    parse_date,
    time_slots,
    get_week_dates
)
from utils.colors import *
import calendar

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.selected_date = datetime.now()
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Configure colors
        self.configure(fg_color=BG_WHITE)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize dashboard UI components"""
        # Left panel - Calendar
        left_panel = ctk.CTkFrame(self)
        left_panel.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        left_panel.configure(fg_color=BG_WHITE)
        
        # Set fixed size for left panel
        left_panel.grid_propagate(False)  # Prevent size from changing
        left_panel.configure(width=500, height=500)  # Fixed size
        
        # Calendar container with shadow effect
        calendar_container = ctk.CTkFrame(
            left_panel,
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
        
        # Right panel with modern medical design
        right_panel = ctk.CTkFrame(self)
        right_panel.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.configure(fg_color=BG_WHITE)
        
        # Date navigation with modern style
        nav_container = ctk.CTkFrame(right_panel, fg_color=BG_WHITE)
        nav_container.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="ew")
        
        # Title for appointments
        appointments_title = ctk.CTkLabel(
            nav_container,
            text="Schedule",
            font=("Helvetica", 20, "bold"),
            text_color=TEXT_PRIMARY
        )
        appointments_title.pack(pady=(5, 10))
        
        # Navigation buttons with modern style
        nav_frame = ctk.CTkFrame(nav_container, fg_color=BG_WHITE)
        nav_frame.pack(fill="x", padx=5, pady=(0, 10))
        
        # View selection frame
        view_frame = ctk.CTkFrame(nav_frame, fg_color=BG_WHITE)
        view_frame.pack(side="left", padx=5)
        
        # Store view_frame as instance variable
        self.view_frame = view_frame
        
        # View selection buttons
        self.view_var = tk.StringVar(value="today")
        views = [("Today", "today"), ("Weekly", "weekly"), ("Monthly", "monthly")]
        
        for text, value in views:
            ctk.CTkButton(
                self.view_frame,  # Use instance variable
                text=text,
                command=lambda v=value: self.change_view(v),
                fg_color=BG_WHITE if value != "today" else PRIMARY_BLUE,
                text_color=TEXT_PRIMARY if value != "today" else TEXT_WHITE,
                hover_color=BG_LIGHT,
                border_width=1,
                border_color=BORDER_LIGHT,
                width=80,
                height=32,
                corner_radius=16
            ).pack(side="left", padx=2)
        
        # Navigation buttons
        nav_buttons_frame = ctk.CTkFrame(nav_frame, fg_color=BG_WHITE)
        nav_buttons_frame.pack(side="right", padx=5)
        
        ctk.CTkButton(
            nav_buttons_frame,
            text="Previous",
            command=self.previous_day,
            fg_color=BG_WHITE,
            text_color=TEXT_PRIMARY,
            hover_color=BG_LIGHT,
            border_width=1,
            border_color=BORDER_LIGHT,
            width=100,
            height=32,
            corner_radius=16
        ).pack(side="left", padx=5)
        
        self.date_label = ctk.CTkLabel(
            nav_buttons_frame,
            text=format_date(self.selected_date),
            font=("Helvetica", 14, "bold"),
            text_color=TEXT_PRIMARY
        )
        self.date_label.pack(side="left", padx=20)
        
        ctk.CTkButton(
            nav_buttons_frame,
            text="Next",
            command=self.next_day,
            fg_color=BG_WHITE,
            text_color=TEXT_PRIMARY,
            hover_color=BG_LIGHT,
            border_width=1,
            border_color=BORDER_LIGHT,
            width=100,
            height=32,
            corner_radius=16
        ).pack(side="left", padx=5)
        
        # Subtle separator
        separator = ttk.Separator(right_panel, orient="horizontal")
        separator.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        
        # Appointments list with modern style
        self.setup_appointment_list(right_panel)
        
        # Action buttons with modern style
        actions_frame = ctk.CTkFrame(right_panel)
        actions_frame.grid(row=3, column=0, padx=10, pady=(10, 10), sticky="ew")
        actions_frame.configure(fg_color=BG_WHITE)
        
        # Modern action buttons
        ctk.CTkButton(
            actions_frame,
            text="+ Add Appointment",
            command=self.add_appointment,
            fg_color=ACCENT_TEAL,
            text_color=TEXT_WHITE,
            hover_color="#0097A7",  # Darker teal
            width=150,
            height=36,
            corner_radius=18
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            actions_frame,
            text="Edit",
            command=self.edit_appointment,
            fg_color=PRIMARY_BLUE,
            text_color=TEXT_WHITE,
            hover_color=PRIMARY_DARK,
            width=100,
            height=36,
            corner_radius=18
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            actions_frame,
            text="Cancel",
            command=self.cancel_appointment,
            fg_color=ERROR_RED,
            text_color=TEXT_WHITE,
            hover_color="#DC2626",  # Darker red
            width=100,
            height=36,
            corner_radius=18
        ).pack(side="left", padx=10)
    
    def setup_appointment_list(self, parent):
        """Set up the appointments treeview with modern style"""
        tree_frame = ctk.CTkFrame(parent)
        tree_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        tree_frame.configure(fg_color=BG_WHITE)
        
        # Modern treeview style
        style = ttk.Style()
        style.configure(
            "Treeview",
            background=BG_WHITE,
            fieldbackground=BG_WHITE,
            foreground=TEXT_PRIMARY,
            rowheight=40,
            font=("Helvetica", 11)
        )
        style.configure(
            "Treeview.Heading",
            background=BG_LIGHT,
            foreground=TEXT_PRIMARY,
            font=("Helvetica", 12, "bold")
        )
        
        # Configure selection colors
        style.map(
            "Treeview",
            background=[("selected", PRIMARY_LIGHT)],
            foreground=[("selected", TEXT_PRIMARY)]
        )
        
        # Create treeview with modern columns
        columns = ("Time", "Patient", "Status", "Notes")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Treeview"
        )
        
        # Configure columns with modern proportions
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="w")  # Left-align all columns
        
        self.tree.column("Time", width=80, minwidth=80)
        self.tree.column("Patient", width=150, minwidth=150)
        self.tree.column("Status", width=100, minwidth=100)
        self.tree.column("Notes", width=300, minwidth=200)
        
        # Modern scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack with modern padding
        self.tree.pack(side="left", fill="both", expand=True, padx=(0, 5))
        scrollbar.pack(side="right", fill="y")
        
        # Modern status colors with better visibility
        self.tree.tag_configure("pending", foreground=WARNING_AMBER, background=WARNING_AMBER_LIGHT)
        self.tree.tag_configure("done", foreground=SUCCESS_GREEN, background=SUCCESS_GREEN_LIGHT)
        self.tree.tag_configure("cancelled", foreground=ERROR_RED, background=ERROR_RED_LIGHT)
        
        # Load appointments
        self.refresh_appointments()
        
    def refresh_appointments(self):
        """Refresh the appointments list"""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get appointments for selected date
        appointments = self.db.get_appointments_by_date(format_date(self.selected_date))
        
        # Add appointments to tree
        for appt in appointments:
            status = appt["status"].lower()  # Convert status to lowercase
            self.tree.insert(
                "",
                "end",
                iid=str(appt["id"]),  # Use appointment ID as the item ID
                values=(
                    appt["appointment_time"],
                    appt["patient_name"],
                    status.capitalize(),  # Capitalize status for display
                    appt["notes"]
                ),
                tags=(status,)  # Use status as tag for color
            )
    
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
            return
        
        # Get appointment details
        item_id = selected[0]
        values = self.tree.item(item_id)["values"]
        if not values:
            return
        
        dialog = AppointmentDialog(
            self,
            self.db,
            self.selected_date,
            edit_mode=True,
            initial_values={
                "id": item_id,
                "time": values[0],
                "patient": values[1],
                "status": values[2],
                "notes": values[3]
            }
        )
        self.wait_window(dialog)
        self.refresh_appointments()
    
    def cancel_appointment(self):
        """Cancel selected appointment"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an appointment to cancel")
            return
        
        # Get appointment details
        item_id = selected[0]
        values = self.tree.item(item_id)["values"]
        if not values:
            return
        
        # Ask for cancellation reason
        dialog = AppointmentDialog(
            self,
            self.db,
            self.selected_date,
            edit_mode=True,
            initial_values={
                "id": item_id,
                "time": values[0],
                "patient": values[1],
                "status": "cancelled",
                "notes": values[3]
            }
        )
        self.wait_window(dialog)
        self.refresh_appointments()

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
                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            appt["appointment_time"],
                            appt["patient_name"],
                            status.capitalize(),
                            appt["notes"]
                        ),
                        tags=(status,)
                    )

    def show_monthly_view(self):
        """Display monthly appointments"""
        # Get all dates for the current month
        year = self.selected_date.year
        month = self.selected_date.month
        _, last_day = calendar.monthrange(year, month)
        month_dates = [datetime(year, month, day) for day in range(1, last_day + 1)]
        
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
                    self.tree.insert(
                        "",
                        "end",
                        values=(
                            appt["appointment_time"],
                            appt["patient_name"],
                            status.capitalize(),
                            appt["notes"]
                        ),
                        tags=(status,)
                    )

class AppointmentDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, date, edit_mode=False, initial_values=None):
        super().__init__(parent)
        self.db = db
        self.date = date
        self.edit_mode = edit_mode
        self.initial_values = initial_values or {}
        self.selected_patient_id = None
        
        # If in edit mode, get the patient ID from the existing appointment
        if edit_mode and initial_values:
            try:
                # Get the appointment ID
                appointment_id = initial_values.get('id')
                if appointment_id:
                    # Get the month_year from the date
                    month_year = format_date(self.date)
                    # Query the appointment to get patient_id
                    appointments = self.db.get_appointments_by_date(format_date(self.date))
                    for appt in appointments:
                        if str(appt['id']) == str(appointment_id):
                            # Get patient details to ensure they exist
                            patient = self.db.get_patient(appt['patient_id'])
                            if patient:
                                self.selected_patient_id = appt['patient_id']
                                break
            except Exception as e:
                print(f"Error getting initial patient ID: {str(e)}")
        
        self.title("Edit Appointment" if edit_mode else "New Appointment")
        self.setup_ui()
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
    def setup_ui(self):
        """Initialize dialog UI components"""
        # Main container with light gray background
        main_frame = ctk.CTkFrame(self, fg_color="#F5F7FA")
        main_frame.pack(fill="both", expand=True)
        
        # Time selection
        time_frame = ctk.CTkFrame(main_frame, fg_color="#F5F7FA")
        time_frame.pack(padx=20, pady=(20, 10), fill="x")
        
        ctk.CTkLabel(
            time_frame,
            text="Time:",
            text_color="#2C3E50",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=(0, 10))
        
        # Convert initial time to components if it exists
        initial_time = self.initial_values.get("time", "")
        initial_hour = ""
        initial_minute = "00"
        initial_period = "AM"
        
        if initial_time:
            try:
                time_obj = datetime.strptime(initial_time, "%H:%M")
                initial_hour = int(time_obj.strftime("%I"))
                initial_minute = time_obj.strftime("%M")
                initial_period = time_obj.strftime("%p")
            except ValueError:
                pass
        
        # Hour selection (1-12)
        hour_values = [str(i) for i in range(1, 13)]
        self.hour_var = tk.StringVar(value=str(initial_hour))
        hour_cb = ctk.CTkComboBox(
            time_frame,
            values=hour_values,
            variable=self.hour_var,
            fg_color="white",
            border_color="#3B82F6",
            button_color="#3B82F6",
            button_hover_color="#2563EB",
            dropdown_fg_color="white",
            dropdown_hover_color="#EFF6FF",
            width=70
        )
        hour_cb.pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(
            time_frame,
            text=":",
            text_color="#2C3E50",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=(0, 5))
        
        # Minute selection (00-59)
        minute_values = [f"{i:02d}" for i in range(0, 60, 30)]
        self.minute_var = tk.StringVar(value=initial_minute)
        minute_cb = ctk.CTkComboBox(
            time_frame,
            values=minute_values,
            variable=self.minute_var,
            fg_color="white",
            border_color="#3B82F6",
            button_color="#3B82F6",
            button_hover_color="#2563EB",
            dropdown_fg_color="white",
            dropdown_hover_color="#EFF6FF",
            width=70
        )
        minute_cb.pack(side="left", padx=(0, 10))
        
        # AM/PM selection
        self.period_var = tk.StringVar(value=initial_period)
        period_cb = ctk.CTkComboBox(
            time_frame,
            values=["AM", "PM"],
            variable=self.period_var,
            fg_color="white",
            border_color="#3B82F6",
            button_color="#3B82F6",
            button_hover_color="#2563EB",
            dropdown_fg_color="white",
            dropdown_hover_color="#EFF6FF",
            width=70
        )
        period_cb.pack(side="left", padx=(0, 10))
        
        # Patient selection
        patient_frame = ctk.CTkFrame(main_frame, fg_color="#F5F7FA")
        patient_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(
            patient_frame,
            text="Patient:",
            text_color="#2C3E50",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=(0, 10))
        
        # Create a frame for patient search and dropdown
        patient_search_frame = ctk.CTkFrame(patient_frame, fg_color="#F5F7FA")
        patient_search_frame.pack(side="left", fill="x", expand=True)
        
        # Patient search entry
        self.patient_var = tk.StringVar(value=self.initial_values.get("patient", ""))
        self.patient_var.trace_add("write", self.on_patient_search)
        
        self.patient_entry = ctk.CTkEntry(
            patient_search_frame,
            textvariable=self.patient_var,
            fg_color="white",
            border_color="#3B82F6",
            text_color="#2C3E50",
            placeholder_text="Search by name or name + filter (e.g., John + 45 or John + 123)",
            placeholder_text_color="#94A3B8",
            height=35,
            font=("Helvetica", 12)
        )
        self.patient_entry.pack(fill="x", expand=True)
        
        # Patient listbox with modern styling
        self.patient_listbox = tk.Listbox(
            patient_search_frame,
            height=5,
            selectmode="single",
            font=("Helvetica", 11),
            bg="white",
            fg="#2C3E50",
            selectbackground="#EFF6FF",
            selectforeground="#2563EB",
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground="#E2E8F0",
            highlightcolor="#3B82F6"
        )
        self.patient_listbox.pack(fill="x", expand=True, pady=(5, 0))
        self.patient_listbox.bind('<<ListboxSelect>>', self.on_patient_select)
        
        # Add tooltip/help text
        help_text = ctk.CTkLabel(
            patient_search_frame,
            text="💡 Tip: Use + to filter (e.g., 'John + 45' for age, 'John + 123' for phone)",
            text_color="#64748B",
            font=("Helvetica", 10)
        )
        help_text.pack(pady=(2, 0), anchor="w")
        
        # Initially hide the listbox
        self.patient_listbox.pack_forget()
        
        # Store all patients for searching
        self.all_patients = self.db.search_patients("")
        
        # Status selection
        status_frame = ctk.CTkFrame(main_frame, fg_color="#F5F7FA")
        status_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(
            status_frame,
            text="Status:",
            text_color="#2C3E50",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=(0, 10))
        
        self.status_var = tk.StringVar(value=self.initial_values.get("status", "pending"))
        
        # Status radio buttons
        status_options = [
            ("Pending", "pending", WARNING_ORANGE),
            ("Done", "done", SUCCESS_GREEN),
            ("Cancelled", "cancelled", ERROR_RED)
        ]
        
        for text, value, color in status_options:
            radio = ctk.CTkRadioButton(
                status_frame,
                text=text,
                variable=self.status_var,
                value=value,
                fg_color=color,
                border_color=color,
                hover_color=color,
                text_color="#2C3E50"
            )
            radio.pack(side="left", padx=10)
        
        # Bind status change event
        self.status_var.trace_add("write", self.on_status_change)
        
        # Cancellation reason (initially hidden)
        self.cancel_frame = ctk.CTkFrame(main_frame, fg_color="#F5F7FA")
        
        ctk.CTkLabel(
            self.cancel_frame,
            text="Reason for cancellation:",
            text_color="#2C3E50",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.cancel_reason = ctk.CTkTextbox(
            self.cancel_frame,
            height=60,
            fg_color="white",
            border_color="#3B82F6",
            text_color="#2C3E50"
        )
        self.cancel_reason.pack(fill="x", padx=20, pady=(0, 10))
        
        # Notes
        notes_frame = ctk.CTkFrame(main_frame, fg_color="#F5F7FA")
        notes_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        ctk.CTkLabel(
            notes_frame,
            text="Notes:",
            text_color="#2C3E50",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")
        
        self.notes_text = ctk.CTkTextbox(
            notes_frame,
            height=100,
            fg_color="white",
            border_color="#3B82F6",
            text_color="#2C3E50"
        )
        self.notes_text.pack(fill="both", expand=True, pady=(5, 0))
        
        if self.initial_values.get("notes"):
            self.notes_text.insert("1.0", self.initial_values["notes"])
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="#F5F7FA")
        button_frame.pack(padx=20, pady=(10, 20), fill="x")
        
        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save,
            fg_color="#3B82F6",
            hover_color="#2563EB"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#EF4444",
            hover_color="#DC2626"
        ).pack(side="left", padx=5)
        
        # Show/hide cancel reason based on initial status
        if self.initial_values.get("status") == "cancelled":
            self.cancel_frame.pack(fill="x")
        
    def on_status_change(self, *args):
        """Handle status change"""
        if self.status_var.get() == "cancelled":
            self.cancel_frame.pack(fill="x")
        else:
            self.cancel_frame.pack_forget()
    
    def on_patient_search(self, *args):
        """Handle patient search input change"""
        search_text = self.patient_var.get().lower()
        
        # Clear listbox
        self.patient_listbox.delete(0, tk.END)
        
        if search_text:
            # Show listbox when searching
            self.patient_listbox.pack(fill="x", expand=True, pady=(5, 0))
            
            # Parse search terms (support name + phone/age)
            terms = search_text.split('+')
            name_term = terms[0].strip()
            filter_term = terms[1].strip() if len(terms) > 1 else None
            
            # Get matching patients
            matching_patients = []
            for patient in self.all_patients:
                full_name = f"{patient['first_name']} {patient['last_name']}".lower()
                phone = patient.get('phone', '').lower()
                age = str(patient.get('age', ''))
                
                # Check if name matches
                if name_term in full_name:
                    # If filter term exists, check additional criteria
                    if filter_term:
                        if (filter_term in phone or 
                            filter_term == age or 
                            filter_term in str(patient.get('registration_date', ''))):
                            matching_patients.append(patient)
                    else:
                        matching_patients.append(patient)
            
            # Format and display matching patients
            for patient in matching_patients:
                try:
                    # Format phone number for display
                    phone = patient.get('phone', 'N/A')
                    if len(phone) == 10:
                        phone = f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
                    
                    # Get last visit date
                    last_visit = self.db.get_patient_last_visit(patient['id'])
                    last_visit_str = last_visit.strftime("%d-%b-%Y") if last_visit else "No visits yet"
                    
                    # Format display string
                    display_text = (
                        f"[ID: {patient['id']}] {patient['first_name']} {patient['last_name']} | "
                        f"📞 {phone} | Age: {patient.get('age', 'N/A')} | "
                        f"Last Visit: {last_visit_str}"
                    )
                    
                    self.patient_listbox.insert(tk.END, display_text)
                except Exception as e:
                    # If there's any error getting patient details, show basic info
                    display_text = (
                        f"[ID: {patient['id']}] {patient['first_name']} {patient['last_name']} | "
                        f"📞 {patient.get('phone', 'N/A')} | Age: {patient.get('age', 'N/A')}"
                    )
                    self.patient_listbox.insert(tk.END, display_text)
            
            # Configure listbox height based on results
            self.patient_listbox.configure(height=min(5, len(matching_patients)))
        else:
            # Hide listbox when search is empty
            self.patient_listbox.pack_forget()
    
    def on_patient_select(self, event):
        """Handle patient selection from listbox"""
        selection = self.patient_listbox.curselection()
        if selection:
            selected_text = self.patient_listbox.get(selection[0])
            try:
                # Extract patient ID from the selection
                patient_id = int(selected_text.split('[ID: ')[1].split(']')[0])
                
                # Store the selected patient ID
                self.selected_patient_id = patient_id
                
                # Set the display name (everything after the ID until the |)
                display_name = selected_text.split(']')[1].split('|')[0].strip()
                self.patient_var.set(display_name)
                
                # Hide the listbox after selection
                self.patient_listbox.pack_forget()
            except (IndexError, ValueError) as e:
                print(f"Error parsing patient selection: {str(e)}")
                messagebox.showerror("Error", "Invalid patient selection format")
    
    def save(self):
        """Save appointment"""
        try:
            # Validate input
            if not self.hour_var.get() or not self.minute_var.get() or not self.period_var.get():
                messagebox.showerror("Error", "Time is required")
                return
            
            # Construct time string in 12-hour format
            time_str = f"{self.hour_var.get()}:{self.minute_var.get()} {self.period_var.get()}"
            
            # Convert to 24-hour format for database
            try:
                time_24h = datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")
            except ValueError:
                messagebox.showerror("Error", "Invalid time format")
                return
            
            # Check if cancellation reason is provided when status is cancelled
            if self.status_var.get() == "cancelled" and not self.cancel_reason.get("1.0", "end-1c").strip():
                messagebox.showerror("Error", "Please provide a reason for cancellation")
                return
            
            # Get patient ID - first use the stored ID from initialization or selection
            patient_id = self.selected_patient_id
            
            # If we still don't have a patient ID and we're in edit mode, try to get it from the appointment
            if not patient_id and self.edit_mode and self.initial_values:
                try:
                    appointment_id = self.initial_values.get('id')
                    if appointment_id:
                        appointments = self.db.get_appointments_by_date(format_date(self.date))
                        for appt in appointments:
                            if str(appt['id']) == str(appointment_id):
                                patient_id = appt['patient_id']
                                break
                except Exception as e:
                    print(f"Error getting patient ID from appointment: {str(e)}")
            
            # If we still don't have a patient ID, try to get it from the patient var
            if not patient_id:
                patient_text = self.patient_var.get().strip()
                if '[ID:' in patient_text:
                    try:
                        patient_id = int(patient_text.split('[ID: ')[1].split(']')[0])
                    except (IndexError, ValueError):
                        pass
                
                if not patient_id:
                    # Search by name as fallback
                    patients = self.db.search_patients(patient_text)
                    if patients:
                        patient_id = patients[0]['id']
            
            # Verify we have a patient ID before proceeding
            if not patient_id:
                messagebox.showerror("Error", "Could not determine patient ID. Please select a patient.")
                return
            
            # Prepare notes
            notes = self.notes_text.get("1.0", "end-1c")
            if self.status_var.get() == "cancelled":
                cancel_reason = self.cancel_reason.get("1.0", "end-1c")
                notes = f"Cancelled: {cancel_reason}\n\nNotes: {notes}"
            
            if self.edit_mode:
                # Update existing appointment
                month_year = format_date(self.date)
                
                # For status changes (done or cancelled), use update_appointment_status
                if self.status_var.get() in ["done", "cancelled"]:
                    self.db.update_appointment_status(
                        self.initial_values.get("id"),
                        month_year,
                        self.status_var.get(),
                        notes
                    )
                else:
                    # For other updates (time, patient, etc.) use update_appointment
                    self.db.update_appointment(
                        self.initial_values.get("id"),
                        patient_id,
                        format_date(self.date),
                        time_24h,
                        notes,
                        self.status_var.get()
                    )
            else:
                # Create new appointment
                self.db.create_appointment(
                    patient_id,
                    format_date(self.date),
                    time_24h,
                    notes
                )
            
            messagebox.showinfo("Success", "Appointment saved successfully")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save appointment: {str(e)}")
            print(f"Error saving appointment: {str(e)}")
            import traceback
            traceback.print_exc() 