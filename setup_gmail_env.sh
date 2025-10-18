#!/bin/bash

# This script helps you set up Gmail credentials as environment variables for Coolify deployment

echo "=========================================="
echo "Gmail Credentials Setup for Coolify"
echo "=========================================="
echo ""

# Check if token.json exists
if [ ! -f "token.json" ]; then
    echo "❌ Error: token.json not found!"
    echo ""
    echo "Please run the application locally first to generate token.json:"
    echo "  1. Make sure credentials.json is in the project directory"
    echo "  2. Run: python main.py"
    echo "  3. Complete the OAuth flow in your browser"
    echo "  4. Run this script again"
    echo ""
    exit 1
fi

echo "✅ Found token.json"
echo ""
echo "Copy the following JSON and add it to Coolify as an environment variable:"
echo ""
echo "Variable Name: GMAIL_TOKEN_JSON"
echo "Variable Value (copy everything below):"
echo "=========================================="
cat token.json | tr -d '\n'
echo ""
echo "=========================================="
echo ""
echo "📋 Instructions for Coolify:"
echo "  1. Go to your application in Coolify dashboard"
echo "  2. Navigate to 'Environment Variables' section"
echo "  3. Add a new variable:"
echo "     - Name: GMAIL_TOKEN_JSON"
echo "     - Value: [paste the JSON above]"
echo "  4. Save and redeploy your application"
echo ""
echo "✅ Done! Your FastAPI app will now be able to access Gmail API in Coolify"
