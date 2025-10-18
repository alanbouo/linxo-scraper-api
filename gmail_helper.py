import os
import re
import time
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
import logging

logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Authenticate and return Gmail API service"""
    creds = None
    
    # First, try to load from environment variable (for Docker/Coolify deployment)
    token_json_env = os.getenv('GMAIL_TOKEN_JSON')
    if token_json_env:
        logger.info("Loading Gmail credentials from GMAIL_TOKEN_JSON environment variable")
        try:
            token_data = json.loads(token_json_env)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
            logger.info("Successfully loaded credentials from environment variable")
        except Exception as e:
            logger.error(f"Error loading credentials from environment: {str(e)}")
    
    # Fallback: Check if token.json file exists (for local development)
    if not creds and os.path.exists('token.json'):
        logger.info("Loading Gmail credentials from token.json file")
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If credentials are invalid or don't exist, try to refresh or authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials...")
            try:
                creds.refresh(Request())
                logger.info("Credentials refreshed successfully")
            except Exception as e:
                logger.error(f"Error refreshing credentials: {str(e)}")
                raise Exception(
                    "Gmail credentials expired and refresh failed. "
                    "Please regenerate token.json locally and update GMAIL_TOKEN_JSON environment variable."
                )
        else:
            # Interactive authentication (only works locally, not in Docker)
            logger.warning("No valid credentials found. Attempting interactive authentication...")
            
            # Check for credentials.json file or environment variable
            credentials_json_env = os.getenv('GMAIL_CREDENTIALS_JSON')
            
            if credentials_json_env:
                # Use credentials from environment variable
                logger.info("Using OAuth credentials from GMAIL_CREDENTIALS_JSON environment variable")
                credentials_data = json.loads(credentials_json_env)
                # Save temporarily to file for the flow
                with open('/tmp/credentials.json', 'w') as f:
                    json.dump(credentials_data, f)
                flow = InstalledAppFlow.from_client_secrets_file('/tmp/credentials.json', SCOPES)
            elif os.path.exists('credentials.json'):
                logger.info("Using OAuth credentials from credentials.json file")
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            else:
                raise Exception(
                    "No Gmail credentials found. For Docker deployment:\n"
                    "1. Generate token.json locally by running the app once\n"
                    "2. Set GMAIL_TOKEN_JSON environment variable with the token.json content\n"
                    "3. Optionally set GMAIL_CREDENTIALS_JSON with credentials.json content\n\n"
                    "For local development:\n"
                    "1. Download credentials.json from Google Cloud Console\n"
                    "2. Run the app to generate token.json"
                )
            
            creds = flow.run_local_server(port=9090)
            
            # Save credentials for future use
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            
            logger.info("New credentials saved to token.json. "
                       "Copy this file content to GMAIL_TOKEN_JSON environment variable for Docker deployment.")
    
    return build('gmail', 'v1', credentials=creds)

def extract_verification_code(email_body):
    """Extract 6-digit verification code from email body"""
    # Look for 6-digit codes in various formats
    patterns = [
        r'\b(\d{6})\b',  # 6 consecutive digits
        r'code[:\s]+(\d{6})',  # "code: 123456"
        r'verification[:\s]+(\d{6})',  # "verification: 123456"
        r'confirmation[:\s]+(\d{6})',  # "confirmation: 123456"
        r'est votre code[:\s]*(\d{6})',  # "est votre code 123456" (French)
        r'(\d{6}) est votre code',  # "123456 est votre code" (French)
        r'code de vérification[:\s]*(\d{6})',  # "code de vérification 123456" (French)
        r'votre code[:\s]*(\d{6})',  # "votre code 123456" (French)
    ]

    for pattern in patterns:
        match = re.search(pattern, email_body, re.IGNORECASE)
        if match:
            return match.group(1)

    return None

def get_linxo_verification_code(max_wait_seconds=60):
    """
    Fetch the latest Linxo verification code from Gmail
    Args:
        max_wait_seconds: Maximum time to wait for the email (default: 60 seconds)

    Returns:
        str: The 6-digit verification code, or None if not found
    """
    try:
        service = get_gmail_service()

        start_time = time.time()

        while time.time() - start_time < max_wait_seconds:
            # Search for recent emails from Linxo (last hour to get more results)
            query = 'from:linxo.com subject:"code de vérification" newer_than:1h'

            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10  # Get more results
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                logger.info("No Linxo verification email found yet, waiting...")
                time.sleep(5)
                continue

            # Sort messages by internal date (newest first)
            # Gmail API doesn't guarantee order, so we'll check all and pick the most recent
            logger.info(f"Found {len(messages)} Linxo emails, checking for codes...")

            for message in messages:
                msg = service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()

                # Get email headers to check subject and date
                headers = msg.get('payload', {}).get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')

                # Get email body
                payload = msg.get('payload', {})
                body = ''

                # Extract body from different parts
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            body_data = part['body'].get('data', '')
                            if body_data:
                                body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                                break
                else:
                    body_data = payload.get('body', {}).get('data', '')
                    if body_data:
                        body = base64.urlsafe_b64decode(body_data).decode('utf-8')

                # Try to extract code from subject first, then body
                code = extract_verification_code(subject)
                if not code:
                    code = extract_verification_code(body)

                if code:
                    logger.info(f"Found verification code: {code} in email dated {date}")
                    return code

            logger.info("Checked all emails but no code extracted, waiting for new email...")
            time.sleep(5)

        logger.error("Timeout waiting for verification code email")
        return None

    except Exception as e:
        logger.error(f"Error fetching verification code: {str(e)}")
        return None
