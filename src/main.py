import customtkinter as ctk
from tkinter import ttk
from pathlib import Path
import sys
from ui.dashboard import DashboardFrame
from ui.patient_view import PatientFrame
from ui.settings import SettingsFrame
from ui.statistics import StatisticsFrame
from database.db_manager import DatabaseManager
from utils.backup_scheduler import BackupScheduler
from utils.colors import *

class ChiropracticApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Junaid Chiropractic Management System")
        self.setup_window()
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Initialize backup scheduler
        self.backup_scheduler = BackupScheduler(self.db)
        self.backup_scheduler.start()
        
        # Configure appearance
        self.setup_appearance()
        
        # Initialize UI components
        self.setup_ui()
        
        # Bind cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_appearance(self):
        """Configure application appearance"""
        # Set light mode
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Configure colors for better visibility
        self.root.configure(fg_color="#F5F7FA")  # Light gray background
        
        # Configure text color for all widgets
        style = ttk.Style()
        style.configure(
            "Treeview",
            background="white",
            foreground="#2C3E50",
            fieldbackground="white",
            rowheight=25
        )
        style.configure(
            "Treeview.Heading",
            background="#F8FAFC",
            foreground="#2C3E50",
            relief="flat"
        )
        
        # Configure selection colors
        style.map(
            "Treeview",
            background=[("selected", "#3B82F6")],
            foreground=[("selected", "white")]
        )

    def setup_window(self):
        """Configure main window properties"""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window size to full screen
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.minsize(1024, 768)  # Set minimum window size
        
        # Configure grid weights for better expansion
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Add padding around the main container
        self.root.configure(padx=20, pady=20)

    def setup_ui(self):
        """Initialize and configure UI components"""
        # Create tab view with modern styling
        self.tab_view = ctk.CTkTabview(self.root)
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        
        # Configure tab view appearance
        self.tab_view.configure(
            fg_color="white",
            text_color="#2C3E50",
            segmented_button_fg_color="#3B82F6",
            segmented_button_selected_color="#2563EB",
            segmented_button_selected_hover_color="#1D4ED8",
            segmented_button_unselected_color="#F1F5F9",
            segmented_button_unselected_hover_color="#E2E8F0"
        )
        
        # Add tabs
        self.tab_view.add("Dashboard")
        self.tab_view.add("Patients")
        self.tab_view.add("Statistics")
        self.tab_view.add("Settings")
        
        # Initialize frames
        self.dashboard_frame = DashboardFrame(
            self.tab_view.tab("Dashboard"),
            self.db
        )
        self.patient_frame = PatientFrame(
            self.tab_view.tab("Patients"),
            self.db,
            self.dashboard_frame.refresh_appointments
        )
        self.statistics_frame = StatisticsFrame(
            self.tab_view.tab("Statistics"),
            self.db
        )
        self.settings_frame = SettingsFrame(
            self.tab_view.tab("Settings"),
            self.db
        )
        
        # Configure tab frames to use full space
        self.dashboard_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.patient_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.statistics_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.settings_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configure tab grid weights
        for tab in ["Dashboard", "Patients", "Statistics", "Settings"]:
            self.tab_view.tab(tab).grid_columnconfigure(0, weight=1)
            self.tab_view.tab(tab).grid_rowconfigure(0, weight=1)
            self.tab_view.tab(tab).configure(fg_color="white")
        
        # Set default tab
        self.tab_view.set("Dashboard")
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

    def on_closing(self):
        """Handle application closing"""
        # Stop the backup scheduler
        if self.backup_scheduler:
            self.backup_scheduler.stop()
        
        # Close database connection
        if self.db:
            self.db.close()
        
        # Destroy the window
        self.root.destroy()

if __name__ == "__main__":
    # Create and run application
    app = ChiropracticApp()
    app.run() 