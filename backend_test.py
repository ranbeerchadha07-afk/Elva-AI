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
BACKEND_URL = "https://9816ab7e-1989-433b-aa5b-8094d21fd269.preview.emergentagent.com/api"

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

    def test_approval_workflow_approved(self):
        """Test 6: Approval workflow - approved action"""
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
        """Test 7: Approval workflow - rejected action"""
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
        """Test 8: Approval workflow with edited data"""
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
        """Test 9: Chat history retrieval"""
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
        """Test 10: Chat history clearing"""
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
        """Test 11: Error handling scenarios"""
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
            self.test_approval_workflow_approved,
            self.test_approval_workflow_rejected,
            self.test_approval_workflow_edited_data,
            self.test_chat_history_retrieval,
            self.test_chat_history_clearing,
            self.test_error_handling
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