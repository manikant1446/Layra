"""
Layra Email Manager Module
====================================
Gmail management using Google Gmail API (OAuth2).
Read, search, send, and manage emails.
"""

import os
import json
import base64
import logging
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger("layra.email")


class EmailManager:
    """
    Gmail integration using Google API.
    Requires OAuth2 credentials from Google Cloud Console.
    """

    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path
        self._service = None
        self._initialized = False

    def _get_service(self):
        """Initialize Gmail API service with OAuth2."""
        if self._service:
            return self._service

        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
            creds = None
            token_path = Path(self.credentials_path).parent / 'gmail_token.json'

            # Load existing token
            if token_path.exists():
                creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not Path(self.credentials_path).exists():
                        return None
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Save token
                token_path.parent.mkdir(parents=True, exist_ok=True)
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())

            self._service = build('gmail', 'v1', credentials=creds)
            self._initialized = True
            logger.info("✅ Gmail API initialized")
            return self._service

        except ImportError:
            logger.error("Gmail dependencies not installed")
            return None
        except Exception as e:
            logger.error(f"Gmail init error: {e}")
            return None

    def check_emails(self, count: int = 5) -> str:
        """Check unread emails and return a summary."""
        service = self._get_service()
        if not service:
            return self._fallback_check_emails()

        try:
            results = service.users().messages().list(
                userId='me', labelIds=['INBOX', 'UNREAD'], maxResults=count
            ).execute()

            messages = results.get('messages', [])
            if not messages:
                return "No unread emails! Your inbox is clean, Sir."

            email_summaries = []
            for msg_data in messages:
                msg = service.users().messages().get(
                    userId='me', id=msg_data['id'], format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()

                headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
                sender = headers.get('From', 'Unknown')
                subject = headers.get('Subject', 'No subject')
                date = headers.get('Date', '')

                # Clean sender name
                if '<' in sender:
                    sender = sender.split('<')[0].strip().strip('"')

                email_summaries.append(f"From: {sender}\nSubject: {subject}\nDate: {date}")

            result = f"You have {len(messages)} unread email(s):\n\n"
            result += "\n\n---\n\n".join(email_summaries)
            return result

        except Exception as e:
            logger.error(f"Email check error: {e}")
            return f"Error checking emails: {e}"

    def send_email(self, to: str, subject: str, body: str) -> str:
        """Send an email."""
        service = self._get_service()
        if not service:
            return "Gmail API not configured. Please set up OAuth credentials first."

        try:
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            send_message = {'raw': raw}

            service.users().messages().send(
                userId='me', body=send_message
            ).execute()

            logger.info(f"📧 Email sent to: {to}")
            return f"Email sent to {to} with subject: {subject}"

        except Exception as e:
            logger.error(f"Email send error: {e}")
            return f"Failed to send email: {e}"

    def search_emails(self, query: str) -> str:
        """Search emails by query."""
        service = self._get_service()
        if not service:
            return "Gmail API not configured."

        try:
            results = service.users().messages().list(
                userId='me', q=query, maxResults=5
            ).execute()

            messages = results.get('messages', [])
            if not messages:
                return f"No emails found matching: {query}"

            email_summaries = []
            for msg_data in messages:
                msg = service.users().messages().get(
                    userId='me', id=msg_data['id'], format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()

                headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
                sender = headers.get('From', 'Unknown')
                subject = headers.get('Subject', 'No subject')

                if '<' in sender:
                    sender = sender.split('<')[0].strip().strip('"')

                email_summaries.append(f"From: {sender} | Subject: {subject}")

            return f"Found {len(messages)} email(s) for '{query}':\n" + "\n".join(email_summaries)

        except Exception as e:
            return f"Email search error: {e}"

    def _fallback_check_emails(self) -> str:
        """Fallback: open Gmail in browser."""
        try:
            import subprocess
            subprocess.run(['open', 'https://mail.google.com'], check=True)
            return "Gmail API not configured. I've opened Gmail in your browser instead. To enable voice email management, set up OAuth credentials."
        except Exception:
            return "Gmail API not configured. Please set up OAuth credentials in the credentials folder."
