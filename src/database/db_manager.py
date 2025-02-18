import sqlite3
from datetime import datetime
import calendar
from pathlib import Path
from .schema import (
    CREATE_PATIENTS_TABLE,
    CREATE_APPOINTMENTS_TABLE_TEMPLATE,
    CREATE_SESSION_HISTORY_TABLE,
    CREATE_PATIENT_NAME_INDEX,
    CREATE_PATIENT_PHONE_INDEX,
    CREATE_PATIENT_DOB_INDEX,
    CREATE_SESSION_DATE_INDEX,
    CREATE_SESSION_PATIENT_INDEX,
    CREATE_APPOINTMENT_DATE_INDEX,
    CREATE_PATIENT_HISTORY_TABLE
)

class DatabaseManager:
    def __init__(self, db_path="chiropractic.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.initialize_database()

    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def initialize_database(self):
        """Initialize database with required tables"""
        self.connect()
        try:
            # Create core tables
            self.cursor.execute(CREATE_PATIENTS_TABLE)
            self.cursor.execute(CREATE_PATIENT_HISTORY_TABLE)
            self.cursor.execute(CREATE_SESSION_HISTORY_TABLE)
            
            # Create indices
            self.cursor.execute(CREATE_PATIENT_NAME_INDEX)
            self.cursor.execute(CREATE_PATIENT_PHONE_INDEX)
            self.cursor.execute(CREATE_PATIENT_DOB_INDEX)
            self.cursor.execute(CREATE_SESSION_DATE_INDEX)
            self.cursor.execute(CREATE_SESSION_PATIENT_INDEX)
            
            # Create current month's appointment table
            self._create_month_appointment_table(datetime.now())
            
            self.conn.commit()
        finally:
            self.close()

    def _create_month_appointment_table(self, date):
        """Create appointment table for specific month if it doesn't exist"""
        month_year = date.strftime("%Y_%m")
        
        # Create the appointments table for this month
        self.cursor.execute(
            CREATE_APPOINTMENTS_TABLE_TEMPLATE.format(month_year=month_year)
        )
        
        # Create the index
        self.cursor.execute(
            CREATE_APPOINTMENT_DATE_INDEX.format(month_year=month_year)
        )
        
        self.conn.commit()

    def ensure_month_table_exists(self, date):
        """Ensure the appointments table exists for the given date"""
        month_year = date.strftime("%Y_%m")
        
        # Check if table exists
        self.cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?
            """,
            (f"appointments_{month_year}",)
        )
        
        if not self.cursor.fetchone():
            # Create table if it doesn't exist
            self._create_month_appointment_table(date)

    # Patient Management
    def add_patient(self, patient_data):
        """Add a new patient to the database"""
        self.connect()
        try:
            # Ensure age is an integer
            if 'age' in patient_data:
                patient_data['age'] = int(patient_data['age'])
            
            # Prepare the query dynamically based on provided fields
            fields = []
            values = []
            placeholders = []
            
            for field, value in patient_data.items():
                if value is not None:  # Only include non-None values
                    fields.append(field)
                    values.append(value)
                    placeholders.append('?')
            
            query = f"""
            INSERT INTO patients ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
            """
            
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.lastrowid
        finally:
            self.close()

    def get_patient(self, patient_id):
        """Retrieve patient details by ID"""
        self.connect()
        try:
            # Get patient details
            query = "SELECT * FROM patients WHERE id = ?"
            self.cursor.execute(query, (patient_id,))
            patient = self.cursor.fetchone()
            
            if not patient:
                raise ValueError(f"No patient found with ID {patient_id}")
            
            patient_data = dict(patient)
            
            # Get session history
            query = """
            SELECT * FROM session_history 
            WHERE patient_id = ?
            ORDER BY session_date DESC
            """
            self.cursor.execute(query, (patient_id,))
            patient_data['session_history'] = [dict(row) for row in self.cursor.fetchall()]
            
            return patient_data
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error retrieving patient data: {str(e)}")
        finally:
            self.close()

    def update_patient(self, patient_id, patient_data):
        """Update patient details"""
        self.connect()
        try:
            # Ensure age is an integer
            if 'age' in patient_data:
                patient_data['age'] = int(patient_data['age'])
            
            # Prepare the query dynamically based on provided fields
            updates = []
            values = []
            
            for field, value in patient_data.items():
                if value is not None:  # Only include non-None values
                    updates.append(f"{field} = ?")
                    values.append(value)
            
            values.append(patient_id)  # Add patient_id for WHERE clause
            
            query = f"""
            UPDATE patients 
            SET {', '.join(updates)}
            WHERE id = ?
            """
            
            self.cursor.execute(query, values)
            self.conn.commit()
        finally:
            self.close()

    def delete_patient(self, patient_id):
        """Delete patient and their related records"""
        self.connect()
        try:
            # Delete patient history
            self.cursor.execute("DELETE FROM patient_history WHERE patient_id=?", (patient_id,))
            
            # Delete appointments (from all monthly tables)
            tables = self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'appointments_%'"
            ).fetchall()
            
            for table in tables:
                self.cursor.execute(
                    f"DELETE FROM {table[0]} WHERE patient_id=?", (patient_id,)
                )
            
            # Delete patient
            self.cursor.execute("DELETE FROM patients WHERE id=?", (patient_id,))
            self.conn.commit()
        finally:
            self.close()

    # Appointment Management
    def add_appointment(self, patient_id, appointment_date, appointment_time, notes=""):
        """Add a new appointment"""
        self.connect()
        try:
            date_obj = datetime.strptime(appointment_date, "%Y-%m-%d")
            month_year = date_obj.strftime("%Y_%m")
            
            # Ensure table exists for this month
            self.ensure_month_table_exists(date_obj)
            
            query = f"""
            INSERT INTO appointments_{month_year} 
            (patient_id, appointment_date, appointment_time, status, notes)
            VALUES (?, ?, ?, 'pending', ?)
            """
            self.cursor.execute(query, (patient_id, appointment_date, appointment_time, notes))
            self.conn.commit()
            return self.cursor.lastrowid
        finally:
            self.close()

    def create_appointment(self, patient_id, appointment_date, appointment_time, notes=""):
        """Create a new appointment (alias for add_appointment)"""
        return self.add_appointment(patient_id, appointment_date, appointment_time, notes)

    def update_appointment(self, appointment_id, patient_id, appointment_date, appointment_time, notes="", status=None):
        """Update an existing appointment"""
        self.connect()
        try:
            date_obj = datetime.strptime(appointment_date, "%Y-%m-%d")
            month_year = date_obj.strftime("%Y_%m")
            
            # Ensure table exists for this month
            self.ensure_month_table_exists(date_obj)
            
            # Include status in update if provided
            if status:
                query = f"""
                UPDATE appointments_{month_year}
                SET patient_id = ?, appointment_date = ?, appointment_time = ?, notes = ?, status = ?
                WHERE id = ?
                """
                self.cursor.execute(query, (patient_id, appointment_date, appointment_time, notes, status.lower(), appointment_id))
            else:
                query = f"""
                UPDATE appointments_{month_year}
                SET patient_id = ?, appointment_date = ?, appointment_time = ?, notes = ?
                WHERE id = ?
                """
                self.cursor.execute(query, (patient_id, appointment_date, appointment_time, notes, appointment_id))
            
            self.conn.commit()
        finally:
            self.close()

    def cancel_appointment(self, appointment_id, month_year, status, notes=""):
        """Cancel an appointment"""
        self.connect()
        try:
            # Extract year and month from month_year
            date_obj = datetime.strptime(month_year, "%Y-%m-%d")
            table_month_year = date_obj.strftime("%Y_%m")
            
            # Update appointment status
            query = f"""
            UPDATE appointments_{table_month_year}
            SET status = ?, notes = ?
            WHERE id = ?
            """
            self.cursor.execute(query, (status.lower(), notes, appointment_id))
            self.conn.commit()
        finally:
            self.close()

    def get_appointments_by_date(self, date):
        """Get all appointments for a specific date"""
        self.connect()
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            month_year = date_obj.strftime("%Y_%m")
            
            # Ensure table exists for this month
            self.ensure_month_table_exists(date_obj)
            
            query = f"""
            SELECT a.*, p.first_name || ' ' || p.last_name as patient_name
            FROM appointments_{month_year} a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.appointment_date = ?
            ORDER BY a.appointment_time
            """
            self.cursor.execute(query, (date,))
            return [dict(row) for row in self.cursor.fetchall()]
        finally:
            self.close()

    def update_appointment_status(self, appointment_id, month_year, status, notes=""):
        """Update appointment status and add to patient history if completed"""
        self.connect()
        try:
            # Extract year and month from month_year
            date_obj = datetime.strptime(month_year, "%Y-%m-%d")
            table_month_year = date_obj.strftime("%Y_%m")
            
            # Get current appointment details before update
            query = f"""
            SELECT * FROM appointments_{table_month_year}
            WHERE id = ?
            """
            self.cursor.execute(query, (appointment_id,))
            current_appt = self.cursor.fetchone()
            
            if not current_appt:
                return
            
            # Update appointment
            query = f"""
            UPDATE appointments_{table_month_year}
            SET status = ?, notes = ?
            WHERE id = ?
            """
            self.cursor.execute(query, (status.lower(), notes, appointment_id))
            
            # Add to patient history if status is done or cancelled
            if status.lower() in ['done', 'cancelled']:
                history_notes = f"Status: {status.capitalize()}\n{notes}"
                self.cursor.execute(
                    """
                    INSERT INTO patient_history (patient_id, session_date, remarks)
                    VALUES (?, ?, ?)
                    """,
                    (current_appt['patient_id'], current_appt['appointment_date'], history_notes)
                )
            
            self.conn.commit()
        finally:
            self.close()

    def get_patient_history(self, patient_id):
        """Get complete history of a patient's sessions"""
        self.connect()
        try:
            query = """
            SELECT * FROM patient_history
            WHERE patient_id = ?
            ORDER BY session_date DESC
            """
            self.cursor.execute(query, (patient_id,))
            return [dict(row) for row in self.cursor.fetchall()]
        finally:
            self.close()

    def search_patients(self, search_term):
        """Search patients by name, phone, or email"""
        self.connect()
        try:
            query = """
            SELECT * FROM patients
            WHERE first_name LIKE ? 
            OR last_name LIKE ? 
            OR phone LIKE ?
            OR email LIKE ?
            """
            search_pattern = f"%{search_term}%"
            self.cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))
            return [dict(row) for row in self.cursor.fetchall()]
        finally:
            self.close()

    def add_session_history(self, patient_id, session_data):
        """Add a new session history entry"""
        self.connect()
        try:
            fields = []
            values = []
            placeholders = []
            
            # Always include patient_id
            fields.append('patient_id')
            values.append(patient_id)
            placeholders.append('?')
            
            for field, value in session_data.items():
                if value is not None:
                    fields.append(field)
                    values.append(value)
                    placeholders.append('?')
            
            query = f"""
            INSERT INTO session_history ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
            """
            
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.lastrowid
        finally:
            self.close()

    def get_session_history(self, patient_id):
        """Get complete session history for a patient"""
        self.connect()
        try:
            query = """
            SELECT * FROM session_history
            WHERE patient_id = ?
            ORDER BY session_date DESC
            """
            self.cursor.execute(query, (patient_id,))
            return [dict(row) for row in self.cursor.fetchall()]
        finally:
            self.close()

    def get_patient_last_visit(self, patient_id):
        """Get the last visit date for a patient"""
        self.connect()
        try:
            # First check patient_history table
            query = """
            SELECT MAX(session_date) as last_visit
            FROM patient_history
            WHERE patient_id = ?
            """
            self.cursor.execute(query, (patient_id,))
            result = self.cursor.fetchone()
            
            if result and result['last_visit']:
                return datetime.strptime(result['last_visit'], "%Y-%m-%d")
            
            # If no history found, check appointments tables
            tables = self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'appointments_%'"
            ).fetchall()
            
            latest_date = None
            for table in tables:
                query = f"""
                SELECT MAX(appointment_date) as last_visit
                FROM {table[0]}
                WHERE patient_id = ? AND status = 'done'
                """
                self.cursor.execute(query, (patient_id,))
                result = self.cursor.fetchone()
                
                if result and result['last_visit']:
                    date = datetime.strptime(result['last_visit'], "%Y-%m-%d")
                    if not latest_date or date > latest_date:
                        latest_date = date
            
            return latest_date
        finally:
            self.close() 