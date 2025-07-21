#!/usr/bin/env python3
"""
Demo script to test cookie-based authentication features
"""

import asyncio
import json
import requests
from pathlib import Path

BACKEND_URL = "http://localhost:8001"

async def test_cookie_endpoints():
    """Test all cookie management endpoints"""
    print("🧪 Testing Cookie Management Endpoints")
    print("=" * 50)
    
    # Test health check
    response = requests.get(f"{BACKEND_URL}/api/health")
    health_data = response.json()
    
    print(f"✅ Backend Health: {health_data['status']}")
    print(f"🍪 Cookie Sessions: {health_data['cookie_management']['total_sessions']}")
    print(f"🔐 Encryption: {health_data['cookie_management']['encryption']}")
    print()
    
    # Test cookie sessions listing
    response = requests.get(f"{BACKEND_URL}/api/cookie-sessions")
    sessions_data = response.json()
    
    print(f"📋 Saved Cookie Sessions: {sessions_data['total']}")
    if sessions_data['sessions']:
        for session in sessions_data['sessions']:
            status_icon = "✅" if session['status'] == 'valid' else "❌"
            print(f"  {status_icon} {session['service']} - {session['user']} ({session['status']})")
    else:
        print("  📭 No saved sessions found")
    print()
    
    # Test cookie status check
    test_email = "demo@example.com"
    response = requests.get(f"{BACKEND_URL}/api/cookie-sessions/linkedin/{test_email}/status")
    status_data = response.json()
    
    print(f"🔍 LinkedIn Cookie Status for {test_email}:")
    print(f"  Valid Cookies: {'Yes' if status_data['has_valid_cookies'] else 'No'}")
    print(f"  Message: {status_data['message']}")
    print()
    
    print("🎯 Manual Cookie Capture Instructions:")
    print("1. Run: cd /app/backend && python manual_cookie_capture.py")
    print("2. Select your service (LinkedIn, Gmail, etc.)")
    print("3. Enter your email/username")
    print("4. Login manually in the browser that opens")
    print("5. Press Enter after successful login")
    print("6. Test automation features in Elva AI!")

def test_integration_example():
    """Show example of how to integrate with chat"""
    print("\n🤖 Elva AI Integration Examples")
    print("=" * 50)
    
    examples = [
        "Check my LinkedIn notifications",
        "Show my LinkedIn profile views", 
        "Check LinkedIn connection requests",
        "Get my LinkedIn messages",
        "Check my Gmail inbox",
        "Get unread Gmail count",
        "Check my Outlook emails"
    ]
    
    print("Once you've captured cookies, you can use these chat commands:")
    for i, example in enumerate(examples, 1):
        print(f"{i}. \"{example}\"")
    
    print("\n💡 Elva AI will automatically:")
    print("- Detect the service you want to access")
    print("- Load your saved cookies")
    print("- Perform the automation without asking for passwords")
    print("- Return the results in a friendly format")

if __name__ == "__main__":
    try:
        asyncio.run(test_cookie_endpoints())
        test_integration_example()
        
        print(f"\n🎉 Cookie-based authentication system is ready!")
        print(f"📚 Read the full guide: /app/backend/COOKIE_GUIDE.md")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the backend is running!")