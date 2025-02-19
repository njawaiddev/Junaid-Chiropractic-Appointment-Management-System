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
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
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
        
        # Try to authenticate immediately
        try:
            self.authenticate()
        except Exception as e:
            print(f"Failed to authenticate with Google Calendar: {str(e)}")
        
    def _get_app_data_dir(self):
        """Get the appropriate application data directory based on OS"""
        if os.name == 'nt':  # Windows
            app_data = os.path.join(os.environ['LOCALAPPDATA'], 'ChiropracticManager')
        else:  # macOS and Linux
            app_data = os.path.join(os.path.expanduser('~'), '.chiropracticmanager')
        return app_data
        
    def authenticate(self):
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
                print(f"Error refreshing token: {str(e)}")
                creds = None
                
        # If no valid credentials, initiate OAuth flow
        if not creds:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(
                    "Google Calendar credentials not found. Please download credentials.json from Google Cloud Console"
                )
                
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
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            existing_events = events_result.get('items', [])
            
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
                
                # Find existing event for this appointment
                existing_event = None
                for event_item in existing_events:
                    props = event_item.get('extendedProperties', {}).get('private', {})
                    if (props.get('appointmentId') == str(appointment['id']) and 
                        props.get('patientId') == str(appointment['patient_id'])):
                        # Check if status has changed
                        if props.get('status') != appointment.get('status', 'scheduled').lower():
                            existing_event = event_item
                            break
                        # If status hasn't changed, skip this appointment
                        else:
                            continue
                
                try:
                    if existing_event:
                        # Update existing event
                        self.service.events().update(
                            calendarId=calendar_id,
                            eventId=existing_event['id'],
                            body=event
                        ).execute()
                        print(f"Updated event for appointment {appointment['id']}")
                    else:
                        # Check for any other events with same appointment ID
                        duplicate_events = [
                            e for e in existing_events 
                            if e.get('extendedProperties', {}).get('private', {}).get('appointmentId') == str(appointment['id'])
                        ]
                        
                        # Delete any duplicate events
                        for dup_event in duplicate_events:
                            try:
                                self.service.events().delete(
                                    calendarId=calendar_id,
                                    eventId=dup_event['id']
                                ).execute()
                                print(f"Deleted duplicate event for appointment {appointment['id']}")
                            except Exception as e:
                                print(f"Error deleting duplicate event: {str(e)}")
                        
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