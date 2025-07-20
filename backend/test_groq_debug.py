import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

load_dotenv()

async def test_groq_intent():
    # Initialize Groq LLM
    groq_llm = ChatOpenAI(
        temperature=0,
        openai_api_key=os.getenv("GROQ_API_KEY"),
        model="llama3-8b-8192",
        base_url="https://api.groq.com/openai/v1"
    )
    
    intent_prompt = """You are an AI assistant that detects user intent and extracts structured JSON.

CRITICAL: Respond with ONLY valid JSON, no additional text.

For "Send an email to Sarah about the meeting":
{
  "intent": "send_email",
  "recipient_name": "Sarah",
  "subject": "Meeting Update",
  "body": "Hi Sarah, I wanted to update you about our upcoming meeting."
}

For general chat:
{
  "intent": "general_chat",
  "message": "original message"
}

User input: Send an email to Sarah about the quarterly meeting"""

    prompt_template = ChatPromptTemplate.from_messages([
        ("user", intent_prompt)
    ])
    
    chain = prompt_template | groq_llm
    response = chain.invoke({})
    
    print("Raw Groq Response:")
    print(repr(response.content))
    print("\nFormatted Response:")
    print(response.content)

asyncio.run(test_groq_intent())