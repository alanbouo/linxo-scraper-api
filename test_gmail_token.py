#!/usr/bin/env python3
"""
Test script to verify GMAIL_TOKEN_JSON environment variable format
Run this to check if your Gmail token is properly formatted before deployment
"""

import os
import json
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("=" * 80)
print("Gmail Token Environment Variable Checker")
print("=" * 80)

# Get the token from environment
token_json_env = os.getenv('GMAIL_TOKEN_JSON')

if not token_json_env:
    print("\n❌ ERROR: GMAIL_TOKEN_JSON environment variable is not set!")
    print("\nTo fix this:")
    print("1. Run: bash setup_gmail_env.sh")
    print("2. Copy the JSON output")
    print("3. Add to .env file as: GMAIL_TOKEN_JSON='<json_here>'")
    print("   Note: Use SINGLE QUOTES around the JSON")
    exit(1)

print(f"\n✅ GMAIL_TOKEN_JSON is set")
print(f"Length: {len(token_json_env)} characters")
print(f"First 50 chars: {token_json_env[:50]}")

# Try to parse it
try:
    token_data = json.loads(token_json_env)
    print("\n✅ JSON is valid!")
    print(f"\nToken contains these keys: {list(token_data.keys())}")
    
    # Check required fields
    required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret']
    missing_fields = [field for field in required_fields if field not in token_data]
    
    if missing_fields:
        print(f"\n⚠️  WARNING: Missing required fields: {missing_fields}")
    else:
        print("\n✅ All required fields present!")
        
    print("\n" + "=" * 80)
    print("✅ Your GMAIL_TOKEN_JSON is correctly formatted!")
    print("=" * 80)
    
except json.JSONDecodeError as e:
    print(f"\n❌ ERROR: Invalid JSON format!")
    print(f"Error: {str(e)}")
    print(f"\nProblem at position {e.pos}")
    print(f"Line {e.lineno}, Column {e.colno}")
    
    print("\n" + "=" * 80)
    print("COMMON ISSUES:")
    print("=" * 80)
    print("\n1. Missing quotes around the value in .env:")
    print("   ❌ GMAIL_TOKEN_JSON={...}")
    print("   ✅ GMAIL_TOKEN_JSON='{...}'")
    
    print("\n2. Using double quotes in .env (bash will interpret them):")
    print("   ❌ GMAIL_TOKEN_JSON=\"{...}\"")
    print("   ✅ GMAIL_TOKEN_JSON='{...}'")
    
    print("\n3. Special characters not escaped:")
    print("   - Make sure to copy the EXACT output from setup_gmail_env.sh")
    
    print("\n4. Newlines in the JSON:")
    print("   - The JSON must be on ONE line")
    
    print("\n" + "=" * 80)
    print("HOW TO FIX:")
    print("=" * 80)
    print("\n1. Run: bash setup_gmail_env.sh")
    print("2. Copy the ENTIRE JSON output (one line)")
    print("3. Edit your .env file:")
    print("   GMAIL_TOKEN_JSON='<paste_json_here>'")
    print("   (Use SINGLE quotes!)")
    print("\n4. Run this script again to verify")
    
    exit(1)
except Exception as e:
    print(f"\n❌ Unexpected error: {str(e)}")
    exit(1)
