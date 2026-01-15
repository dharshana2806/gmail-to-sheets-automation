"""
Service to interact with Gmail API
"""
import pickle
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import SCOPES, CREDENTIALS_PATH, TOKEN_PATH

class GmailService:
    def __init__(self):
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Authenticate and create Gmail service instance"""
        creds = None
        
        # Load existing token if available
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
        
        return build('gmail', 'v1', credentials=creds)
    
    def get_unread_emails(self, query='is:unread', max_results=50):
        """Fetch unread emails from Gmail"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            return messages
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def get_email_details(self, msg_id):
        """Get full email details by message ID"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            return message
        except Exception as e:
            print(f"Error fetching email {msg_id}: {e}")
            return None
    
    def mark_as_read(self, msg_id):
        """Mark email as read by removing UNREAD label"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error marking email {msg_id} as read: {e}")
            return False