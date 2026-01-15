"""
Parse email content and extract relevant data
"""
import base64
import re
from email import message_from_bytes
from email.header import decode_header
import html2text
from bs4 import BeautifulSoup
from datetime import datetime
import dateutil.parser

class EmailParser:
    @staticmethod
    def decode_header_value(header):
        """Decode email header (subject, from)"""
        if header is None:
            return ""
        
        decoded_parts = decode_header(header)
        result = []
        for content, charset in decoded_parts:
            if isinstance(content, bytes):
                try:
                    result.append(content.decode(charset if charset else 'utf-8'))
                except:
                    result.append(content.decode('utf-8', errors='ignore'))
            else:
                result.append(content)
        return ' '.join(result)
    
    @staticmethod
    def get_email_body(payload):
        """Extract plain text from email body"""
        if isinstance(payload, str):
            return payload
        
        body = ""
        if isinstance(payload, list):
            for part in payload:
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif part.get('mimeType') == 'text/html':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        html_content = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        # Convert HTML to plain text
                        soup = BeautifulSoup(html_content, 'html.parser')
                        body += soup.get_text(separator='\n')
                elif 'parts' in part:
                    body += EmailParser.get_email_body(part.get('parts', []))
        
        # Clean up the text
        body = re.sub(r'\s+', ' ', body).strip()
        return body
    
    @staticmethod
    def parse_email(email_data):
        """Parse email data into structured format"""
        if not email_data:
            return None
        
        headers = email_data.get('payload', {}).get('headers', [])
        
        # Extract headers
        from_email = ""
        subject = ""
        date_str = ""
        
        for header in headers:
            name = header.get('name', '').lower()
            value = header.get('value', '')
            
            if name == 'from':
                from_email = EmailParser.decode_header_value(value)
            elif name == 'subject':
                subject = EmailParser.decode_header_value(value)
            elif name == 'date':
                date_str = value
        
        # Parse date
        try:
            date_obj = dateutil.parser.parse(date_str)
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
        except:
            formatted_date = date_str
        
        # Get email body
        body = EmailParser.get_email_body(email_data.get('payload', {}))
        
        return {
            'id': email_data.get('id'),
            'from': from_email,
            'subject': subject,
            'date': formatted_date,
            'content': body,
            'internalDate': email_data.get('internalDate')
        }