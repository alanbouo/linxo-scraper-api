from fastapi import FastAPI, HTTPException, status, Security, Depends
from fastapi.responses import StreamingResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
import os
import logging
import asyncio
import platform
from dotenv import load_dotenv
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
import tempfile
import io
import httpx
from typing import Dict, Any, Optional, Tuple
from gmail_helper import get_linxo_verification_code

# Load environment variables from .env file
load_dotenv()

# Debug: Check if .env file is loaded and show available variables (only in development)
if os.getenv('DEBUG', 'false').lower() == 'true':
    print("\n=== Environment Variables Loaded ===")
    print(f"Current working directory: {os.getcwd()}")
    print(f"LINXO_EMAIL present: {'Yes' if os.getenv('LINXO_EMAIL') else 'No'}")
    print(f"LINXO_PASSWORD present: {'Yes' if os.getenv('LINXO_PASSWORD') else 'No'}")
    print("================================\n")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Key Security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify the API key from the request header"""
    expected_api_key = os.getenv("API_KEY")
    
    if not expected_api_key:
        logger.error("API_KEY not configured in environment variables")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API authentication not properly configured"
        )
    
    if api_key != expected_api_key:
        logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return api_key

app = FastAPI(
    title="Linxo CSV Exporter",
    description="API to export transaction data from Linxo to CSV",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation"""
    return RedirectResponse(url="/docs")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}

async def setup_playwright():
    """Setup Playwright browser and context"""
    try:
        logger.info("Initializing Playwright...")
        playwright = await async_playwright().start()
        logger.info("Launching browser...")
        # Set headless=False to see the browser (for debugging)
        browser = await playwright.chromium.launch(headless=True, args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
            '--window-size=1920,1080'
        ])
        logger.info("Creating new context...")
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
            java_script_enabled=True
        )
        logger.info("Creating new page...")
        page = await context.new_page()
        return playwright, browser, context, page
    except Exception as e:
        logger.error(f"Error setting up Playwright: {str(e)}", exc_info=True)
        raise

async def teardown_playwright(playwright, browser, context):
    """Clean up Playwright resources"""
    if context:
        await context.close()
    if browser:
        await browser.close()
    if playwright:
        await playwright.stop()

