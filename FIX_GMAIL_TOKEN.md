# Fix GMAIL_TOKEN_JSON Error

## The Problem

You're getting this error:
```
ERROR:gmail_helper:Error loading credentials from environment: 
Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
```

This means the `GMAIL_TOKEN_JSON` environment variable is **not properly formatted**.

---

## ✅ Solution for Local Development (.env file)

### Step 1: Get the correct token value

Run this command:
```bash
bash setup_gmail_env.sh
```

You'll see output like this:
```json
{"token": "ya29...", "refresh_token": "1//03...", ...}
```

### Step 2: Copy the ENTIRE JSON (one line)

Copy everything from the opening `{` to the closing `}`

### Step 3: Add to your .env file

**IMPORTANT:** Use **SINGLE QUOTES** around the JSON:

```bash
# ✅ CORRECT - Use single quotes
GMAIL_TOKEN_JSON='{"token": "ya29.xxxxx...", "refresh_token": "1//xxxxx...", "token_uri": "https://oauth2.googleapis.com/token", "client_id": "YOUR-CLIENT-ID.apps.googleusercontent.com", "client_secret": "YOUR-CLIENT-SECRET", "scopes": ["https://www.googleapis.com/auth/gmail.readonly"], "universe_domain": "googleapis.com", "account": "", "expiry": "2025-10-13T09:39:11Z"}'
```

### ❌ WRONG Ways to Format

```bash
# ❌ WRONG - No quotes (will break)
GMAIL_TOKEN_JSON={"token": "..."}

# ❌ WRONG - Double quotes (bash will interpret them)
GMAIL_TOKEN_JSON="{"token": "..."}"

# ❌ WRONG - Multiple lines
GMAIL_TOKEN_JSON='{
  "token": "..."
}'
```

---

## ✅ Solution for Coolify/Docker Deployment

In Coolify, you don't need quotes at all. Just paste the raw JSON:

### Step 1: Go to Coolify Dashboard
- Navigate to your application
- Click "Environment Variables"

### Step 2: Add Variable
- **Name:** `GMAIL_TOKEN_JSON`
- **Value:** Paste the entire JSON (no quotes needed)
  ```json
  {"token": "ya29.xxxxx...", "refresh_token": "1//xxxxx...", "token_uri": "https://oauth2.googleapis.com/token", "client_id": "YOUR-CLIENT-ID.apps.googleusercontent.com", "client_secret": "YOUR-CLIENT-SECRET", "scopes": ["https://www.googleapis.com/auth/gmail.readonly"], "universe_domain": "googleapis.com", "account": "", "expiry": "2025-10-13T09:39:11Z"}
  ```

### Step 3: Save and Redeploy

---

## Quick Test

After adding to .env, test it:

```bash
# Restart your local server
# Check logs for:
# ✅ "Loading Gmail credentials from GMAIL_TOKEN_JSON environment variable"
# ✅ "Successfully loaded credentials from environment variable"
```

---

## Still Having Issues?

### Check your .env file format:

```bash
# View your current setting (check the format)
cat .env | grep GMAIL_TOKEN_JSON
```

The output should show single quotes around the entire JSON.

### Verify the JSON is valid:

```bash
# This should print the JSON nicely formatted
echo $GMAIL_TOKEN_JSON | python3 -m json.tool
```

If this fails, your JSON is malformed.

---

## Common Mistakes

1. **Forgetting quotes in .env file**
   - Solution: Add single quotes around the JSON

2. **Using double quotes in .env file**
   - Solution: Use single quotes instead

3. **Adding line breaks in the JSON**
   - Solution: Keep it as ONE line

4. **Copying only part of the JSON**
   - Solution: Copy from `{` to `}` including both braces

---

## Summary

**For .env file (local development):**
```bash
GMAIL_TOKEN_JSON='{"token":"...","refresh_token":"...","token_uri":"...","client_id":"...","client_secret":"...","scopes":["..."],"universe_domain":"...","account":"","expiry":"..."}'
```

**For Coolify (production):**
- Paste the raw JSON without any quotes
- Coolify's UI handles the environment variable properly

✅ **Remember:** The JSON must be on ONE line!
