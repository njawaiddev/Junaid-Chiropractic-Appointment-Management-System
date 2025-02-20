import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from datetime import datetime, timedelta
from utils.colors import *
import calendar

class StatisticsFrame(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Configure colors
        self.configure(fg_color=BG_WHITE)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize statistics UI components"""
        # Title
        title_frame = ctk.CTkFrame(self, fg_color=BG_WHITE)
        title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="Statistics & Analytics",
            font=("Helvetica", 24, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")
        
        # Main content
        content = ctk.CTkScrollableFrame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure((0, 1), weight=1)
        
        # Patient Statistics Section
        self.setup_patient_statistics(content)
        
        # Appointment Statistics Section
        self.setup_appointment_statistics(content)
        
        # Treatment Analytics Section
        self.setup_treatment_analytics(content)
        
        # Refresh button
        refresh_frame = ctk.CTkFrame(self, fg_color=BG_WHITE)
        refresh_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkButton(
            refresh_frame,
            text="Refresh Statistics",
            command=self.refresh_all,
            height=36,
            corner_radius=18
        ).pack(side="right", padx=5)
    
    def setup_patient_statistics(self, parent):
        """Setup patient statistics section"""
        # Section Frame
        section = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        section.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Header
        ctk.CTkLabel(
            section,
            text="Patient Statistics",
            font=("Helvetica", 18, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=10, pady=5)
        
        # Stats container
        stats_frame = ctk.CTkFrame(section, fg_color=BG_LIGHT)
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        # Total Patients
        self.total_patients_label = self.create_stat_label(
            stats_frame,
            "Total Patients",
            "0",
            PRIMARY_BLUE
        )
        
        # New Patients This Month
        self.new_patients_label = self.create_stat_label(
            stats_frame,
            "New This Month",
            "0",
            SUCCESS_GREEN
        )
        
        # Gender Distribution
        self.gender_dist_frame = ctk.CTkFrame(section, fg_color=BG_LIGHT)
        self.gender_dist_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            self.gender_dist_frame,
            text="Gender Distribution",
            font=("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=10, pady=5)
        
        # Age Groups
        self.age_groups_frame = ctk.CTkFrame(section, fg_color=BG_LIGHT)
        self.age_groups_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            self.age_groups_frame,
            text="Age Groups",
            font=("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=10, pady=5)
    
    def setup_appointment_statistics(self, parent):
        """Setup appointment statistics section"""
        # Section Frame
        section = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        section.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Header
        ctk.CTkLabel(
            section,
            text="Appointment Statistics",
            font=("Helvetica", 18, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=10, pady=5)
        
        # Stats container
        stats_frame = ctk.CTkFrame(section, fg_color=BG_LIGHT)
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        # Total Appointments
        self.total_appointments_label = self.create_stat_label(
            stats_frame,
            "Total Appointments",
            "0",
            PRIMARY_BLUE
        )
        
        # This Month's Appointments
        self.month_appointments_label = self.create_stat_label(
            stats_frame,
            "This Month",
            "0",
            SUCCESS_GREEN
        )
        
        # Appointment Status
        status_frame = ctk.CTkFrame(section, fg_color=BG_LIGHT)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            status_frame,
            text="Appointment Status",
            font=("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=10, pady=5)
        
        # Status breakdown
        self.completed_label = self.create_stat_label(
            status_frame,
            "Completed",
            "0",
            SUCCESS_GREEN
        )
        self.pending_label = self.create_stat_label(
            status_frame,
            "Pending",
            "0",
            WARNING_AMBER
        )
        self.cancelled_label = self.create_stat_label(
            status_frame,
            "Cancelled",
            "0",
            ERROR_RED
        )
        
        # Busiest Days
        busiest_frame = ctk.CTkFrame(section, fg_color=BG_LIGHT)
        busiest_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            busiest_frame,
            text="Busiest Days",
            font=("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=10, pady=5)
        
        self.busiest_days_text = ctk.CTkTextbox(
            busiest_frame,
            height=100,
            fg_color="white"
        )
        self.busiest_days_text.pack(fill="x", padx=10, pady=5)
    
    def setup_treatment_analytics(self, parent):
        """Setup treatment analytics section"""
        # Section Frame
        section = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        section.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Header
        ctk.CTkLabel(
            section,
            text="Treatment Analytics",
            font=("Helvetica", 18, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=10, pady=5)
        
        # Treatment History
        history_frame = ctk.CTkFrame(section, fg_color=BG_LIGHT)
        history_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            history_frame,
            text="Treatment History",
            font=("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=10, pady=5)
        
        # Create treeview for treatment history
        self.setup_treatment_history_tree(history_frame)
    
    def setup_treatment_history_tree(self, parent):
        """Setup treatment history treeview"""
        # Configure style
        style = ttk.Style()
        style.configure(
            "Stats.Treeview",
            background=BG_WHITE,
            fieldbackground=BG_WHITE,
            foreground=TEXT_PRIMARY,
            rowheight=30
        )
        style.configure(
            "Stats.Treeview.Heading",
            background=BG_LIGHT,
            foreground=TEXT_PRIMARY,
            font=("Helvetica", 10, "bold")
        )
        
        # Create frame for tree and buttons
        tree_container = ctk.CTkFrame(parent, fg_color=BG_LIGHT)
        tree_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create treeview
        columns = ("Date", "Patient", "Treatment", "Notes", "Actions")
        self.treatment_tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            height=10,
            style="Stats.Treeview"
        )
        
        # Configure columns
        self.treatment_tree.column("Date", width=100, minwidth=100)
        self.treatment_tree.column("Patient", width=150, minwidth=150)
        self.treatment_tree.column("Treatment", width=150, minwidth=150)
        self.treatment_tree.column("Notes", width=250, minwidth=200)
        self.treatment_tree.column("Actions", width=100, minwidth=100)
        
        for col in columns:
            self.treatment_tree.heading(col, text=col)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            tree_container,
            orient="vertical",
            command=self.treatment_tree.yview
        )
        self.treatment_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack elements
        self.treatment_tree.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Bind double-click event for viewing notes
        self.treatment_tree.bind('<Double-1>', self.view_notes)
    
    def create_stat_label(self, parent, title, value, color):
        """Create a styled statistic label"""
        frame = ctk.CTkFrame(parent, fg_color=BG_WHITE)
        frame.pack(fill="x", padx=10, pady=5)
        
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=("Helvetica", 12),
            text_color=TEXT_PRIMARY
        )
        title_label.pack(side="left", padx=5)
        
        value_label = ctk.CTkLabel(
            frame,
            text=value,
            font=("Helvetica", 14, "bold"),
            text_color=color
        )
        value_label.pack(side="right", padx=5)
        
        return value_label
    
    def refresh_all(self):
        """Refresh all statistics"""
        self.refresh_patient_statistics()
        self.refresh_appointment_statistics()
        self.refresh_treatment_statistics()
    
    def refresh_patient_statistics(self):
        """Refresh patient statistics"""
        try:
            # Get total patients
            total_patients = len(self.db.search_patients(""))
            self.total_patients_label.configure(text=str(total_patients))
            
            # Get new patients this month
            current_month = datetime.now().strftime("%Y-%m")
            new_patients = sum(
                1 for p in self.db.search_patients("")
                if p.get('registration_date', '').startswith(current_month)
            )
            self.new_patients_label.configure(text=str(new_patients))
            
            # Calculate gender distribution
            patients = self.db.search_patients("")
            gender_dist = {'Male': 0, 'Female': 0, 'Other': 0}
            for patient in patients:
                gender = patient.get('gender', 'Other')
                gender_dist[gender] = gender_dist.get(gender, 0) + 1
            
            # Update gender distribution display
            for widget in self.gender_dist_frame.winfo_children()[1:]:
                widget.destroy()
            
            for gender, count in gender_dist.items():
                percentage = (count / total_patients * 100) if total_patients > 0 else 0
                ctk.CTkLabel(
                    self.gender_dist_frame,
                    text=f"{gender}: {count} ({percentage:.1f}%)",
                    font=("Helvetica", 12),
                    text_color=TEXT_PRIMARY
                ).pack(anchor="w", padx=20, pady=2)
            
            # Calculate age groups
            age_groups = {
                '0-17': 0,
                '18-30': 0,
                '31-50': 0,
                '51-70': 0,
                '71+': 0
            }
            
            for patient in patients:
                age = patient.get('age', 0)
                if age <= 17:
                    age_groups['0-17'] += 1
                elif age <= 30:
                    age_groups['18-30'] += 1
                elif age <= 50:
                    age_groups['31-50'] += 1
                elif age <= 70:
                    age_groups['51-70'] += 1
                else:
                    age_groups['71+'] += 1
            
            # Update age groups display
            for widget in self.age_groups_frame.winfo_children()[1:]:
                widget.destroy()
            
            for age_range, count in age_groups.items():
                percentage = (count / total_patients * 100) if total_patients > 0 else 0
                ctk.CTkLabel(
                    self.age_groups_frame,
                    text=f"{age_range}: {count} ({percentage:.1f}%)",
                    font=("Helvetica", 12),
                    text_color=TEXT_PRIMARY
                ).pack(anchor="w", padx=20, pady=2)
            
        except Exception as e:
            print(f"Error refreshing patient statistics: {str(e)}")
    
    def refresh_appointment_statistics(self):
        """Refresh appointment statistics"""
        try:
            # Get all appointment tables
            self.db.connect()
            tables = self.db.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'appointments_%'"
            ).fetchall()
            
            # Get current month and year
            current_month = datetime.now().strftime("%Y-%m")
            
            # Initialize counters
            total_appointments = 0
            month_appointments = 0
            status_counts = {'done': 0, 'pending': 0, 'cancelled': 0}
            day_counts = {}
            
            # Process each appointments table
            for table in tables:
                table_name = table[0]
                
                # Get appointments from this table
                appointments = self.db.cursor.execute(
                    f"""
                    SELECT appointment_date, appointment_time, status
                    FROM {table_name}
                    """
                ).fetchall()
                
                # Count appointments
                for appt in appointments:
                    total_appointments += 1
                    
                    # Check if appointment is in current month
                    if appt[0].startswith(current_month):
                        month_appointments += 1
                    
                    # Count status
                    status = appt[2].lower() if appt[2] else 'pending'
                    status_counts[status] = status_counts.get(status, 0) + 1
                    
                    # Count days
                    try:
                        date = datetime.strptime(appt[0], "%Y-%m-%d")
                        day_name = date.strftime("%A")
                        day_counts[day_name] = day_counts.get(day_name, 0) + 1
                    except ValueError:
                        continue
            
            # Update display
            self.total_appointments_label.configure(text=str(total_appointments))
            self.month_appointments_label.configure(text=str(month_appointments))
            
            self.completed_label.configure(text=str(status_counts['done']))
            self.pending_label.configure(text=str(status_counts['pending']))
            self.cancelled_label.configure(text=str(status_counts['cancelled']))
            
            # Sort and display busiest days
            busiest_days = sorted(
                day_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            self.busiest_days_text.delete("1.0", tk.END)
            for day, count in busiest_days:
                percentage = (count / total_appointments * 100) if total_appointments > 0 else 0
                self.busiest_days_text.insert(
                    tk.END,
                    f"{day}: {count} appointments ({percentage:.1f}%)\n"
                )
            
        except Exception as e:
            print(f"Error refreshing appointment statistics: {str(e)}")
        finally:
            self.db.close()
    
    def refresh_treatment_statistics(self):
        """Refresh treatment statistics"""
        try:
            # Clear existing items
            for item in self.treatment_tree.get_children():
                self.treatment_tree.delete(item)
            
            # Connect to database
            self.db.connect()
            
            try:
                # Get all sessions with patient information using a JOIN
                query = """
                SELECT 
                    s.session_date,
                    s.treatment_notes,
                    s.follow_up_instructions,
                    p.first_name || ' ' || p.last_name as patient_name
                FROM session_history s
                JOIN patients p ON s.patient_id = p.id
                ORDER BY s.session_date DESC
                """
                
                sessions = self.db.cursor.execute(query).fetchall()
                
                # Insert sessions into treeview
                for session in sessions:
                    # Check if there are any notes
                    has_notes = bool(session[1] or session[2])
                    
                    self.treatment_tree.insert(
                        "",
                        "end",
                        values=(
                            session[0],  # session_date
                            session[3],  # patient_name
                            "Regular Treatment",  # treatment type
                            "",  # Empty notes column
                            "View Notes" if has_notes else ""  # Show button if there are notes
                        )
                    )
                
                # If no sessions found, add a placeholder message
                if not sessions:
                    self.treatment_tree.insert(
                        "",
                        "end",
                        values=("No treatment history available", "", "", "", "")
                    )
                
            finally:
                self.db.close()
            
        except Exception as e:
            print(f"Error refreshing treatment statistics: {str(e)}")
            import traceback
            traceback.print_exc()

    def view_notes(self, event):
        """Handle double-click event to view notes"""
        region = self.treatment_tree.identify_region(event.x, event.y)
        if region == "cell":
            try:
                item = self.treatment_tree.selection()[0]
                column = self.treatment_tree.identify_column(event.x)
                values = self.treatment_tree.item(item)["values"]
                
                # If clicked on Notes column or Actions column
                if column == "#4" or (column == "#5" and values[4] == "View Notes"):
                    # Get the session date and patient name
                    session_date = values[0]
                    patient_name = values[1]
                    
                    # Get full notes from database
                    notes = self.get_full_notes(session_date, patient_name)
                    
                    # Show notes in dialog
                    dialog = NotesDialog(
                        self,
                        f"Treatment Notes for {patient_name} - {session_date}",
                        notes
                    )
            except Exception as e:
                print(f"Error viewing notes: {str(e)}")
                import traceback
                traceback.print_exc()

    def get_full_notes(self, session_date, patient_name):
        """Get full notes for a session"""
        try:
            self.db.connect()
            query = """
            SELECT s.treatment_notes, s.follow_up_instructions
            FROM session_history s
            JOIN patients p ON s.patient_id = p.id
            WHERE s.session_date = ?
            AND p.first_name || ' ' || p.last_name = ?
            """
            result = self.db.cursor.execute(query, (session_date, patient_name)).fetchone()
            
            if result:
                notes = []
                if result[0]:  # Treatment notes
                    notes.append(f"Treatment Notes:\n{result[0]}")
                if result[1]:  # Follow-up instructions
                    notes.append(f"\nFollow-up Instructions:\n{result[1]}")
                
                return "\n".join(notes) if notes else "No notes available"
            return "No notes available"
            
        except Exception as e:
            print(f"Error getting full notes: {str(e)}")
            return f"Error retrieving notes: {str(e)}"
        finally:
            self.db.close()

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
        
        # Close button with updated styling and functionality
        self.close_button = ctk.CTkButton(
            main_frame,
            text="Close",
            command=self.on_close,
            width=100,
            height=32,
            corner_radius=16,
            fg_color=PRIMARY_BLUE,
            hover_color=PRIMARY_DARK
        )
        self.close_button.pack(pady=(10, 0))
        
        # Bind escape key to close
        self.bind("<Escape>", lambda e: self.on_close())
        
    def on_close(self):
        """Handle dialog closing"""
        self.grab_release()  # Release the modal grab
        self.destroy()  # Destroy the dialog 