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
        
    def sync_appointments(self, appointments, calendar_id='primary'):
        """Sync appointments with Google Calendar"""
        if not self.service:
            if not self.authenticate():
                return False
                
        try:
            # Get existing events for deduplication
            # Get events for the date range of appointments
            if appointments:
                dates = [datetime.strptime(a['appointment_date'], "%Y-%m-%d") for a in appointments]
                min_date = min(dates).isoformat() + 'Z'
                max_date = (max(dates) + timedelta(days=1)).isoformat() + 'Z'
            else:
                min_date = datetime.utcnow().isoformat() + 'Z'
                max_date = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=min_date,
                timeMax=max_date,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            existing_events = events_result.get('items', [])
            
            # Create lookup of existing events by appointment ID
            existing_event_map = {}
            for event in existing_events:
                props = event.get('extendedProperties', {}).get('private', {})
                appt_id = props.get('appointmentId')
                if appt_id:
                    if appt_id not in existing_event_map:
                        existing_event_map[appt_id] = []
                    existing_event_map[appt_id].append(event)
            
            # Create or update events
            for appointment in appointments:
                # Calculate end time (45 minutes after start)
                start_datetime = datetime.strptime(f"{appointment['appointment_date']}T{appointment['appointment_time']}", "%Y-%m-%dT%H:%M")
                end_datetime = start_datetime + timedelta(minutes=self.APPOINTMENT_DURATION)
                
                # Format detailed description with end time
                description = f"""
Patient Details:
---------------
Name: {appointment['patient_name']}
Status: {appointment.get('status', 'Scheduled').title()}

Appointment Time:
--------------
Start: {start_datetime.strftime('%I:%M %p')}
End: {end_datetime.strftime('%I:%M %p')}
Duration: {self.APPOINTMENT_DURATION} minutes

Appointment Notes:
----------------
{appointment.get('notes', 'No notes provided')}

Additional Information:
--------------------
Patient ID: {appointment['patient_id']}
Appointment ID: {appointment['id']}
Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

                event = {
                    'summary': f"🏥 Chiropractic: {appointment['patient_name']}",
                    'description': description,
                    'start': {
                        'dateTime': start_datetime.isoformat(),
                        'timeZone': 'UTC'
                    },
                    'end': {
                        'dateTime': end_datetime.isoformat(),
                        'timeZone': 'UTC'
                    },
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 24 * 60},
                            {'method': 'popup', 'minutes': 30}
                        ]
                    },
                    'colorId': self._get_status_color(appointment.get('status', 'scheduled')),
                    'extendedProperties': {
                        'private': {
                            'appointmentId': str(appointment['id']),
                            'patientId': str(appointment['patient_id']),
                            'status': appointment.get('status', 'scheduled').lower(),
                            'lastUpdated': datetime.now().isoformat()
                        }
                    }
                }
                
                # Get existing events for this appointment
                existing_events_for_appt = existing_event_map.get(str(appointment['id']), [])
                
                try:
                    if existing_events_for_appt:
                        # Keep the first event and update it
                        primary_event = existing_events_for_appt[0]
                        self.service.events().update(
                            calendarId=calendar_id,
                            eventId=primary_event['id'],
                            body=event
                        ).execute()
                        print(f"Updated event for appointment {appointment['id']}")
                        
                        # Delete any duplicate events
                        for dup_event in existing_events_for_appt[1:]:
                            try:
                                self.service.events().delete(
                                    calendarId=calendar_id,
                                    eventId=dup_event['id']
                                ).execute()
                                print(f"Deleted duplicate event for appointment {appointment['id']}")
                            except Exception as e:
                                print(f"Error deleting duplicate event: {str(e)}")
                    else:
                        # Create new event
                        self.service.events().insert(
                            calendarId=calendar_id,
                            body=event
                        ).execute()
                        print(f"Created new event for appointment {appointment['id']}")
                except Exception as e:
                    print(f"Error syncing appointment {appointment['id']}: {str(e)}")
                    continue
                    
            return True
            
        except Exception as e:
            print(f"Error syncing with Google Calendar: {str(e)}")
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