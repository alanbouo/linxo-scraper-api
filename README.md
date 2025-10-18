# Linxo CSV Exporter API

A FastAPI-based service that exports transaction data from Linxo to CSV format.

## Features

- Secure authentication using environment variables
- Headless browser automation with Playwright
- CSV export functionality
- Integration with n8n via webhook for automated data processing
- Environment-based configuration

## Prerequisites

- Python 3.8+
- Playwright browser binaries
- Linxo account credentials

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd linxo-scraper-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Playwright browsers:
   ```bash
   playwright install
   ```

## Configuration

1. Copy the example environment file and update with your credentials:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your Linxo credentials:
   ```
   LINXO_EMAIL=your_email@example.com
   LINXO_PASSWORD=your_secure_password
   
   # API Security - REQUIRED for production
   # Generate a strong random key with: openssl rand -hex 32
   API_KEY=your_secure_api_key_here
   
   # Optional: n8n webhook URL for sending CSV data
   N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/your-webhook-id
   
   # Optional: Server configuration
   HOST=0.0.0.0
   PORT=8000
   ```

3. Generate a secure API key:
   ```bash
   openssl rand -hex 32
   ```
   Copy the output and use it as your `API_KEY` in the `.env` file.

## Deployment

### Coolify Deployment
This application is ready for deployment on Coolify. See the detailed deployment guide: [COOLIFY_DEPLOYMENT.md](COOLIFY_DEPLOYMENT.md)

**Quick Start:**
1. Connect your Git repository to Coolify
2. Configure environment variables (see Configuration section)
3. Deploy using the included Dockerfile
4. Your API will be available at the configured domain

### Local Development
1. Start the server:
   ```bash
   python main.py
   ```

2. Access the API at `http://localhost:8000/export-csv` with authentication:
   ```bash
   curl -H "X-API-Key: your_api_key_here" http://localhost:8000/export-csv
   ```

## API Endpoints

### Protected Endpoints (require API key)
- `GET /export-csv`: Exports Linxo transaction data, sends it to an n8n webhook if configured, saves it locally, and returns a JSON status response.
  - **Header required**: `X-API-Key: your_api_key_here`

### Public Endpoints
- `GET /health`: Health check endpoint (no authentication required)
- `GET /`: Redirects to API documentation

## Debugging Webhook Integration

If you're having issues with the n8n webhook:

1. Run the test script: `python test_webhook.py`
2. Check the detailed debugging guide: [WEBHOOK_DEBUG.md](WEBHOOK_DEBUG.md)
3. Review the API response JSON for the `webhook_error` field

## Security

### API Key Authentication
This API uses API key authentication to prevent unauthorized access. All requests to protected endpoints must include the `X-API-Key` header.

**Important security practices:**
- Never commit your `.env` file to version control
- The `.gitignore` file is pre-configured to exclude sensitive files
- Generate a strong, random API key using `openssl rand -hex 32`
- Use different API keys for different environments (dev, staging, production)
- Always use HTTPS in production environments
- Restrict CORS origins in production (update `allow_origins` in `main.py`)
- Rotate your API keys regularly
- Monitor failed authentication attempts in logs

### Example authenticated request:
```bash
# Using curl
curl -H "X-API-Key: your_api_key_here" https://your-domain.com/export-csv

# Using Python requests
import requests
headers = {"X-API-Key": "your_api_key_here"}
response = requests.get("https://your-domain.com/export-csv", headers=headers)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
