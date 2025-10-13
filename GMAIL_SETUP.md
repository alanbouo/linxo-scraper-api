# Gmail API Setup for Linxo Verification Code

This guide will help you set up Gmail API access to automatically retrieve verification codes from your email.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Name it something like "Linxo Scraper"

## Step 2: Enable Gmail API

1. In the Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Gmail API"
3. Click on it and press **Enable**

## Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - Choose **External** user type
   - Fill in the required fields (App name, User support email, Developer contact)
   - Add your Gmail address to **Test users**
   - Save and continue
4. Back in **Create OAuth client ID**:
   - Application type: **Desktop app**
   - Name: "Linxo Scraper Client"
   - Click **Create**
5. Download the JSON file
6. Rename it to `credentials.json` and place it in your project root directory

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 5: First-Time Authentication

The first time you run the script, it will:
1. Open a browser window
2. Ask you to log in to your Google account
3. Ask for permission to read your Gmail
4. Save the authentication token to `token.json`

After this, the script will automatically use the saved token.

## File Structure

Your project should have:
```
linxo-scraper-api/
├── credentials.json  (OAuth credentials from Google Cloud)
├── token.json        (Auto-generated after first auth)
├── gmail_helper.py   (Gmail API helper functions)
├── main.py          (Main FastAPI application)
└── .env             (Your Linxo credentials)
```

## Security Notes

⚠️ **Important**: 
- Never commit `credentials.json` or `token.json` to version control
- Add them to `.gitignore`
- Keep these files secure as they provide access to your Gmail

## Troubleshooting

### "credentials.json not found"
- Make sure you downloaded the OAuth credentials from Google Cloud Console
- Rename the file to exactly `credentials.json`
- Place it in the project root directory

### "Access blocked: This app's request is invalid"
- Make sure you added your Gmail address to the Test users in OAuth consent screen
- The app must be in "Testing" mode for personal use

### "Token has been expired or revoked"
- Delete `token.json`
- Run the script again to re-authenticate

## How It Works

1. When Linxo requires a verification code, the script:
   - Waits for an email from Linxo (checks every 5 seconds)
   - Searches for emails with subject containing "code", "confirmation", or "verification"
   - Extracts the 6-digit code from the email body
   - Automatically enters it on the Linxo verification page
   - Continues with the CSV export

2. The verification code is extracted using regex patterns that look for:
   - 6 consecutive digits
   - Patterns like "code: 123456"
   - Patterns like "verification: 123456"
