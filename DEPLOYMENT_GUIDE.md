# Deployment Guide for Linxo Scraper API

This guide explains how to deploy the Linxo Scraper API to Coolify or any Docker-based environment.

## Prerequisites

1. **Gmail API Credentials** - You must have `token.json` generated locally
2. **Linxo Account** - Valid email and password
3. **API Key** - A secure random key for API authentication

## Pre-Deployment Checklist

### 1. Generate Gmail Token Locally

Before deploying, you must generate the Gmail API token on your local machine:

```bash
# Run the application locally once
python main.py

# This will open a browser for OAuth authentication
# After authentication, token.json will be created
```

### 2. Extract Gmail Token for Coolify

Run the helper script to get the token value:

```bash
bash setup_gmail_env.sh
```

This will output the JSON content you need to copy.

## Coolify Deployment Steps

### Step 1: Set Environment Variables

Go to your Coolify application → **Environment Variables** and add:

#### Required Variables:

```bash
# Linxo Credentials
LINXO_EMAIL=your_linxo_email@example.com
LINXO_PASSWORD=your_linxo_password

# API Security
API_KEY=your_secure_random_api_key_here

# Gmail API Token (CRITICAL!)
GMAIL_TOKEN_JSON={"token": "...", "refresh_token": "...", ...}
```

#### Optional Variables:

```bash
# n8n Webhook (optional)
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/your-id

# Server Configuration (optional)
HOST=0.0.0.0
PORT=8000
```

### Step 2: Generate API Key

Generate a secure API key:

```bash
openssl rand -hex 32
```

Copy the output and use it as your `API_KEY` value.

### Step 3: Deploy

Push your code to GitHub and Coolify will automatically:
1. Pull the latest code
2. Build the Docker image using the official Playwright image
3. Start the FastAPI application

## Pre-Flight Checks

The application performs automatic pre-flight checks before attempting to log in to Linxo:

### 1. Gmail API Verification
- ✅ Verifies Gmail API access **BEFORE** starting Playwright
- ✅ Checks that `GMAIL_TOKEN_JSON` is valid
- ✅ Fails immediately with clear error if Gmail API is not accessible

### 2. Error Handling
- ✅ Stops immediately on failures (no retries)
- ✅ Returns clear HTTP error codes and messages
- ✅ Takes screenshots for debugging

## API Usage

Once deployed, test your API:

```bash
# Test health endpoint
curl https://your-app.coolify.com/health

# Export CSV (requires API key)
curl -X GET "https://your-app.coolify.com/export-csv" \
  -H "X-API-Key: your_api_key_here"
```

## Error Response Codes

| Code | Description |
|------|-------------|
| `500` | Missing Linxo credentials |
| `503` | Gmail API not accessible OR Linxo website changed |
| `504` | Timeout waiting for verification code |
| `401` | Verification code validation failed |

## Troubleshooting

### Error: "Gmail API pre-flight check failed"

**Solution:**
1. Verify `GMAIL_TOKEN_JSON` environment variable is set correctly
2. Check that the token hasn't expired
3. Regenerate token locally and update the environment variable

### Error: "Could not find email/password field"

**Solution:**
- The Linxo website structure may have changed
- Check the screenshot files in logs for debugging
- Update the selectors in `main.py` if necessary

### Error: "Could not retrieve verification code from Gmail"

**Solution:**
1. Check that Linxo sent the verification email
2. Verify Gmail API has read access to inbox
3. Check Gmail inbox for the verification email manually

## Security Notes

⚠️ **Important:**
- Never commit `token.json` or `.env` to version control
- Keep your API key secure and rotate it periodically
- Use HTTPS for all API requests in production
- Gmail token contains sensitive OAuth credentials - protect it

## Updating Gmail Token

If your Gmail token expires:

1. Run the app locally to regenerate `token.json`
2. Run `bash setup_gmail_env.sh` to get the new token
3. Update `GMAIL_TOKEN_JSON` in Coolify
4. Redeploy the application

The token should auto-refresh, but if it fails, follow the above steps.

## Monitoring

Check application logs in Coolify for:
- ✅ "Gmail API pre-flight check passed" - Good!
- ✅ "Successfully logged in" - Good!
- ❌ "Gmail API verification failed" - Fix Gmail token
- ❌ "Could not find email field" - Website changed

## Support

If you encounter issues:
1. Check the application logs in Coolify
2. Look for screenshot files (downloaded automatically on errors)
3. Verify all environment variables are set correctly
4. Test Gmail API access locally first
