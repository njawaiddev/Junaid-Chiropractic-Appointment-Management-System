CREATE_PATIENTS_TABLE = """
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Mandatory Fields
    first_name TEXT NOT NULL,  -- Given Name
    last_name TEXT DEFAULT '',   -- Family Name (optional)
    gender TEXT NOT NULL DEFAULT 'Other',
    age INTEGER NOT NULL DEFAULT 1,
    phone TEXT NOT NULL,       -- Primary Phone
    registration_date DATE DEFAULT CURRENT_DATE,
    
    -- Optional Personal & Contact Details
    title TEXT DEFAULT '',
    middle_name TEXT DEFAULT '',          -- Additional Name
    nickname TEXT DEFAULT '',             -- Nickname
    organization TEXT DEFAULT '',         -- Company/Organization
    job_title TEXT DEFAULT '',           -- Job Title/Department
    email TEXT DEFAULT '',               -- Primary Email
    secondary_phone TEXT DEFAULT '',      -- Secondary Phone
    work_phone TEXT DEFAULT '',          -- Work Phone
    secondary_email TEXT DEFAULT '',      -- Secondary Email
    work_email TEXT DEFAULT '',          -- Work Email
    website TEXT DEFAULT '',             -- Website
    
    -- Primary Address
    address_street TEXT DEFAULT '',
    address_city TEXT DEFAULT '',
    address_state TEXT DEFAULT '',
    address_zip TEXT DEFAULT '',
    
    -- Secondary Address
    secondary_address_street TEXT DEFAULT '',
    secondary_address_city TEXT DEFAULT '',
    secondary_address_state TEXT DEFAULT '',
    secondary_address_zip TEXT DEFAULT '',
    
    -- Work Address
    work_address_street TEXT DEFAULT '',
    work_address_city TEXT DEFAULT '',
    work_address_state TEXT DEFAULT '',
    work_address_zip TEXT DEFAULT '',
    
    -- Emergency Contact
    emergency_contact_name TEXT DEFAULT '',
    emergency_contact_phone TEXT DEFAULT '',
    emergency_contact_relation TEXT DEFAULT '',
    
    -- Optional Medical & Chiropractic Information
    reference_source TEXT DEFAULT '',
    medical_conditions TEXT DEFAULT '',
    past_surgeries TEXT DEFAULT '',
    current_medications TEXT DEFAULT '',
    allergies TEXT DEFAULT '',
    chiropractic_history TEXT DEFAULT '',
    
    -- Optional Insurance Information
    insurance_provider TEXT DEFAULT '',
    insurance_policy_number TEXT DEFAULT '',
    insurance_coverage_details TEXT DEFAULT '',
    
    -- General Notes
    remarks TEXT DEFAULT '',
    notes TEXT DEFAULT '',               -- Additional Notes
    
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