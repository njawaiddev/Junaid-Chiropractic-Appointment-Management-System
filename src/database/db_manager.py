import sqlite3
from datetime import datetime
import calendar
from pathlib import Path
import os
from .schema import (
    CREATE_PATIENTS_TABLE,
    CREATE_APPOINTMENTS_TABLE_TEMPLATE,
    CREATE_SESSION_HISTORY_TABLE,
    CREATE_PATIENT_NAME_INDEX,
    CREATE_PATIENT_PHONE_INDEX,
    CREATE_SESSION_DATE_INDEX,
    CREATE_SESSION_PATIENT_INDEX,
    CREATE_APPOINTMENT_DATE_INDEX,
    CREATE_PATIENT_HISTORY_TABLE
)

class DatabaseManager:
    def __init__(self, db_path=None):
        """Initialize database manager with proper path handling"""
        if db_path is None:
            # Get the appropriate application data directory
            app_data = self._get_app_data_dir()
            self.db_path = os.path.join(app_data, "chiropractic.db")
        else:
            self.db_path = db_path
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.conn = None
        self.cursor = None
        self.initialize_database()

    def _get_app_data_dir(self):
        """Get the appropriate application data directory based on OS"""
        if os.name == 'nt':  # Windows
            app_data = os.path.join(os.environ['LOCALAPPDATA'], 'ChiropracticManager')
        else:  # macOS and Linux
            app_data = os.path.join(os.path.expanduser('~'), '.chiropracticmanager')
        return app_data

    def connect(self):
        """Connect to the database if not already connected"""
        try:
            if not self.conn:
                self.conn = sqlite3.connect(self.db_path)
                self.conn.row_factory = sqlite3.Row
                self.cursor = self.conn.cursor()
            elif not self.cursor:
                self.cursor = self.conn.cursor()
            return self.conn
        except sqlite3.Error as e:
            print(f"Error connecting to database: {str(e)}")
            raise

    def close(self):
        """Close the database connection"""
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
            self.cursor.execute(CREATE_SESSION_DATE_INDEX)
            self.cursor.execute(CREATE_SESSION_PATIENT_INDEX)
            
            # Create current month's appointment table
            self._create_month_appointment_table(datetime.now())
            
            # Reconnect as _create_month_appointment_table closes the connection
            self.connect()
            self.conn.commit()
        finally:
            self.close()

    def _create_month_appointment_table(self, date):
        """Create appointment table for specific month if it doesn't exist"""
        self.connect()  # Ensure we have a connection
        try:
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
        finally:
            self.close()

    def ensure_month_table_exists(self, date):
        """Ensure the appointments table exists for the given date"""
        # Convert date to string if it's a datetime object
        if isinstance(date, datetime):
            date = date.strftime("%Y-%m-%d")
        
        # Convert string to datetime if needed
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")
            
        month_year = date.strftime("%Y_%m")
        
        self.connect()  # Ensure we have a connection
        try:
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
        finally:
            self.close()

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
    def is_timeslot_available(self, date, appointment_time, exclude_appointment_id=None):
        """Check if a timeslot is available
        Args:
            date: The appointment date (string or datetime)
            appointment_time: The appointment time
            exclude_appointment_id: Optional ID to exclude from check (used when updating appointments)
        Returns:
            bool: True if available, False if already booked
        """
        self.connect()
        try:
            # Convert date to datetime if it's a string
            if isinstance(date, str):
                date_obj = datetime.strptime(date, "%Y-%m-%d")
            else:
                date_obj = date
            
            month_year = date_obj.strftime("%Y_%m")
            
            # Ensure the month table exists
            self.ensure_month_table_exists(date_obj)
            
            # Reconnect as ensure_month_table_exists closes the connection
            self.connect()
            
            # Check for existing appointments at this time
            query = f"""
            SELECT id, status FROM appointments_{month_year}
            WHERE appointment_date = ? 
            AND appointment_time = ?
            AND status != 'cancelled'
            """
            
            self.cursor.execute(query, (date_obj.strftime("%Y-%m-%d"), appointment_time))
            existing = self.cursor.fetchall()
            
            # If no appointments found, timeslot is available
            if not existing:
                return True
            
            # If updating an existing appointment, exclude it from the check
            if exclude_appointment_id:
                return all(str(row[0]) == str(exclude_appointment_id) for row in existing)
            
            return False
        finally:
            self.close()

    def add_appointment(self, appointment_data):
        """Add a new appointment"""
        self.connect()
        try:
            # Get the month_year from the appointment date
            date_obj = datetime.strptime(appointment_data['appointment_date'], "%Y-%m-%d")
            month_year = date_obj.strftime("%Y_%m")
            
            # First check if timeslot is available
            if not self.is_timeslot_available(date_obj, appointment_data['appointment_time']):
                raise ValueError("This timeslot is already booked. Please select another time.")
            
            # Ensure table exists for this month
            self.ensure_month_table_exists(date_obj)
            
            # Reconnect as ensure_month_table_exists closes the connection
            self.connect()
            
            # Prepare the query dynamically based on provided fields
            fields = []
            values = []
            placeholders = []
            
            for field, value in appointment_data.items():
                if value is not None:  # Only include non-None values
                    fields.append(field)
                    values.append(value)
                    placeholders.append('?')
            
            query = f"""
            INSERT INTO appointments_{month_year} ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
            """
            
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.lastrowid
        finally:
            self.close()

    def create_appointment(self, patient_id, appointment_date, appointment_time, notes=""):
        """Create a new appointment (alias for add_appointment)"""
        return self.add_appointment(patient_id, appointment_date, appointment_time, notes)

    def update_appointment(self, appointment_id, patient_id, appointment_date, appointment_time, notes="", status=None):
        """Update an existing appointment"""
        # Convert appointment_date to string if it's a datetime object
        if isinstance(appointment_date, datetime):
            appointment_date = appointment_date.strftime("%Y-%m-%d")
            
        # Convert string to datetime if needed
        if isinstance(appointment_date, str):
            date_obj = datetime.strptime(appointment_date, "%Y-%m-%d")
        else:
            date_obj = appointment_date
            
        month_year = date_obj.strftime("%Y_%m")
        
        self.connect()
        try:
            # First check if timeslot is available (excluding this appointment)
            if not self.is_timeslot_available(date_obj, appointment_time, appointment_id):
                raise ValueError("This timeslot is already booked. Please select another time.")
            
            # Ensure table exists for this month
            self.ensure_month_table_exists(date_obj)
            
            # Reconnect as ensure_month_table_exists closes the connection
            self.connect()
            
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
        # Convert date to string if it's a datetime object
        if isinstance(date, datetime):
            date = date.strftime("%Y-%m-%d")
            
        # Convert string to datetime if needed
        if isinstance(date, str):
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        else:
            date_obj = date
            
        month_year = date_obj.strftime("%Y_%m")
        
        self.connect()
        try:
            # Ensure table exists for this month
            self.ensure_month_table_exists(date_obj)
            
            # Reconnect as ensure_month_table_exists closes the connection
            self.connect()
            
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

    def check_appointment_exists(self, patient_id, appointment_date, appointment_time):
        """Check if an appointment already exists for the given patient, date and time"""
        self.connect()
        try:
            # Get the month_year from the date
            month_year = datetime.strptime(appointment_date, "%Y-%m-%d").strftime("%Y_%m")
            
            # Query the appropriate appointments table
            query = f"""
            SELECT COUNT(*) as count
            FROM appointments_{month_year}
            WHERE patient_id = ? 
            AND appointment_date = ?
            AND appointment_time = ?
            """
            
            self.cursor.execute(query, (patient_id, appointment_date, appointment_time))
            result = self.cursor.fetchone()
            return result['count'] > 0
        finally:
            self.close()

    def update_appointment_status(self, appointment_id, month_year, status, notes=""):
        """Update appointment status and add to session history if completed"""
        self.connect()
        try:
            # Convert month_year to string if it's a datetime object
            if isinstance(month_year, datetime):
                table_month_year = month_year.strftime("%Y_%m")
            else:
                # Extract year and month from month_year string
                date_obj = datetime.strptime(month_year, "%Y-%m-%d")
                table_month_year = date_obj.strftime("%Y_%m")
            
            # Get current appointment details before update
            query = f"""
            SELECT a.*, p.first_name || ' ' || p.last_name as patient_name
            FROM appointments_{table_month_year} a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.id = ?
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
            
            # Add to session history if status is done
            if status.lower() == 'done':
                # First check if a session already exists for this appointment
                self.cursor.execute(
                    """
                    SELECT id FROM session_history 
                    WHERE patient_id = ? AND session_date = ?
                    """,
                    (current_appt['patient_id'], current_appt['appointment_date'])
                )
                
                existing_session = self.cursor.fetchone()
                
                if not existing_session:
                    # Split notes into treatment notes and follow-up instructions
                    # Assuming notes might contain both, separated by a marker or format
                    treatment_notes = notes
                    follow_up = ""
                    
                    # If notes contain follow-up instructions (marked by "Follow-up:" or similar)
                    if "follow-up:" in notes.lower():
                        parts = notes.split("Follow-up:", 1)
                        treatment_notes = parts[0].strip()
                        follow_up = parts[1].strip() if len(parts) > 1 else ""
                    
                    self.cursor.execute(
                        """
                        INSERT INTO session_history 
                        (patient_id, session_date, treatment_notes, follow_up_instructions)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            current_appt['patient_id'],
                            current_appt['appointment_date'],
                            treatment_notes,
                            follow_up
                        )
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

    def get_future_appointments(self, patient_id):
        """Get future appointments for a patient"""
        try:
            self.connect()
            future_appointments = []
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Get all appointment tables
            tables = self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'appointments_%'"
            ).fetchall()
            
            # Check each table for future appointments
            for table in tables:
                table_name = table[0]
                query = f"""
                SELECT appointment_date, appointment_time
                FROM {table_name}
                WHERE patient_id = ?
                AND appointment_date >= ?
                AND status != 'cancelled'
                ORDER BY appointment_date, appointment_time
                """
                
                appointments = self.cursor.execute(
                    query,
                    (patient_id, current_date)
                ).fetchall()
                
                future_appointments.extend(appointments)
            
            # Sort all appointments by date and time
            future_appointments.sort(key=lambda x: (x[0], x[1]))
            return future_appointments
            
        except Exception as e:
            print(f"Error getting future appointments: {str(e)}")
            return []
        finally:
            self.close()

    def transaction(self):
        """Context manager for database transactions"""
        class Transaction:
            def __init__(self, db):
                self.db = db
                self.conn = None
                self.previous_conn = None
                self.previous_cursor = None
                self.in_transaction = False
            
            def __enter__(self):
                # Store the previous connection state
                self.previous_conn = self.db.conn
                self.previous_cursor = self.db.cursor
                
                # Create a new connection if needed
                self.conn = self.db.connect()
                self.in_transaction = True
                return self.db
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                try:
                    if self.in_transaction:
                        if exc_type is None:
                            # No exception occurred, commit the transaction
                            if self.db.conn:
                                self.db.conn.commit()
                        else:
                            # An exception occurred, rollback the transaction
                            if self.db.conn:
                                self.db.conn.rollback()
                except sqlite3.Error as e:
                    print(f"Error in transaction: {str(e)}")
                    if exc_type is None:
                        # If there wasn't already an exception, raise this one
                        raise
                finally:
                    try:
                        # Only close if this is not a reused connection
                        if self.db.conn and self.db.conn != self.previous_conn:
                            self.db.close()
                        # Restore previous connection state if it existed
                        elif self.previous_conn:
                            self.db.conn = self.previous_conn
                            self.db.cursor = self.previous_cursor
                    except Exception as e:
                        print(f"Error cleaning up transaction: {str(e)}")
                    self.in_transaction = False
                return False  # Re-raise any exceptions
        
        return Transaction(self)

    def get_complete_patient_history(self, patient_id):
        """Get complete history of a patient including all appointments and sessions"""
        self.connect()
        try:
            all_history = []
            
            # Get all appointment tables
            tables = self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'appointments_%'"
            ).fetchall()
            
            # Get appointments from all tables
            for table in tables:
                table_name = table[0]
                query = f"""
                SELECT 
                    a.id,
                    a.appointment_date,
                    a.appointment_time,
                    a.status,
                    a.notes,
                    'appointment' as entry_type,
                    datetime(a.appointment_date || ' ' || a.appointment_time) as sort_date
                FROM {table_name} a
                WHERE a.patient_id = ?
                """
                self.cursor.execute(query, (patient_id,))
                appointments = [dict(row) for row in self.cursor.fetchall()]
                all_history.extend(appointments)
            
            # Get session history
            query = """
            SELECT 
                id,
                session_date as appointment_date,
                '' as appointment_time,
                'completed' as status,
                treatment_notes as notes,
                'session' as entry_type,
                datetime(session_date) as sort_date
            FROM session_history 
            WHERE patient_id = ?
            """
            self.cursor.execute(query, (patient_id,))
            sessions = [dict(row) for row in self.cursor.fetchall()]
            all_history.extend(sessions)
            
            # Sort all entries by date and time
            all_history.sort(key=lambda x: x['sort_date'], reverse=True)
            
            return all_history
            
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            return []
        finally:
            self.close() 