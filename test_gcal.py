from src.utils.google_calendar import GoogleCalendarManager
from src.database.db_manager import DatabaseManager
from datetime import datetime, timedelta

def test_calendar_sync():
    try:
        # Initialize managers
        db = DatabaseManager()
        gcal = GoogleCalendarManager()
        
        # Get all appointment tables
        db.connect()
        tables = db.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'appointments_%'"
        ).fetchall()
        db.close()
        
        all_appointments = []
        
        # Get appointments from each table
        for table in tables:
            table_name = table[0]
            month_year = table_name.replace('appointments_', '')
            date_obj = datetime.strptime(month_year, "%Y_%m")
            
            # Get appointments for this month
            db.connect()
            query = f"""
            SELECT a.*, p.first_name || ' ' || p.last_name as patient_name
            FROM {table_name} a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.status != 'cancelled'
            ORDER BY a.appointment_date, a.appointment_time
            """
            appointments = [dict(row) for row in db.cursor.execute(query).fetchall()]
            db.close()
            
            all_appointments.extend(appointments)
            print(f"Found {len(appointments)} appointments in {month_year}")
        
        print(f"\nTotal appointments to sync: {len(all_appointments)}")
        
        # Try to authenticate and sync
        print("\nAttempting to authenticate with Google Calendar...")
        if gcal.authenticate():
            print("Authentication successful!")
            print("\nAttempting to sync appointments...")
            
            # Sync in batches to avoid overwhelming the API
            batch_size = 50
            for i in range(0, len(all_appointments), batch_size):
                batch = all_appointments[i:i + batch_size]
                print(f"\nSyncing batch {i//batch_size + 1} ({len(batch)} appointments)...")
                if gcal.sync_appointments(batch):
                    print("Batch sync successful!")
                else:
                    print("Batch sync failed!")
            
            print("\nAll syncs completed!")
        else:
            print("Authentication failed!")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_calendar_sync() 