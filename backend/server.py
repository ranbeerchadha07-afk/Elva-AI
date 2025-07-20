from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import json
import httpx
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Setup LLM connection (Groq + LLaMA3)
llm = ChatOpenAI(
    temperature=0,
    openai_api_key=os.getenv("GROQ_API_KEY", "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"),
    model="llama3-8b-8192",
    base_url="https://api.groq.com/openai/v1"
)

# N8N webhook URL
N8N_WEBHOOK_URL = "https://kumararpit9468.app.n8n.cloud/webhook/elva-entry"

# Intent detection prompt
intent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI assistant that detects user intent and extracts structured JSON for different tasks.

You can detect the following intents:
1. send_email
2. create_event
3. add_todo
4. set_reminder
5. linkedin_post
6. general_chat

Return only valid JSON based on the examples below.

---- Examples ----

👉 send_email:
{{
  "intent": "send_email",
  "recipient_name": "",
  "recipient_email": "",
  "subject": "",
  "body": ""
}}

👉 create_event:
{{
  "intent": "create_event",
  "event_title": "",
  "date": "",
  "time": "",
  "participants": [],
  "location": ""
}}

👉 add_todo:
{{
  "intent": "add_todo",
  "task": "",
  "due_date": ""
}}

👉 set_reminder:
{{
  "intent": "set_reminder",
  "reminder_text": "",
  "reminder_time": "",
  "reminder_date": ""
}}

👉 linkedin_post:
{{
  "intent": "linkedin_post",
  "topic": "",
  "category": "",
  "post_content": ""
}}

👉 general_chat:
{{
  "intent": "general_chat",
  "message": "original user message"
}}
"""),
    ("user", "{input}")
])

# Friendly draft prompt
friendly_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a friendly assistant that converts structured intent data into human-friendly messages.

Respond based on intent type:

- send_email → Draft a friendly email
- linkedin_post → Draft a professional LinkedIn post
- create_event / add_todo / set_reminder → Summarize task or reminder
- general_chat → Return the user message

Return plain text.

Examples:

Input: {"intent": "send_email", "recipient_name": "Priya", "subject": "AI Update", "body": "Here's the latest..."}
Output: ✉️ Here's a draft email to Priya:
Subject: AI Update
Body: Here's the latest...

Input: {"intent": "set_reminder", "reminder_text": "Meeting with HR", "reminder_time": "10 AM", "reminder_date": "tomorrow"}
Output: ⏰ I'll remind you about "Meeting with HR" at 10 AM tomorrow.
"""),
    ("user", "{input_json}")
])

# General chat prompt
general_chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are Elva AI – a friendly and helpful assistant."),
    ("user", "{input}")
])

# Models
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str = "default_user"
    message: str
    response: str
    intent_data: Optional[dict] = None
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

# Helper functions
def convert_objectid_to_str(doc):
    """Convert MongoDB ObjectId to string for JSON serialization"""
    if isinstance(doc, dict):
        for key, value in doc.items():
            if hasattr(value, '__dict__') and hasattr(value, 'binary'):
                # This is likely an ObjectId
                doc[key] = str(value)
            elif isinstance(value, dict):
                doc[key] = convert_objectid_to_str(value)
            elif isinstance(value, list):
                doc[key] = [convert_objectid_to_str(item) if isinstance(item, dict) else item for item in value]
    return doc

def detect_intent(user_input: str) -> dict:
    try:
        chain = intent_prompt | llm
        response = chain.invoke({"input": user_input})
        logger.info(f"LLM response for intent detection: {response.content}")
        return json.loads(response.content)
    except Exception as e:
        logger.error(f"Intent detection error: {e}")
        return {
            "intent": "general_chat",
            "message": user_input,
            "error": str(e)
        }

def generate_friendly_draft(intent_data: dict) -> str:
    try:
        chain = friendly_prompt | llm
        response = chain.invoke({"input_json": json.dumps(intent_data)})
        return response.content
    except Exception as e:
        logger.error(f"Draft generation error: {e}")
        return "⚠️ Could not generate a friendly message."

def handle_general_chat(user_input: str) -> str:
    try:
        chain = general_chat_prompt | llm
        response = chain.invoke({"input": user_input})
        return response.content
    except Exception as e:
        return "🤖 Sorry, I couldn't answer that."

def format_intent_for_webhook(intent_data: dict, user_id: str, session_id: str) -> dict:
    return {
        "user_id": user_id,
        "session_id": session_id,
        "intent": intent_data.get("intent"),
        "data": intent_data,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

async def send_to_n8n(webhook_data: dict) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(N8N_WEBHOOK_URL, json=webhook_data)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"N8N webhook error: {e}")
        return {"error": str(e), "success": False}

# Routes
@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Detect intent
        intent_data = detect_intent(request.message)
        
        # Handle general chat directly
        if intent_data.get("intent") == "general_chat":
            response_text = handle_general_chat(request.message)
            
            # Save to database
            chat_msg = ChatMessage(
                session_id=request.session_id,
                user_id=request.user_id,
                message=request.message,
                response=response_text,
                intent_data=intent_data
            )
            await db.chat_messages.insert_one(chat_msg.dict())
            
            return ChatResponse(
                id=chat_msg.id,
                message=request.message,
                response=response_text,
                intent_data=intent_data,
                needs_approval=False,
                timestamp=chat_msg.timestamp
            )
        
        # Generate friendly draft for other intents
        draft_response = generate_friendly_draft(intent_data)
        
        # Save to database
        chat_msg = ChatMessage(
            session_id=request.session_id,
            user_id=request.user_id,
            message=request.message,
            response=draft_response,
            intent_data=intent_data
        )
        await db.chat_messages.insert_one(chat_msg.dict())
        
        return ChatResponse(
            id=chat_msg.id,
            message=request.message,
            response=draft_response,
            intent_data=intent_data,
            needs_approval=True,
            timestamp=chat_msg.timestamp
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/approve")
async def approve_action(request: ApprovalRequest):
    try:
        # Get the message from database
        message = await db.chat_messages.find_one({"id": request.message_id})
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        if not request.approved:
            return {"success": True, "message": "Action cancelled"}
        
        # Use edited data if provided, otherwise use original intent data
        final_data = request.edited_data if request.edited_data else message["intent_data"]
        
        # Format for n8n webhook
        webhook_data = format_intent_for_webhook(
            final_data, 
            message["user_id"], 
            message["session_id"]
        )
        
        # Send to n8n
        n8n_response = await send_to_n8n(webhook_data)
        
        # Update message in database with approval status
        await db.chat_messages.update_one(
            {"id": request.message_id},
            {"$set": {"approved": request.approved, "n8n_response": n8n_response}}
        )
        
        return {
            "success": True,
            "message": "Action executed successfully!",
            "n8n_response": n8n_response
        }
        
    except Exception as e:
        logger.error(f"Approval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    try:
        messages = await db.chat_messages.find(
            {"session_id": session_id}
        ).sort("timestamp", 1).to_list(1000)
        
        # Convert ObjectIds to strings for JSON serialization
        serializable_messages = [convert_objectid_to_str(msg) for msg in messages]
        
        return {"messages": serializable_messages}
    except Exception as e:
        logger.error(f"History error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    try:
        await db.chat_messages.delete_many({"session_id": session_id})
        return {"success": True, "message": "Chat history cleared"}
    except Exception as e:
        logger.error(f"Clear history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/")
async def root():
    return {"message": "Elva AI Backend is running! 🤖✨"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()