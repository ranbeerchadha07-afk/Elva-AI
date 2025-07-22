#!/usr/bin/env python3
"""
Debug Gmail Login Issue
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from playwright_service import playwright_service
from cookie_manager import cookie_manager

async def debug_gmail_login():
    """Debug Gmail login with cookies"""
    print("🔍 Debugging Gmail login with saved cookies...")
    
    # Check if cookies exist
    cookies = cookie_manager.load_cookies("gmail", "brainlyarpit8649@gmail.com")
    if not cookies:
        print("❌ No cookies found!")
        return
    
    print(f"✅ Found {len(cookies)} cookies")
    
    # Try to access Gmail
    try:
        result = await playwright_service.automate_email_interaction(
            "gmail", 
            "brainlyarpit8649@gmail.com", 
            "check_inbox"
        )
        
        print(f"📧 Gmail automation result:")
        print(f"  Success: {result.success}")
        print(f"  Message: {result.message}")
        print(f"  Execution time: {result.execution_time:.2f}s")
        print(f"  Data: {result.data}")
        
        if result.errors:
            print(f"  Errors: {result.errors}")
            
    except Exception as e:
        print(f"❌ Exception during Gmail automation: {e}")
    
    finally:
        await playwright_service.close()

if __name__ == "__main__":
    asyncio.run(debug_gmail_login())