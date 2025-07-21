# 🍪 Cookie-Based Authentication Guide for Elva AI

## Overview
Elva AI now supports cookie-based authentication to bypass OAuth bot blocks and access your personal LinkedIn and Gmail data seamlessly.

## 🚀 Quick Start Guide

### 1. Manual Cookie Capture

#### For LinkedIn:
```bash
cd /app/backend
python manual_cookie_capture.py
# Select option 1 (LinkedIn)
# Enter your LinkedIn email
# Browser will open - login manually
# Press Enter after successful login
```

#### For Gmail:
```bash
cd /app/backend
python manual_cookie_capture.py
# Select option 2 (Gmail)
# Enter your Gmail address
# Browser will open - login manually via Google
# Press Enter after successful login
```

#### For Other Email Providers:
```bash
cd /app/backend
python manual_cookie_capture.py
# Select option 3 (Outlook) or 4 (Yahoo)
# Follow the same process
```

### 2. Verify Saved Sessions
```bash
cd /app/backend
python manual_cookie_capture.py list
```

### 3. Using Elva AI with Cookies

Once cookies are captured, Elva AI can automatically:

#### LinkedIn Features:
- **"Check my LinkedIn notifications"** - Get latest notifications
- **"Show my LinkedIn profile views"** - See who viewed your profile
- **"Check LinkedIn connection requests"** - View pending connections
- **"Check LinkedIn messages"** - Get recent message threads

#### Email Features:
- **"Check my Gmail inbox"** - Get latest emails
- **"Check unread Gmail count"** - Get unread email count
- **"Check my Outlook inbox"** - Access Outlook emails

## 🔧 API Endpoints

### Cookie Management:
- `GET /api/cookie-sessions` - List all saved sessions
- `DELETE /api/cookie-sessions/{service}/{user}` - Delete specific session
- `POST /api/cookie-sessions/cleanup` - Remove expired sessions
- `GET /api/cookie-sessions/{service}/{user}/status` - Check session status

### Direct Automation:
- `POST /api/automation/linkedin-insights` - Get LinkedIn data
- `POST /api/automation/email-check` - Check email with cookies

## 🔒 Security Features

- **Encrypted Storage**: All cookies are encrypted using Fernet encryption
- **Auto Expiry**: Cookies expire after 30 days
- **Secure Cleanup**: Automatic cleanup of expired sessions
- **User Isolation**: Cookies are stored per user and service

## 💡 Usage Tips

1. **Cookie Validity**: Cookies last 30 days. Recapture if automation fails.
2. **Multiple Accounts**: You can save cookies for multiple accounts per service.
3. **Service Detection**: Elva AI automatically detects which service to use based on your request.
4. **Privacy**: Cookies are stored locally and encrypted - never transmitted.

## 🛠️ Troubleshooting

### "No valid cookies found" error:
1. Run manual cookie capture for the service
2. Ensure you completed the login process fully
3. Check cookie status via API

### Automation fails:
1. Cookies may have expired - recapture them
2. Service may have changed interface - may need updates
3. Check logs for specific errors

### Browser doesn't open:
1. Ensure you're running from the backend directory
2. Check that Playwright browsers are installed
3. Try running: `playwright install chromium`

## 📝 Example Usage

```python
# Example API calls (using curl or your HTTP client)

# List saved cookie sessions
curl http://localhost:8001/api/cookie-sessions

# Check LinkedIn notifications
curl -X POST http://localhost:8001/api/automation/linkedin-insights \
  -H "Content-Type: application/json" \
  -d '{"user_email": "your@email.com", "insight_type": "notifications"}'

# Check Gmail inbox
curl -X POST http://localhost:8001/api/automation/email-check \
  -H "Content-Type: application/json" \
  -d '{"user_email": "your@gmail.com", "provider": "gmail", "action": "check_inbox"}'
```

## 🎯 Integration with Chat

When chatting with Elva AI, it will automatically use your saved cookies for:
- LinkedIn automation requests
- Email checking requests
- Any web automation that requires authentication

No need to provide passwords or manually login each time!

---

**Remember**: Keep your cookie sessions secure and recapture them monthly for best results.