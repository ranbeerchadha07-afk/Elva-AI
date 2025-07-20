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
            return json.loads(json_str)
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