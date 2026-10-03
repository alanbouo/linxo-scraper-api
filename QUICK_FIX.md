# ⚡ QUICK FIX: Gmail API Error on Coolify

## You're Getting This Error:

```json
{
  "detail": "Gmail API pre-flight check failed: Cannot access Gmail API..."
}
```

## ✅ The Problem

Your **Coolify deployment** doesn't have the `GMAIL_TOKEN_JSON` environment variable set.

The `.env` file only works **locally** - it's not included in Docker builds (correctly, for security).

---

## 🚀 **SOLUTION: Add Environment Variable to Coolify**

### Step 1: Get Your Token

Run this command on your local machine:

```bash
bash setup_gmail_env.sh
```

You'll see output like:
```
==========================================
{"token": "ya29...", "refresh_token": "1//...", ...}
==========================================
```

### Step 2: Copy the ENTIRE JSON Line

**Copy everything from `{` to `}`** (it's all on one line)

### Step 3: Add to Coolify

1. **Go to Coolify Dashboard**
2. **Navigate to your application**
3. **Click on "Environment Variables"**
4. **Click "Add"** or edit existing variables
5. **Add this variable:**
   - **Name:** `GMAIL_TOKEN_JSON`
   - **Value:** Paste the entire JSON you copied (NO quotes needed!)

### Step 4: Save & Redeploy

1. Click **Save**
2. **Redeploy** your application (Coolify should do this automatically)
3. Wait for the build to complete

---

## ✅ Verify It Works

After redeployment, test your API:

```bash
curl -X GET "https://your-app.coolify.com/export-csv" \
  -H "X-API-Key: your_api_key_here"
```

You should NO LONGER see the Gmail API error!

---

## 📋 **Complete Environment Variables Needed in Coolify:**

Make sure you have ALL of these set:

```
LINXO_EMAIL=your_email@example.com
LINXO_PASSWORD=your_password
API_KEY=your_api_key_here
GMAIL_TOKEN_JSON={"token":"ya29...","refresh_token":"1//...","token_uri":"https://oauth2.googleapis.com/token",...}
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/id  # (optional)
```

---

## ⚠️ **Important Notes:**

1. **Don't use quotes** around the JSON in Coolify's UI
2. **Copy the EXACT output** from `setup_gmail_env.sh`
3. **Make sure it's all on ONE line** (no line breaks)
4. **Redeploy after adding** the environment variable

---

## 🧪 **Local Testing Works?**

If you want to test locally:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the server
python main.py

# Test it
curl -X GET "http://localhost:8000/export-csv" \
  -H "X-API-Key: your_api_key_here"
```

Your local setup is already working (the .env file has the token).

---

## 💡 **Why This Happens:**

| Environment | Uses | Status |
|-------------|------|--------|
| **Local** | `.env` file | ✅ Working (you have it) |
| **Coolify/Docker** | Environment variables in UI | ❌ Missing (needs to be added) |

The `.env` file is **gitignored** and **not included in Docker builds** (correct for security).

For Docker/Coolify, you must set environment variables through the platform's UI.

---

## 🎯 **After You Add the Variable:**

You should see in Coolify logs:
```
INFO:gmail_helper:Loading Gmail credentials from GMAIL_TOKEN_JSON environment variable
INFO:gmail_helper:Successfully loaded credentials from environment variable
✅ Gmail API pre-flight check passed
```

Then your API will work! 🚀
