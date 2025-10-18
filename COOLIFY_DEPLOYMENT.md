# Coolify Deployment Guide

## Overview
This guide will help you deploy your FastAPI Linxo scraper API to Coolify. The application is containerized with Docker and includes all necessary dependencies for Playwright automation.

## Prerequisites
- Coolify server installed and accessible
- Git repository accessible to Coolify
- Your `.env` file with production credentials

## Step 1: Prepare Your Repository

### 1.1 Ensure Required Files Are Present
Your repository should contain:
- `Dockerfile` ✅ (Created)
- `.dockerignore` ✅ (Created)
- `requirements.txt` ✅ (Exists)
- `main.py` ✅ (Updated for production)
- `.env.example` ✅ (Template created)

### 1.2 Environment Variables Setup
Copy your production environment variables to a secure location (not in your repo):

```bash
# Required for production
LINXO_EMAIL=your_production_email@example.com
LINXO_PASSWORD=your_secure_password
API_KEY=your_generated_api_key_here

# Optional
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/your-webhook-id
HOST=0.0.0.0
PORT=8000

# For debugging (set to 'false' in production)
DEBUG=false
```

## Step 2: Coolify Deployment

### 2.1 Connect Your Repository
1. Log into your Coolify dashboard
2. Click "Add New Resource" → "Application"
3. Choose "Git Repository"
4. Enter your repository URL
5. Select the branch (usually `main` or `master`)

### 2.2 Configure Build Settings
- **Build Pack**: Docker
- **Dockerfile Path**: `./Dockerfile` (should auto-detect)
- **Build Context Directory**: `/` (root directory)
- **Port**: `8000`

### 2.3 Configure Environment Variables
Add the following environment variables in Coolify:

#### Required Variables
```
LINXO_EMAIL=your_production_email@example.com
LINXO_PASSWORD=your_secure_password
API_KEY=your_generated_api_key_here
```

#### Optional Variables
```
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/your-webhook-id
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### 2.4 Configure Domains (Optional)
- Add a custom domain or use the auto-generated Coolify URL
- Enable HTTPS (recommended)

### 2.5 Deploy
1. Click "Deploy" to start the build
2. Monitor the build logs for any issues
3. Once deployed, your API will be available at the configured domain

## Step 3: Verify Deployment

### 3.1 Test Health Check
```bash
curl https://your-coolify-domain.com/health
```

Expected response:
```json
{
  "status": "healthy"
}
```

### 3.2 Test API Endpoint
```bash
curl -H "X-API-Key: your_api_key_here" https://your-coolify-domain.com/export-csv
```

### 3.3 Check Logs
- Monitor Coolify logs for any startup issues
- Check that Playwright browsers installed correctly
- Verify environment variables are loaded

## Troubleshooting

### Build Failures
- **Playwright installation fails**: Check that all system dependencies are installed in Dockerfile
- **Import errors**: Ensure all Python packages are in `requirements.txt`
- **Port conflicts**: Make sure port 8000 is available

### Runtime Issues
- **API Key errors**: Verify `API_KEY` environment variable is set correctly
- **Linxo login fails**: Check `LINXO_EMAIL` and `LINXO_PASSWORD` are correct
- **Webhook errors**: Verify `N8N_WEBHOOK_URL` is accessible

### Common Issues
- **Browser not found**: Playwright might need additional system dependencies
- **Memory issues**: The container might need more memory for browser automation
- **Timeout issues**: Increase timeouts in Coolify resource limits

## Production Optimizations

### Resource Allocation
- **Memory**: Allocate at least 2GB RAM
- **CPU**: At least 1 CPU core
- **Disk**: Sufficient space for temporary files and screenshots

### Security
- Use strong API keys (generate with `openssl rand -hex 32`)
- Restrict CORS origins in production
- Enable HTTPS
- Regularly rotate API keys

### Monitoring
- Enable Coolify's built-in monitoring
- Set up alerts for failed deployments
- Monitor resource usage during API calls

## Scaling Considerations

### Horizontal Scaling
- Coolify supports multiple instances
- Each instance is stateless (good for this API)
- Consider load balancing for high traffic

### Database Integration (Future)
- If you add persistent storage, consider external databases
- Use environment variables for connection strings

## Alternative Deployment Methods

### Using Docker Compose (if needed)
If you need additional services (like Redis for rate limiting):

```yaml
version: '3.8'
services:
  linxo-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LINXO_EMAIL=${LINXO_EMAIL}
      - LINXO_PASSWORD=${LINXO_PASSWORD}
      - API_KEY=${API_KEY}
      - N8N_WEBHOOK_URL=${N8N_WEBHOOK_URL}
    restart: unless-stopped
```

### Using Pre-built Image
If you want to build the image separately:
```bash
docker build -t linxo-scraper-api .
docker tag linxo-scraper-api your-registry/linxo-scraper-api:latest
docker push your-registry/linxo-scraper-api:latest
```

Then configure Coolify to pull from your registry.

## Support

If you encounter issues:
1. Check Coolify logs
2. Verify environment variables
3. Test locally with Docker (if possible)
4. Check network connectivity to external services (Linxo, n8n)