@app.get("/export-csv", response_description="CSV file with transaction data")
async def export_linxo_csv(api_key: str = Depends(verify_api_key)) -> JSONResponse:
    """Export transaction data from Linxo to CSV"""
    # Get credentials from environment
    email = os.getenv("LINXO_EMAIL")
    password = os.getenv("LINXO_PASSWORD")
    webhook_url = os.getenv("N8N_WEBHOOK_URL")
    
    if not email or not password:
        error_msg = "Missing Linxo credentials in environment variables"
        logger.error(error_msg)
        logger.error(f"Email present: {'yes' if email else 'no'}, Password present: {'yes' if password else 'no'}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
        
    logger.info("Starting export process")

    playwright = None
    browser = None
    context = None
    page = None
    csv_content = None
    
    try:
        logger.info("Starting Playwright browser")
        playwright, browser, context, page = await setup_playwright()
        
        # Login
        logger.info("Navigating to Linxo login page")
        await page.goto("https://wwws.linxo.com/auth.page#Login", timeout=60000)
        
        # Take a screenshot of the current page for debugging
        await page.screenshot(path='login_page.png')
        
        # Wait for and fill login form
        logger.info("Waiting for login form...")
        try:
            # Try multiple possible selectors for the email field
            email_selectors = [
                'input[name="username"]',
                'input[data-cy="email-input"]',
                'input[type="email"]',
                'input[type="text"][name="username"]',
                'input[name*="mail"]',
                'input[id*="mail"]',
                'input[placeholder*="mail"]',
                'input[autocomplete*="mail"]'
            ]
            
            # Wait for any of the possible email fields
            logger.info("Looking for email field...")
            email_field = None
            for selector in email_selectors:
                try:
                    email_field = await page.wait_for_selector(selector, state='visible', timeout=3000)
                    if email_field:
                        logger.info(f"Found email field with selector: {selector}")
                        break
                except:
                    continue
            
            if not email_field:
                raise Exception("Could not find email field on the page")
            
            # Fill in the email
            logger.info("Filling email...")
            await email_field.fill(email)
            
            # Click on the email field again to activate the submit button
            logger.info("Clicking email field to activate submit button...")
            await email_field.click()
            await page.wait_for_timeout(500)  # Small delay to let the button activate
            
            # Try to find and click the continue button
            logger.info("Looking for continue button...")
            button_selectors = [
                'button[data-cy="submit-button"]',
                'button[type="submit"]',
                'button:has-text("Continuer")',
                'button:has-text("Continue")'
            ]
            
            clicked = False
            for selector in button_selectors:
                try:
                    button = await page.wait_for_selector(selector, timeout=2000)
                    if button:
                        logger.info(f"Clicking button with selector: {selector}")
                        await button.click()
                        clicked = True
                        break
                except:
                    continue
            
            if not clicked:
                logger.warning("Could not find continue button, trying to press Enter...")
                await page.keyboard.press('Enter')
            
            # Wait for password field with multiple possible selectors
            logger.info("Waiting for password field...")
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                'input[data-cy="password-input"]',
                'input[name*="pass"]',
                'input[id*="pass"]'
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = await page.wait_for_selector(selector, state='visible', timeout=5000)
                    if password_field:
                        logger.info(f"Found password field with selector: {selector}")
                        break
                except:
                    continue
            
            if not password_field:
                # Take another screenshot to see what's on the page
                await page.screenshot(path='password_field_not_found.png')
                raise Exception("Could not find password field on the page")
            
            # Fill in the password
            logger.info("Filling password...")
            await password_field.fill(password)
            
            # Click on the password field again to activate the submit button
            logger.info("Clicking password field to activate submit button...")
            await password_field.click()
            await page.wait_for_timeout(500)  # Small delay to let the button activate
            
            # Click the login button
            logger.info("Clicking login...")
            login_clicked = False
            for selector in button_selectors:
                try:
                    login_button = await page.wait_for_selector(selector, timeout=2000)
                    if login_button:
                        logger.info(f"Clicking login button with selector: {selector}")
                        await login_button.click()
                        login_clicked = True
                        break
                except:
                    continue
            
            if not login_clicked:
                logger.warning("Could not find login button, trying to press Enter...")
                await page.keyboard.press('Enter')
            
            # Wait for successful login or verification code page
            logger.info("Waiting for login to complete...")
            try:
                # Wait a bit to see if we're redirected to secured page or verification page
                await page.wait_for_timeout(3000)
                
                current_url = page.url
                logger.info(f"Current URL after login: {current_url}")
                
                # Check if we need to enter verification code
                if "auth.page" in current_url or await page.query_selector('input[type="text"][maxlength="1"]'):
                    logger.info("Verification code required, fetching from Gmail...")
                    
                    # Take a screenshot
                    await page.screenshot(path='verification_page.png')
                    
                    # Fetch verification code from Gmail
                    verification_code = await asyncio.to_thread(get_linxo_verification_code, 60)
                    
                    if not verification_code:
                        raise Exception("Could not retrieve verification code from Gmail")
                    
                    logger.info(f"Retrieved verification code: {verification_code}")
                    
                    # Enter the verification code (6 digits in separate input fields)
                    code_inputs = await page.query_selector_all('input[type="text"][maxlength="1"]')

                    if len(code_inputs) == 6:
                        logger.info(f"Found 6 input fields, entering verification code: {verification_code}")
                        for i, digit in enumerate(verification_code):
                            logger.info(f"Filling digit {i+1}: {digit}")

                            # Wait for the input field to be ready and focus it
                            await code_inputs[i].wait_for_element_state('visible')
                            await code_inputs[i].wait_for_element_state('enabled')
                            await code_inputs[i].scroll_into_view_if_needed()

                            # Click and clear the field first
                            await code_inputs[i].click()
                            await code_inputs[i].fill('')

                            # Type the digit with a small delay
                            await code_inputs[i].type(digit, delay=100)

                            # Verify the digit was entered
                            value = await code_inputs[i].input_value()
                            logger.info(f"Digit {i+1} entered: {value}")

                        # Wait for all digits to be processed
                        await page.wait_for_timeout(2000)

                        # Try to trigger form validation by tabbing through fields
                        for i in range(5):  # Tab through first 5 fields
                            await code_inputs[i].press('Tab')
                            await page.wait_for_timeout(200)

                        # Click outside to trigger any validation
                        await page.click('body')
                        await page.wait_for_timeout(1000)
                    else:
                        logger.info(f"Found {len(code_inputs)} input fields, trying alternative approach")

                        # Try different selectors for verification code input
                        alternative_selectors = [
                            'input[name="code"]',
                            'input[id*="code"]',
                            'input[placeholder*="code"]',
                            'input[type="text"]:not([name="username"]):not([name="password"])'
                        ]

                        code_entered = False
                        for selector in alternative_selectors:
                            try:
                                logger.info(f"Trying selector: {selector}")
                                code_input = await page.query_selector(selector)
                                if code_input:
                                    await code_input.wait_for_element_state('visible')
                                    await code_input.wait_for_element_state('enabled')
                                    await code_input.scroll_into_view_if_needed()
                                    await code_input.click()
                                    await code_input.fill('')
                                    await code_input.type(verification_code, delay=100)

                                    value = await code_input.input_value()
                                    logger.info(f"Code entered with {selector}: {value}")
                                    code_entered = True
                                    break
                            except Exception as e:
                                logger.warning(f"Selector {selector} failed: {str(e)}")
                                continue

                        if not code_entered:
                            logger.error("Could not find any suitable input field for verification code")
                            await page.screenshot(path='verification_fields_not_found.png')
                            raise Exception("Could not find verification code input field")
                    
                    # Click validate button
                    logger.info("Looking for validation button...")
                    validate_selectors = [
                        'button:has-text("Valider")',
                        'button:has-text("Validate")',
                        'button[type="submit"]',
                        'button[data-cy="submit-button"]',
                        'input[type="submit"]',
                        'button[class*="validate"]',
                        'button[class*="submit"]'
                    ]

                    validate_clicked = False
                    for selector in validate_selectors:
                        try:
                            logger.info(f"Trying validate button selector: {selector}")
                            validate_button = await page.wait_for_selector(selector, timeout=5000, state='visible')
                            if validate_button:
                                logger.info(f"Found validate button with selector: {selector}")

                                # Scroll into view and click
                                await validate_button.scroll_into_view_if_needed()
                                await validate_button.click()

                                validate_clicked = True
                                logger.info("Validate button clicked successfully")

                                # Wait for the click to process
                                await page.wait_for_timeout(2000)
                                break
                        except Exception as e:
                            logger.warning(f"Validate button selector {selector} failed: {str(e)}")
                            continue

                    if not validate_clicked:
                        logger.warning("No validate button found with standard selectors, trying Enter key...")
                        # Try pressing Enter on the last code input field
                        if len(code_inputs) == 6:
                            await code_inputs[5].press('Enter')
                        else:
                            await page.keyboard.press('Enter')
                        await page.wait_for_timeout(2000)
                    
                    # Wait for redirect after validation
                    logger.info("Waiting for redirect after code validation...")

                    try:
                        # Wait for URL change with longer timeout
                        await page.wait_for_url("**/secured/**", timeout=45000)
                        logger.info("Successfully validated verification code - URL redirected")
                    except Exception as url_timeout:
                        logger.warning(f"URL redirect timeout: {str(url_timeout)}")

                        # Check current URL to see where we are
                        current_url = page.url
                        logger.info(f"Current URL after validation attempt: {current_url}")

                        # Check if we're already on a secured page (maybe the pattern is different)
                        if "linxo.com" in current_url and ("secured" in current_url or "overview" in current_url or "history" in current_url):
                            logger.info("Detected secured page with different URL pattern")
                        else:
                            # Check for error messages on the verification page
                            error_selectors = [
                                '.error-message', '.alert-danger', '.invalid-feedback',
                                '.text-danger', '[class*="error"]', '[class*="invalid"]'
                            ]

                            for selector in error_selectors:
                                try:
                                    error_element = await page.query_selector(selector)
                                    if error_element:
                                        error_text = await error_element.inner_text()
                                        logger.error(f"Verification error: {error_text}")
                                        break
                                except:
                                    continue

                            # Take screenshot of the verification result
                            await page.screenshot(path='verification_result.png')
                            logger.info("Screenshot saved to verification_result.png")

                            raise Exception(f"Verification failed - still on verification page. Current URL: {current_url}")
                else:
                    # Already on secured page
                    logger.info("Successfully logged in without verification code")

            except Exception as e:
                logger.error(f"Error during login: {str(e)}")
                # Check if there's an error message on the page
                error_message = await page.query_selector('.error-message, .alert, .error, .error-text, .notification--error, .invalid-feedback')
                if error_message:
                    error_text = await error_message.inner_text()
                    logger.error(f"Login error message: {error_text}")
                else:
                    logger.error("No error message found on page")

                # Take a screenshot for debugging
                await page.screenshot(path='login_error.png')
                logger.error("Screenshot saved to login_error.png for debugging")
                raise
                    
        except PlaywrightTimeoutError as e:
            logger.error(f"Login timeout or element not found: {str(e)}")
            # Take a screenshot for debugging
            await page.screenshot(path='login_timeout.png')
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Timeout while trying to log in to Linxo. The login form might have changed or the service is unavailable."
            )
        
        # Navigate to transaction history
        logger.info("Navigating to transaction history")
        await page.goto("https://wwws.linxo.com/secured/history.page#Search;pageNumber=0;excludeDuplicates=false", timeout=30000)
        
        try:
            # Wait for the page to load
            logger.info("Waiting for transaction history page to load...")
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            # Take a screenshot for debugging
            await page.screenshot(path='history_page.png')
            
            # Wait for and click CSV export button
            logger.info("Looking for CSV export button...")
            csv_button_selectors = [
                'button:has-text("CSV")',
                'button[type="button"]:has-text("CSV")',
                '.GJALL4ABCV.GJALL4ABLW',
                'button.GJALL4ABCV'
            ]
            
            csv_button = None
            for selector in csv_button_selectors:
                try:
                    csv_button = await page.wait_for_selector(selector, state='visible', timeout=5000)
                    if csv_button:
                        logger.info(f"Found CSV button with selector: {selector}")
                        break
                except:
                    continue
            
            if not csv_button:
                logger.error("Could not find CSV export button")
                await page.screenshot(path='csv_button_not_found.png')
                raise Exception("Could not find CSV export button on the page")
            
            # Click the CSV export button and wait for download
            logger.info("Clicking CSV export button...")
            async with page.expect_download(timeout=30000) as download_info:
                await csv_button.click()
            
            # Save the downloaded file
            logger.info("Saving downloaded CSV file...")
            download = await download_info.value
            with tempfile.TemporaryDirectory() as tmpdir:
                file_path = os.path.join(tmpdir, "linxo_transactions.csv")
                await download.save_as(file_path)
                
                # Read the file content
                with open(file_path, "rb") as f:
                    csv_content = f.read()
            
            logger.info("CSV file downloaded successfully")
    
        except PlaywrightTimeoutError as e:
            logger.error(f"Export timeout or element not found: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Timeout while trying to export transactions. The page structure might have changed."
            )
        
    except PlaywrightError as e:
        error_msg = f"Playwright error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Take a screenshot if page is available
        if page:
            try:
                screenshot = await page.screenshot()
                screenshot_path = "error_screenshot.png"
                with open(screenshot_path, "wb") as f:
                    f.write(screenshot)
                logger.info(f"Screenshot saved to {screenshot_path}")
            except Exception as screenshot_error:
                logger.error(f"Failed to take screenshot: {str(screenshot_error)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
        
    finally:
        # Ensure resources are always cleaned up
        try:
            await teardown_playwright(playwright, browser, context)
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}", exc_info=True)
    
    # Send CSV to n8n webhook first
    logger.info("Sending CSV to n8n webhook...")
    webhook_success = False
    webhook_error = None
    if webhook_url:
        try:
            logger.info(f"Webhook URL: {webhook_url}")
            logger.info(f"Original CSV content size: {len(csv_content)} bytes")
            
            # Convert CSV from UTF-16 to UTF-8 for better n8n compatibility
            try:
                # Try UTF-16 LE (Little Endian) first - most common for Windows/Linxo
                csv_text = csv_content.decode('utf-16-le')
                logger.info("Decoded CSV as UTF-16 LE")
            except UnicodeDecodeError:
                try:
                    # Try UTF-16 BE (Big Endian) as fallback
                    csv_text = csv_content.decode('utf-16-be')
                    logger.info("Decoded CSV as UTF-16 BE")
                except UnicodeDecodeError:
                    # If both fail, try UTF-8 (maybe it's already UTF-8)
                    csv_text = csv_content.decode('utf-8')
                    logger.info("CSV is already UTF-8")
            
            # Re-encode as UTF-8
            csv_utf8 = csv_text.encode('utf-8')
            logger.info(f"Converted CSV to UTF-8, new size: {len(csv_utf8)} bytes")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    webhook_url,
                    content=csv_utf8,
                    headers={
                        "Content-Type": "text/csv; charset=utf-8",
                        "Content-Length": str(len(csv_utf8))
                    }
                )
                logger.info(f"Webhook response status: {response.status_code}")
                logger.info(f"Webhook response body: {response.text[:200]}")
                if response.status_code == 200:
                    webhook_success = True
                    logger.info("CSV successfully sent to n8n webhook")
                else:
                    webhook_error = f"Status {response.status_code}: {response.text[:200]}"
                    logger.warning(f"n8n webhook returned non-200 status: {webhook_error}")
        except httpx.TimeoutException as e:
            webhook_error = f"Timeout: {str(e)}"
            logger.error(f"Timeout sending CSV to n8n: {str(e)}")
        except httpx.RequestError as e:
            webhook_error = f"Request error: {str(e)}"
            logger.error(f"Request error sending CSV to n8n: {str(e)}")
        except Exception as e:
            webhook_error = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error sending CSV to n8n: {str(e)}")
    else:
        webhook_error = "N8N_WEBHOOK_URL not configured"
        logger.warning("N8N_WEBHOOK_URL not set, skipping webhook send")

    # Save CSV locally after webhook attempt
    logger.info("Saving CSV locally...")
    local_save_path = "linxo_transactions.csv"
    try:
        with open(local_save_path, "wb") as f:
            f.write(csv_content)
        logger.info(f"CSV saved locally to {local_save_path}")
        local_save_success = True
    except Exception as e:
        logger.error(f"Error saving CSV locally: {str(e)}")
        local_save_success = False

    # Return JSON response with status
    response_data = {
        "message": "CSV export completed",
        "webhook_sent": webhook_success,
        "webhook_error": webhook_error if not webhook_success else None,
        "local_save_success": local_save_success,
        "local_save_path": local_save_path if local_save_success else None,
        "csv_size_bytes": len(csv_content)
    }
    logger.info(f"Returning status response: {response_data}")
    return JSONResponse(content=response_data)

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)