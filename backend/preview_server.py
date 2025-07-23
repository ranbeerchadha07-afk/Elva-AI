from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app without a prefix
app = FastAPI(title="Elva AI Preview", description="Smart AI Assistant with Hybrid Architecture")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.preview.emergentag*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Models
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str = "default_user"
    message: str
    response: str
    intent_data: Optional[dict] = None
    approved: Optional[bool] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    id: str
    message: str
    response: str
    intent_data: Optional[dict] = None
    needs_approval: bool = False
    timestamp: datetime

class ApprovalRequest(BaseModel):
    session_id: str
    message_id: str
    approved: bool
    edited_data: Optional[dict] = None

# Mock AI responses for preview
def mock_detect_intent(user_input: str) -> dict:
    """Mock intent detection for preview"""
    user_input_lower = user_input.lower()
    
    if any(word in user_input_lower for word in ['email', 'send', 'mail']):
        return {
            "intent": "send_email",
            "recipient_name": "John",
            "recipient_email": "john@example.com",
            "subject": "Meeting Update",
            "body": "Hi John,\n\nI wanted to update you about our upcoming meeting.\n\nBest regards"
        }
    elif any(word in user_input_lower for word in ['linkedin', 'post', 'share']):
        return {
            "intent": "linkedin_post",
            "topic": "AI Technology",
            "category": "Technology",
            "post_content": "Excited to share insights about AI advancements! #AI #Technology"
        }
    elif any(word in user_input_lower for word in ['remind', 'reminder', 'alert']):
        return {
            "intent": "set_reminder",
            "reminder_text": "Team meeting",
            "reminder_time": "2:00 PM",
            "reminder_date": "tomorrow"
        }
    else:
        return {
            "intent": "general_chat",
            "message": user_input
        }

def mock_generate_response(intent_data: dict, user_input: str) -> str:
    """Mock AI response generation for preview"""
    intent = intent_data.get("intent")
    
    if intent == "send_email":
        return f"✉️ **Email Draft Ready**\n\n📧 **To**: {intent_data.get('recipient_name', 'Recipient')}\n🎯 **Subject**: {intent_data.get('subject', 'No Subject')}\n\n📝 **Message**:\n{intent_data.get('body', 'Email content')}\n\n*Would you like me to send this email?*"
    
    elif intent == "linkedin_post":
        return f"📱 **LinkedIn Post Draft**\n\n🎯 **Topic**: {intent_data.get('topic', 'General')}\n📂 **Category**: {intent_data.get('category', 'Professional')}\n\n📝 **Content**:\n{intent_data.get('post_content', 'Post content')}\n\n*Ready to post on LinkedIn?*"
    
    elif intent == "set_reminder":
        return f"⏰ **Reminder Set**\n\n📝 **Task**: {intent_data.get('reminder_text', 'Reminder')}\n📅 **When**: {intent_data.get('reminder_date', 'Today')} at {intent_data.get('reminder_time', 'Now')}\n\n*I'll remind you about this!*"
    
    else:
        # General chat response
        greetings = ["Hello! I'm Elva AI, your intelligent assistant.", 
                    "Hi there! How can I help you today?",
                    "Great to meet you! I'm here to assist with emails, reminders, LinkedIn posts, and more.",
                    "Hello! I can help you with automation, send emails, create reminders, and handle various tasks."]
        
        if any(word in user_input.lower() for word in ['hello', 'hi', 'hey', 'greet']):
            return greetings[0]
        elif 'what' in user_input.lower() and 'do' in user_input.lower():
            return "I'm Elva AI! I can help you with:\n\n📧 **Email Management** - Send and compose emails\n📱 **LinkedIn Posts** - Create and share professional content\n⏰ **Reminders** - Set and manage your tasks\n🤖 **General Chat** - Answer questions and have conversations\n🔧 **Automation** - Handle various automated tasks\n\nTry asking me to 'send an email' or 'create a LinkedIn post'!"
        else:
            return f"I understand you said: '{user_input}'\n\nI'm Elva AI with hybrid architecture combining Claude Sonnet and Groq for optimal performance. I can help with emails, LinkedIn posts, reminders, and general questions. What would you like me to help you with?"

# API Routes
@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for Elva AI"""
    try:
        logger.info(f"Processing chat request: {request.message}")
        
        # Mock intent detection
        intent_data = mock_detect_intent(request.message)
        
        # Generate response based on intent
        response = mock_generate_response(intent_data, request.message)
        
        # Determine if approval is needed
        needs_approval = intent_data.get("intent") in ["send_email", "linkedin_post", "set_reminder"]
        
        chat_response = ChatResponse(
            id=str(uuid.uuid4()),
            message=request.message,
            response=response,
            intent_data=intent_data,
            needs_approval=needs_approval,
            timestamp=datetime.utcnow()
        )
        
        return chat_response
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Error processing chat request")

@api_router.post("/approve")
async def approve_action(request: ApprovalRequest):
    """Handle approval/rejection of AI-suggested actions"""
    try:
        if request.approved:
            return {
                "success": True,
                "message": "✅ Action approved and executed successfully!",
                "n8n_response": {"status": "completed", "id": str(uuid.uuid4())}
            }
        else:
            return {
                "success": True,
                "message": "❌ Action cancelled as requested.",
                "n8n_response": {"status": "cancelled"}
            }
    except Exception as e:
        logger.error(f"Approval error: {e}")
        raise HTTPException(status_code=500, detail="Error processing approval")

@api_router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    # Mock empty history for preview
    return {"messages": [], "session_id": session_id}

@api_router.get("/gmail/status")
async def get_gmail_status(session_id: str = None):
    """Check real Gmail status"""
    try:
        from gmail_oauth_service import GmailOAuthService
        gmail_service = GmailOAuthService()
        status = await gmail_service.get_auth_status(session_id)
        return status
    except Exception as e:
        return {
            "success": False,
            "authenticated": False,
            "credentials_configured": False,
            "requires_auth": True,
            "service": "gmail",
            "session_id": session_id,
            "error": str(e)
        }

@api_router.get("/gmail/auth")
async def initiate_gmail_auth(session_id: str = None):
    """Initiate real Gmail authentication"""
    try:
        from gmail_oauth_service import GmailOAuthService
        gmail_service = GmailOAuthService()
        auth_response = gmail_service.get_auth_url()
        if auth_response.get('success', False):
            auth_url = auth_response.get('auth_url')
        else:
            raise Exception(auth_response.get('message', 'Unknown error'))
        return {
            "success": True,
            "auth_url": auth_url,
            "session_id": session_id
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Gmail authentication error: {str(e)}",
            "auth_url": None
        }

@api_router.get("/gmail/callback")
async def gmail_callback(code: str = None, state: str = None, error: str = None):
    """Handle Gmail OAuth callback"""
    try:
        if error:
            return RedirectResponse(url=f"https://radar-concerns-control-affect.trycloudflare.com?auth=error&service=gmail&message={error}")
        
        if not code:
            return RedirectResponse(url=f"https://radar-concerns-control-affect.trycloudflare.com?auth=error&service=gmail&message=no_code")
        
        # Extract session_id from state if available
        session_id = state.split('_')[0] if state and '_' in state else 'default'
        
        from gmail_oauth_service import GmailOAuthService
        gmail_service = GmailOAuthService()
        result = await gmail_service.handle_oauth_callback(code, session_id)
        
        if result.get('success'):
            return RedirectResponse(url=f"https://radar-concerns-control-affect.trycloudflare.com?auth=success&service=gmail&session_id={session_id}")
        else:
            return RedirectResponse(url=f"https://radar-concerns-control-affect.trycloudflare.com?auth=error&service=gmail&message=auth_failed&details={result.get('message', '')}")
            
    except Exception as e:
        return RedirectResponse(url=f"https://radar-concerns-control-affect.trycloudflare.com?auth=error&service=gmail&message=server_error&details={str(e)}")

@api_router.get("/gmail/profile")
async def get_gmail_profile(session_id: str = None):
    """Get real Gmail profile for authenticated user"""
    try:
        from gmail_oauth_service import GmailOAuthService
        gmail_service = GmailOAuthService()
        profile_result = await gmail_service.get_user_profile(session_id)
        return profile_result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Elva AI Preview",
        "version": "preview-mode",
        "architecture": "Hybrid Claude + Groq",
        "features": {
            "chat": "✅ Available",
            "intent_detection": "✅ Available (Mock)",
            "email_automation": "⚠️ Preview Mode",
            "linkedin_integration": "⚠️ Preview Mode",
            "gmail_oauth": "❌ Requires Setup",
            "database": "❌ Mock Data"
        }
    }

# Add API router to main app
app.include_router(api_router)

# Root redirect
@app.get("/")
async def root():
    """Redirect to health check"""
    return RedirectResponse(url="/api/health")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("preview_server:app", host="0.0.0.0", port=8000, reload=True)