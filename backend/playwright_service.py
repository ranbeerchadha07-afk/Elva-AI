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
        
    async def _get_browser_context(self) -> Tuple[Browser, BrowserContext]:
        """Get or create browser context with stealth mode"""
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
                    '--disable-gpu',
                    '--disable-extensions',
                    '--no-first-run',
                    '--disable-default-apps',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                ]
            )
            
            # Create browser context with enhanced settings
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                java_script_enabled=True,
                accept_downloads=False,
                bypass_csp=True,
                ignore_https_errors=True
            )
            
        return self.browser, self.context

    async def _create_stealth_page(self) -> Page:
        """Create a new page with stealth mode enabled"""
        browser, context = await self._get_browser_context()
        page = await context.new_page()
        
        if self.stealth_mode:
            await stealth_async(page)
            
        # Set default timeout
        page.set_default_timeout(self.default_timeout)
        
        return page

    async def extract_dynamic_data(
        self, 
        url: str, 
        selectors: Dict[str, str], 
        wait_for_element: str = None,
        scroll_to_load: bool = True,
        screenshots: bool = False
    ) -> AutomationResult:
        """
        Extract data from dynamic web pages with JavaScript rendering
        
        Args:
            url: Target URL to scrape
            selectors: Dict mapping field names to CSS selectors
            wait_for_element: CSS selector to wait for before extracting
            scroll_to_load: Whether to scroll to trigger lazy loading
            screenshots: Whether to take screenshots
            
        Returns:
            AutomationResult with extracted data
        """
        start_time = time.time()
        extracted_data = {}
        page = None
        
        try:
            logger.info(f"🔍 Starting data extraction from {url}")
            page = await self._create_stealth_page()
            
            # Navigate to the page
            await page.goto(url, wait_until="domcontentloaded", timeout=self.default_timeout)
            logger.info(f"✅ Page loaded: {url}")
            
            # Wait for specific element if provided
            if wait_for_element:
                try:
                    await page.wait_for_selector(wait_for_element, timeout=20000)
                    logger.info(f"🎯 Target element found: {wait_for_element}")
                except Exception as e:
                    logger.warning(f"⚠️ Target element not found within timeout: {wait_for_element}")
            
            # Scroll to trigger lazy loading
            if scroll_to_load:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)  # Wait for dynamic content
                logger.info("📜 Scrolled to trigger lazy loading")
            
            # Extract data using provided selectors
            for field_name, selector in selectors.items():
                try:
                    # Handle different extraction methods
                    if selector.startswith("text:"):
                        # Extract text content
                        actual_selector = selector[5:]
                        element = await page.query_selector(actual_selector)
                        if element:
                            extracted_data[field_name] = await element.text_content()
                        else:
                            extracted_data[field_name] = None
                            logger.warning(f"⚠️ Element not found for {field_name}: {actual_selector}")
                    
                    elif selector.startswith("attr:"):
                        # Extract attribute value
                        parts = selector.split(":", 2)
                        if len(parts) == 3:
                            _, attr_name, actual_selector = parts
                            element = await page.query_selector(actual_selector)
                            if element:
                                extracted_data[field_name] = await element.get_attribute(attr_name)
                            else:
                                extracted_data[field_name] = None
                        else:
                            logger.error(f"❌ Invalid attribute selector format: {selector}")
                            extracted_data[field_name] = None
                    
                    elif selector.startswith("all:"):
                        # Extract all matching elements
                        actual_selector = selector[4:]
                        elements = await page.query_selector_all(actual_selector)
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
                            logger.warning(f"⚠️ Element not found for {field_name}: {selector}")
                    
                    if extracted_data[field_name]:
                        logger.info(f"📊 Extracted {field_name}: {str(extracted_data[field_name])[:100]}...")
                
                except Exception as e:
                    logger.error(f"❌ Error extracting {field_name} with selector {selector}: {e}")
                    extracted_data[field_name] = None
            
            execution_time = time.time() - start_time
            
            # Clean extracted data
            cleaned_data = {}
            for key, value in extracted_data.items():
                if isinstance(value, str):
                    cleaned_data[key] = value.strip() if value else None
                elif isinstance(value, list):
                    cleaned_data[key] = [item.strip() if isinstance(item, str) else item for item in value if item]
                else:
                    cleaned_data[key] = value
            
            logger.info(f"✅ Data extraction completed in {execution_time:.2f}s")
            
            return AutomationResult(
                success=True,
                data=cleaned_data,
                message=f"Successfully extracted data from {url}",
                execution_time=execution_time,
                screenshots=[] if not screenshots else ["screenshot_placeholder"]
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"💥 Data extraction failed: {e}")
            
            return AutomationResult(
                success=False,
                data=extracted_data,
                message=f"Failed to extract data: {str(e)}",
                execution_time=execution_time,
                errors=[str(e)]
            )
            
        finally:
            if page:
                await page.close()

    async def close(self):
        """Clean up resources"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("🧹 Playwright service closed")
        except Exception as e:
            logger.error(f"Error closing Playwright service: {e}")

# Create a singleton instance
playwright_service = PlaywrightService()