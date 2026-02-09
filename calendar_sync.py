import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    """
    Authenticates with Google.
    Requires 'credentials.json' to exist initially.
    Generates 'token.json' after first login.
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                raise FileNotFoundError("credentials.json not found. Please upload it.")
            
            # This flow requires a browser, so it must be done locally first
            # if running on a headless server.
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

def sync_shifts_to_calendar(shifts_df):
    service = get_calendar_service()
    created_events = 0
    errors = []

    for index, row in shifts_df.iterrows():
        try:
            start_dt = f"{row['date']}T{row['start_time']}:00"
            end_dt = f"{row['date']}T{row['end_time']}:00"

            event = {
                'summary': row.get('title', 'Work Shift'),
                'description': 'Uploaded via ShiftPlanner',
                'start': {
                    'dateTime': start_dt,
                    'timeZone': 'Europe/Berlin', # Update this to your timezone
                },
                'end': {
                    'dateTime': end_dt,
                    'timeZone': 'Europe/Berlin', # Update this to your timezone
                },
            }

            service.events().insert(calendarId='primary', body=event).execute()
            created_events += 1
            
        except Exception as e:
            errors.append(f"Failed to add {row['date']}: {str(e)}")

    return created_events, errors