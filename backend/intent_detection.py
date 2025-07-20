import os
import json
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

load_dotenv()
logger = logging.getLogger(__name__)

# Setup LLM connection (Groq + LLaMA3)
llm = ChatOpenAI(
    temperature=0,
    openai_api_key=os.getenv("GROQ_API_KEY"),
    model="llama3-8b-8192",
    base_url="https://api.groq.com/openai/v1"
)

# --- INTENT DETECTION PROMPT ---
intent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI assistant that detects user intent and extracts structured JSON for different tasks.

You can detect the following intents:
1. send_email
2. create_event
3. add_todo
4. set_reminder
5. linkedin_post
6. general_chat

IMPORTANT: For all intents except general_chat, you must populate ALL fields with realistic content based on the user's request. DO NOT leave fields empty unless absolutely no information can be inferred.

Return only valid JSON based on the examples below.

---- Examples ----

👉 send_email - ALWAYS populate recipient_name, subject, and body:
{{
  "intent": "send_email",
  "recipient_name": "John Smith",
  "recipient_email": "john.smith@company.com",
  "subject": "Project Status Update",
  "body": "Hi John,\n\nI wanted to provide you with an update on the current project status. We've made significant progress and are on track to meet our deadline.\n\nBest regards"
}}

👉 create_event - ALWAYS populate event_title, date, time:
{{
  "intent": "create_event",
  "event_title": "Team Meeting",
  "date": "2024-01-15",
  "time": "10:00 AM",
  "participants": ["team@company.com", "manager@company.com"],
  "location": "Conference Room A"
}}

👉 add_todo - ALWAYS populate task:
{{
  "intent": "add_todo",
  "task": "Complete quarterly report and submit to management",
  "due_date": "2024-01-20"
}}

👉 set_reminder - ALWAYS populate reminder_text:
{{
  "intent": "set_reminder",
  "reminder_text": "Call client about contract renewal",
  "reminder_time": "2:00 PM",
  "reminder_date": "tomorrow"
}}

👉 linkedin_post - ALWAYS populate topic and post_content:
{{
  "intent": "linkedin_post",
  "topic": "Artificial Intelligence in Business",
  "category": "Technology",
  "post_content": "Excited to share insights on how AI is transforming business operations. The future of work is here! #AI #Technology #Business"
}}

👉 general_chat:
{{
  "intent": "general_chat",
  "message": "original user message"
}}

RULES:
- If user mentions a specific person's name, use it for recipient_name
- If no email is mentioned, leave recipient_email empty but fill other fields
- Generate realistic, professional content for email body, event details, etc.
- Infer reasonable dates/times if not specified (e.g., "tomorrow", "next week", "2:00 PM")
- For participants, include relevant stakeholders based on context
"""),
    ("user", "{input}")
])

# --- FRIENDLY DRAFT PROMPT ---
friendly_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a friendly assistant that converts structured intent data into human-friendly messages.

Respond based on intent type:

- send_email → Draft a friendly email
- linkedin_post → Draft a professional LinkedIn post
- create_event / add_todo / set_reminder → Summarize task or reminder
- general_chat → Return the user message

Return plain text.

Examples:

Input: {{"intent": "send_email", "recipient_name": "Priya", "subject": "AI Update", "body": "Here's the latest..."}}
Output: ✉️ Here's a draft email to Priya:
Subject: AI Update
Body: Here's the latest...

Input: {{"intent": "set_reminder", "reminder_text": "Meeting with HR", "reminder_time": "10 AM", "reminder_date": "tomorrow"}}
Output: ⏰ I'll remind you about "Meeting with HR" at 10 AM tomorrow.
"""),
    ("user", "{input_json}")
])

# --- GENERAL CHAT PROMPT ---
general_chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are Elva AI – a friendly and helpful assistant."),
    ("user", "{input}")
])

def detect_intent(user_input: str) -> dict:
    try:
        chain = intent_prompt | llm
        response = chain.invoke({"input": user_input})
        logger.info(f"LLM response for intent detection: {response.content}")
        
        # Extract JSON from the response (LLM might add extra text)
        content = response.content.strip()
        
        # Find the first { and last } to extract JSON
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = content[start_idx:end_idx + 1]
            
            # Clean up common JSON issues
            json_str = json_str.replace('\n', '\\n')  # Escape newlines
            json_str = json_str.replace('\r', '\\r')  # Escape carriage returns
            json_str = json_str.replace('\t', '\\t')  # Escape tabs
            json_str = json_str.replace('\b', '\\b')  # Escape backspaces
            json_str = json_str.replace('\f', '\\f')  # Escape form feeds
            
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as json_err:
                logger.error(f"JSON decode error: {json_err}")
                logger.error(f"Problematic JSON: {json_str}")
                
                # Try to fix common issues and retry
                # Remove any remaining control characters
                import re
                json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
                
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    # If still failing, treat as general chat
                    return {
                        "intent": "general_chat",
                        "message": user_input,
                        "error": f"JSON parsing failed: {str(json_err)}"
                    }
        else:
            # If no JSON found, treat as general chat
            return {
                "intent": "general_chat",
                "message": user_input
            }
            
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
    from datetime import datetime
    return {
        "user_id": user_id,
        "session_id": session_id,
        "intent": intent_data.get("intent"),
        "data": intent_data,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }