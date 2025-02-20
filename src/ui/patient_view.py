import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime
from utils.helpers import (
    validate_phone_number,
    validate_age,
    validate_name,
    format_phone_number,
    format_time,
    format_time_12hr
)
from utils.colors import *

class PatientFrame(ctk.CTkFrame):
    def __init__(self, parent, db, refresh_callback):
        super().__init__(parent)
        self.db = db
        self.refresh_callback = refresh_callback
        self.patient_id = None  # Initialize patient_id
        
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
        columns = ("ID", "Name", "Age", "Phone")
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
        
        self.patient_tree.column("ID", width=80, minwidth=80)
        self.patient_tree.column("Name", width=250, minwidth=200)
        self.patient_tree.column("Age", width=80, minwidth=80)
        self.patient_tree.column("Phone", width=150, minwidth=150)
        
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
        container.pack(fill="both", expand=True, padx=10, pady=10)
        container.grid_columnconfigure(0, weight=1)
        
        # Title and mandatory fields section
        mandatory_frame = ctk.CTkFrame(container)
        mandatory_frame.pack(fill="x", pady=(0, 10))
        mandatory_frame.grid_columnconfigure(1, weight=1)  # Make entry fields expand
        
        row = 0
        
        # Title selection
        ctk.CTkLabel(
            mandatory_frame,
            text="Title:",
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12)
        ).grid(row=row, column=0, sticky="w", padx=10, pady=10)
        
        self.title_var = tk.StringVar()
        title_cb = ctk.CTkComboBox(
            mandatory_frame,
            values=["Mr.", "Mrs.", "Ms.", "Dr.", "Prof."],
            variable=self.title_var,
            width=120,
            height=35,
            font=("Helvetica", 12)
        )
        title_cb.grid(row=row, column=1, sticky="w", padx=10, pady=10)
        row += 1
        
        # Name Section
        name_frame = ctk.CTkFrame(mandatory_frame)
        name_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        name_frame.grid_columnconfigure((1, 3, 5), weight=1)
        
        # First Name (Given Name)
        ctk.CTkLabel(
            name_frame,
            text="Given Name:*",
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12)
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.first_name_var = tk.StringVar()
        self.first_name_var.trace_add("write", lambda *args: self.validate_name(self.first_name_var))
        self.first_name_entry = self.create_entry(name_frame)
        self.first_name_entry.configure(textvariable=self.first_name_var)
        self.first_name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Middle Name (Additional Name)
        ctk.CTkLabel(
            name_frame,
            text="Middle Name:",
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12)
        ).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        self.middle_name_var = tk.StringVar()
        self.middle_name_var.trace_add("write", lambda *args: self.validate_name(self.middle_name_var))
        self.middle_name_entry = self.create_entry(name_frame)
        self.middle_name_entry.configure(textvariable=self.middle_name_var)
        self.middle_name_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        
        # Last Name (Family Name)
        ctk.CTkLabel(
            name_frame,
            text="Family Name:*",
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12)
        ).grid(row=0, column=4, sticky="w", padx=5, pady=5)
        
        self.last_name_var = tk.StringVar()
        self.last_name_var.trace_add("write", lambda *args: self.validate_name(self.last_name_var))
        self.last_name_entry = self.create_entry(name_frame)
        self.last_name_entry.configure(textvariable=self.last_name_var)
        self.last_name_entry.grid(row=0, column=5, sticky="ew", padx=5, pady=5)
        
        # Nickname
        ctk.CTkLabel(
            name_frame,
            text="Nickname:",
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12)
        ).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.nickname_var = tk.StringVar()
        self.nickname_entry = self.create_entry(name_frame)
        self.nickname_entry.configure(textvariable=self.nickname_var)
        self.nickname_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        row += 1
        
        # Organization Section
        org_frame = ctk.CTkFrame(mandatory_frame)
        org_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        org_frame.grid_columnconfigure((1, 3), weight=1)
        
        # Organization
        ctk.CTkLabel(
            org_frame,
            text="Organization:",
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12)
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.organization_var = tk.StringVar()
        self.organization_entry = self.create_entry(org_frame)
        self.organization_entry.configure(textvariable=self.organization_var)
        self.organization_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Job Title
        ctk.CTkLabel(
            org_frame,
            text="Job Title:",
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12)
        ).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        self.job_title_var = tk.StringVar()
        self.job_title_entry = self.create_entry(org_frame)
        self.job_title_entry.configure(textvariable=self.job_title_var)
        self.job_title_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        row += 1
        
        # Gender and Age
        gender_age_frame = ctk.CTkFrame(mandatory_frame)
        gender_age_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        gender_age_frame.grid_columnconfigure(3, weight=1)
        
        # Gender
        ctk.CTkLabel(
            gender_age_frame,
            text="Gender:*",
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12)
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.gender_var = tk.StringVar(value="Male")
        for i, gender in enumerate(["Male", "Female", "Other"]):
            ctk.CTkRadioButton(
                gender_age_frame,
                text=gender,
                variable=self.gender_var,
                value=gender,
                font=("Helvetica", 12)
            ).grid(row=0, column=i+1, padx=10, pady=5)
        
        # Age
        ctk.CTkLabel(
            gender_age_frame,
            text="Age:*",
            text_color=TEXT_PRIMARY,
            font=("Helvetica", 12)
        ).grid(row=0, column=4, sticky="w", padx=5, pady=5)
        
        self.age_var = tk.StringVar()
        self.age_var.trace_add("write", self.validate_age)
        self.age_entry = self.create_entry(gender_age_frame, placeholder="Enter age")
        self.age_entry.configure(textvariable=self.age_var, width=120)
        self.age_entry.grid(row=0, column=5, sticky="w", padx=5, pady=5)
        row += 1
        
        # Contact Information Section
        contact_frame = ctk.CTkFrame(container)
        contact_frame.pack(fill="x", pady=5)
        contact_frame.grid_columnconfigure(1, weight=1)
        
        # Contact header
        ctk.CTkLabel(
            contact_frame,
            text="Contact Information",
            font=("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(5, 10))
        
        # Phone Numbers
        phones_frame = ctk.CTkFrame(contact_frame)
        phones_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        phones_frame.grid_columnconfigure((1, 3, 5), weight=1)
        
        # Primary Phone
        ctk.CTkLabel(phones_frame, text="Primary Phone:*", text_color=TEXT_PRIMARY).grid(row=0, column=0, sticky="w", padx=5)
        self.phone_var = tk.StringVar()
        self.phone_var.trace_add("write", self.validate_phone)
        self.phone_entry = self.create_entry(phones_frame)
        self.phone_entry.configure(textvariable=self.phone_var)
        self.phone_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        # Secondary Phone
        ctk.CTkLabel(phones_frame, text="Secondary Phone:", text_color=TEXT_PRIMARY).grid(row=0, column=2, sticky="w", padx=5)
        self.secondary_phone_var = tk.StringVar()
        self.secondary_phone_var.trace_add("write", self.validate_phone)
        self.secondary_phone_entry = self.create_entry(phones_frame)
        self.secondary_phone_entry.configure(textvariable=self.secondary_phone_var)
        self.secondary_phone_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=2)
        
        # Work Phone
        ctk.CTkLabel(phones_frame, text="Work Phone:", text_color=TEXT_PRIMARY).grid(row=0, column=4, sticky="w", padx=5)
        self.work_phone_var = tk.StringVar()
        self.work_phone_var.trace_add("write", self.validate_phone)
        self.work_phone_entry = self.create_entry(phones_frame)
        self.work_phone_entry.configure(textvariable=self.work_phone_var)
        self.work_phone_entry.grid(row=0, column=5, sticky="ew", padx=5, pady=2)
        
        # Email Addresses
        emails_frame = ctk.CTkFrame(contact_frame)
        emails_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        emails_frame.grid_columnconfigure((1, 3, 5), weight=1)
        
        # Primary Email
        ctk.CTkLabel(emails_frame, text="Primary Email:", text_color=TEXT_PRIMARY).grid(row=0, column=0, sticky="w", padx=5)
        self.email_var = tk.StringVar()
        self.email_var.trace_add("write", self.validate_email)
        self.email_entry = self.create_entry(emails_frame)
        self.email_entry.configure(textvariable=self.email_var)
        self.email_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        # Secondary Email
        ctk.CTkLabel(emails_frame, text="Secondary Email:", text_color=TEXT_PRIMARY).grid(row=0, column=2, sticky="w", padx=5)
        self.secondary_email_var = tk.StringVar()
        self.secondary_email_var.trace_add("write", self.validate_email)
        self.secondary_email_entry = self.create_entry(emails_frame)
        self.secondary_email_entry.configure(textvariable=self.secondary_email_var)
        self.secondary_email_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=2)
        
        # Work Email
        ctk.CTkLabel(emails_frame, text="Work Email:", text_color=TEXT_PRIMARY).grid(row=0, column=4, sticky="w", padx=5)
        self.work_email_var = tk.StringVar()
        self.work_email_var.trace_add("write", self.validate_email)
        self.work_email_entry = self.create_entry(emails_frame)
        self.work_email_entry.configure(textvariable=self.work_email_var)
        self.work_email_entry.grid(row=0, column=5, sticky="ew", padx=5, pady=2)
        
        # Website
        website_frame = ctk.CTkFrame(contact_frame)
        website_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        website_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(website_frame, text="Website:", text_color=TEXT_PRIMARY).grid(row=0, column=0, sticky="w", padx=5)
        self.website_var = tk.StringVar()
        self.website_entry = self.create_entry(website_frame)
        self.website_entry.configure(textvariable=self.website_var)
        self.website_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        # Primary Address Section
        address_frame = ctk.CTkFrame(container)
        address_frame.pack(fill="x", pady=5)
        address_frame.grid_columnconfigure(1, weight=1)
        
        # Address header
        ctk.CTkLabel(
            address_frame,
            text="Primary Address",
            font=("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(5, 10))
        
        # Street
        ctk.CTkLabel(address_frame, text="Street:", text_color=TEXT_PRIMARY).grid(row=1, column=0, sticky="w", padx=5)
        self.street_var = tk.StringVar()
        self.street_entry = self.create_entry(address_frame)
        self.street_entry.configure(textvariable=self.street_var)
        self.street_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        # City and State
        city_state_frame = ctk.CTkFrame(address_frame)
        city_state_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        city_state_frame.grid_columnconfigure((1, 3), weight=1)
        
        # City
        ctk.CTkLabel(city_state_frame, text="City:", text_color=TEXT_PRIMARY).grid(row=0, column=0, sticky="w", padx=5)
        self.city_var = tk.StringVar()
        self.city_entry = self.create_entry(city_state_frame)
        self.city_entry.configure(textvariable=self.city_var)
        self.city_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        # State
        ctk.CTkLabel(city_state_frame, text="State:", text_color=TEXT_PRIMARY).grid(row=0, column=2, sticky="w", padx=5)
        self.state_var = tk.StringVar()
        self.state_entry = self.create_entry(city_state_frame)
        self.state_entry.configure(textvariable=self.state_var)
        self.state_entry.grid(row=0, column=3, sticky="ew", padx=5)
        
        # ZIP
        ctk.CTkLabel(address_frame, text="ZIP:", text_color=TEXT_PRIMARY).grid(row=3, column=0, sticky="w", padx=5)
        self.zip_var = tk.StringVar()
        self.zip_entry = self.create_entry(address_frame)
        self.zip_entry.configure(textvariable=self.zip_var)
        self.zip_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        
        # Secondary Address Section
        secondary_address_frame = ctk.CTkFrame(container)
        secondary_address_frame.pack(fill="x", pady=5)
        secondary_address_frame.grid_columnconfigure(1, weight=1)
        
        # Secondary Address header
        ctk.CTkLabel(
            secondary_address_frame,
            text="Secondary Address",
            font=("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(5, 10))
        
        # Secondary Street
        ctk.CTkLabel(secondary_address_frame, text="Street:", text_color=TEXT_PRIMARY).grid(row=1, column=0, sticky="w", padx=5)
        self.secondary_street_var = tk.StringVar()
        self.secondary_street_entry = self.create_entry(secondary_address_frame)
        self.secondary_street_entry.configure(textvariable=self.secondary_street_var)
        self.secondary_street_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        # Secondary City and State
        secondary_city_state_frame = ctk.CTkFrame(secondary_address_frame)
        secondary_city_state_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        secondary_city_state_frame.grid_columnconfigure((1, 3), weight=1)
        
        # Secondary City
        ctk.CTkLabel(secondary_city_state_frame, text="City:", text_color=TEXT_PRIMARY).grid(row=0, column=0, sticky="w", padx=5)
        self.secondary_city_var = tk.StringVar()
        self.secondary_city_entry = self.create_entry(secondary_city_state_frame)
        self.secondary_city_entry.configure(textvariable=self.secondary_city_var)
        self.secondary_city_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        # Secondary State
        ctk.CTkLabel(secondary_city_state_frame, text="State:", text_color=TEXT_PRIMARY).grid(row=0, column=2, sticky="w", padx=5)
        self.secondary_state_var = tk.StringVar()
        self.secondary_state_entry = self.create_entry(secondary_city_state_frame)
        self.secondary_state_entry.configure(textvariable=self.secondary_state_var)
        self.secondary_state_entry.grid(row=0, column=3, sticky="ew", padx=5)
        
        # Secondary ZIP
        ctk.CTkLabel(secondary_address_frame, text="ZIP:", text_color=TEXT_PRIMARY).grid(row=3, column=0, sticky="w", padx=5)
        self.secondary_zip_var = tk.StringVar()
        self.secondary_zip_entry = self.create_entry(secondary_address_frame)
        self.secondary_zip_entry.configure(textvariable=self.secondary_zip_var)
        self.secondary_zip_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        
        # Work Address Section
        work_address_frame = ctk.CTkFrame(container)
        work_address_frame.pack(fill="x", pady=5)
        work_address_frame.grid_columnconfigure(1, weight=1)
        
        # Work Address header
        ctk.CTkLabel(
            work_address_frame,
            text="Work Address",
            font=("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(5, 10))
        
        # Work Street
        ctk.CTkLabel(work_address_frame, text="Street:", text_color=TEXT_PRIMARY).grid(row=1, column=0, sticky="w", padx=5)
        self.work_street_var = tk.StringVar()
        self.work_street_entry = self.create_entry(work_address_frame)
        self.work_street_entry.configure(textvariable=self.work_street_var)
        self.work_street_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        # Work City and State
        work_city_state_frame = ctk.CTkFrame(work_address_frame)
        work_city_state_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        work_city_state_frame.grid_columnconfigure((1, 3), weight=1)
        
        # Work City
        ctk.CTkLabel(work_city_state_frame, text="City:", text_color=TEXT_PRIMARY).grid(row=0, column=0, sticky="w", padx=5)
        self.work_city_var = tk.StringVar()
        self.work_city_entry = self.create_entry(work_city_state_frame)
        self.work_city_entry.configure(textvariable=self.work_city_var)
        self.work_city_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        # Work State
        ctk.CTkLabel(work_city_state_frame, text="State:", text_color=TEXT_PRIMARY).grid(row=0, column=2, sticky="w", padx=5)
        self.work_state_var = tk.StringVar()
        self.work_state_entry = self.create_entry(work_city_state_frame)
        self.work_state_entry.configure(textvariable=self.work_state_var)
        self.work_state_entry.grid(row=0, column=3, sticky="ew", padx=5)
        
        # Work ZIP
        ctk.CTkLabel(work_address_frame, text="ZIP:", text_color=TEXT_PRIMARY).grid(row=3, column=0, sticky="w", padx=5)
        self.work_zip_var = tk.StringVar()
        self.work_zip_entry = self.create_entry(work_address_frame)
        self.work_zip_entry.configure(textvariable=self.work_zip_var)
        self.work_zip_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        
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
        self.emergency_name_var = tk.StringVar()
        self.emergency_name_entry = self.create_entry(emergency_frame)
        self.emergency_name_entry.configure(textvariable=self.emergency_name_var)
        self.emergency_name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        # Emergency Phone
        ctk.CTkLabel(emergency_frame, text="Phone:", text_color=TEXT_PRIMARY).grid(row=2, column=0, sticky="w", padx=5)
        self.emergency_phone_var = tk.StringVar()
        self.emergency_phone_var.trace_add("write", self.validate_emergency_phone)
        self.emergency_phone_entry = self.create_entry(emergency_frame)
        self.emergency_phone_entry.configure(textvariable=self.emergency_phone_var)
        self.emergency_phone_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        
        # Relationship
        ctk.CTkLabel(emergency_frame, text="Relationship:", text_color=TEXT_PRIMARY).grid(row=3, column=0, sticky="w", padx=5)
        self.emergency_relation_var = tk.StringVar()
        self.emergency_relation_entry = self.create_entry(emergency_frame)
        self.emergency_relation_entry.configure(textvariable=self.emergency_relation_var)
        self.emergency_relation_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        
        # Notes Section
        notes_frame = ctk.CTkFrame(container)
        notes_frame.pack(fill="x", pady=5)
        notes_frame.grid_columnconfigure(0, weight=1)
        
        # Notes header
        ctk.CTkLabel(
            notes_frame,
            text="Additional Notes",
            font=("Helvetica", 12, "bold"),
            text_color=TEXT_PRIMARY
        ).grid(row=0, column=0, sticky="w", padx=5, pady=(5, 2))
        
        self.notes_text = self.create_textbox(notes_frame, height=100)
        self.notes_text.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
    
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
        self.session_tree.tag_configure('info', foreground=TEXT_SECONDARY)
        self.session_tree.tag_configure('error', foreground=ERROR_RED)
    
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
            height=35,  # Increased height for better visibility
            font=("Helvetica", 12)  # Consistent font size
        )
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
        try:
            # Collect all field values
            patient_data = {
                'title': self.title_var.get(),
                'first_name': self.first_name_var.get().strip(),
                'middle_name': self.middle_name_var.get().strip(),
                'last_name': self.last_name_var.get().strip(),
                'nickname': self.nickname_var.get().strip(),
                'organization': self.organization_var.get().strip(),
                'job_title': self.job_title_var.get().strip(),
                'gender': self.gender_var.get(),
                'age': int(self.age_var.get().strip()),
                'phone': self.phone_var.get().strip(),
                'secondary_phone': self.secondary_phone_var.get().strip(),
                'work_phone': self.work_phone_var.get().strip(),
                'email': self.email_var.get().strip(),
                'secondary_email': self.secondary_email_var.get().strip(),
                'work_email': self.work_email_var.get().strip(),
                'website': self.website_var.get().strip(),
                
                # Primary Address
                'address_street': self.street_var.get().strip(),
                'address_city': self.city_var.get().strip(),
                'address_state': self.state_var.get().strip(),
                'address_zip': self.zip_var.get().strip(),
                
                # Secondary Address
                'secondary_address_street': self.secondary_street_var.get().strip(),
                'secondary_address_city': self.secondary_city_var.get().strip(),
                'secondary_address_state': self.secondary_state_var.get().strip(),
                'secondary_address_zip': self.secondary_zip_var.get().strip(),
                
                # Work Address
                'work_address_street': self.work_street_var.get().strip(),
                'work_address_city': self.work_city_var.get().strip(),
                'work_address_state': self.work_state_var.get().strip(),
                'work_address_zip': self.work_zip_var.get().strip(),
                
                # Emergency Contact
                'emergency_contact_name': self.emergency_name_var.get().strip(),
                'emergency_contact_phone': self.emergency_phone_var.get().strip(),
                'emergency_contact_relation': self.emergency_relation_var.get().strip(),
                
                # Medical Information
                'reference_source': self.reference_entry.get().strip(),
                'medical_conditions': self.conditions_text.get("1.0", "end-1c"),
                'past_surgeries': self.surgeries_text.get("1.0", "end-1c"),
                'current_medications': self.medications_text.get("1.0", "end-1c"),
                'allergies': self.allergies_text.get("1.0", "end-1c"),
                'chiropractic_history': self.history_text.get("1.0", "end-1c"),
                
                # Insurance Information
                'insurance_provider': self.insurance_provider_entry.get().strip(),
                'insurance_policy_number': self.policy_number_entry.get().strip(),
                'insurance_coverage_details': self.coverage_text.get("1.0", "end-1c"),
                
                # Additional Notes
                'notes': self.notes_text.get("1.0", "end-1c")
            }
            
            # Remove empty values
            patient_data = {k: v for k, v in patient_data.items() if v}
            
            selected = self.patient_tree.selection()
            
            # Use transaction context manager
            with self.db.transaction() as db:
                if selected:
                    # Update existing patient
                    patient_id = int(self.patient_tree.item(selected[0])["tags"][0])
                    db.update_patient(patient_id, patient_data)
                    
                    # Refresh session history for the updated patient
                    patient = db.get_patient(patient_id)
                    self.refresh_session_history(patient.get('session_history', []))
                    
                    messagebox.showinfo("Success", "Patient updated successfully")
                else:
                    # Add new patient
                    new_patient_id = db.add_patient(patient_data)
                    
                    # Refresh session history for the new patient
                    patient = db.get_patient(new_patient_id)
                    self.refresh_session_history(patient.get('session_history', []))
                    
                    messagebox.showinfo("Success", "Patient added successfully")
            
            # Refresh UI components
            self.refresh_patient_list()  # Refresh patient list
            self.refresh_callback()      # Refresh dashboard appointments
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save patient: {str(e)}")
            print(f"Error saving patient: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def validate_mandatory_fields(self):
        """Validate all mandatory fields"""
        if not self.first_name_var.get().strip():
            messagebox.showerror("Error", "First Name is required")
            return False
        
        if not self.last_name_var.get().strip():
            messagebox.showerror("Error", "Last Name is required")
            return False
        
        if not self.phone_var.get().strip():
            messagebox.showerror("Error", "Phone number is required")
            return False
        
        if not self.age_var.get().strip():
            messagebox.showerror("Error", "Age is required")
            return False
        
        return True
    
    def refresh_patient_list(self, search_term=""):
        """Refresh the patient list"""
        # Clear existing items
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)
        
        # Get patients matching search term
        patients = self.db.search_patients(search_term)
        
        # Add patients to tree
        for patient in patients:
            self.patient_tree.insert(
                "",
                "end",
                values=(
                    patient['id'],
                    f"{patient['first_name']} {patient['last_name']}",
                    patient['age'],
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
            
            # Name fields
            self.first_name_var.set(patient['first_name'])
            self.middle_name_var.set(patient.get('middle_name', ''))
            self.last_name_var.set(patient['last_name'])
            self.nickname_var.set(patient.get('nickname', ''))
            
            # Organization fields
            self.organization_var.set(patient.get('organization', ''))
            self.job_title_var.set(patient.get('job_title', ''))
            
            # Gender and Age
            self.gender_var.set(patient.get('gender', 'Male'))
            self.age_var.set(str(patient['age']))
            
            # Contact Information
            # Phone numbers
            self.phone_var.set(patient['phone'])
            self.secondary_phone_var.set(patient.get('secondary_phone', ''))
            self.work_phone_var.set(patient.get('work_phone', ''))
            
            # Email addresses
            self.email_var.set(patient.get('email', ''))
            self.secondary_email_var.set(patient.get('secondary_email', ''))
            self.work_email_var.set(patient.get('work_email', ''))
            
            # Website
            self.website_var.set(patient.get('website', ''))
            
            # Primary Address
            self.street_var.set(patient.get('address_street', ''))
            self.city_var.set(patient.get('address_city', ''))
            self.state_var.set(patient.get('address_state', ''))
            self.zip_var.set(patient.get('address_zip', ''))
            
            # Secondary Address
            self.secondary_street_var.set(patient.get('secondary_address_street', ''))
            self.secondary_city_var.set(patient.get('secondary_address_city', ''))
            self.secondary_state_var.set(patient.get('secondary_address_state', ''))
            self.secondary_zip_var.set(patient.get('secondary_address_zip', ''))
            
            # Work Address
            self.work_street_var.set(patient.get('work_address_street', ''))
            self.work_city_var.set(patient.get('work_address_city', ''))
            self.work_state_var.set(patient.get('work_address_state', ''))
            self.work_zip_var.set(patient.get('work_address_zip', ''))
            
            # Emergency Contact
            self.emergency_name_var.set(patient.get('emergency_contact_name', ''))
            self.emergency_phone_var.set(patient.get('emergency_contact_phone', ''))
            self.emergency_relation_var.set(patient.get('emergency_contact_relation', ''))
            
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
            
            # Additional Notes
            self.notes_text.delete("1.0", tk.END)
            if patient.get('notes'):
                self.notes_text.insert("1.0", patient['notes'])
            
            # Update session history
            self.refresh_session_history(patient.get('session_history', []))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load patient details: {str(e)}")
            print(f"Error loading patient details: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def refresh_session_history(self, sessions):
        """Refresh the session history tree with both appointments and session history"""
        try:
            # Clear existing items
            for item in self.session_tree.get_children():
                self.session_tree.delete(item)
            
            # Get patient ID from selection
            selected = self.patient_tree.selection()
            if not selected:
                return
                
            self.patient_id = int(self.patient_tree.item(selected[0])["tags"][0])
            if not self.patient_id:
                return

            # Get future appointments
            future_appointments = self.db.get_future_appointments(self.patient_id)
            
            # Get all appointment tables
            self.db.connect()
            try:
                tables = self.db.cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'appointments_%'"
                ).fetchall()
                
                # Get all past appointments
                all_appointments = []
                current_date = datetime.now().strftime("%Y-%m-%d")
                
                # Check each appointments table for past appointments
                for table in tables:
                    table_name = table[0]
                    appointments = self.db.cursor.execute(
                        f"""
                        SELECT appointment_date, appointment_time, status, notes
                        FROM {table_name}
                        WHERE patient_id = ?
                        ORDER BY appointment_date DESC, appointment_time DESC
                        """,
                        (self.patient_id,)
                    ).fetchall()
                    all_appointments.extend(appointments)
                
                # Sort all entries by date
                all_entries = []
                
                # Add all appointments (both past and future)
                for appt in all_appointments:
                    # Find next appointment
                    next_appt = ""
                    if future_appointments:
                        next_date = future_appointments[0][0]
                        next_time = format_time_12hr(future_appointments[0][1])
                        next_appt = f"{next_date} {next_time}"
                    
                    # Format current appointment time
                    current_time = format_time_12hr(appt[1])
                    
                    entry = {
                        'date': f"{appt[0]} {current_time}",
                        'type': 'Appointment',
                        'status': appt[2] or 'pending',
                        'notes': appt[3] or '',
                        'next_appointment': next_appt if appt[0] < current_date else ''
                    }
                    all_entries.append(entry)
                
                # Add session history entries
                for session in sessions:
                    # Find next appointment
                    next_appt = ""
                    if future_appointments:
                        next_date = future_appointments[0][0]
                        next_time = format_time_12hr(future_appointments[0][1])
                        next_appt = f"{next_date} {next_time}"
                    
                    entry = {
                        'date': session['session_date'],
                        'type': 'Session',
                        'status': 'done',
                        'notes': session.get('treatment_notes', '') or '',
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
                    
                # If no entries found, add a placeholder message
                if not all_entries:
                    self.session_tree.insert(
                        "",
                        "end",
                        values=("No session history available", "-", "-", "-", "-"),
                        tags=('info',)
                    )
                    
            finally:
                self.db.close()
            
        except Exception as e:
            print(f"Error refreshing session history: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Show error in tree
            self.session_tree.insert(
                "",
                "end",
                values=("Error loading session history", "-", "-", str(e), "-"),
                tags=('error',)
            )
    
    def add_patient(self):
        """Clear fields for new patient"""
        self.patient_tree.selection_remove(self.patient_tree.selection())
        
        # Clear Name fields
        self.title_var.set("")
        self.first_name_var.set("")
        self.middle_name_var.set("")
        self.last_name_var.set("")
        self.nickname_var.set("")
        
        # Clear Organization fields
        self.organization_var.set("")
        self.job_title_var.set("")
        
        # Clear Gender and Age
        self.gender_var.set("Male")
        self.age_var.set("")
        
        # Clear Contact Information
        # Phone numbers
        self.phone_var.set("")
        self.secondary_phone_var.set("")
        self.work_phone_var.set("")
        
        # Email addresses
        self.email_var.set("")
        self.secondary_email_var.set("")
        self.work_email_var.set("")
        
        # Website
        self.website_var.set("")
        
        # Clear Primary Address
        self.street_var.set("")
        self.city_var.set("")
        self.state_var.set("")
        self.zip_var.set("")
        
        # Clear Secondary Address
        self.secondary_street_var.set("")
        self.secondary_city_var.set("")
        self.secondary_state_var.set("")
        self.secondary_zip_var.set("")
        
        # Clear Work Address
        self.work_street_var.set("")
        self.work_city_var.set("")
        self.work_state_var.set("")
        self.work_zip_var.set("")
        
        # Clear Emergency Contact
        self.emergency_name_var.set("")
        self.emergency_phone_var.set("")
        self.emergency_relation_var.set("")
        
        # Clear Reference
        self.reference_entry.delete(0, "end")
        
        # Clear Medical Information
        self.conditions_text.delete("1.0", "end")
        self.surgeries_text.delete("1.0", "end")
        self.medications_text.delete("1.0", "end")
        self.allergies_text.delete("1.0", "end")
        self.history_text.delete("1.0", "end")
        
        # Clear Insurance Information
        self.insurance_provider_entry.delete(0, "end")
        self.policy_number_entry.delete(0, "end")
        self.coverage_text.delete("1.0", "end")
        
        # Clear Additional Notes
        self.notes_text.delete("1.0", "end")
        
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
    
    def validate_name(self, var):
        """Validate name input - only letters, spaces, and hyphens allowed"""
        current = var.get()
        # Remove any non-allowed characters immediately
        valid = ''.join(c for c in current if c.isalpha() or c in [' ', '-'])
        if current != valid:
            var.set(valid)
            return False
        return True

    def validate_age(self, *args):
        """Validate age input - only numbers allowed and must be between 1-150"""
        current = self.age_var.get()
        # Remove any non-numeric characters immediately
        valid = ''.join(c for c in current if c.isdigit())
        
        # Update the entry if non-numeric characters were removed
        if current != valid:
            self.age_var.set(valid)
            self.age_entry.configure(border_color=ERROR_RED)
            return False
            
        # Check age range if there's a value
        if valid:
            try:
                age = int(valid)
                if age < 1 or age > 150:
                    self.age_entry.configure(border_color=ERROR_RED)
                    return False
                else:
                    self.age_entry.configure(border_color=PRIMARY_BLUE)
                    return True
            except ValueError:
                self.age_entry.configure(border_color=ERROR_RED)
                return False
        else:
            self.age_entry.configure(border_color=PRIMARY_BLUE)
            return True

    def validate_phone(self, *args):
        """Validate phone input - allow + for country code and numbers, length 10-15 digits"""
        current = self.phone_var.get()
        
        # Allow + only at the start
        if current.startswith('+'):
            # Remove any non-numeric characters after the +
            valid = '+' + ''.join(c for c in current[1:] if c.isdigit())
        else:
            # Remove any non-numeric characters
            valid = ''.join(c for c in current if c.isdigit())
        
        # Update the entry if invalid characters were removed
        if current != valid:
            self.phone_var.set(valid)
            self.phone_entry.configure(border_color=ERROR_RED)
            return False
            
        # Check phone number length (10-15 digits, not counting the + if present)
        digits = valid.replace('+', '')
        if len(digits) > 0:
            if len(digits) < 10 or len(digits) > 15:
                self.phone_entry.configure(border_color=ERROR_RED)
                return False
            else:
                self.phone_entry.configure(border_color=PRIMARY_BLUE)
                return True
        else:
            self.phone_entry.configure(border_color=PRIMARY_BLUE)
            return True

    def validate_email(self, *args):
        """Validate email input - only allow valid email characters"""
        current = self.email_var.get()
        valid = ''.join(c for c in current if c.isalnum() or c in ['@', '.', '_', '-'])
        if current != valid:
            self.email_var.set(valid)

    def validate_street(self, *args):
        """Validate street input - allow alphanumeric, spaces, hyphens, commas, periods, #, and /"""
        current = self.street_var.get()
        valid = ''.join(c for c in current if c.isalnum() or c in [' ', '-', ',', '.', '#', '/'])
        if current != valid:
            self.street_var.set(valid)

    def validate_zip(self, *args):
        """Validate ZIP input - only numbers allowed"""
        current = self.zip_var.get()
        # Remove any non-numeric characters
        valid = ''.join(c for c in current if c.isdigit())
        
        # Update the entry if non-numeric characters were removed
        if current != valid:
            self.zip_var.set(valid)
            self.zip_entry.configure(border_color=ERROR_RED)
        else:
            # Check ZIP code length (5 or 9 digits for US format)
            if len(valid) > 0 and len(valid) not in [5, 9]:
                self.zip_entry.configure(border_color=ERROR_RED)
            else:
                self.zip_entry.configure(border_color=PRIMARY_BLUE)

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
        name = self.first_name_var.get().strip()
        age = self.age_var.get().strip()
        phone = self.phone_var.get().strip()
        
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

    def validate_emergency_phone(self, *args):
        """Validate emergency contact phone input - allow + for country code and numbers"""
        current = self.emergency_phone_var.get()
        
        # Allow + only at the start
        if current.startswith('+'):
            # Remove any non-numeric characters after the +
            valid = '+' + ''.join(c for c in current[1:] if c.isdigit())
        else:
            # Remove any non-numeric characters
            valid = ''.join(c for c in current if c.isdigit())
        
        # Update the entry if invalid characters were removed
        if current != valid:
            self.emergency_phone_var.set(valid)
            self.emergency_phone_entry.configure(border_color=ERROR_RED)
        else:
            # Check phone number length (10-15 digits, not counting the + if present)
            digits = valid.replace('+', '')
            if len(digits) > 0 and (len(digits) < 10 or len(digits) > 15):
                self.emergency_phone_entry.configure(border_color=ERROR_RED)
            else:
                self.emergency_phone_entry.configure(border_color=PRIMARY_BLUE) 