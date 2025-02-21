import customtkinter as ctk
from tkinter import ttk, PhotoImage, messagebox
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
from utils.network import check_internet_connection, show_offline_prompt
from utils.colors import *

APP_NAME = "Junaid Chiropractic Management System"
APP_VERSION = "2.0.0"  # Updated version number
DEVELOPER_NAME = "Naveed Jawaid"

# Add macOS specific imports
if sys.platform == "darwin":
    try:
        import objc
        from Foundation import NSBundle
    except ImportError:
        pass

class ChiropracticApp:
    def __init__(self):
        # Check internet connectivity first
        self.offline_mode = not check_internet_connection()
        if self.offline_mode:
            if not show_offline_prompt():
                raise SystemExit("User chose not to continue in offline mode")
        
        # Initialize the main window
        self.root = ctk.CTk()
        self.root.title(APP_NAME + (" (Offline Mode)" if self.offline_mode else ""))
        
        # Set window size and position
        window_width = 1200
        window_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Configure window grid
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Initialize backup scheduler only if online
        if not self.offline_mode:
            self.backup_scheduler = BackupScheduler(self.db)
        else:
            self.backup_scheduler = None
        
        # Setup UI
        self.setup_ui()
        
        # Configure window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Load logo
        self.load_logo()
        
        # Configure appearance
        self.setup_appearance()
        
        # Add exception handler
        def handle_exception(exc_type, exc_value, exc_traceback):
            """Handle uncaught exceptions"""
            print("An error occurred:")
            import traceback
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            
            # Show error to user but keep application running
            messagebox.showerror(
                "Error",
                "An error occurred but the application will continue running.\n\n" +
                str(exc_value)
            )
            return True  # Prevent the exception from propagating
            
        self.root.report_callback_exception = handle_exception
        
        # Keep a reference to prevent garbage collection
        self._keep_alive = True
        
        # Schedule a keep-alive check
        self.root.after(1000, self._check_alive)
        
        # For macOS: Set up Info.plist
        if sys.platform == "darwin":
            try:
                bundle = NSBundle.mainBundle()
                info = bundle.infoDictionary()
                if info:
                    info['NSHighResolutionCapable'] = True
                    info['LSUIElement'] = False  # Ensure dock icon is shown
            except Exception as e:
                print(f"Error configuring macOS bundle: {str(e)}")
    
    def _check_alive(self):
        """Periodic check to ensure window stays alive"""
        if self._keep_alive and hasattr(self, 'root') and self.root.winfo_exists():
            # Schedule next check
            self.root.after(1000, self._check_alive)
    
    def load_logo(self):
        """Load and set application logo"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(script_dir, "assets", "logo.png")
            icon_path = os.path.join(script_dir, "..", "assets", "icon.ico")
            
            if os.path.exists(logo_path):
                # Load and resize logo for window icon
                logo_image = Image.open(logo_path)
                # Resize to a reasonable icon size (e.g., 64x64)
                logo_image.thumbnail((64, 64))
                # Convert to PhotoImage
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                # Set as window icon
                self.root.iconphoto(True, self.logo_photo)
                
                # On Windows, also try to set the taskbar icon
                if sys.platform == "win32" and os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Error loading logo: {str(e)}")
            import traceback
            traceback.print_exc()

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
        
    def on_closing(self):
        """Handle application closing"""
        try:
            # Set flag to stop keep-alive checks
            self._keep_alive = False
            
            # Stop the backup scheduler
            if hasattr(self, 'backup_scheduler') and self.backup_scheduler:
                self.backup_scheduler.stop()
            
            # Close database connection
            if hasattr(self, 'db') and self.db:
                self.db.close()
            
            # Destroy the window
            if hasattr(self, 'root') and self.root:
                self.root.quit()
                self.root.destroy()
                
        except Exception as e:
            print(f"Error during shutdown: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Start the application"""
        try:
            # Check internet connectivity before starting
            if not check_internet_connection():
                if not show_offline_prompt():
                    # User chose not to continue
                    self.on_closing()
                    return
                
            # Start the main event loop
            self.root.mainloop()
        except Exception as e:
            print(f"Critical error in main loop: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.on_closing()

if __name__ == "__main__":
    try:
        # Create and run application
        app = ChiropracticApp()
        app.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc() 