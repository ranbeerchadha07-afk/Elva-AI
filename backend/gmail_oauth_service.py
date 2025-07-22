import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class GmailOAuthService:
    """
    Gmail API service with OAuth2 authentication
    Handles authentication, email reading, sending, and management
    """
    
    def __init__(self):
        self.credentials = None
        self.service = None
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
        
        # Load credentials configuration
        self.credentials_file_path = Path(__file__).parent / 'credentials.json'
        self.token_file_path = Path(__file__).parent / 'gmail_token.json'
        
        # OAuth2 configuration from environment
        self.redirect_uri = os.getenv('GMAIL_REDIRECT_URI', 'http://localhost:3000/auth/gmail/callback')
        
    def _load_credentials_config(self) -> Dict[str, Any]:
        """Load OAuth2 credentials configuration from credentials.json"""
        try:
            if not self.credentials_file_path.exists():
                logger.warning("⚠️ Gmail credentials.json not found. Please add it to enable Gmail API integration.")
                return None
                
            with open(self.credentials_file_path, 'r') as f:
                credentials_config = json.load(f)
                
            if 'web' in credentials_config:
                return credentials_config['web']
            elif 'installed' in credentials_config:
                return credentials_config['installed']
            else:
                logger.error("❌ Invalid credentials.json format")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error loading credentials.json: {e}")
            return None
    
    def _save_token(self, credentials: Credentials):
        """Save OAuth2 token to file"""
        try:
            token_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }
            
            with open(self.token_file_path, 'w') as f:
                json.dump(token_data, f, indent=2)
                
            logger.info("✅ Gmail OAuth2 token saved successfully")
            
        except Exception as e:
            logger.error(f"❌ Error saving OAuth2 token: {e}")
    
    def _load_token(self) -> Optional[Credentials]:
        """Load OAuth2 token from file"""
        try:
            if not self.token_file_path.exists():
                return None
                
            with open(self.token_file_path, 'r') as f:
                token_data = json.load(f)
            
            credentials = Credentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes')
            )
            
            # Set expiry if available
            if token_data.get('expiry'):
                credentials.expiry = datetime.fromisoformat(token_data['expiry'])
            
            return credentials
            
        except Exception as e:
            logger.error(f"❌ Error loading OAuth2 token: {e}")
            return None
    
    def get_auth_url(self) -> Dict[str, str]:
        """Get OAuth2 authentication URL for user authorization"""
        try:
            credentials_config = self._load_credentials_config()
            if not credentials_config:
                return {
                    'success': False,
                    'message': 'Gmail credentials.json not configured'
                }
            
            flow = Flow.from_client_config(
                {'web': credentials_config},
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            return {
                'success': True,
                'auth_url': auth_url,
                'message': 'OAuth2 authorization URL generated successfully'
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating auth URL: {e}")
            return {
                'success': False,
                'message': f'Failed to generate auth URL: {str(e)}'
            }
    
    def handle_oauth_callback(self, authorization_code: str) -> Dict[str, Any]:
        """Handle OAuth2 callback and exchange code for credentials"""
        try:
            credentials_config = self._load_credentials_config()
            if not credentials_config:
                return {
                    'success': False,
                    'message': 'Gmail credentials.json not configured'
                }
            
            flow = Flow.from_client_config(
                {'web': credentials_config},
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            
            # Exchange authorization code for credentials
            flow.fetch_token(code=authorization_code)
            
            self.credentials = flow.credentials
            self._save_token(self.credentials)
            
            # Initialize Gmail service
            self.service = build('gmail', 'v1', credentials=self.credentials)
            
            return {
                'success': True,
                'message': 'Gmail OAuth2 authentication completed successfully'
            }
            
        except Exception as e:
            logger.error(f"❌ OAuth2 callback error: {e}")
            return {
                'success': False,
                'message': f'OAuth2 authentication failed: {str(e)}'
            }
    
    def _authenticate(self) -> bool:
        """Authenticate with Gmail API using stored or refreshed credentials"""
        try:
            # Try to load existing credentials
            if not self.credentials:
                self.credentials = self._load_token()
            
            if not self.credentials:
                logger.info("ℹ️ No Gmail credentials found. OAuth2 flow required.")
                return False
            
            # Refresh credentials if expired
            if self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
                self._save_token(self.credentials)
                logger.info("🔄 Gmail credentials refreshed successfully")
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=self.credentials)
            logger.info("✅ Gmail API service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Gmail authentication failed: {e}")
            return False
    
    def check_inbox(self, max_results: int = 10, query: str = 'is:unread') -> Dict[str, Any]:
        """Check Gmail inbox and return email list"""
        try:
            if not self._authenticate():
                return {
                    'success': False,
                    'message': 'Gmail authentication required. Please complete OAuth2 flow.',
                    'requires_auth': True
                }
            
            # Search for messages
            results = self.service.users().messages().list(
                userId='me', 
                q=query, 
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            email_list = []
            
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = msg.get('payload', {}).get('headers', [])
                email_data = {
                    'id': message['id'],
                    'thread_id': msg.get('threadId'),
                    'snippet': msg.get('snippet', ''),
                    'from': next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown'),
                    'subject': next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject'),
                    'date': next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date'),
                    'labels': msg.get('labelIds', [])
                }
                email_list.append(email_data)
            
            return {
                'success': True,
                'data': {
                    'emails': email_list,
                    'total_count': len(email_list),
                    'query_used': query
                },
                'message': f'Successfully retrieved {len(email_list)} emails'
            }
            
        except HttpError as e:
            logger.error(f"❌ Gmail API error: {e}")
            return {
                'success': False,
                'message': f'Gmail API error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"❌ Inbox check error: {e}")
            return {
                'success': False,
                'message': f'Failed to check inbox: {str(e)}'
            }
    
    def send_email(
        self, 
        to: str, 
        subject: str, 
        body: str, 
        sender_email: str = None,
        cc: str = None,
        bcc: str = None
    ) -> Dict[str, Any]:
        """Send email using Gmail API"""
        try:
            if not self._authenticate():
                return {
                    'success': False,
                    'message': 'Gmail authentication required. Please complete OAuth2 flow.',
                    'requires_auth': True
                }
            
            # Create message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            if sender_email:
                message['from'] = sender_email
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send message
            send_result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                'success': True,
                'data': {
                    'message_id': send_result['id'],
                    'thread_id': send_result.get('threadId'),
                    'to': to,
                    'subject': subject
                },
                'message': f'Email sent successfully to {to}'
            }
            
        except HttpError as e:
            logger.error(f"❌ Gmail send error: {e}")
            return {
                'success': False,
                'message': f'Failed to send email: {str(e)}'
            }
        except Exception as e:
            logger.error(f"❌ Email send error: {e}")
            return {
                'success': False,
                'message': f'Failed to send email: {str(e)}'
            }
    
    def get_email_content(self, message_id: str) -> Dict[str, Any]:
        """Get full email content by message ID"""
        try:
            if not self._authenticate():
                return {
                    'success': False,
                    'message': 'Gmail authentication required. Please complete OAuth2 flow.',
                    'requires_auth': True
                }
            
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            payload = message.get('payload', {})
            headers = payload.get('headers', [])
            
            # Extract email content
            email_data = {
                'id': message_id,
                'thread_id': message.get('threadId'),
                'snippet': message.get('snippet', ''),
                'from': next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown'),
                'to': next((h['value'] for h in headers if h['name'] == 'To'), 'Unknown'),
                'subject': next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject'),
                'date': next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date'),
                'body': self._extract_body(payload),
                'labels': message.get('labelIds', [])
            }
            
            return {
                'success': True,
                'data': email_data,
                'message': 'Email content retrieved successfully'
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting email content: {e}")
            return {
                'success': False,
                'message': f'Failed to get email content: {str(e)}'
            }
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
        else:
            if payload.get('mimeType') == 'text/plain':
                data = payload.get('body', {}).get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated with Gmail API"""
        return self._authenticate()
    
    def get_auth_status(self) -> Dict[str, Any]:
        """Get current authentication status"""
        credentials_exists = self.credentials_file_path.exists()
        token_exists = self.token_file_path.exists()
        
        return {
            'credentials_configured': credentials_exists,
            'token_exists': token_exists,
            'authenticated': self.is_authenticated() if credentials_exists else False,
            'redirect_uri': self.redirect_uri,
            'scopes': self.scopes
        }

# Create singleton instance
gmail_oauth_service = GmailOAuthService()