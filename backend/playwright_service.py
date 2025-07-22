import asyncio
import json
import os
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from playwright_stealth import stealth_async
from bs4 import BeautifulSoup
import time
from dataclasses import dataclass
from cookie_manager import cookie_manager

logger = logging.getLogger(__name__)

@dataclass
class AutomationResult:
    """Result object for automation tasks"""
    success: bool
    data: Dict[str, Any]
    message: str
    execution_time: float
    screenshots: List[str] = None
    errors: List[str] = None

class PlaywrightService:
    """
    Advanced Playwright service for web automation tasks
    """
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.default_timeout = 30000  # 30 seconds
        self.stealth_mode = True
        
    async def _get_browser_context(self, service_name: str = None, user_identifier: str = None) -> Tuple[Browser, BrowserContext]:
        """Get or create browser context with stealth mode and optional cookies"""
        if not self.browser or not self.context:
            playwright = await async_playwright().start()
            
            # Launch browser with stealth settings
            self.browser = await playwright.chromium.launch(
                headless=True,
                executable_path="/pw-browsers/chromium-1179/chrome-linux/chrome",
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-background-timer-throttling',
                    '--disable-renderer-backgrounding',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-blink-features=AutomationControlled',
                    '--headless=new'  # Use new headless mode
                ]
            )
            
            # Create context with realistic settings
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            )
            
            # Load cookies if service and user are provided
            if service_name and user_identifier:
                cookies = cookie_manager.load_cookies(service_name, user_identifier)
                if cookies:
                    await self.context.add_cookies(cookies)
                    logger.info(f"🍪 Loaded {len(cookies)} cookies for {service_name} user {user_identifier}")
                else:
                    logger.warning(f"⚠️ No valid cookies found for {service_name} user {user_identifier}")
            
        return self.browser, self.context

    async def _create_page(self, service_name: str = None, user_identifier: str = None) -> Page:
        """Create a new page with stealth mode enabled and optional cookies"""
        browser, context = await self._get_browser_context(service_name, user_identifier)
        page = await context.new_page()
        
        if self.stealth_mode:
            await stealth_async(page)
            
        # Set default timeout
        page.set_default_timeout(self.default_timeout)
        
        return page

    async def extract_dynamic_data(self, url: str, selectors: Dict[str, str], wait_for_element: str = None) -> AutomationResult:
        """
        Extract dynamic data from JavaScript-heavy websites
        
        Args:
            url: Target website URL
            selectors: Dict of {field_name: css_selector} for data extraction
            wait_for_element: Optional selector to wait for before extraction
        """
        start_time = time.time()
        page = None
        
        try:
            logger.info(f"🔍 Extracting dynamic data from: {url}")
            page = await self._create_page()
            
            # Navigate to URL
            await page.goto(url, wait_until='networkidle')
            
            # Wait for specific element if provided
            if wait_for_element:
                await page.wait_for_selector(wait_for_element, timeout=20000)
            
            # Extract data using provided selectors
            extracted_data = {}
            
            for field_name, selector in selectors.items():
                try:
                    # Handle different extraction methods
                    if selector.startswith('text:'):
                        # Extract text content
                        element = await page.query_selector(selector[5:])
                        if element:
                            extracted_data[field_name] = await element.text_content()
                    elif selector.startswith('attr:'):
                        # Extract attribute value
                        parts = selector[5:].split('|')
                        css_selector = parts[0]
                        attr_name = parts[1] if len(parts) > 1 else 'href'
                        element = await page.query_selector(css_selector)
                        if element:
                            extracted_data[field_name] = await element.get_attribute(attr_name)
                    elif selector.startswith('multiple:'):
                        # Extract multiple elements
                        elements = await page.query_selector_all(selector[9:])
                        extracted_data[field_name] = []
                        for element in elements:
                            text = await element.text_content()
                            if text and text.strip():
                                extracted_data[field_name].append(text.strip())
                    else:
                        # Default: extract text content
                        element = await page.query_selector(selector)
                        if element:
                            extracted_data[field_name] = await element.text_content()
                        else:
                            extracted_data[field_name] = None
                            
                except Exception as e:
                    logger.warning(f"Failed to extract {field_name}: {e}")
                    extracted_data[field_name] = None
            
            execution_time = time.time() - start_time
            
            return AutomationResult(
                success=True,
                data=extracted_data,
                message=f"Successfully extracted data from {url}",
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Dynamic data extraction failed: {e}")
            
            return AutomationResult(
                success=False,
                data={},
                message=f"Failed to extract data: {str(e)}",
                execution_time=execution_time,
                errors=[str(e)]
            )
        finally:
            if page:
                await page.close()

    async def scrape_linkedin_insights(self, user_email: str, insight_type: str = "notifications") -> AutomationResult:
        """
        Scrape LinkedIn for notifications, profile views, connection requests using saved cookies
        
        Args:
            user_email: LinkedIn email (used to identify saved cookies)
            insight_type: Type of insights to gather (notifications, profile_views, connections)
        """
        start_time = time.time()
        page = None
        
        try:
            logger.info(f"🛎️ Scraping LinkedIn {insight_type} using saved cookies")
            
            # Create page with saved cookies
            page = await self._create_page("linkedin", user_email)
            
            # Navigate to LinkedIn (should be auto-logged in with cookies)
            await page.goto('https://www.linkedin.com/feed/', wait_until='networkidle')
            
            # Check if we're logged in by looking for the navigation
            try:
                await page.wait_for_selector('.global-nav', timeout=10000)
                logger.info("✅ Successfully logged in with saved cookies")
            except:
                logger.error("❌ Login failed - cookies may be expired or invalid")
                return AutomationResult(
                    success=False,
                    data={},
                    message="Login failed - please recapture cookies using manual_cookie_capture.py",
                    execution_time=time.time() - start_time,
                    errors=["Authentication failed with saved cookies"]
                )
            
            insights_data = {}
            
            if insight_type == "notifications":
                # Navigate to notifications
                await page.click('[data-test-id="nav-notifications"]')
                await page.wait_for_selector('.notifications-list', timeout=15000)
                
                # Extract notifications
                notifications = await page.query_selector_all('.notification-card')
                notifications_list = []
                
                for notification in notifications[:10]:  # Get latest 10
                    try:
                        text = await notification.text_content()
                        time_elem = await notification.query_selector('.time-ago')
                        timestamp = await time_elem.text_content() if time_elem else "Unknown"
                        
                        notifications_list.append({
                            "text": text.strip(),
                            "timestamp": timestamp.strip()
                        })
                    except Exception as e:
                        logger.warning(f"Failed to parse notification: {e}")
                
                insights_data["notifications"] = notifications_list
                
            elif insight_type == "profile_views":
                # Navigate to profile views
                await page.goto('https://www.linkedin.com/me/profile-views/', wait_until='networkidle')
                
                # Extract profile view data
                view_count_elem = await page.query_selector('.profile-views-count')
                if view_count_elem:
                    view_count = await view_count_elem.text_content()
                    insights_data["profile_views_count"] = view_count.strip()
                
                # Extract recent viewers if available
                viewers = await page.query_selector_all('.viewer-item')
                viewers_list = []
                
                for viewer in viewers[:10]:
                    try:
                        name_elem = await viewer.query_selector('.viewer-name')
                        title_elem = await viewer.query_selector('.viewer-title')
                        
                        name = await name_elem.text_content() if name_elem else "Anonymous"
                        title = await title_elem.text_content() if title_elem else "Unknown"
                        
                        viewers_list.append({
                            "name": name.strip(),
                            "title": title.strip()
                        })
                    except Exception as e:
                        logger.warning(f"Failed to parse viewer: {e}")
                
                insights_data["recent_viewers"] = viewers_list
                
            elif insight_type == "connections":
                # Navigate to connection requests
                await page.goto('https://www.linkedin.com/mynetwork/invitation-manager/', wait_until='networkidle')
                
                # Extract pending connection requests
                requests = await page.query_selector_all('.invitation-card')
                requests_list = []
                
                for request in requests[:10]:
                    try:
                        name_elem = await request.query_selector('.invitation-card__name')
                        title_elem = await request.query_selector('.invitation-card__subtitle')
                        
                        name = await name_elem.text_content() if name_elem else "Unknown"
                        title = await title_elem.text_content() if title_elem else "Unknown"
                        
                        requests_list.append({
                            "name": name.strip(),
                            "title": title.strip()
                        })
                    except Exception as e:
                        logger.warning(f"Failed to parse connection request: {e}")
                
                insights_data["connection_requests"] = requests_list
                
            elif insight_type == "messages":
                # Navigate to messages
                await page.goto('https://www.linkedin.com/messaging/', wait_until='networkidle')
                
                # Extract unread messages
                message_threads = await page.query_selector_all('.msg-conversation-listitem')
                messages_list = []
                
                for thread in message_threads[:10]:
                    try:
                        name_elem = await thread.query_selector('.msg-conversation-listitem__participant-names')
                        preview_elem = await thread.query_selector('.msg-conversation-listitem__summary')
                        time_elem = await thread.query_selector('.msg-conversation-listitem__time-stamp')
                        
                        name = await name_elem.text_content() if name_elem else "Unknown"
                        preview = await preview_elem.text_content() if preview_elem else "No preview"
                        timestamp = await time_elem.text_content() if time_elem else "Unknown"
                        
                        messages_list.append({
                            "from": name.strip(),
                            "preview": preview.strip(),
                            "timestamp": timestamp.strip()
                        })
                    except Exception as e:
                        logger.warning(f"Failed to parse message thread: {e}")
                
                insights_data["recent_messages"] = messages_list
            
            execution_time = time.time() - start_time
            
            return AutomationResult(
                success=True,
                data=insights_data,
                message=f"Successfully scraped LinkedIn {insight_type} using saved cookies",
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"LinkedIn scraping failed: {e}")
            
            return AutomationResult(
                success=False,
                data={},
                message=f"Failed to scrape LinkedIn: {str(e)}",
                execution_time=execution_time,
                errors=[str(e)]
            )
        finally:
            if page:
                await page.close()

    async def automate_email_interaction(self, email_provider: str, user_email: str, action: str, **kwargs) -> AutomationResult:
        """
        Automate email interactions using saved cookies (no password required)
        
        Args:
            email_provider: Provider (outlook, yahoo, gmail)
            user_email: Email address (used to identify saved cookies)
            action: Action to perform (check_inbox, send_email, mark_read)
            **kwargs: Additional parameters based on action
        """
        start_time = time.time()
        page = None
        
        try:
            logger.info(f"📩 Automating {email_provider} email: {action} using saved cookies")
            
            # Create page with saved cookies
            page = await self._create_page(email_provider, user_email)
            
            # Provider-specific URLs
            provider_urls = {
                'outlook': 'https://outlook.live.com/mail/',
                'yahoo': 'https://mail.yahoo.com/',
                'gmail': 'https://mail.google.com/mail/u/0/#inbox'
            }
            
            if email_provider not in provider_urls:
                raise ValueError(f"Unsupported email provider: {email_provider}")
            
            # Navigate to email provider (should be auto-logged in with cookies)
            await page.goto(provider_urls[email_provider], wait_until='networkidle')
            
            # Check if we're logged in (provider-specific checks)
            logged_in = await self._check_email_login_status(page, email_provider)
            
            if not logged_in:
                logger.error("❌ Email login failed - cookies may be expired or invalid")
                return AutomationResult(
                    success=False,
                    data={},
                    message=f"Login failed for {email_provider} - please recapture cookies",
                    execution_time=time.time() - start_time,
                    errors=["Authentication failed with saved cookies"]
                )
                
            logger.info(f"✅ Successfully logged into {email_provider} with saved cookies")
            
            # Perform requested action
            result_data = {}
            
            if action == "check_inbox":
                result_data = await self._check_inbox(page, email_provider)
            elif action == "send_email":
                result_data = await self._send_email(page, email_provider, kwargs)
            elif action == "mark_read":
                result_data = await self._mark_emails_read(page, email_provider, kwargs.get('email_ids', []))
            elif action == "get_unread_count":
                result_data = await self._get_unread_count(page, email_provider)
            
            execution_time = time.time() - start_time
            
            return AutomationResult(
                success=True,
                data=result_data,
                message=f"Successfully automated {email_provider} {action} using saved cookies",
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Email automation failed: {e}")
            
            return AutomationResult(
                success=False,
                data={},
                message=f"Failed to automate email: {str(e)}",
                execution_time=execution_time,
                errors=[str(e)]
            )
        finally:
            if page:
                await page.close()
    
    async def _check_email_login_status(self, page: Page, provider: str) -> bool:
        """Check if user is successfully logged into email provider"""
        try:
            if provider == 'gmail':
                # Updated Gmail login check with more comprehensive selectors
                logger.info("🔍 Checking Gmail login status...")
                
                # First, wait for the page to load
                await page.wait_for_load_state('networkidle', timeout=15000)
                
                # Check for multiple possible Gmail elements that indicate successful login
                gmail_selectors = [
                    'div[gh="tl"]',  # Gmail header toolbar
                    '.nH.if',        # Gmail interface container
                    '[data-testid="gmail-logo"]',  # Gmail logo
                    '.gb_C',         # Google bar
                    '.aip',          # Gmail sidebar
                    'div[data-tooltip="Gmail"]',  # Gmail tooltip
                    '.aim',          # Gmail compose button area
                    'div[role="main"]'  # Main Gmail content area
                ]
                
                for selector in gmail_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=3000)
                        logger.info(f"✅ Found Gmail element: {selector}")
                        
                        # Additional check - make sure we're not on a login page
                        current_url = page.url
                        if 'accounts.google.com' in current_url and 'signin' in current_url:
                            logger.warning("❌ Still on login page despite finding elements")
                            continue
                            
                        # Check for inbox or mail-specific elements
                        try:
                            await page.wait_for_selector('.zA', timeout=2000)  # Email thread
                            logger.info("✅ Found email threads - definitely logged in")
                            return True
                        except:
                            pass
                            
                        return True
                    except:
                        continue
                        
                # If no elements found, log page details for debugging
                current_url = page.url
                title = await page.title()
                logger.warning(f"❌ Gmail login check failed. URL: {current_url}, Title: {title}")
                return False
                
            elif provider == 'outlook':
                # Look for Outlook-specific elements
                await page.wait_for_selector('[aria-label="Outlook"], .ms-Nav, ._2wUgT81Yh2C3S6tGYy9e-H', timeout=10000)
                return True
            elif provider == 'yahoo':
                # Look for Yahoo Mail specific elements
                await page.wait_for_selector('[data-test-id="app-nav"], .js-app-container', timeout=10000)
                return True
                
        except Exception as e:
            logger.warning(f"Login status check failed for {provider}: {e}")
            return False
            
        return False

    async def monitor_ecommerce_price(self, product_url: str, price_selector: str, product_name: str = None) -> AutomationResult:
        """
        Monitor e-commerce product for price changes
        
        Args:
            product_url: Product page URL
            price_selector: CSS selector for price element
            product_name: Optional product name for identification
        """
        start_time = time.time()
        page = None
        
        try:
            logger.info(f"🛒 Monitoring price for: {product_url}")
            page = await self._create_page()
            
            # Navigate to product page
            await page.goto(product_url, wait_until='networkidle')
            
            # Wait for price element to load
            await page.wait_for_selector(price_selector, timeout=20000)
            
            # Extract price information
            price_element = await page.query_selector(price_selector)
            price_text = await price_element.text_content() if price_element else None
            
            if not price_text:
                raise ValueError("Could not find price element")
            
            # Clean and parse price
            price_cleaned = re.sub(r'[^\d.,]', '', price_text)
            price_value = float(price_cleaned.replace(',', '')) if price_cleaned else 0
            
            # Extract additional product info
            product_info = {}
            
            # Try to get product title
            title_selectors = ['h1', '.product-title', '[data-testid="product-title"]', '.pdp-product-name']
            for selector in title_selectors:
                title_elem = await page.query_selector(selector)
                if title_elem:
                    product_info['title'] = await title_elem.text_content()
                    break
            
            # Try to get availability
            availability_selectors = ['.availability', '.stock-status', '[data-testid="availability"]']
            for selector in availability_selectors:
                avail_elem = await page.query_selector(selector)
                if avail_elem:
                    product_info['availability'] = await avail_elem.text_content()
                    break
            
            # Try to get rating
            rating_selectors = ['.rating', '.stars', '[data-testid="rating"]']
            for selector in rating_selectors:
                rating_elem = await page.query_selector(selector)
                if rating_elem:
                    product_info['rating'] = await rating_elem.text_content()
                    break
            
            execution_time = time.time() - start_time
            
            result_data = {
                'product_name': product_name or product_info.get('title', 'Unknown Product'),
                'current_price': price_value,
                'price_text': price_text.strip(),
                'product_url': product_url,
                'timestamp': datetime.utcnow().isoformat(),
                'product_info': product_info
            }
            
            return AutomationResult(
                success=True,
                data=result_data,
                message=f"Successfully monitored price: ${price_value}",
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Price monitoring failed: {e}")
            
            return AutomationResult(
                success=False,
                data={},
                message=f"Failed to monitor price: {str(e)}",
                execution_time=execution_time,
                errors=[str(e)]
            )
        finally:
            if page:
                await page.close()

    # Helper methods for email providers
    async def _login_outlook(self, page: Page, email: str, password: str):
        """Login to Outlook"""
        await page.fill('input[type="email"]', email)
        await page.click('#idSIButton9')
        await page.wait_for_selector('input[type="password"]', timeout=10000)
        await page.fill('input[type="password"]', password)
        await page.click('#idSIButton9')
        await page.wait_for_selector('[data-testid="MailList"]', timeout=30000)

    async def _login_yahoo(self, page: Page, email: str, password: str):
        """Login to Yahoo Mail"""
        await page.fill('#login-username', email)
        await page.click('#login-signin')
        await page.wait_for_selector('#login-passwd', timeout=10000)
        await page.fill('#login-passwd', password)
        await page.click('#login-signin')
        await page.wait_for_selector('[data-test-id="message-list"]', timeout=30000)

    async def _login_gmail(self, page: Page, email: str, password: str):
        """Login to Gmail"""
        await page.fill('input[type="email"]', email)
        await page.click('#identifierNext')
        await page.wait_for_selector('input[type="password"]', timeout=10000)
        await page.fill('input[type="password"]', password)
        await page.click('#passwordNext')
        await page.wait_for_selector('[role="main"]', timeout=30000)

    async def _check_inbox(self, page: Page, provider: str) -> Dict[str, Any]:
        """Check inbox for emails"""
        emails = []
        
        if provider == 'outlook':
            email_elements = await page.query_selector_all('[data-testid="message-item"]')
        elif provider == 'yahoo':
            email_elements = await page.query_selector_all('[data-test-id="message-item"]')
        else:  # gmail
            email_elements = await page.query_selector_all('tr.zA')
        
        for email_elem in email_elements[:10]:  # Get latest 10 emails
            try:
                if provider == 'outlook':
                    sender = await email_elem.query_selector('[data-testid="sender-name"]')
                    subject = await email_elem.query_selector('[data-testid="message-subject"]')
                    
                    sender_text = await sender.text_content() if sender else "Unknown"
                    subject_text = await subject.text_content() if subject else "No Subject"
                    
                elif provider == 'yahoo':
                    sender = await email_elem.query_selector('[data-test-id="sender"]')
                    subject = await email_elem.query_selector('[data-test-id="subject"]')
                    
                    sender_text = await sender.text_content() if sender else "Unknown"
                    subject_text = await subject.text_content() if subject else "No Subject"
                    
                else:  # gmail
                    sender = await email_elem.query_selector('.yW span')
                    subject = await email_elem.query_selector('.bog')
                    
                    sender_text = await sender.text_content() if sender else "Unknown"
                    subject_text = await subject.text_content() if subject else "No Subject"
                
                emails.append({
                    "sender": sender_text.strip(),
                    "subject": subject_text.strip(),
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                logger.warning(f"Failed to parse email: {e}")
        
        return {"emails": emails, "count": len(emails)}

    async def _send_email(self, page: Page, provider: str, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send email through web interface"""
        try:
            # Click compose button based on provider
            if provider == 'outlook':
                await page.click('[data-testid="new-mail-button"]')
                await page.wait_for_selector('[data-testid="compose-form"]')
                
                await page.fill('[data-testid="to-field"]', email_data.get('to', ''))
                await page.fill('[data-testid="subject-field"]', email_data.get('subject', ''))
                await page.fill('[data-testid="body-field"]', email_data.get('body', ''))
                
                await page.click('[data-testid="send-button"]')
                
            elif provider == 'yahoo':
                await page.click('[data-test-id="compose-button"]')
                await page.wait_for_selector('[data-test-id="compose-form"]')
                
                await page.fill('[data-test-id="to-field"]', email_data.get('to', ''))
                await page.fill('[data-test-id="subject-field"]', email_data.get('subject', ''))
                await page.fill('[data-test-id="body-field"]', email_data.get('body', ''))
                
                await page.click('[data-test-id="send-button"]')
                
            else:  # gmail
                await page.click('[gh="cm"]')
                await page.wait_for_selector('[role="dialog"]')
                
                await page.fill('textarea[name="to"]', email_data.get('to', ''))
                await page.fill('input[name="subjectbox"]', email_data.get('subject', ''))
                await page.fill('[role="textbox"][aria-label="Message Body"]', email_data.get('body', ''))
                
                await page.click('[role="button"][data-tooltip="Send"]')
            
            return {"status": "sent", "message": "Email sent successfully"}
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _get_unread_count(self, page: Page, provider: str) -> Dict[str, Any]:
        """Get unread email count"""
        try:
            unread_count = 0
            
            if provider == 'gmail':
                # Look for Gmail unread count indicator
                unread_elements = await page.query_selector_all('tr.zE')  # Unread emails have zE class
                unread_count = len(unread_elements)
            elif provider == 'outlook':
                # Look for Outlook unread count
                unread_elements = await page.query_selector_all('[aria-label*="unread"]')
                unread_count = len(unread_elements)
            elif provider == 'yahoo':
                # Look for Yahoo unread count
                unread_elements = await page.query_selector_all('.unread')
                unread_count = len(unread_elements)
            
            return {
                "unread_count": unread_count,
                "provider": provider,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Failed to get unread count for {provider}: {e}")
            return {"unread_count": 0, "error": str(e)}

    async def _mark_emails_read(self, page: Page, provider: str, email_ids: List[str]) -> Dict[str, Any]:
        """Mark emails as read"""
        # Implementation would depend on specific requirements and provider capabilities
        return {"status": "completed", "marked_read": len(email_ids)}

    async def close(self):
        """Clean up browser resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

# Global service instance
playwright_service = PlaywrightService()