import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime
from utils.helpers import (
    validate_phone_number,
    validate_age,
    validate_name,
    format_phone_number
)
from utils.colors import *

class PatientFrame(ctk.CTkFrame):
    def __init__(self, parent, db, refresh_callback):
        super().__init__(parent)
        self.db = db
        self.refresh_callback = refresh_callback
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Configure colors
        self.configure(fg_color=BG_WHITE)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize patient view UI components"""
        # Configure main frame to use full space
        self.pack(fill="both", expand=True)
        
        # Left panel - Patient list with search (25% width)
        left_panel = ctk.CTkFrame(self)
        left_panel.pack(side="left", fill="y", padx=(10, 5), pady=10, expand=False)
        left_panel.configure(width=int(self.winfo_screenwidth() * 0.25))
        
        # Search box
        search_frame = ctk.CTkFrame(left_panel)
        search_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search)
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search patients...",
            textvariable=self.search_var,
            height=35,
            font=("Helvetica", 12)
        )
        search_entry.pack(fill="x", padx=5, pady=5)
        
        # Patient list with modern style
        list_frame = ctk.CTkFrame(left_panel)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Configure list frame for the tree
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Create and pack the patient list
        self.setup_patient_list(list_frame)
        
        # Add patient button
        ctk.CTkButton(
            left_panel,
            text="+ Add Patient",
            command=self.add_patient,
            height=40,
            corner_radius=20
        ).pack(fill="x", padx=10, pady=(5, 10))
        
        # Right panel - Patient details with tabs (75% width)
        right_panel = ctk.CTkFrame(self)
        right_panel.pack(side="left", fill="both", padx=(5, 10), pady=10, expand=True)
        
        # Configure right panel grid
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(0, weight=1)
        
        # Create tab view
        self.tab_view = ctk.CTkTabview(right_panel)
        self.tab_view.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Add tabs
        self.tab_view.add("Personal Info")
        self.tab_view.add("Medical Info")
        self.tab_view.add("Insurance")
        self.tab_view.add("Session History")
        
        # Setup each tab
        self.setup_personal_info_tab(self.tab_view.tab("Personal Info"))
        self.setup_medical_info_tab(self.tab_view.tab("Medical Info"))
        self.setup_insurance_tab(self.tab_view.tab("Insurance"))
        self.setup_session_history_tab(self.tab_view.tab("Session History"))
        
        # Configure tab view to use full space
        for tab in ["Personal Info", "Medical Info", "Insurance", "Session History"]:
            self.tab_view.tab(tab).grid_columnconfigure(0, weight=1)
            self.tab_view.tab(tab).grid_rowconfigure(0, weight=1)
        
        # Action buttons at the bottom
        button_frame = ctk.CTkFrame(right_panel)
        button_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        # Configure button frame
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Save button
        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_patient,
            width=150,
            height=40,
            corner_radius=20
        ).grid(row=0, column=0, padx=5, pady=5)
        
        # Delete button
        ctk.CTkButton(
            button_frame,
            text="Delete",
            command=self.delete_patient,
            fg_color=ERROR_RED,
            hover_color=ERROR_RED_HOVER,
            width=150,
            height=40,
            corner_radius=20
        ).grid(row=0, column=1, padx=5, pady=5)
    
    def setup_patient_list(self, parent):
        """Set up the patient list treeview"""
        tree_frame = ctk.CTkFrame(parent)
        tree_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        tree_frame.configure(fg_color=BG_WHITE)
        tree_frame.grid_columnconfigure(0, weight=1)  # Make tree frame expand horizontally
        tree_frame.grid_rowconfigure(0, weight=1)     # Make tree frame expand vertically
        
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
        columns = ("Name", "Phone")
        self.patient_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Treeview"
        )
        
        # Configure columns with modern proportions
        for col in columns:
            self.patient_tree.heading(col, text=col)
            self.patient_tree.column(col, anchor="w")
        
        self.patient_tree.column("Name", width=250, minwidth=200)
        self.patient_tree.column("Phone", width=200, minwidth=150)
        
        # Modern scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.patient_tree.yview)
        self.patient_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack with modern padding and expansion
        self.patient_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind selection event
        self.patient_tree.bind("<<TreeviewSelect>>", self.on_patient_select)
        
        # Load initial data
        self.refresh_patient_list()
    
    def setup_personal_info_tab(self, parent):
        """Setup personal information tab"""
        # Create scrollable frame
        container = ctk.CTkScrollableFrame(parent)
        container.pack(fill="both", expand=True, padx=5, pady=5)
        container.grid_columnconfigure(0, weight=1)
        
        # Title and mandatory fields section
        mandatory_frame = ctk.CTkFrame(container)
        mandatory_frame.pack(fill="x", pady=(0, 5))
        mandatory_frame.grid_columnconfigure((0, 1), weight=1)  # Both columns expand equally
        
        # Left column fields
        row = 0
        
        # Title selection
        ctk.CTkLabel(mandatory_frame, text="Title:", text_color=TEXT_PRIMARY).grid(row=row, column=0, sticky="w", padx=5)
        self.title_var = tk.StringVar()
        title_cb = ctk.CTkComboBox(
            mandatory_frame,
            values=["Mr.", "Mrs.", "Ms.", "Dr."],
            variable=self.title_var,
            width=100
        )
        title_cb.grid(row=row, column=1, sticky="w", padx=5, pady=2)
        row += 1
        
        # First Name (mandatory)
        ctk.CTkLabel(mandatory_frame, text="First Name:*", text_color=TEXT_PRIMARY).grid(row=row, column=0, sticky="w", padx=5)
        self.first_name_entry = self.create_entry(mandatory_frame)
        self.first_name_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        row += 1
        
        # Last Name (mandatory)
        ctk.CTkLabel(mandatory_frame, text="Last Name:*", text_color=TEXT_PRIMARY).grid(row=row, column=0, sticky="w", padx=5)
        self.last_name_entry = self.create_entry(mandatory_frame)
        self.last_name_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        row += 1
        
        # Gender (mandatory)
        ctk.CTkLabel(mandatory_frame, text="Gender:*", text_color=TEXT_PRIMARY).grid(row=row, column=0, sticky="w", padx=5)
        gender_frame = ctk.CTkFrame(mandatory_frame)
        gender_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        gender_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.gender_var = tk.StringVar(value="Male")
        for i, gender in enumerate(["Male", "Female", "Other"]):
            ctk.CTkRadioButton(
                gender_frame,
                text=gender,
                variable=self.gender_var,
                value=gender
            ).grid(row=0, column=i, padx=10)
        row += 1
        
        # Age
        ctk.CTkLabel(mandatory_frame, text="Age:*", text_color=TEXT_PRIMARY).grid(row=row, column=0, sticky="w", padx=5)
        self.age_entry = self.create_entry(mandatory_frame, placeholder="Enter age")
        self.age_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        row += 1
        
        # Phone (mandatory)
        ctk.CTkLabel(mandatory_frame, text="Phone:*", text_color=TEXT_PRIMARY).grid(row=row, column=0, sticky="w", padx=5)
        self.phone_entry = self.create_entry(mandatory_frame)
        self.phone_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        row += 1
        
        # Email
        ctk.CTkLabel(mandatory_frame, text="Email:", text_color=TEXT_PRIMARY).grid(row=row, column=0, sticky="w", padx=5)
        self.email_entry = self.create_entry(mandatory_frame)
        self.email_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        row += 1
        
        # Address Section
        address_frame = ctk.CTkFrame(container)
        address_frame.pack(fill="x", pady=5)
        address_frame.grid_columnconfigure(1, weight=1)
        
        # Address header
        ctk.CTkLabel(
            address_frame,
            text="Address",
            font=("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(5, 10))
        
        # Street
        ctk.CTkLabel(address_frame, text="Street:", text_color=TEXT_PRIMARY).grid(row=1, column=0, sticky="w", padx=5)
        self.street_entry = self.create_entry(address_frame)
        self.street_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        # City and State (side by side)
        city_state_frame = ctk.CTkFrame(address_frame)
        city_state_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        city_state_frame.grid_columnconfigure((0, 1), weight=1)
        
        # City
        ctk.CTkLabel(city_state_frame, text="City:", text_color=TEXT_PRIMARY).grid(row=0, column=0, sticky="w", padx=5)
        self.city_entry = self.create_entry(city_state_frame)
        self.city_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        # State
        ctk.CTkLabel(city_state_frame, text="State:", text_color=TEXT_PRIMARY).grid(row=0, column=2, sticky="w", padx=5)
        self.state_entry = self.create_entry(city_state_frame)
        self.state_entry.grid(row=0, column=3, sticky="ew", padx=5)
        
        # ZIP
        ctk.CTkLabel(address_frame, text="ZIP:", text_color=TEXT_PRIMARY).grid(row=3, column=0, sticky="w", padx=5)
        self.zip_entry = self.create_entry(address_frame)
        self.zip_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        
        # Emergency Contact Section
        emergency_frame = ctk.CTkFrame(container)
        emergency_frame.pack(fill="x", pady=5)
        emergency_frame.grid_columnconfigure(1, weight=1)
        
        # Emergency Contact header
        ctk.CTkLabel(
            emergency_frame,
            text="Emergency Contact",
            font=("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(5, 10))
        
        # Name
        ctk.CTkLabel(emergency_frame, text="Name:", text_color=TEXT_PRIMARY).grid(row=1, column=0, sticky="w", padx=5)
        self.emergency_name_entry = self.create_entry(emergency_frame)
        self.emergency_name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        # Phone
        ctk.CTkLabel(emergency_frame, text="Phone:", text_color=TEXT_PRIMARY).grid(row=2, column=0, sticky="w", padx=5)
        self.emergency_phone_entry = self.create_entry(emergency_frame)
        self.emergency_phone_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        
        # Relationship
        ctk.CTkLabel(emergency_frame, text="Relationship:", text_color=TEXT_PRIMARY).grid(row=3, column=0, sticky="w", padx=5)
        self.emergency_relation_entry = self.create_entry(emergency_frame)
        self.emergency_relation_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
    
    def setup_medical_info_tab(self, parent):
        """Setup medical information tab"""
        container = ctk.CTkScrollableFrame(parent)
        container.pack(fill="both", expand=True, padx=5, pady=5)
        container.grid_columnconfigure(0, weight=1)
        
        # Reference source
        ref_frame = ctk.CTkFrame(container)
        ref_frame.pack(fill="x", pady=(0, 5))
        ref_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(ref_frame, text="Reference:", text_color=TEXT_PRIMARY).grid(row=0, column=0, sticky="w", padx=5)
        self.reference_entry = self.create_entry(ref_frame)
        self.reference_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        # Medical Conditions
        conditions_frame = ctk.CTkFrame(container)
        conditions_frame.pack(fill="x", pady=5)
        conditions_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            conditions_frame,
            text="Medical Conditions:",
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=(5, 2))
        
        self.conditions_text = self.create_textbox(conditions_frame, height=100)
        self.conditions_text.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        # Past Surgeries
        surgeries_frame = ctk.CTkFrame(container)
        surgeries_frame.pack(fill="x", pady=5)
        surgeries_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            surgeries_frame,
            text="Past Surgeries:",
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=(5, 2))
        
        self.surgeries_text = self.create_textbox(surgeries_frame, height=100)
        self.surgeries_text.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        # Current Medications
        medications_frame = ctk.CTkFrame(container)
        medications_frame.pack(fill="x", pady=5)
        medications_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            medications_frame,
            text="Current Medications:",
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=(5, 2))
        
        self.medications_text = self.create_textbox(medications_frame, height=100)
        self.medications_text.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        # Allergies
        allergies_frame = ctk.CTkFrame(container)
        allergies_frame.pack(fill="x", pady=5)
        allergies_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            allergies_frame,
            text="Allergies:",
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=(5, 2))
        
        self.allergies_text = self.create_textbox(allergies_frame, height=100)
        self.allergies_text.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        # Chiropractic History
        history_frame = ctk.CTkFrame(container)
        history_frame.pack(fill="x", pady=5)
        history_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            history_frame,
            text="Chiropractic History:",
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=(5, 2))
        
        self.history_text = self.create_textbox(history_frame, height=100)
        self.history_text.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
    
    def setup_insurance_tab(self, parent):
        """Setup insurance information tab"""
        container = ctk.CTkScrollableFrame(parent)
        container.pack(fill="both", expand=True, padx=5, pady=5)
        container.grid_columnconfigure(0, weight=1)
        
        # Insurance Provider
        provider_frame = ctk.CTkFrame(container)
        provider_frame.pack(fill="x", pady=(0, 5))
        provider_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            provider_frame,
            text="Insurance Provider:",
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.insurance_provider_entry = self.create_entry(provider_frame)
        self.insurance_provider_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Policy Number
        policy_frame = ctk.CTkFrame(container)
        policy_frame.pack(fill="x", pady=5)
        policy_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            policy_frame,
            text="Policy Number:",
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.policy_number_entry = self.create_entry(policy_frame)
        self.policy_number_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Coverage Details
        coverage_frame = ctk.CTkFrame(container)
        coverage_frame.pack(fill="x", pady=5)
        coverage_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            coverage_frame,
            text="Coverage Details:",
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=(5, 2))
        
        self.coverage_text = self.create_textbox(coverage_frame, height=200)
        self.coverage_text.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
    
    def setup_session_history_tab(self, parent):
        """Setup session history tab"""
        # Create a frame to hold the tree and scrollbar
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=5, pady=5)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        
        # Configure modern style for treeview
        style = ttk.Style()
        style.configure(
            "SessionTree.Treeview",
            background=BG_WHITE,
            fieldbackground=BG_WHITE,
            foreground=TEXT_PRIMARY,
            rowheight=40,
            font=("Helvetica", 11)
        )
        style.configure(
            "SessionTree.Treeview.Heading",
            background=BG_LIGHT,
            foreground=TEXT_PRIMARY,
            font=("Helvetica", 12, "bold")
        )
        style.map(
            "SessionTree.Treeview",
            background=[("selected", PRIMARY_LIGHT)],
            foreground=[("selected", TEXT_PRIMARY)]
        )
        
        # Session history list with updated columns
        columns = ("Date", "Type", "Status", "Notes", "Next Appointment")
        self.session_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="SessionTree.Treeview"
        )
        
        # Configure column widths and headings
        column_widths = {
            "Date": 120,
            "Type": 100,
            "Status": 100,
            "Notes": 400,
            "Next Appointment": 150
        }
        
        for col, width in column_widths.items():
            self.session_tree.column(col, width=width, minwidth=width-20)
            self.session_tree.heading(col, text=col)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.session_tree.yview
        )
        x_scrollbar = ttk.Scrollbar(
            frame,
            orient="horizontal",
            command=self.session_tree.xview
        )
        self.session_tree.configure(
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
        
        # Grid layout for better space utilization
        self.session_tree.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure tags for different status colors
        self.session_tree.tag_configure('done', foreground=SUCCESS_GREEN)
        self.session_tree.tag_configure('pending', foreground=WARNING_AMBER)
        self.session_tree.tag_configure('cancelled', foreground=ERROR_RED)
    
    def create_field_frame(self, parent, label_text):
        """Create a frame for a field with label"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=2)
        frame.grid_columnconfigure(1, weight=1)  # Make the entry field expand
        
        label = ctk.CTkLabel(
            frame,
            text=label_text,
            text_color=TEXT_PRIMARY,
            anchor="w"  # Left-align the label
        )
        label.grid(row=0, column=0, padx=(5, 10), sticky="w")
        
        return frame
    
    def create_entry(self, parent, placeholder=""):
        """Create a styled entry widget"""
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            fg_color="white",
            border_color=PRIMARY_BLUE,
            text_color=TEXT_PRIMARY,
            height=32  # Increased height for better visibility
        )
        entry.grid(row=0, column=1, sticky="ew", padx=5)  # Use grid instead of pack
        return entry
    
    def create_textbox(self, parent, height=60):
        """Create a styled textbox widget"""
        textbox = ctk.CTkTextbox(
            parent,
            height=height,
            fg_color="white",
            border_color=PRIMARY_BLUE,
            text_color=TEXT_PRIMARY
        )
        textbox.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(5, 0))  # Use grid instead of pack
        return textbox
    
    def setup_action_buttons(self, parent):
        """Setup action buttons"""
        button_frame = ctk.CTkFrame(parent)
        button_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_patient,
            fg_color=ACCENT_TEAL,
            text_color=TEXT_WHITE,
            hover_color="#0097A7"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Delete",
            command=self.delete_patient,
            fg_color=ERROR_RED,
            text_color=TEXT_WHITE,
            hover_color="#DC2626"
        ).pack(side="left", padx=5)
    
    def save_patient(self):
        """Save patient details"""
        # Validate mandatory fields
        if not self.validate_mandatory_fields():
            return
        
        # Collect all field values
        patient_data = {
            'title': self.title_var.get(),
            'first_name': self.first_name_entry.get().strip(),
            'last_name': self.last_name_entry.get().strip(),
            'gender': self.gender_var.get(),
            'age': int(self.age_entry.get().strip()),
            'phone': self.phone_entry.get().strip(),
            'email': self.email_entry.get().strip(),
            'address_street': self.street_entry.get().strip(),
            'address_city': self.city_entry.get().strip(),
            'address_state': self.state_entry.get().strip(),
            'address_zip': self.zip_entry.get().strip(),
            'emergency_contact_name': self.emergency_name_entry.get().strip(),
            'emergency_contact_phone': self.emergency_phone_entry.get().strip(),
            'emergency_contact_relation': self.emergency_relation_entry.get().strip(),
            'reference_source': self.reference_entry.get().strip(),
            'medical_conditions': self.conditions_text.get("1.0", "end-1c"),
            'past_surgeries': self.surgeries_text.get("1.0", "end-1c"),
            'current_medications': self.medications_text.get("1.0", "end-1c"),
            'allergies': self.allergies_text.get("1.0", "end-1c"),
            'chiropractic_history': self.history_text.get("1.0", "end-1c"),
            'insurance_provider': self.insurance_provider_entry.get().strip(),
            'insurance_policy_number': self.policy_number_entry.get().strip(),
            'insurance_coverage_details': self.coverage_text.get("1.0", "end-1c")
        }
        
        # Remove empty values
        patient_data = {k: v for k, v in patient_data.items() if v}
        
        try:
            selected = self.patient_tree.selection()
            if selected:
                # Update existing patient
                patient_id = int(self.patient_tree.item(selected[0])["tags"][0])
                self.db.update_patient(patient_id, patient_data)
                messagebox.showinfo("Success", "Patient updated successfully")
            else:
                # Add new patient
                self.db.add_patient(patient_data)
                messagebox.showinfo("Success", "Patient added successfully")
            
            # Refresh list
            self.refresh_patient_list()
            self.refresh_callback()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save patient: {str(e)}")
    
    def validate_mandatory_fields(self):
        """Validate all mandatory fields"""
        if not self.first_name_entry.get().strip():
            messagebox.showerror("Error", "First Name is required")
            return False
        
        if not self.last_name_entry.get().strip():
            messagebox.showerror("Error", "Last Name is required")
            return False
        
        if not self.phone_entry.get().strip():
            messagebox.showerror("Error", "Phone number is required")
            return False
        
        if not self.age_entry.get().strip():
            messagebox.showerror("Error", "Age is required")
            return False
        
        # Validate age range
        try:
            age = int(self.age_entry.get().strip())
            if age <= 0 or age > 150:
                messagebox.showerror("Error", "Age must be between 1 and 150")
                return False
        except ValueError:
            messagebox.showerror("Error", "Invalid age format. Must be a number")
            return False
        
        return True
    
    def refresh_patient_list(self, search_term=""):
        """Refresh the patient list"""
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)
        
        patients = self.db.search_patients(search_term)
        
        for patient in patients:
            self.patient_tree.insert(
                "",
                "end",
                values=(
                    f"{patient['first_name']} {patient['last_name']}",
                    patient['phone']
                ),
                tags=(str(patient['id']),)
            )
    
    def on_patient_select(self, event):
        """Handle patient selection"""
        selected = self.patient_tree.selection()
        if not selected:
            return
        
        try:
            patient_id = int(self.patient_tree.item(selected[0])["tags"][0])
            patient = self.db.get_patient(patient_id)
            
            # Clear and update fields with patient data
            # Title
            self.title_var.set(patient.get('title', ''))
            
            # First Name
            self.first_name_entry.delete(0, tk.END)
            if patient.get('first_name'):
                self.first_name_entry.insert(0, patient['first_name'])
            
            # Last Name
            self.last_name_entry.delete(0, tk.END)
            if patient.get('last_name'):
                self.last_name_entry.insert(0, patient['last_name'])
            
            # Gender
            self.gender_var.set(patient.get('gender', 'Male'))
            
            # Age
            self.age_entry.delete(0, tk.END)
            if patient.get('age'):
                self.age_entry.insert(0, str(patient['age']))
            
            # Phone
            self.phone_entry.delete(0, tk.END)
            if patient.get('phone'):
                self.phone_entry.insert(0, patient['phone'])
            
            # Email
            self.email_entry.delete(0, tk.END)
            if patient.get('email'):
                self.email_entry.insert(0, patient['email'])
            
            # Address
            self.street_entry.delete(0, tk.END)
            if patient.get('address_street'):
                self.street_entry.insert(0, patient['address_street'])
            
            self.city_entry.delete(0, tk.END)
            if patient.get('address_city'):
                self.city_entry.insert(0, patient['address_city'])
            
            self.state_entry.delete(0, tk.END)
            if patient.get('address_state'):
                self.state_entry.insert(0, patient['address_state'])
            
            self.zip_entry.delete(0, tk.END)
            if patient.get('address_zip'):
                self.zip_entry.insert(0, patient['address_zip'])
            
            # Emergency Contact
            self.emergency_name_entry.delete(0, tk.END)
            if patient.get('emergency_contact_name'):
                self.emergency_name_entry.insert(0, patient['emergency_contact_name'])
            
            self.emergency_phone_entry.delete(0, tk.END)
            if patient.get('emergency_contact_phone'):
                self.emergency_phone_entry.insert(0, patient['emergency_contact_phone'])
            
            self.emergency_relation_entry.delete(0, tk.END)
            if patient.get('emergency_contact_relation'):
                self.emergency_relation_entry.insert(0, patient['emergency_contact_relation'])
            
            # Reference
            self.reference_entry.delete(0, tk.END)
            if patient.get('reference_source'):
                self.reference_entry.insert(0, patient['reference_source'])
            
            # Medical Information
            self.conditions_text.delete("1.0", tk.END)
            if patient.get('medical_conditions'):
                self.conditions_text.insert("1.0", patient['medical_conditions'])
            
            self.surgeries_text.delete("1.0", tk.END)
            if patient.get('past_surgeries'):
                self.surgeries_text.insert("1.0", patient['past_surgeries'])
            
            self.medications_text.delete("1.0", tk.END)
            if patient.get('current_medications'):
                self.medications_text.insert("1.0", patient['current_medications'])
            
            self.allergies_text.delete("1.0", tk.END)
            if patient.get('allergies'):
                self.allergies_text.insert("1.0", patient['allergies'])
            
            self.history_text.delete("1.0", tk.END)
            if patient.get('chiropractic_history'):
                self.history_text.insert("1.0", patient['chiropractic_history'])
            
            # Insurance Information
            self.insurance_provider_entry.delete(0, tk.END)
            if patient.get('insurance_provider'):
                self.insurance_provider_entry.insert(0, patient['insurance_provider'])
            
            self.policy_number_entry.delete(0, tk.END)
            if patient.get('insurance_policy_number'):
                self.policy_number_entry.insert(0, patient['insurance_policy_number'])
            
            self.coverage_text.delete("1.0", tk.END)
            if patient.get('insurance_coverage_details'):
                self.coverage_text.insert("1.0", patient['insurance_coverage_details'])
            
            # Update session history
            self.refresh_session_history(patient.get('session_history', []))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load patient data: {str(e)}")
            print(f"Error loading patient data: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def refresh_session_history(self, sessions):
        """Refresh the session history tree with both appointments and session history"""
        # Clear existing items
        for item in self.session_tree.get_children():
            self.session_tree.delete(item)
        
        try:
            # Get patient ID from the selected patient
            selected = self.patient_tree.selection()
            if not selected:
                return
            
            patient_id = int(self.patient_tree.item(selected[0])["tags"][0])
            
            # Get all appointments for this patient from all monthly tables
            all_appointments = []
            
            # Connect to database
            self.db.connect()
            
            try:
                # First, get all appointments to create a lookup for next appointments
                tables = self.db.cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'appointments_%'"
                ).fetchall()
                
                # Get all future appointments for this patient
                future_appointments = []
                for table in tables:
                    table_name = table[0]
                    appointments = self.db.cursor.execute(
                        f"""
                        SELECT appointment_date, appointment_time, status, notes
                        FROM {table_name}
                        WHERE patient_id = ? AND status = 'pending'
                        AND appointment_date >= CURRENT_DATE
                        ORDER BY appointment_date, appointment_time
                        """,
                        (patient_id,)
                    ).fetchall()
                    future_appointments.extend(appointments)
                
                # Get all past appointments
                for table in tables:
                    table_name = table[0]
                    appointments = self.db.cursor.execute(
                        f"""
                        SELECT appointment_date, appointment_time, status, notes
                        FROM {table_name}
                        WHERE patient_id = ?
                        """,
                        (patient_id,)
                    ).fetchall()
                    all_appointments.extend(appointments)
            finally:
                # Always close the connection
                self.db.close()
            
            # Sort all entries by date
            all_entries = []
            
            # Add appointments
            for appt in all_appointments:
                # Find next appointment
                next_appt = ""
                if future_appointments:
                    next_date = future_appointments[0][0]
                    next_time = future_appointments[0][1]
                    # Convert time from 24h to 12h format
                    try:
                        time_obj = datetime.strptime(next_time, "%H:%M")
                        next_time = time_obj.strftime("%I:%M %p")
                    except ValueError:
                        pass
                    next_appt = f"{next_date} {next_time}"
                
                entry = {
                    'date': appt[0],
                    'type': 'Appointment',
                    'status': appt[2],
                    'notes': appt[3],
                    'next_appointment': next_appt
                }
                all_entries.append(entry)
            
            # Add session history entries
            for session in sessions:
                # Find next appointment
                next_appt = ""
                if future_appointments:
                    next_date = future_appointments[0][0]
                    next_time = future_appointments[0][1]
                    # Convert time from 24h to 12h format
                    try:
                        time_obj = datetime.strptime(next_time, "%H:%M")
                        next_time = time_obj.strftime("%I:%M %p")
                    except ValueError:
                        pass
                    next_appt = f"{next_date} {next_time}"
                
                entry = {
                    'date': session['session_date'],
                    'type': 'Session',
                    'status': 'done',
                    'notes': session.get('treatment_notes', ''),
                    'next_appointment': next_appt
                }
                all_entries.append(entry)
            
            # Sort all entries by date in descending order (most recent first)
            all_entries.sort(key=lambda x: x['date'], reverse=True)
            
            # Insert into treeview
            for entry in all_entries:
                self.session_tree.insert(
                    "",
                    "end",
                    values=(
                        entry['date'],
                        entry['type'],
                        entry['status'].capitalize(),
                        entry['notes'],
                        entry['next_appointment']
                    ),
                    tags=(entry['status'].lower(),)
                )
            
        except Exception as e:
            print(f"Error refreshing session history: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def add_patient(self):
        """Clear fields for new patient"""
        self.patient_tree.selection_remove(self.patient_tree.selection())
        
        self.title_var.set("")
        self.first_name_entry.delete(0, "end")
        self.last_name_entry.delete(0, "end")
        self.gender_var.set("Male")
        self.age_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.street_entry.delete(0, "end")
        self.city_entry.delete(0, "end")
        self.state_entry.delete(0, "end")
        self.zip_entry.delete(0, "end")
        self.emergency_name_entry.delete(0, "end")
        self.emergency_phone_entry.delete(0, "end")
        self.emergency_relation_entry.delete(0, "end")
        self.reference_entry.delete(0, "end")
        self.conditions_text.delete("1.0", "end")
        self.surgeries_text.delete("1.0", "end")
        self.medications_text.delete("1.0", "end")
        self.allergies_text.delete("1.0", "end")
        self.history_text.delete("1.0", "end")
        self.insurance_provider_entry.delete(0, "end")
        self.policy_number_entry.delete(0, "end")
        self.coverage_text.delete("1.0", "end")
        
        # Clear session history
        for item in self.session_tree.get_children():
            self.session_tree.delete(item)
    
    def delete_patient(self):
        """Delete selected patient"""
        selected = self.patient_tree.selection()
        if not selected:
            return
        
        # Get patient ID
        patient_id = int(self.patient_tree.item(selected[0])["tags"][0])
        
        # Delete patient
        self.db.delete_patient(patient_id)
        
        # Refresh list
        self.refresh_patient_list()
        self.refresh_callback()
        
        # Clear fields
        self.add_patient()

    def on_search(self, *args):
        """Handle search input change"""
        self.refresh_patient_list(self.search_var.get())
    
    def validate_name_input(self, event):
        """Validate name input - only letters, spaces, and hyphens allowed"""
        widget = event.widget
        current = widget.get()
        valid = ''.join(char for char in current if char.isalpha() or char in [' ', '-'])
        if current != valid:
            widget.delete(0, 'end')
            widget.insert(0, valid)

    def validate_age_input(self, event):
        """Validate age input - only numbers allowed, max 150"""
        current = self.age_entry.get()
        valid = ''.join(char for char in current if char.isdigit())
        if current != valid:
            self.age_entry.delete(0, 'end')
            self.age_entry.insert(0, valid)
        if valid and int(valid) > 150:
            self.age_entry.delete(0, 'end')
            self.age_entry.insert(0, '150')

    def validate_phone_input(self, event):
        """Validate phone input - only numbers allowed"""
        widget = event.widget
        current = widget.get()
        valid = ''.join(char for char in current if char.isdigit())
        if current != valid:
            widget.delete(0, 'end')
            widget.insert(0, valid)

    def validate_email_input(self, event):
        """Validate email input - alphanumeric, @, ., and common email characters"""
        current = self.email_entry.get()
        valid = ''.join(char for char in current if char.isalnum() or char in ['@', '.', '_', '-'])
        if current != valid:
            self.email_entry.delete(0, 'end')
            self.email_entry.insert(0, valid)

    def validate_address_input(self, event):
        """Validate address input - alphanumeric, spaces, and common address characters"""
        current = self.street_entry.get()
        valid = ''.join(char for char in current if char.isalnum() or char in [' ', '-', ',', '.', '#', '/'])
        if current != valid:
            self.street_entry.delete(0, 'end')
            self.street_entry.insert(0, valid)

    def validate_city_input(self, event):
        """Validate city input - only letters, spaces, and hyphens allowed"""
        current = self.city_entry.get()
        valid = ''.join(char for char in current if char.isalpha() or char in [' ', '-'])
        if current != valid:
            self.city_entry.delete(0, 'end')
            self.city_entry.insert(0, valid)

    def validate_state_input(self, event):
        """Validate state input - only letters allowed"""
        current = self.state_entry.get()
        valid = ''.join(char for char in current if char.isalpha())
        if current != valid:
            self.state_entry.delete(0, 'end')
            self.state_entry.insert(0, valid)

    def validate_zip_input(self, event):
        """Validate zip input - only numbers allowed"""
        current = self.zip_entry.get()
        valid = ''.join(char for char in current if char.isdigit())
        if current != valid:
            self.zip_entry.delete(0, 'end')
            self.zip_entry.insert(0, valid)

    def validate_text_input(self, event):
        """Validate text input - alphanumeric, spaces, and common punctuation"""
        widget = event.widget
        if isinstance(widget, ctk.CTkEntry):
            current = widget.get()
            valid = ''.join(char for char in current if char.isalnum() or char in [' ', '-', ',', '.', '(', ')', '/', '&'])
            if current != valid:
                widget.delete(0, 'end')
                widget.insert(0, valid)
        else:  # CTkTextbox
            current = widget.get("1.0", "end-1c")
            valid = ''.join(char for char in current if char.isalnum() or char in [' ', '-', ',', '.', '(', ')', '/', '&', '\n'])
            if current != valid:
                widget.delete("1.0", "end")
                widget.insert("1.0", valid)

    def validate_alphanumeric_input(self, event):
        """Validate alphanumeric input - letters and numbers only"""
        widget = event.widget
        current = widget.get()
        valid = ''.join(char for char in current if char.isalnum())
        if current != valid:
            widget.delete(0, 'end')
            widget.insert(0, valid)

    def validate_inputs(self):
        """Validate all input fields"""
        name = self.first_name_entry.get().strip()
        age = self.age_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "First Name is required")
            return False
        
        if not age:
            messagebox.showerror("Error", "Age is required")
            return False
        
        if not phone:
            messagebox.showerror("Error", "Phone number is required")
            return False
        
        if not validate_phone_number(phone):
            messagebox.showerror("Error", "Invalid phone number format. Must be 10-15 digits")
            return False
        
        return True 