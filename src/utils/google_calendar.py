import os
import pickle
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pathlib import Path

class GoogleCalendarManager:
    def __init__(self, credentials_path=None, token_path=None):
        """Initialize Google Calendar Manager"""
        self.SCOPES = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/userinfo.email',
            'openid'
        ]
        self.APPOINTMENT_DURATION = 45  # Duration in minutes
        
        # Set default paths if not provided
        if credentials_path is None:
            app_data = self._get_app_data_dir()
            credentials_path = os.path.join(app_data, "google_credentials.json")
        if token_path is None:
            app_data = self._get_app_data_dir()
            token_path = os.path.join(app_data, "google_token.pickle")
            
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self._flow = None
        
        # Try to authenticate immediately
        try:
            self.authenticate(silent=True)
        except Exception as e:
            print(f"Failed to authenticate with Google Calendar: {str(e)}")
        
    def _get_app_data_dir(self):
        """Get the appropriate application data directory based on OS"""
        if os.name == 'nt':  # Windows
            app_data = os.path.join(os.environ['LOCALAPPDATA'], 'ChiropracticManager')
        else:  # macOS and Linux
            app_data = os.path.join(os.path.expanduser('~'), '.chiropracticmanager')
        return app_data
        
    def is_authenticated(self):
        """Check if currently authenticated with Google Calendar"""
        try:
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
                    if creds and not creds.expired:
                        return True
            return False
        except Exception:
            return False
    
    def get_authorization_url(self):
        """Get the URL for Google Calendar authorization"""
        try:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(
                    "Google Calendar credentials not found. Please download credentials.json from Google Cloud Console"
                )
            
            self._flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path,
                self.SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # Use out-of-band flow for desktop apps
            )
            
            # Generate authorization URL for desktop application
            auth_url, _ = self._flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            
            return auth_url
            
        except Exception as e:
            print(f"Error generating authorization URL: {str(e)}")
            return None
    
    def complete_authorization(self, auth_code):
        """Complete the authorization process with the provided code"""
        try:
            if not self._flow:
                raise ValueError("Authorization flow not initialized")
            
            try:
                # Exchange auth code for credentials
                self._flow.fetch_token(code=auth_code)
                creds = self._flow.credentials
                
                # Save the credentials
                os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
                
                # Initialize service with new credentials
                self.service = build('calendar', 'v3', credentials=creds)
                
                return True
            except Exception as token_error:
                print(f"Error exchanging auth code: {str(token_error)}")
                return False
            
        except Exception as e:
            print(f"Error completing authorization: {str(e)}")
            return False
    
    def authenticate(self, silent=False):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
                
        # Refresh token if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                if not silent:
                    print(f"Error refreshing token: {str(e)}")
                creds = None
                
        # If no valid credentials available
        if not creds:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(
                    "Google Calendar credentials not found. Please download credentials.json from Google Cloud Console"
                )
            
            if silent:
                return False
                
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path,
                self.SCOPES
            )
            creds = flow.run_local_server(port=0)
            
            # Save token for future use
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
                
        # Build service
        self.service = build('calendar', 'v3', credentials=creds)
        return True
        
    def sync_appointments(self, appointments):
        """Sync appointments with Google Calendar"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False
            
            calendar_id = 'primary'  # Use primary calendar
            
            # Get existing events for the date range
            start_date = min(appt['appointment_date'] for appt in appointments) if appointments else None
            end_date = max(appt['appointment_date'] for appt in appointments) if appointments else None
            
            if not start_date or not end_date:
                return True  # No appointments to sync
            
            # Get timezone-aware datetime objects
            start_datetime = datetime.strptime(f"{start_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
            end_datetime = datetime.strptime(f"{end_date} 23:59:59", "%Y-%m-%d %H:%M:%S")
            
            # Get existing events
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_datetime.isoformat() + 'Z',
                timeMax=end_datetime.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            existing_events = events_result.get('items', [])
            
            # Create a map of existing events by date and time
            event_map = {}
            for event in existing_events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                if start:
                    event_map[start] = event
            
            # Process each appointment
            for appointment in appointments:
                try:
                    # Create event datetime
                    event_date = appointment['appointment_date']
                    event_time = appointment['appointment_time']
                    event_datetime = datetime.strptime(f"{event_date} {event_time}", "%Y-%m-%d %H:%M")
                    
                    # Format event details
                    patient_name = appointment.get('patient_name', 'Patient')
                    event = {
                        'summary': f'🏥 Chiropractic: {patient_name}',
                        'description': appointment.get('notes', ''),
                        'start': {
                            'dateTime': event_datetime.isoformat(),
                            'timeZone': 'UTC'
                        },
                        'end': {
                            'dateTime': (event_datetime + timedelta(minutes=30)).isoformat(),
                            'timeZone': 'UTC'
                        },
                        'reminders': {
                            'useDefault': True
                        }
                    }
                    
                    # Check if event already exists
                    existing_event = event_map.get(event_datetime.isoformat() + 'Z')
                    
                    if existing_event:
                        # Update existing event
                        self.service.events().update(
                            calendarId=calendar_id,
                            eventId=existing_event['id'],
                            body=event
                        ).execute()
                    else:
                        # Create new event
                        self.service.events().insert(
                            calendarId=calendar_id,
                            body=event
                        ).execute()
                    
                except Exception as e:
                    print(f"Error syncing appointment: {str(e)}")
                    continue
            
            return True
            
        except Exception as e:
            print(f"Error in sync_appointments: {str(e)}")
            return False
            
    def get_calendar_events(self, start_date=None, end_date=None, calendar_id='primary'):
        """Get events from Google Calendar"""
        if not self.service:
            if not self.authenticate():
                return []
                
        try:
            if not start_date:
                start_date = datetime.utcnow()
            if not end_date:
                end_date = start_date + timedelta(days=7)
                
            # Format dates for API
            start = start_date.isoformat() + 'Z'
            end = end_date.isoformat() + 'Z'
            
            # Get events
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start,
                timeMax=end,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Format events for application
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'title': event['summary'],
                    'description': event.get('description', ''),
                    'start': start,
                    'end': end,
                    'status': event.get('status', '')
                })
                
            return formatted_events
            
        except Exception as e:
            print(f"Error getting Google Calendar events: {str(e)}")
            return []
            
    def _calculate_end_time(self, date, time, duration_minutes=30):
        """Calculate end time for an appointment"""
        start_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        return end_datetime.isoformat()

    def _get_status_color(self, status):
        """Get Google Calendar color ID based on appointment status"""
        status_colors = {
            'scheduled': '9',    # Blue
            'confirmed': '10',   # Green
            'pending': '5',      # Yellow
            'done': '2',         # Green
            'cancelled': '4',    # Red
        }
        return status_colors.get(status.lower(), '1')  # Default to blue 

    def get_connected_email(self):
        """Get the email address of the authenticated user"""
        try:
            if not self.service:
                if not self.authenticate(silent=True):
                    return None
            
            # Get credentials from the calendar service
            credentials = self.service._http.credentials
            
            # Build the OAuth2 service
            from googleapiclient.discovery import build
            oauth2_service = build('oauth2', 'v2', credentials=credentials)
            
            # Get user info
            user_info = oauth2_service.userinfo().get().execute()
            return user_info.get('email')
            
        except Exception as e:
            print(f"Error getting user email: {str(e)}")
            return None 

    def sync_all_appointments(self, db):
        """Sync all appointments with Google Calendar"""
        try:
            # Get all appointment tables
            db.connect()
            tables = db.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'appointments_%'"
            ).fetchall()
            
            total_synced = 0
            
            # Process each appointments table
            for table in tables:
                table_name = table[0]
                
                # Get appointments from this table
                query = f"""
                SELECT a.*, p.first_name || ' ' || p.last_name as patient_name
                FROM {table_name} a
                JOIN patients p ON a.patient_id = p.id
                WHERE a.status != 'cancelled'
                ORDER BY a.appointment_date, a.appointment_time
                """
                
                appointments = [dict(row) for row in db.cursor.execute(query).fetchall()]
                
                if appointments:
                    print(f"\nSyncing batch of {len(appointments)} appointments...")
                    if self.sync_appointments(appointments):
                        total_synced += len(appointments)
                        print(f"Successfully synced batch of {len(appointments)} appointments")
                    else:
                        print(f"Failed to sync batch of {len(appointments)} appointments")
            
            print(f"\nSuccessfully synced all {total_synced} appointments")
            return total_synced
            
        except Exception as e:
            print(f"Error syncing all appointments: {str(e)}")
            return 0
        finally:
            db.close() 