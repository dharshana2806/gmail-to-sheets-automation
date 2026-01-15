"""
Service to interact with Google Sheets API
"""
import pickle
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import SCOPES, CREDENTIALS_PATH, TOKEN_PATH, SPREADSHEET_ID, SHEET_NAME, HEADERS

class SheetsService:
    def __init__(self):
        self.service = self._authenticate()
        self.spreadsheet_id = SPREADSHEET_ID
        self._setup_sheet()
    
    def _authenticate(self):
        """Authenticate and create Sheets service instance"""
        # Reuse token from gmail_service since scopes overlap
        creds = None
        
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
        
        return build('sheets', 'v4', credentials=creds)
    
    def _setup_sheet(self):
        """Setup sheet with headers if not exists"""
        try:
            # Check if sheet exists and has headers
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{SHEET_NAME}!A1:E1"
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                # Add headers
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{SHEET_NAME}!A1",
                    valueInputOption='RAW',
                    body={'values': [HEADERS]}
                ).execute()
                print("Headers added to sheet.")
                
        except HttpError as e:
            print(f"Error setting up sheet: {e}")
            # Create new sheet if doesn't exist
            self._create_sheet()
    
    def _create_sheet(self):
        """Create new sheet with headers"""
        try:
            # Add sheet
            body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': SHEET_NAME
                        }
                    }
                }]
            }
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            
            # Add headers
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{SHEET_NAME}!A1",
                valueInputOption='RAW',
                body={'values': [HEADERS]}
            ).execute()
            print(f"Sheet '{SHEET_NAME}' created with headers.")
            
        except Exception as e:
            print(f"Error creating sheet: {e}")
    
    def append_email(self, email_data):
        """Append email data as new row"""
        try:
            values = [[
                email_data['from'],
                email_data['subject'],
                email_data['date'],
                email_data['content'],
                email_data['id']
            ]]
            
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{SHEET_NAME}!A:E",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            print(f"Email appended: {email_data['id'][:10]}...")
            return True
            
        except Exception as e:
            print(f"Error appending email to sheet: {e}")
            return False
    
    def check_duplicate(self, email_id):
        """Check if email already exists in sheet"""
        try:
            # Get all email IDs from column E
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{SHEET_NAME}!E:E"
            ).execute()
            
            values = result.get('values', [])
            existing_ids = [row[0] for row in values if row]
            
            return email_id in existing_ids
            
        except Exception as e:
            print(f"Error checking duplicates: {e}")
            return False