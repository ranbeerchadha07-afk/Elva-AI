#!/usr/bin/env python3
"""
Direct Automation Testing for Enhanced Elva AI
Tests the new direct automation flow specifically
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Use localhost for testing
BACKEND_URL = "http://localhost:8001/api"

class DirectAutomationTester:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data=None):
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
            print(f"    Response: {json.dumps(response_data, indent=2)[:200]}...")
        print()

    def test_server_connectivity(self):
        """Test basic server connectivity"""
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "Elva AI Backend" in data.get("message", ""):
                    self.log_test("Server Connectivity", True, "Backend server accessible")
                    return True
                else:
                    self.log_test("Server Connectivity", False, "Unexpected response", data)
                    return False
            else:
                self.log_test("Server Connectivity", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Server Connectivity", False, f"Connection error: {str(e)}")
            return False

    def test_direct_automation_intents(self):
        """Test direct automation intents detection and processing"""
        direct_automation_test_cases = [
            {
                "message": "Check my LinkedIn notifications",
                "expected_intent": "check_linkedin_notifications",
                "description": "LinkedIn notifications check"
            },
            {
                "message": "What's the current price of laptop on Amazon?",
                "expected_intent": "scrape_price",
                "description": "Price scraping"
            },
            {
                "message": "Scrape new laptop listings from Flipkart",
                "expected_intent": "scrape_product_listings",
                "description": "Product listings scraping"
            },
            {
                "message": "Check LinkedIn job alerts for software engineer positions",
                "expected_intent": "linkedin_job_alerts",
                "description": "LinkedIn job alerts"
            },
            {
                "message": "Check for updates on TechCrunch website",
                "expected_intent": "check_website_updates",
                "description": "Website updates monitoring"
            },
            {
                "message": "Monitor competitor pricing for Apple products",
                "expected_intent": "monitor_competitors",
                "description": "Competitor monitoring"
            },
            {
                "message": "Scrape latest AI news articles from tech blogs",
                "expected_intent": "scrape_news_articles",
                "description": "News articles scraping"
            }
        ]
        
        all_passed = True
        results = []
        
        for test_case in direct_automation_test_cases:
            try:
                payload = {
                    "message": test_case["message"],
                    "session_id": self.session_id,
                    "user_id": "test_user"
                }
                
                response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    intent_data = data.get("intent_data", {})
                    detected_intent = intent_data.get("intent")
                    
                    # Check intent detection
                    if detected_intent == test_case["expected_intent"]:
                        # Check direct automation flags
                        needs_approval = data.get("needs_approval", True)
                        has_automation_result = "automation_result" in intent_data
                        has_automation_success = "automation_success" in intent_data
                        has_execution_time = "execution_time" in intent_data
                        has_direct_automation_flag = intent_data.get("direct_automation", False)
                        
                        if (not needs_approval and has_automation_result and 
                            has_automation_success and has_execution_time and has_direct_automation_flag):
                            results.append(f"✅ {test_case['description']}: Direct automation working - {detected_intent}")
                        else:
                            results.append(f"❌ {test_case['description']}: Missing direct automation flags - needs_approval: {needs_approval}, automation_result: {has_automation_result}, automation_success: {has_automation_success}, execution_time: {has_execution_time}, direct_automation: {has_direct_automation_flag}")
                            all_passed = False
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
        self.log_test("Direct Automation Intents", all_passed, result_summary)
        return all_passed

    def test_automation_status_endpoint(self):
        """Test automation status endpoint"""
        direct_automation_intents = [
            "check_linkedin_notifications",
            "scrape_price", 
            "scrape_product_listings",
            "linkedin_job_alerts",
            "check_website_updates",
            "monitor_competitors",
            "scrape_news_articles"
        ]
        
        all_passed = True
        results = []
        
        for intent in direct_automation_intents:
            try:
                response = requests.get(f"{BACKEND_URL}/automation-status/{intent}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check response structure
                    required_fields = ["intent", "status_message", "is_direct_automation", "timestamp"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        results.append(f"❌ {intent}: Missing fields {missing_fields}")
                        all_passed = False
                    elif data.get("is_direct_automation") != True:
                        results.append(f"❌ {intent}: is_direct_automation should be True, got {data.get('is_direct_automation')}")
                        all_passed = False
                    elif not data.get("status_message"):
                        results.append(f"❌ {intent}: Empty status_message")
                        all_passed = False
                    else:
                        results.append(f"✅ {intent}: Status endpoint working")
                else:
                    results.append(f"❌ {intent}: HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                results.append(f"❌ {intent}: Error {str(e)}")
                all_passed = False
        
        result_summary = "\n    ".join(results)
        self.log_test("Automation Status Endpoint", all_passed, result_summary)
        return all_passed

    def test_direct_automation_response_format(self):
        """Test direct automation response format verification"""
        try:
            # Test with a direct automation intent
            payload = {
                "message": "Check my LinkedIn notifications",
                "session_id": self.session_id,
                "user_id": "test_user"
            }
            
            response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                intent_data = data.get("intent_data", {})
                
                # Check all required fields for direct automation
                required_fields = {
                    "automation_result": "Automation result data",
                    "automation_success": "Success flag",
                    "execution_time": "Execution time",
                    "direct_automation": "Direct automation flag"
                }
                
                missing_fields = []
                for field, description in required_fields.items():
                    if field not in intent_data:
                        missing_fields.append(f"{field} ({description})")
                
                if missing_fields:
                    self.log_test("Direct Automation Response Format", False, f"Missing fields: {', '.join(missing_fields)}", data)
                    return False
                
                # Check needs_approval is False
                if data.get("needs_approval") != False:
                    self.log_test("Direct Automation Response Format", False, f"needs_approval should be False, got {data.get('needs_approval')}", data)
                    return False
                
                # Check response contains automation result
                response_text = data.get("response", "")
                if "LinkedIn Notifications" not in response_text:
                    self.log_test("Direct Automation Response Format", False, "Response doesn't contain automation result", data)
                    return False
                
                # Check execution time is reasonable
                execution_time = intent_data.get("execution_time", 0)
                if execution_time <= 0 or execution_time > 30:
                    self.log_test("Direct Automation Response Format", False, f"Unreasonable execution time: {execution_time}s", data)
                    return False
                
                self.log_test("Direct Automation Response Format", True, f"All required fields present, execution_time: {execution_time}s, automation_success: {intent_data.get('automation_success')}")
                return True
            else:
                self.log_test("Direct Automation Response Format", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Direct Automation Response Format", False, f"Error: {str(e)}")
            return False

    def test_traditional_vs_direct_automation(self):
        """Test traditional automation vs direct automation flow"""
        try:
            # Test traditional automation (should need approval)
            traditional_payload = {
                "message": "Scrape data from Wikipedia about artificial intelligence",
                "session_id": self.session_id,
                "user_id": "test_user"
            }
            
            traditional_response = requests.post(f"{BACKEND_URL}/chat", json=traditional_payload, timeout=30)
            
            if traditional_response.status_code != 200:
                self.log_test("Traditional vs Direct Automation", False, "Traditional automation request failed")
                return False
            
            traditional_data = traditional_response.json()
            
            # Test direct automation (should not need approval)
            direct_payload = {
                "message": "Check my LinkedIn notifications",
                "session_id": self.session_id,
                "user_id": "test_user"
            }
            
            direct_response = requests.post(f"{BACKEND_URL}/chat", json=direct_payload, timeout=30)
            
            if direct_response.status_code != 200:
                self.log_test("Traditional vs Direct Automation", False, "Direct automation request failed")
                return False
            
            direct_data = direct_response.json()
            
            # Compare the responses
            traditional_needs_approval = traditional_data.get("needs_approval", False)
            direct_needs_approval = direct_data.get("needs_approval", True)
            
            traditional_has_automation_result = "automation_result" in traditional_data.get("intent_data", {})
            direct_has_automation_result = "automation_result" in direct_data.get("intent_data", {})
            
            # Traditional should need approval, direct should not
            if traditional_needs_approval and not direct_needs_approval:
                if not traditional_has_automation_result and direct_has_automation_result:
                    self.log_test("Traditional vs Direct Automation", True, 
                                f"Traditional: needs_approval={traditional_needs_approval}, has_result={traditional_has_automation_result}; "
                                f"Direct: needs_approval={direct_needs_approval}, has_result={direct_has_automation_result}")
                    return True
                else:
                    self.log_test("Traditional vs Direct Automation", False, 
                                f"Automation result flags incorrect - Traditional: {traditional_has_automation_result}, Direct: {direct_has_automation_result}")
                    return False
            else:
                self.log_test("Traditional vs Direct Automation", False, 
                            f"Approval flags incorrect - Traditional: {traditional_needs_approval}, Direct: {direct_needs_approval}")
                return False
                
        except Exception as e:
            self.log_test("Traditional vs Direct Automation", False, f"Error: {str(e)}")
            return False

    def run_direct_automation_tests(self):
        """Run direct automation specific tests"""
        print("🚀 Starting Enhanced Direct Automation Testing for Elva AI")
        print("=" * 70)
        
        tests = [
            self.test_server_connectivity,
            self.test_direct_automation_intents,
            self.test_automation_status_endpoint,
            self.test_direct_automation_response_format,
            self.test_traditional_vs_direct_automation
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_test(test.__name__, False, f"Test execution error: {str(e)}")
                failed += 1
            
            # Small delay between tests
            time.sleep(1)
        
        print("=" * 70)
        print(f"🎯 DIRECT AUTOMATION TESTING COMPLETE!")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed == 0:
            print("🎉 ALL DIRECT AUTOMATION TESTS PASSED! Enhanced automation flow working perfectly!")
        else:
            print(f"⚠️  {failed} tests failed. Please check the details above.")
        
        return {
            "total_tests": len(tests),
            "passed": passed,
            "failed": failed,
            "success_rate": passed/(passed+failed)*100 if (passed+failed) > 0 else 0,
            "results": self.test_results
        }

if __name__ == "__main__":
    tester = DirectAutomationTester()
    results = tester.run_direct_automation_tests()
    
    # Save detailed results
    with open("/app/direct_automation_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📝 Detailed results saved to: /app/direct_automation_test_results.json")