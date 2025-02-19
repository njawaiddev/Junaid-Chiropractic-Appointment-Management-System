import customtkinter as ctk
from tkinter import ttk, PhotoImage
from pathlib import Path
import sys
import os
from PIL import Image, ImageTk
from ui.dashboard import DashboardFrame
from ui.patient_view import PatientFrame
from ui.settings import SettingsFrame
from ui.statistics import StatisticsFrame
from database.db_manager import DatabaseManager
from utils.backup_scheduler import BackupScheduler
from utils.colors import *

DEVELOPER_NAME = "Naveed Jawaid"
APP_NAME = "Junaid Chiropractic Management System"

class ChiropracticApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title(f"{APP_NAME} - Developed by {DEVELOPER_NAME}")
        self.setup_window()
        
        # Load logo
        self.load_logo()
        
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
        
    def load_logo(self):
        """Load and set application logo"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(script_dir, "assets", "logo.png")
            if os.path.exists(logo_path):
                # Load and resize logo
                logo_image = Image.open(logo_path)
                # Resize to a reasonable icon size (e.g., 64x64)
                logo_image.thumbnail((64, 64))
                # Convert to PhotoImage
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                # Set as window icon
                self.root.iconphoto(True, self.logo_photo)
        except Exception as e:
            print(f"Error loading logo: {str(e)}")

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
        
        # Calculate window size (80% of screen size)
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # Calculate position to center the window
        position_x = (screen_width - window_width) // 2
        position_y = (screen_height - window_height) // 2
        
        # Set window size and position
        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        
        # Set minimum window size (1024x768 or 60% of screen size, whichever is smaller)
        min_width = min(1024, int(screen_width * 0.6))
        min_height = min(768, int(screen_height * 0.6))
        self.root.minsize(min_width, min_height)
        
        # Allow window to be maximized
        self.root.state('zoomed')
        
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