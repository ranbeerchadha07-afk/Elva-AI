#!/usr/bin/env python3
"""
Manual Cookie Capture Script for Elva AI
Opens a real browser for manual login and saves cookies securely for future automation
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from playwright.async_api import async_playwright, BrowserContext
from cookie_manager import cookie_manager

# Add backend directory to path for imports
sys.path.append(str(Path(__file__).parent))

class ManualLoginCapture:
    """
    Interactive browser session for manual login and cookie capture
    """
    
    def __init__(self):
        self.browser = None
        self.context = None
        
    async def capture_service_cookies(self, service_name: str, user_identifier: str, login_url: str):
        """
        Open browser for manual login and capture cookies
        
        Args:
            service_name: Service identifier ('linkedin', 'gmail', 'outlook')
            user_identifier: User email or identifier
            login_url: Login URL for the service
        """
        print(f"\n🚀 Starting manual login capture for {service_name}")
        print(f"👤 User: {user_identifier}")
        print(f"🔗 URL: {login_url}")
        
        async with async_playwright() as playwright:
            # Launch browser in headful mode with realistic settings
            self.browser = await playwright.chromium.launch(
                headless=False,
                args=[
                    '--start-maximized',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions-except',
                    '--disable-extensions',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )
            
            # Create context with realistic user agent and viewport
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
            
            # Create new page
            page = await self.context.new_page()
            
            # Navigate to login URL
            await page.goto(login_url, wait_until='networkidle')
            
            print(f"\n🌐 Browser opened at {login_url}")
            print("📋 Manual Login Instructions:")
            print("1. Complete the login process manually in the browser")
            print("2. Ensure you're fully logged in (check dashboard/inbox)")
            print("3. Once logged in successfully, return here and press Enter")
            print("4. The browser will close and cookies will be saved")
            
            # Wait for user confirmation
            input("\n⏳ Press Enter after completing login...")
            
            # Capture cookies
            cookies = await self.context.cookies()
            
            if not cookies:
                print("❌ No cookies found! Make sure you completed login successfully.")
                return False
            
            # Save cookies securely
            success = cookie_manager.save_cookies(service_name, user_identifier, cookies)
            
            if success:
                print(f"✅ Successfully saved {len(cookies)} cookies for {service_name}")
                print(f"🔐 Cookies encrypted and stored securely")
                print(f"📅 Valid for 30 days")
            else:
                print("❌ Failed to save cookies")
                return False
            
            await self.browser.close()
            return True

async def interactive_login():
    """Interactive login session selector"""
    print("🎭 Elva AI - Manual Cookie Capture Tool")
    print("=" * 50)
    
    # Service options
    services = {
        "1": {
            "name": "linkedin", 
            "url": "https://www.linkedin.com/login",
            "description": "LinkedIn (for notifications, connections, job alerts)"
        },
        "2": {
            "name": "gmail", 
            "url": "https://accounts.google.com/signin",
            "description": "Gmail (for email automation)"
        },
        "3": {
            "name": "outlook", 
            "url": "https://outlook.live.com/owa/",
            "description": "Outlook (for email automation)"
        },
        "4": {
            "name": "yahoo", 
            "url": "https://login.yahoo.com/",
            "description": "Yahoo Mail (for email automation)"
        }
    }
    
    print("\nSelect service to capture login for:")
    for key, service in services.items():
        print(f"{key}. {service['description']}")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice not in services:
        print("❌ Invalid choice")
        return
    
    service_info = services[choice]
    
    # Get user identifier
    user_identifier = input(f"\nEnter your {service_info['name'].title()} email/username: ").strip()
    
    if not user_identifier:
        print("❌ User identifier required")
        return
    
    # Start capture process
    capture = ManualLoginCapture()
    success = await capture.capture_service_cookies(
        service_info['name'],
        user_identifier,
        service_info['url']
    )
    
    if success:
        print("\n🎉 Cookie capture completed successfully!")
        print("💡 You can now use Elva AI automation features without manual login")
        print("🔄 Cookies will be automatically used for future automation tasks")
    else:
        print("\n💥 Cookie capture failed. Please try again.")

async def list_sessions():
    """List all saved cookie sessions"""
    sessions = cookie_manager.list_saved_sessions()
    
    if not sessions:
        print("📭 No saved cookie sessions found")
        return
    
    print("\n💾 Saved Cookie Sessions:")
    print("-" * 60)
    
    for session in sessions:
        status_icon = "✅" if session['status'] == 'valid' else "❌"
        print(f"{status_icon} {session['service'].title()} - {session['user']}")
        print(f"   📅 Saved: {session['saved_at'][:19]}")
        print(f"   ⏰ Expires: {session['expires_at'][:19]} ({session['status']})")
        print()

async def cleanup_expired():
    """Clean up expired cookie sessions"""
    print("🧹 Cleaning up expired cookies...")
    cleaned = cookie_manager.cleanup_expired_cookies()
    print(f"✅ Cleaned {cleaned} expired cookie sessions")

async def main():
    """Main application entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            await list_sessions()
        elif command == "cleanup":
            await cleanup_expired()
        elif command == "login":
            await interactive_login()
        else:
            print(f"❌ Unknown command: {command}")
            print("Usage: python manual_cookie_capture.py [login|list|cleanup]")
    else:
        await interactive_login()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")