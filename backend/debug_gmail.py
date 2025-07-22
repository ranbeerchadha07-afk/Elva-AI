#!/usr/bin/env python3
"""
Debug Gmail cookie functionality
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).parent))

from playwright_service import playwright_service
from cookie_manager import cookie_manager

async def test_gmail_cookies():
    """Test Gmail cookie functionality"""
    
    # Check if cookies exist
    cookies = cookie_manager.load_cookies('gmail', 'brainlyarpit8649@gmail.com')
    print(f"📊 Found {len(cookies) if cookies else 0} Gmail cookies")
    
    if not cookies:
        print("❌ No cookies found!")
        return False
    
    # Test the actual Gmail automation
    print("🧪 Testing Gmail automation with cookies...")
    
    try:
        result = await playwright_service.automate_email_interaction(
            email_provider='gmail',
            user_email='brainlyarpit8649@gmail.com',
            action='check_inbox'
        )
        
        print(f"🎯 Result: {result.success}")
        print(f"📝 Message: {result.message}")
        print(f"⏱️ Execution time: {result.execution_time:.2f}s")
        
        if result.data:
            print(f"📧 Data: {result.data}")
            
        return result.success
        
    except Exception as e:
        print(f"💥 Error: {e}")
        return False
    
    finally:
        await playwright_service.close()

async def main():
    print("🔬 Gmail Cookie Debug Test")
    print("=" * 40)
    
    success = await test_gmail_cookies()
    
    if success:
        print("✅ Gmail automation working!")
    else:
        print("❌ Gmail automation failed")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test cancelled")