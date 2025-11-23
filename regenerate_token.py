#!/usr/bin/env python3
"""
Simple script to regenerate Gmail OAuth token
This bypasses the FastAPI app and just handles OAuth authentication
"""

import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def regenerate_token():
    """Regenerate Gmail OAuth token"""
    print("=" * 80)
    print("Gmail Token Regeneration")
    print("=" * 80)
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("\n❌ ERROR: credentials.json not found!")
        print("Please download it from Google Cloud Console")
        return False
    
    print("\n✅ Found credentials.json")
    print("\n🔐 Starting OAuth authentication...")
    print("    A browser window will open for you to authenticate.")
    print("    Please sign in and grant permissions.")
    print()
    
    try:
        # Start OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=9090)
        
        # Save credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        
        print("\n" + "=" * 80)
        print("✅ SUCCESS! Token generated successfully!")
        print("=" * 80)
        
        # Test the token
        print("\n🧪 Testing the new token...")
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress', 'unknown')
        
        print(f"✅ Token verified! Connected to: {email}")
        
        # Show token info
        token_data = json.loads(creds.to_json())
        print(f"\n📊 Token info:")
        print(f"   - Has refresh_token: {'Yes' if token_data.get('refresh_token') else 'No'}")
        print(f"   - Token length: {len(creds.to_json())} characters")
        
        print("\n" + "=" * 80)
        print("Next steps:")
        print("=" * 80)
        print("\n1. For LOCAL use:")
        print("   ✅ token.json is already saved and ready to use")
        print("   ✅ Your local .env already has GMAIL_TOKEN_JSON set")
        print("   ✅ Just restart your local server: python main.py")
        
        print("\n2. For COOLIFY deployment:")
        print("   Run this command to get the value for Coolify:")
        print("   ./get_token_for_coolify.sh")
        print("\n   Then update GMAIL_TOKEN_JSON in Coolify and redeploy.")
        
        print("\n" + "=" * 80)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = regenerate_token()
    exit(0 if success else 1)
