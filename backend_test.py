#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Elva AI
Tests all backend functionality including Groq API integration, chat flow, and n8n webhook
"""

import requests
import json
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from frontend/.env
BACKEND_URL = "https://b7f8dd7e-fd4a-4694-b226-77b3ed7c9ae3.preview.emergentagent.com/api"

class ElvaBackendTester:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.test_results = []
        self.message_ids = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()

    def test_server_connectivity(self):
        """Test 1: Basic server connectivity"""
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "Elva AI Backend is running" in data.get("message", ""):
                    self.log_test("Server Connectivity", True, "Backend server is running and accessible")
                    return True
                else:
                    self.log_test("Server Connectivity", False, "Unexpected response message", data)
                    return False
            else:
                self.log_test("Server Connectivity", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Server Connectivity", False, f"Connection error: {str(e)}")
            return False

    def test_intent_detection_general_chat(self):
        """Test 2: Intent detection for general chat"""
        try:
            payload = {
                "message": "Hello, how are you today?",
                "session_id": self.session_id,
                "user_id": "test_user"
            }
            
            response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["id", "message", "response", "intent_data", "needs_approval", "timestamp"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Intent Detection - General Chat", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                # Check intent classification
                intent_data = data.get("intent_data", {})
                if intent_data.get("intent") != "general_chat":
                    self.log_test("Intent Detection - General Chat", False, f"Wrong intent: {intent_data.get('intent')}", data)
                    return False
                
                # Check needs_approval is False for general chat
                if data.get("needs_approval") != False:
                    self.log_test("Intent Detection - General Chat", False, "General chat should not need approval", data)
                    return False
                
                # Check response is not empty
                if not data.get("response") or len(data.get("response", "").strip()) == 0:
                    self.log_test("Intent Detection - General Chat", False, "Empty response from Groq", data)
                    return False
                
                self.message_ids.append(data["id"])
                self.log_test("Intent Detection - General Chat", True, f"Correctly classified as general_chat, response: {data['response'][:100]}...")
                return True
            else:
                self.log_test("Intent Detection - General Chat", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Intent Detection - General Chat", False, f"Error: {str(e)}")
            return False

    def test_intent_detection_send_email(self):
        """Test 3: Intent detection for send_email with pre-filled data"""
        try:
            payload = {
                "message": "Send an email to Sarah about the quarterly report",
                "session_id": self.session_id,
                "user_id": "test_user"
            }
            
            response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check intent classification
                intent_data = data.get("intent_data", {})
                if intent_data.get("intent") != "send_email":
                    self.log_test("Intent Detection - Send Email", False, f"Wrong intent: {intent_data.get('intent')}", data)
                    return False
                
                # Check needs_approval is True for action intents
                if data.get("needs_approval") != True:
                    self.log_test("Intent Detection - Send Email", False, "Email intent should need approval", data)
                    return False
                
                # Check intent data structure and pre-filled content
                expected_fields = ["recipient_name", "subject", "body"]
                intent_fields = list(intent_data.keys())
                missing_fields = [field for field in expected_fields if field not in intent_fields]
                
                if missing_fields:
                    self.log_test("Intent Detection - Send Email", False, f"Missing intent fields: {missing_fields}", intent_data)
                    return False
                
                # Check if recipient name was extracted and populated
                recipient_name = intent_data.get("recipient_name", "")
                if not recipient_name or recipient_name.strip() == "":
                    self.log_test("Intent Detection - Send Email", False, "recipient_name field is empty", intent_data)
                    return False
                
                # Check if subject was populated with meaningful content
                subject = intent_data.get("subject", "")
                if not subject or subject.strip() == "":
                    self.log_test("Intent Detection - Send Email", False, "subject field is empty", intent_data)
                    return False
                
                # Check if body was populated with meaningful content
                body = intent_data.get("body", "")
                if not body or body.strip() == "":
                    self.log_test("Intent Detection - Send Email", False, "body field is empty", intent_data)
                    return False
                
                self.message_ids.append(data["id"])
                self.log_test("Intent Detection - Send Email", True, f"Correctly classified as send_email with pre-filled data: recipient_name='{recipient_name}', subject='{subject[:50]}...', body populated")
                return True
            else:
                self.log_test("Intent Detection - Send Email", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Intent Detection - Send Email", False, f"Error: {str(e)}")
            return False

    def test_intent_detection_create_event(self):
        """Test 4: Intent detection for create_event with pre-filled data"""
        try:
            payload = {
                "message": "Create a meeting with the team for tomorrow at 2pm",
                "session_id": self.session_id,
                "user_id": "test_user"
            }
            
            response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check intent classification
                intent_data = data.get("intent_data", {})
                if intent_data.get("intent") != "create_event":
                    self.log_test("Intent Detection - Create Event", False, f"Wrong intent: {intent_data.get('intent')}", data)
                    return False
                
                # Check needs_approval is True
                if data.get("needs_approval") != True:
                    self.log_test("Intent Detection - Create Event", False, "Event intent should need approval", data)
                    return False
                
                # Check intent data structure and pre-filled content
                expected_fields = ["event_title", "date", "time", "participants"]
                intent_fields = list(intent_data.keys())
                missing_fields = [field for field in expected_fields if field not in intent_fields]
                
                if missing_fields:
                    self.log_test("Intent Detection - Create Event", False, f"Missing intent fields: {missing_fields}", intent_data)
                    return False
                
                # Check if event_title was populated with meaningful content
                event_title = intent_data.get("event_title", "")
                if not event_title or event_title.strip() == "":
                    self.log_test("Intent Detection - Create Event", False, "event_title field is empty", intent_data)
                    return False
                
                # Check if date was populated
                date = intent_data.get("date", "")
                if not date or date.strip() == "":
                    self.log_test("Intent Detection - Create Event", False, "date field is empty", intent_data)
                    return False
                
                # Check if time was populated
                time = intent_data.get("time", "")
                if not time or time.strip() == "":
                    self.log_test("Intent Detection - Create Event", False, "time field is empty", intent_data)
                    return False
                
                self.message_ids.append(data["id"])
                self.log_test("Intent Detection - Create Event", True, f"Correctly classified as create_event with pre-filled data: title='{event_title}', date='{date}', time='{time}'")
                return True
            else:
                self.log_test("Intent Detection - Create Event", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Intent Detection - Create Event", False, f"Error: {str(e)}")
            return False

    def test_intent_detection_add_todo(self):
        """Test 5: Intent detection for add_todo with pre-filled data"""
        try:
            payload = {
                "message": "Add finish the project to my todo list",
                "session_id": self.session_id,
                "user_id": "test_user"
            }
            
            response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check intent classification
                intent_data = data.get("intent_data", {})
                if intent_data.get("intent") != "add_todo":
                    self.log_test("Intent Detection - Add Todo", False, f"Wrong intent: {intent_data.get('intent')}", data)
                    return False
                
                # Check needs_approval is True
                if data.get("needs_approval") != True:
                    self.log_test("Intent Detection - Add Todo", False, "Todo intent should need approval", data)
                    return False
                
                # Check intent data structure and pre-filled content
                expected_fields = ["task"]
                intent_fields = list(intent_data.keys())
                missing_fields = [field for field in expected_fields if field not in intent_fields]
                
                if missing_fields:
                    self.log_test("Intent Detection - Add Todo", False, f"Missing intent fields: {missing_fields}", intent_data)
                    return False
                
                # Check if task was populated with meaningful content
                task = intent_data.get("task", "")
                if not task or task.strip() == "":
                    self.log_test("Intent Detection - Add Todo", False, "task field is empty", intent_data)
                    return False
                
                self.message_ids.append(data["id"])
                self.log_test("Intent Detection - Add Todo", True, f"Correctly classified as add_todo with pre-filled data: task='{task}'")
                return True
            else:
                self.log_test("Intent Detection - Add Todo", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Intent Detection - Add Todo", False, f"Error: {str(e)}")
            return False

    def test_intent_detection_set_reminder(self):
        """Test 6: Intent detection for set_reminder with pre-filled data"""
        try:
            payload = {
                "message": "Set a reminder to call mom at 5 PM today",
                "session_id": self.session_id,
                "user_id": "test_user"
            }
            
            response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check intent classification
                intent_data = data.get("intent_data", {})
                if intent_data.get("intent") != "set_reminder":
                    self.log_test("Intent Detection - Set Reminder", False, f"Wrong intent: {intent_data.get('intent')}", data)
                    return False
                
                # Check needs_approval is True
                if data.get("needs_approval") != True:
                    self.log_test("Intent Detection - Set Reminder", False, "Reminder intent should need approval", data)
                    return False
                
                # Check intent data structure and pre-filled content
                expected_fields = ["reminder_text"]
                intent_fields = list(intent_data.keys())
                missing_fields = [field for field in expected_fields if field not in intent_fields]
                
                if missing_fields:
                    self.log_test("Intent Detection - Set Reminder", False, f"Missing intent fields: {missing_fields}", intent_data)
                    return False
                
                # Check if reminder_text was populated with meaningful content
                reminder_text = intent_data.get("reminder_text", "")
                if not reminder_text or reminder_text.strip() == "":
                    self.log_test("Intent Detection - Set Reminder", False, "reminder_text field is empty", intent_data)
                    return False
                
                self.message_ids.append(data["id"])
                self.log_test("Intent Detection - Set Reminder", True, f"Correctly classified as set_reminder with pre-filled data: reminder_text='{reminder_text}'")
                return True
            else:
                self.log_test("Intent Detection - Set Reminder", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Intent Detection - Set Reminder", False, f"Error: {str(e)}")
            return False

    def test_approval_workflow_approved(self):
        """Test 7: Approval workflow - approved action"""
        if not self.message_ids:
            self.log_test("Approval Workflow - Approved", False, "No message IDs available for approval test")
            return False
            
        try:
            # Use the last message ID (should be an action intent)
            message_id = self.message_ids[-1]
            
            payload = {
                "session_id": self.session_id,
                "message_id": message_id,
                "approved": True
            }
            
            response = requests.post(f"{BACKEND_URL}/approve", json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if not data.get("success"):
                    self.log_test("Approval Workflow - Approved", False, "Success flag not set", data)
                    return False
                
                # Check if n8n_response is present (indicates webhook was called)
                if "n8n_response" not in data:
                    self.log_test("Approval Workflow - Approved", False, "No n8n_response in approval result", data)
                    return False
                
                self.log_test("Approval Workflow - Approved", True, f"Action approved and sent to n8n webhook")
                return True
            else:
                self.log_test("Approval Workflow - Approved", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Approval Workflow - Approved", False, f"Error: {str(e)}")
            return False

    def test_approval_workflow_rejected(self):
        """Test 8: Approval workflow - rejected action"""
        # First create a new action intent to reject
        try:
            payload = {
                "message": "Set a reminder to call mom at 5 PM today",
                "session_id": self.session_id,
                "user_id": "test_user"
            }
            
            response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=15)
            
            if response.status_code != 200:
                self.log_test("Approval Workflow - Rejected", False, "Failed to create reminder for rejection test")
                return False
            
            data = response.json()
            message_id = data["id"]
            
            # Now reject the action
            approval_payload = {
                "session_id": self.session_id,
                "message_id": message_id,
                "approved": False
            }
            
            approval_response = requests.post(f"{BACKEND_URL}/approve", json=approval_payload, timeout=15)
            
            if approval_response.status_code == 200:
                approval_data = approval_response.json()
                
                if not approval_data.get("success"):
                    self.log_test("Approval Workflow - Rejected", False, "Success flag not set for rejection", approval_data)
                    return False
                
                if "cancelled" not in approval_data.get("message", "").lower():
                    self.log_test("Approval Workflow - Rejected", False, "Rejection message not appropriate", approval_data)
                    return False
                
                self.log_test("Approval Workflow - Rejected", True, "Action correctly rejected")
                return True
            else:
                self.log_test("Approval Workflow - Rejected", False, f"HTTP {approval_response.status_code}", approval_response.text)
                return False
                
        except Exception as e:
            self.log_test("Approval Workflow - Rejected", False, f"Error: {str(e)}")
            return False

    def test_approval_workflow_edited_data(self):
        """Test 9: Approval workflow with edited data"""
        try:
            # Create an email intent
            payload = {
                "message": "Send email to sarah@company.com about the meeting",
                "session_id": self.session_id,
                "user_id": "test_user"
            }
            
            response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=15)
            
            if response.status_code != 200:
                self.log_test("Approval Workflow - Edited Data", False, "Failed to create email for edit test")
                return False
            
            data = response.json()
            message_id = data["id"]
            
            # Approve with edited data
            edited_data = {
                "intent": "send_email",
                "recipient_email": "sarah.updated@company.com",
                "subject": "Updated Meeting Information",
                "body": "This is the updated email content"
            }
            
            approval_payload = {
                "session_id": self.session_id,
                "message_id": message_id,
                "approved": True,
                "edited_data": edited_data
            }
            
            approval_response = requests.post(f"{BACKEND_URL}/approve", json=approval_payload, timeout=15)
            
            if approval_response.status_code == 200:
                approval_data = approval_response.json()
                
                if not approval_data.get("success"):
                    self.log_test("Approval Workflow - Edited Data", False, "Success flag not set", approval_data)
                    return False
                
                self.log_test("Approval Workflow - Edited Data", True, "Action approved with edited data")
                return True
            else:
                self.log_test("Approval Workflow - Edited Data", False, f"HTTP {approval_response.status_code}", approval_response.text)
                return False
                
        except Exception as e:
            self.log_test("Approval Workflow - Edited Data", False, f"Error: {str(e)}")
            return False

    def test_chat_history_retrieval(self):
        """Test 10: Chat history retrieval"""
        try:
            response = requests.get(f"{BACKEND_URL}/history/{self.session_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "messages" not in data:
                    self.log_test("Chat History - Retrieval", False, "No messages field in response", data)
                    return False
                
                messages = data["messages"]
                if not isinstance(messages, list):
                    self.log_test("Chat History - Retrieval", False, "Messages is not a list", data)
                    return False
                
                # Should have messages from our previous tests
                if len(messages) == 0:
                    self.log_test("Chat History - Retrieval", False, "No messages found in history")
                    return False
                
                # Check message structure
                first_message = messages[0]
                required_fields = ["id", "session_id", "message", "response", "timestamp"]
                missing_fields = [field for field in required_fields if field not in first_message]
                
                if missing_fields:
                    self.log_test("Chat History - Retrieval", False, f"Missing fields in message: {missing_fields}", first_message)
                    return False
                
                self.log_test("Chat History - Retrieval", True, f"Retrieved {len(messages)} messages from history")
                return True
            else:
                self.log_test("Chat History - Retrieval", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Chat History - Retrieval", False, f"Error: {str(e)}")
            return False

    def test_chat_history_clearing(self):
        """Test 11: Chat history clearing"""
        try:
            response = requests.delete(f"{BACKEND_URL}/history/{self.session_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get("success"):
                    self.log_test("Chat History - Clearing", False, "Success flag not set", data)
                    return False
                
                # Verify history is actually cleared
                verify_response = requests.get(f"{BACKEND_URL}/history/{self.session_id}", timeout=10)
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    messages = verify_data.get("messages", [])
                    
                    if len(messages) > 0:
                        self.log_test("Chat History - Clearing", False, f"History not cleared, still has {len(messages)} messages")
                        return False
                
                self.log_test("Chat History - Clearing", True, "Chat history successfully cleared")
                return True
            else:
                self.log_test("Chat History - Clearing", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Chat History - Clearing", False, f"Error: {str(e)}")
            return False

    def test_error_handling(self):
        """Test 12: Error handling scenarios"""
        try:
            # Test invalid message ID for approval
            payload = {
                "session_id": self.session_id,
                "message_id": "invalid-message-id",
                "approved": True
            }
            
            response = requests.post(f"{BACKEND_URL}/approve", json=payload, timeout=10)
            
            if response.status_code == 404:
                self.log_test("Error Handling - Invalid Message ID", True, "Correctly returned 404 for invalid message ID")
                return True
            else:
                self.log_test("Error Handling - Invalid Message ID", False, f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Error Handling - Invalid Message ID", False, f"Error: {str(e)}")
            return False

    def test_health_endpoint(self):
        """Test 13: Health endpoint functionality - Enhanced with Playwright Service"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields for enhanced system
                required_fields = ["status", "mongodb", "advanced_hybrid_ai_system", "n8n_webhook", "playwright_service"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Health Endpoint - Enhanced System", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                # Check status is healthy
                if data.get("status") != "healthy":
                    self.log_test("Health Endpoint - Enhanced System", False, f"Status not healthy: {data.get('status')}", data)
                    return False
                
                # Check MongoDB connection
                if data.get("mongodb") != "connected":
                    self.log_test("Health Endpoint - Enhanced System", False, f"MongoDB not connected: {data.get('mongodb')}", data)
                    return False
                
                # Check advanced hybrid AI system configuration
                hybrid_ai_system = data.get("advanced_hybrid_ai_system", {})
                
                # Check both Claude and Groq API keys are configured
                if hybrid_ai_system.get("groq_api_key") != "configured":
                    self.log_test("Health Endpoint - Enhanced System", False, "Groq API key not configured", data)
                    return False
                    
                if hybrid_ai_system.get("claude_api_key") != "configured":
                    self.log_test("Health Endpoint - Enhanced System", False, "Claude API key not configured", data)
                    return False
                
                # Check model configurations
                if hybrid_ai_system.get("groq_model") != "llama3-8b-8192":
                    self.log_test("Health Endpoint - Enhanced System", False, f"Wrong Groq model: {hybrid_ai_system.get('groq_model')}", data)
                    return False
                    
                if hybrid_ai_system.get("claude_model") != "claude-3-5-sonnet-20241022":
                    self.log_test("Health Endpoint - Enhanced System", False, f"Wrong Claude model: {hybrid_ai_system.get('claude_model')}", data)
                    return False
                
                # Check web automation task routing
                routing_models = hybrid_ai_system.get("routing_models", {})
                web_automation_tasks = routing_models.get("web_automation_tasks", [])
                
                expected_web_automation_intents = ["web_scraping", "linkedin_insights", "email_automation", "price_monitoring", "data_extraction"]
                missing_web_intents = [intent for intent in expected_web_automation_intents if intent not in web_automation_tasks]
                
                if missing_web_intents:
                    self.log_test("Health Endpoint - Enhanced System", False, f"Missing web automation intents: {missing_web_intents}", data)
                    return False
                
                # Check Playwright service configuration
                playwright_service = data.get("playwright_service", {})
                
                if playwright_service.get("status") != "available":
                    self.log_test("Health Endpoint - Enhanced System", False, f"Playwright service not available: {playwright_service.get('status')}", data)
                    return False
                
                expected_capabilities = ["dynamic_data_extraction", "linkedin_insights_scraping", "email_automation", "price_monitoring", "stealth_mode"]
                playwright_capabilities = playwright_service.get("capabilities", [])
                missing_capabilities = [cap for cap in expected_capabilities if cap not in playwright_capabilities]
                
                if missing_capabilities:
                    self.log_test("Health Endpoint - Enhanced System", False, f"Missing Playwright capabilities: {missing_capabilities}", data)
                    return False
                
                # Check N8N webhook
                if data.get("n8n_webhook") != "configured":
                    self.log_test("Health Endpoint - Enhanced System", False, "N8N webhook not configured", data)
                    return False
                
                self.log_test("Health Endpoint - Enhanced System", True, f"Enhanced system healthy: Claude + Groq + Playwright with web automation capabilities: {web_automation_tasks}")
                return True
            else:
                self.log_test("Health Endpoint - Enhanced System", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Health Endpoint - Enhanced System", False, f"Error: {str(e)}")
            return False

    def test_web_automation_intent_detection(self):
        """Test 14: Web automation intent detection"""
        test_cases = [
            {
                "message": "Scrape data from Wikipedia about artificial intelligence",
                "expected_intent": "web_scraping",
                "description": "Web scraping intent"
            },
            {
                "message": "Check my LinkedIn notifications and profile views",
                "expected_intent": "linkedin_insights", 
                "description": "LinkedIn insights intent"
            },
            {
                "message": "Automate my email checking for new messages",
                "expected_intent": "email_automation",
                "description": "Email automation intent"
            },
            {
                "message": "Monitor the price of iPhone 15 on Amazon",
                "expected_intent": "price_monitoring",
                "description": "Price monitoring intent"
            },
            {
                "message": "Extract product information from this e-commerce website",
                "expected_intent": "data_extraction",
                "description": "Data extraction intent"
            }
        ]
        
        all_passed = True
        results = []
        
        for test_case in test_cases:
            try:
                payload = {
                    "message": test_case["message"],
                    "session_id": self.session_id,
                    "user_id": "test_user"
                }
                
                response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    intent_data = data.get("intent_data", {})
                    detected_intent = intent_data.get("intent")
                    
                    if detected_intent == test_case["expected_intent"]:
                        results.append(f"✅ {test_case['description']}: {detected_intent}")
                        self.message_ids.append(data["id"])
                    else:
                        results.append(f"❌ {test_case['description']}: Expected {test_case['expected_intent']}, got {detected_intent}")
                        all_passed = False
                else:
                    results.append(f"❌ {test_case['description']}: HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                results.append(f"❌ {test_case['description']}: Error {str(e)}")
                all_passed = False
        
        result_summary = "\n    ".join(results)
        self.log_test("Web Automation Intent Detection", all_passed, result_summary)
        return all_passed

    def test_web_automation_endpoint_data_extraction(self):
        """Test 15: Web automation endpoint - Data extraction from public website"""
        try:
            # Test data extraction from a public website (Wikipedia)
            payload = {
                "session_id": self.session_id,
                "automation_type": "data_extraction",
                "parameters": {
                    "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
                    "selectors": {
                        "title": "h1.firstHeading",
                        "first_paragraph": "div.mw-parser-output > p:first-of-type",
                        "infobox_data": ".infobox"
                    },
                    "wait_for_element": "h1.firstHeading"
                }
            }
            
            response = requests.post(f"{BACKEND_URL}/web-automation", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["success", "data", "message", "execution_time", "automation_id"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Web Automation - Data Extraction", False, f"Missing response fields: {missing_fields}", data)
                    return False
                
                # Check if automation was successful
                if not data.get("success"):
                    self.log_test("Web Automation - Data Extraction", False, f"Automation failed: {data.get('message')}", data)
                    return False
                
                # Check if data was extracted
                extracted_data = data.get("data", {})
                if not extracted_data:
                    self.log_test("Web Automation - Data Extraction", False, "No data extracted", data)
                    return False
                
                # Check if expected fields are present in extracted data
                expected_fields = ["title", "first_paragraph"]
                found_fields = [field for field in expected_fields if field in extracted_data and extracted_data[field]]
                
                if len(found_fields) == 0:
                    self.log_test("Web Automation - Data Extraction", False, f"No expected data fields found. Got: {list(extracted_data.keys())}", data)
                    return False
                
                execution_time = data.get("execution_time", 0)
                self.log_test("Web Automation - Data Extraction", True, f"Successfully extracted data from Wikipedia. Fields: {found_fields}, Execution time: {execution_time:.2f}s")
                return True
            else:
                self.log_test("Web Automation - Data Extraction", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Web Automation - Data Extraction", False, f"Error: {str(e)}")
            return False

    def test_web_automation_endpoint_price_monitoring(self):
        """Test 16: Web automation endpoint - Price monitoring simulation"""
        try:
            # Test price monitoring with a mock e-commerce site structure
            payload = {
                "session_id": self.session_id,
                "automation_type": "price_monitoring",
                "parameters": {
                    "product_url": "https://example.com/product/test-item",
                    "price_selector": ".price, .cost, [data-price]",
                    "product_name": "Test Product"
                }
            }
            
            response = requests.post(f"{BACKEND_URL}/web-automation", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["success", "data", "message", "execution_time", "automation_id"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Web Automation - Price Monitoring", False, f"Missing response fields: {missing_fields}", data)
                    return False
                
                # For price monitoring, we expect it might fail due to the test URL, but the endpoint should handle it gracefully
                automation_id = data.get("automation_id")
                if not automation_id:
                    self.log_test("Web Automation - Price Monitoring", False, "No automation ID returned", data)
                    return False
                
                execution_time = data.get("execution_time", 0)
                success = data.get("success", False)
                message = data.get("message", "")
                
                # The test is successful if the endpoint processes the request properly (even if scraping fails due to test URL)
                if "automation_id" in data and execution_time >= 0:
                    self.log_test("Web Automation - Price Monitoring", True, f"Price monitoring endpoint working. Success: {success}, Message: {message}, Execution time: {execution_time:.2f}s")
                    return True
                else:
                    self.log_test("Web Automation - Price Monitoring", False, f"Invalid response structure", data)
                    return False
            else:
                self.log_test("Web Automation - Price Monitoring", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Web Automation - Price Monitoring", False, f"Error: {str(e)}")
            return False

    def test_web_automation_endpoint_linkedin_insights(self):
        """Test 17: Web automation endpoint - LinkedIn insights (without credentials)"""
        try:
            # Test LinkedIn insights endpoint without real credentials (should fail gracefully)
            payload = {
                "session_id": self.session_id,
                "automation_type": "linkedin_insights",
                "parameters": {
                    "email": "test@example.com",
                    "password": "test_password",
                    "insight_type": "notifications"
                }
            }
            
            response = requests.post(f"{BACKEND_URL}/web-automation", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["success", "data", "message", "execution_time", "automation_id"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Web Automation - LinkedIn Insights", False, f"Missing response fields: {missing_fields}", data)
                    return False
                
                # LinkedIn automation should fail with test credentials, but endpoint should handle it gracefully
                automation_id = data.get("automation_id")
                if not automation_id:
                    self.log_test("Web Automation - LinkedIn Insights", False, "No automation ID returned", data)
                    return False
                
                execution_time = data.get("execution_time", 0)
                success = data.get("success", False)
                message = data.get("message", "")
                
                # The test is successful if the endpoint processes the request properly
                if "automation_id" in data and execution_time >= 0:
                    self.log_test("Web Automation - LinkedIn Insights", True, f"LinkedIn insights endpoint working. Success: {success}, Message: {message}, Execution time: {execution_time:.2f}s")
                    return True
                else:
                    self.log_test("Web Automation - LinkedIn Insights", False, f"Invalid response structure", data)
                    return False
            else:
                self.log_test("Web Automation - LinkedIn Insights", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Web Automation - LinkedIn Insights", False, f"Error: {str(e)}")
            return False

    def test_web_automation_endpoint_email_automation(self):
        """Test 18: Web automation endpoint - Email automation (without credentials)"""
        try:
            # Test email automation endpoint without real credentials (should fail gracefully)
            payload = {
                "session_id": self.session_id,
                "automation_type": "email_automation",
                "parameters": {
                    "provider": "outlook",
                    "email": "test@example.com",
                    "password": "test_password",
                    "action": "check_inbox"
                }
            }
            
            response = requests.post(f"{BACKEND_URL}/web-automation", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["success", "data", "message", "execution_time", "automation_id"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Web Automation - Email Automation", False, f"Missing response fields: {missing_fields}", data)
                    return False
                
                # Email automation should fail with test credentials, but endpoint should handle it gracefully
                automation_id = data.get("automation_id")
                if not automation_id:
                    self.log_test("Web Automation - Email Automation", False, "No automation ID returned", data)
                    return False
                
                execution_time = data.get("execution_time", 0)
                success = data.get("success", False)
                message = data.get("message", "")
                
                # The test is successful if the endpoint processes the request properly
                if "automation_id" in data and execution_time >= 0:
                    self.log_test("Web Automation - Email Automation", True, f"Email automation endpoint working. Success: {success}, Message: {message}, Execution time: {execution_time:.2f}s")
                    return True
                else:
                    self.log_test("Web Automation - Email Automation", False, f"Invalid response structure", data)
                    return False
            else:
                self.log_test("Web Automation - Email Automation", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Web Automation - Email Automation", False, f"Error: {str(e)}")
            return False

    def test_web_automation_error_handling(self):
        """Test 19: Web automation error handling"""
        test_cases = [
            {
                "name": "Missing URL for web scraping",
                "payload": {
                    "session_id": self.session_id,
                    "automation_type": "web_scraping",
                    "parameters": {
                        "selectors": {"title": "h1"}
                    }
                },
                "expected_status": 400
            },
            {
                "name": "Missing credentials for LinkedIn",
                "payload": {
                    "session_id": self.session_id,
                    "automation_type": "linkedin_insights",
                    "parameters": {
                        "insight_type": "notifications"
                    }
                },
                "expected_status": 400
            },
            {
                "name": "Invalid automation type",
                "payload": {
                    "session_id": self.session_id,
                    "automation_type": "invalid_type",
                    "parameters": {}
                },
                "expected_status": 400
            }
        ]
        
        all_passed = True
        results = []
        
        for test_case in test_cases:
            try:
                response = requests.post(f"{BACKEND_URL}/web-automation", json=test_case["payload"], timeout=15)
                
                if response.status_code == test_case["expected_status"]:
                    results.append(f"✅ {test_case['name']}: Correctly returned {response.status_code}")
                else:
                    results.append(f"❌ {test_case['name']}: Expected {test_case['expected_status']}, got {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                results.append(f"❌ {test_case['name']}: Error {str(e)}")
                all_passed = False
        
        result_summary = "\n    ".join(results)
        self.log_test("Web Automation Error Handling", all_passed, result_summary)
        return all_passed

    def test_automation_history_endpoint(self):
        """Test 20: Automation history endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/automation-history/{self.session_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if "automation_history" not in data:
                    self.log_test("Automation History", False, "No automation_history field in response", data)
                    return False
                
                automation_history = data["automation_history"]
                if not isinstance(automation_history, list):
                    self.log_test("Automation History", False, "automation_history is not a list", data)
                    return False
                
                # Should have automation records from our previous tests
                if len(automation_history) > 0:
                    # Check automation record structure
                    first_record = automation_history[0]
                    required_fields = ["id", "session_id", "automation_type", "parameters", "result", "success", "message", "execution_time", "timestamp"]
                    missing_fields = [field for field in required_fields if field not in first_record]
                    
                    if missing_fields:
                        self.log_test("Automation History", False, f"Missing fields in automation record: {missing_fields}", first_record)
                        return False
                    
                    self.log_test("Automation History", True, f"Retrieved {len(automation_history)} automation records from history")
                else:
                    self.log_test("Automation History", True, "Automation history endpoint working (no records yet)")
                
                return True
            else:
                self.log_test("Automation History", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Automation History", False, f"Error: {str(e)}")
            return False

    def test_direct_web_scraping_execution(self):
        """Test 21: Direct web scraping execution through chat endpoint"""
        try:
            # Test direct execution of web scraping through chat endpoint
            payload = {
                "message": "Scrape the title from https://httpbin.org/html",
                "session_id": self.session_id,
                "user_id": "test_user"
            }
            
            response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if intent was detected as web_scraping
                intent_data = data.get("intent_data", {})
                if intent_data.get("intent") != "web_scraping":
                    self.log_test("Direct Web Scraping Execution", False, f"Wrong intent detected: {intent_data.get('intent')}", data)
                    return False
                
                # Check if URL was extracted
                if not intent_data.get("url"):
                    self.log_test("Direct Web Scraping Execution", False, "URL not extracted from message", intent_data)
                    return False
                
                # Check response for automation results
                response_text = data.get("response", "")
                
                # Look for automation results in response
                if "Web Scraping Results" in response_text or "automation_result" in intent_data:
                    # Direct execution happened
                    needs_approval = data.get("needs_approval", True)
                    if needs_approval == False:
                        self.log_test("Direct Web Scraping Execution", True, f"Direct web scraping executed successfully. URL: {intent_data.get('url')}")
                        return True
                    else:
                        self.log_test("Direct Web Scraping Execution", False, "Web scraping should not need approval when executed directly", data)
                        return False
                else:
                    # Check if it's pending approval (also valid)
                    needs_approval = data.get("needs_approval", False)
                    if needs_approval:
                        self.log_test("Direct Web Scraping Execution", True, f"Web scraping detected and pending approval. URL: {intent_data.get('url')}")
                        return True
                    else:
                        self.log_test("Direct Web Scraping Execution", False, "Web scraping intent not properly handled", data)
                        return False
            else:
                self.log_test("Direct Web Scraping Execution", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Direct Web Scraping Execution", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Elva AI Backend Testing")
        print("=" * 50)
        
        test_methods = [
            self.test_server_connectivity,
            self.test_intent_detection_general_chat,
            self.test_intent_detection_send_email,
            self.test_intent_detection_create_event,
            self.test_intent_detection_add_todo,
            self.test_intent_detection_set_reminder,
            self.test_approval_workflow_approved,
            self.test_approval_workflow_rejected,
            self.test_approval_workflow_edited_data,
            self.test_chat_history_retrieval,
            self.test_chat_history_clearing,
            self.test_error_handling,
            self.test_health_endpoint
        ]
        
        passed = 0
        failed = 0
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL - {test_method.__name__}: Unexpected error: {str(e)}")
                failed += 1
            
            # Small delay between tests
            time.sleep(0.5)
        
        print("=" * 50)
        print(f"🏁 Testing Complete!")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        return {
            "total_tests": len(test_methods),
            "passed": passed,
            "failed": failed,
            "success_rate": passed/(passed+failed)*100 if (passed+failed) > 0 else 0,
            "results": self.test_results
        }

if __name__ == "__main__":
    tester = ElvaBackendTester()
    results = tester.run_all_tests()
    
    # Save detailed results
    with open("/app/backend_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📝 Detailed results saved to: /app/backend_test_results.json")