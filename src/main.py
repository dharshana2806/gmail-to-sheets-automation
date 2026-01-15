"""
Main script to orchestrate the automation
"""
import os
import json
import time
from datetime import datetime
from config import STATE_PATH, MAX_RESULTS, EMAIL_QUERY
from src.gmail_service import GmailService
from src.email_parser import EmailParser
from src.sheets_service import SheetsService

class GmailToSheetsAutomation:
    def __init__(self):
        self.gmail_service = GmailService()
        self.sheets_service = SheetsService()
        self.processed_emails = self._load_state()
    
    def _load_state(self):
        """Load previously processed email IDs"""
        if os.path.exists(STATE_PATH):
            try:
                with open(STATE_PATH, 'r') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()
    
    def _save_state(self):
        """Save processed email IDs to state file"""
        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
        with open(STATE_PATH, 'w') as f:
            json.dump(list(self.processed_emails), f)
    
    def run(self):
        """Main execution flow"""
        print(f"\n{'='*50}")
        print(f"Gmail to Sheets Automation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        # Step 1: Fetch unread emails
        print("\n1. Fetching unread emails from Gmail...")
        emails = self.gmail_service.get_unread_emails(EMAIL_QUERY, MAX_RESULTS)
        print(f"   Found {len(emails)} unread email(s)")
        
        if not emails:
            print("No new emails to process.")
            return
        
        processed_count = 0
        
        # Step 2: Process each email
        for email in emails:
            msg_id = email['id']
            
            # Skip already processed emails
            if msg_id in self.processed_emails:
                print(f"   Skipping already processed email: {msg_id[:10]}...")
                continue
            
            # Skip if already in sheet (safety check)
            if self.sheets_service.check_duplicate(msg_id):
                print(f"   Email {msg_id[:10]}... already exists in sheet")
                self.processed_emails.add(msg_id)
                continue
            
            # Get full email details
            print(f"   Processing email: {msg_id[:10]}...")
            email_data = self.gmail_service.get_email_details(msg_id)
            
            if not email_data:
                continue
            
            # Parse email
            parsed_email = EmailParser.parse_email(email_data)
            
            if not parsed_email:
                continue
            
            # Append to Google Sheets
            if self.sheets_service.append_email(parsed_email):
                # Mark as read in Gmail
                self.gmail_service.mark_as_read(msg_id)
                
                # Add to processed emails
                self.processed_emails.add(msg_id)
                processed_count += 1
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
        
        # Save state
        self._save_state()
        
        print(f"\n✅ Processed {processed_count} new email(s)")
        print(f"📊 Total processed emails in state: {len(self.processed_emails)}")
        print(f"{'='*50}")

def main():
    """Entry point"""
    try:
        automation = GmailToSheetsAutomation()
        automation.run()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()