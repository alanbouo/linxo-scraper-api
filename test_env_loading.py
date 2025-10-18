#!/usr/bin/env python3
"""
Quick test to verify environment variables are loading correctly
"""

import os
import sys
from dotenv import load_dotenv

print("=" * 80)
print("Environment Variable Test")
print("=" * 80)

# Load .env file
print("\nLoading .env file...")
load_dotenv()

# Check if GMAIL_TOKEN_JSON is set
gmail_token = os.getenv('GMAIL_TOKEN_JSON')

if gmail_token:
    print(f"✅ GMAIL_TOKEN_JSON is loaded!")
    print(f"   Length: {len(gmail_token)} characters")
    print(f"   First 50 chars: {gmail_token[:50]}")
    print(f"   Last 50 chars: ...{gmail_token[-50:]}")
    
    # Try to parse it as JSON
    import json
    try:
        data = json.loads(gmail_token)
        print(f"\n✅ JSON parsing successful!")
        print(f"   Keys: {list(data.keys())}")
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON parsing failed: {e}")
        sys.exit(1)
else:
    print("❌ GMAIL_TOKEN_JSON is NOT set!")
    print("\nDebugging info:")
    print(f"   Current directory: {os.getcwd()}")
    print(f"   .env file exists: {os.path.exists('.env')}")
    
    # Check other env vars
    print(f"\n   LINXO_EMAIL set: {'Yes' if os.getenv('LINXO_EMAIL') else 'No'}")
    print(f"   API_KEY set: {'Yes' if os.getenv('API_KEY') else 'No'}")
    
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ All checks passed! Environment is configured correctly.")
print("=" * 80)
