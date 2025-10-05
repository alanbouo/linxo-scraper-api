# Linxo CSV Exporter API

A FastAPI-based service that exports transaction data from Linxo to CSV format.

## Features

- Secure authentication using environment variables
- Headless browser automation with Playwright
- CSV export functionality
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
   
   # Optional: Server configuration
   HOST=0.0.0.0
   PORT=8000
   ```

## Usage

1. Start the server:
   ```bash
   python main.py
   ```

2. Access the API at `http://localhost:8000/export-csv`

3. The API will return a CSV file containing your transaction data.

## API Endpoint

- `GET /export-csv`: Exports Linxo transaction data to CSV format.

## Security

- Never commit your `.env` file to version control
- The `.gitignore` file is pre-configured to exclude sensitive files
- Always use HTTPS in production environments

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
