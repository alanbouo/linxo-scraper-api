from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import tempfile
import io

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Linxo CSV Exporter")

@app.get("/export-csv")
def export_linxo_csv():
    email = os.getenv("LINXO_EMAIL")
    password = os.getenv("LINXO_PASSWORD")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Missing credentials in env vars")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set False for debugging
        page = browser.new_page()
        
        # Login
        page.goto("https://web.linxo.com")
        page.fill('input[name="email"]', email)  # Adjust selector if needed
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_url("**/dashboard**")  # Wait for login success
        
        # Navigate to Historique and export
        page.goto("https://web.linxo.com/historique")  # Or click tab
        page.wait_for_selector(".export-button")  # Adjust selector (inspect page)
        page.click(".export-button")
        page.select_option(".format-select", "csv")  # Adjust
        page.click(".download-btn")
        
        # Wait for download (Playwright auto-handles to temp dir)
        with tempfile.TemporaryDirectory() as tmpdir:
            page.wait_for_download(timeout=30000)
            download = page.wait_for_download()
            download.save_as(os.path.join(tmpdir, "linxo.csv"))
            
            # Read CSV for response
            with open(os.path.join(tmpdir, "linxo.csv"), "rb") as f:
                csv_content = f.read()
        
        browser.close()
        
        # Stream CSV back
        return StreamingResponse(
            io.BytesIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=linxo_transactions.csv"}
        )

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)