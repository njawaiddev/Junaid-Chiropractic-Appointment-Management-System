CREATE_PATIENTS_TABLE = """
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Mandatory Fields
    first_name TEXT NOT NULL,  -- Given Name
    last_name TEXT NOT NULL,   -- Family Name
    gender TEXT NOT NULL,
    age INTEGER NOT NULL,
    phone TEXT NOT NULL,       -- Primary Phone
    registration_date DATE DEFAULT CURRENT_DATE,
    
    -- Optional Personal & Contact Details
    title TEXT,
    middle_name TEXT,          -- Additional Name
    nickname TEXT,             -- Nickname
    organization TEXT,         -- Company/Organization
    job_title TEXT,           -- Job Title/Department
    email TEXT,               -- Primary Email
    secondary_phone TEXT,      -- Secondary Phone
    work_phone TEXT,          -- Work Phone
    secondary_email TEXT,      -- Secondary Email
    work_email TEXT,          -- Work Email
    website TEXT,             -- Website
    
    -- Primary Address
    address_street TEXT,
    address_city TEXT,
    address_state TEXT,
    address_zip TEXT,
    
    -- Secondary Address
    secondary_address_street TEXT,
    secondary_address_city TEXT,
    secondary_address_state TEXT,
    secondary_address_zip TEXT,
    
    -- Work Address
    work_address_street TEXT,
    work_address_city TEXT,
    work_address_state TEXT,
    work_address_zip TEXT,
    
    -- Emergency Contact
    emergency_contact_name TEXT,
    emergency_contact_phone TEXT,
    emergency_contact_relation TEXT,
    
    -- Optional Medical & Chiropractic Information
    reference_source TEXT,
    medical_conditions TEXT,
    past_surgeries TEXT,
    current_medications TEXT,
    allergies TEXT,
    chiropractic_history TEXT,
    
    -- Optional Insurance Information
    insurance_provider TEXT,
    insurance_policy_number TEXT,
    insurance_coverage_details TEXT,
    
    -- General Notes
    remarks TEXT,
    notes TEXT,               -- Additional Notes
    
    -- Validation constraints
    CHECK (
        age > 0 AND age < 150 AND
        gender IN ('Male', 'Female', 'Other')
    )
);
"""

CREATE_APPOINTMENTS_TABLE_TEMPLATE = """
CREATE TABLE IF NOT EXISTS appointments_{month_year} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status TEXT DEFAULT 'scheduled',
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients (id)
);
"""

CREATE_PATIENT_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS patient_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    session_date DATE NOT NULL,
    remarks TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients (id)
);
"""

# Index creation for better performance
CREATE_APPOINTMENT_DATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_appointment_date_{month_year}
ON appointments_{month_year} (appointment_date);
"""

CREATE_PATIENT_NAME_INDEX = """
CREATE INDEX IF NOT EXISTS idx_patient_name
ON patients (last_name, first_name);
"""

CREATE_PATIENT_PHONE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_patient_phone
ON patients (phone);
"""

# Create a table for session history
CREATE_SESSION_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS session_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    session_date DATE NOT NULL,
    treatment_notes TEXT,
    follow_up_instructions TEXT,
    next_appointment_date DATE,
    FOREIGN KEY (patient_id) REFERENCES patients (id)
);
"""

CREATE_SESSION_DATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_session_date
ON session_history (session_date);
"""

CREATE_SESSION_PATIENT_INDEX = """
CREATE INDEX IF NOT EXISTS idx_session_patient
ON session_history (patient_id);
""" 