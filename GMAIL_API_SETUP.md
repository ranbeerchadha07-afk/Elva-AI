# Gmail API OAuth2 Integration Setup

## Overview
Elva AI now supports Gmail API integration with full OAuth2 authentication flow, replacing the deprecated cookie-based approach.

## Features
- ✅ **OAuth2 Authentication**: Secure, Google-approved authentication flow
- ✅ **Inbox Management**: Read emails, check unread messages, search inbox
- ✅ **Email Sending**: Send emails programmatically through Gmail API
- ✅ **Token Management**: Automatic token refresh and secure storage
- ✅ **Multi-scope Access**: Read, send, compose, and modify permissions

## Setup Instructions

### 1. Google Cloud Console Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable the Gmail API:
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API" and enable it

### 2. OAuth2 Credentials Configuration
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Choose "Web application" as application type
4. Configure the following URLs:

**Authorized JavaScript Origins:**
```
http://localhost:3000
https://your-production-domain.com
```

**Authorized Redirect URIs:**
```
http://localhost:3000/auth/gmail/callback
https://your-production-domain.com/auth/gmail/callback
```

### 3. Credentials File Setup
1. Download the OAuth2 credentials JSON file from Google Cloud Console
2. Rename it to `credentials.json`
3. Place it in the `/app/backend/` directory
4. The file structure should match `/app/backend/credentials.json.template`

### 4. Environment Variables
Add to your `.env` file:
```
GMAIL_REDIRECT_URI=http://localhost:3000/auth/gmail/callback
```

## API Endpoints

### Authentication
- `GET /api/gmail/auth` - Get OAuth2 authorization URL
- `POST /api/gmail/callback` - Handle OAuth2 callback
- `GET /api/gmail/status` - Check authentication status

### Email Operations  
- `GET /api/gmail/inbox` - Check inbox (supports query parameters)
- `POST /api/gmail/send` - Send email
- `GET /api/gmail/email/{message_id}` - Get specific email content

## Usage Flow

### 1. Frontend Authentication
```javascript
// Get auth URL
const authResponse = await fetch('/api/gmail/auth');
const { auth_url } = await authResponse.json();

// Redirect user to Google OAuth2
window.location.href = auth_url;

// Handle callback in your app
// POST to /api/gmail/callback with authorization code
```

### 2. Check Inbox
```javascript
const inbox = await fetch('/api/gmail/inbox?max_results=20&query=is:unread');
const { data } = await inbox.json();
console.log(data.emails);
```

### 3. Send Email
```javascript
const sendResult = await fetch('/api/gmail/send', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    to: 'recipient@example.com',
    subject: 'Hello from Elva AI',
    body: 'This email was sent via Gmail API'
  })
});
```

## Security Features
- ✅ Secure OAuth2 flow with PKCE
- ✅ Automatic token refresh
- ✅ Encrypted token storage
- ✅ Scope-limited access (no unnecessary permissions)
- ✅ Error handling and fallback mechanisms

## Migration from Cookie-based System
The old cookie-based Gmail automation has been completely removed for security and reliability reasons. The new OAuth2 system provides:

- **Better Security**: Official Google authentication
- **Better Reliability**: No cookie expiration issues
- **Better Compliance**: Follows Google's API guidelines
- **Better Performance**: Direct API access vs browser automation

## Troubleshooting

### Common Issues
1. **"credentials.json not found"** - Place the credentials file in `/app/backend/`
2. **"Invalid redirect URI"** - Ensure URIs match Google Cloud Console configuration
3. **"Access denied"** - User needs to grant permissions during OAuth2 flow
4. **"Token expired"** - Token refresh is automatic, but user may need to re-authenticate

### Health Check
Check system status at `/api/health` - look for the `gmail_api_integration` section.

## Support
For issues related to Gmail API integration, check the backend logs and health endpoint for detailed status information.