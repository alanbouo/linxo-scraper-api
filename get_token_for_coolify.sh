#!/bin/bash
# Simple script to extract just the Gmail token JSON for Coolify
# Output is ready to copy-paste directly into Coolify's environment variable field

if [ ! -f "token.json" ]; then
    echo "❌ ERROR: token.json not found!"
    echo "Please run the application locally first to generate it."
    exit 1
fi

echo "=========================================="
echo "📋 Copy this value for Coolify:"
echo "=========================================="
echo ""
echo "Environment Variable Name:"
echo "GMAIL_TOKEN_JSON"
echo ""
echo "Environment Variable Value (copy the line below):"
echo "----------------------------------------"
cat token.json | tr -d '\n'
echo ""
echo "----------------------------------------"
echo ""
echo "✅ Copy the JSON above and paste it into Coolify's Environment Variables section"
echo "   (Don't include any quotes - just the raw JSON)"
