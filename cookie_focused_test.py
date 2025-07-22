#!/usr/bin/env python3
"""
Focused Cookie-Based Authentication System Testing for Elva AI
Tests only the new cookie management endpoints
"""

import requests
import json
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from frontend/.env
BACKEND_URL = "https://93401ecf-bdaa-45bb-b264-10122ad53902.preview.emergentagent.com/api"

class CookieSystemTester:
    def __init__(self):
        self.test_results = []
        
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

    def test_cookie_sessions_list(self):
        """Test 1: Cookie sessions list endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/cookie-sessions", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["sessions", "total"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Cookie Sessions - List", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                # Check sessions is a list
                sessions = data.get("sessions", [])
                if not isinstance(sessions, list):
                    self.log_test("Cookie Sessions - List", False, "Sessions is not a list", data)
                    return False
                
                # Check total count matches sessions length
                total = data.get("total", 0)
                if total != len(sessions):
                    self.log_test("Cookie Sessions - List", False, f"Total count {total} doesn't match sessions length {len(sessions)}", data)
                    return False
                
                self.log_test("Cookie Sessions - List", True, f"Retrieved {total} cookie sessions")
                return True
            else:
                self.log_test("Cookie Sessions - List", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Cookie Sessions - List", False, f"Error: {str(e)}")
            return False

    def test_cookie_session_status_check(self):
        """Test 2: Cookie session status check for non-existent user"""
        try:
            service_name = "linkedin"
            user_identifier = "test@example.com"
            
            response = requests.get(f"{BACKEND_URL}/cookie-sessions/{service_name}/{user_identifier}/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["has_valid_cookies", "cookie_count", "message"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Cookie Session Status Check", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                # For non-existent user, should return False
                has_valid_cookies = data.get("has_valid_cookies")
                if has_valid_cookies != False:
                    self.log_test("Cookie Session Status Check", False, f"Expected has_valid_cookies=False for non-existent user, got {has_valid_cookies}", data)
                    return False
                
                # Cookie count should be 0
                cookie_count = data.get("cookie_count", -1)
                if cookie_count != 0:
                    self.log_test("Cookie Session Status Check", False, f"Expected cookie_count=0 for non-existent user, got {cookie_count}", data)
                    return False
                
                # Message should indicate no cookies found
                message = data.get("message", "")
                if "No valid cookies found" not in message:
                    self.log_test("Cookie Session Status Check", False, f"Message doesn't indicate no cookies found: {message}", data)
                    return False
                
                self.log_test("Cookie Session Status Check", True, f"Correctly returned no cookies for {service_name} user {user_identifier}")
                return True
            else:
                self.log_test("Cookie Session Status Check", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Cookie Session Status Check", False, f"Error: {str(e)}")
            return False

    def test_cookie_session_delete_non_existent(self):
        """Test 3: Delete non-existent cookie session"""
        try:
            service_name = "gmail"
            user_identifier = "nonexistent@example.com"
            
            response = requests.delete(f"{BACKEND_URL}/cookie-sessions/{service_name}/{user_identifier}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["success", "message"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Cookie Session Delete - Non-existent", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                # Should return success=False for non-existent cookies
                success = data.get("success")
                if success != False:
                    self.log_test("Cookie Session Delete - Non-existent", False, f"Expected success=False for non-existent cookies, got {success}", data)
                    return False
                
                # Message should indicate cookies not found
                message = data.get("message", "")
                if "not found" not in message.lower():
                    self.log_test("Cookie Session Delete - Non-existent", False, f"Message doesn't indicate cookies not found: {message}", data)
                    return False
                
                self.log_test("Cookie Session Delete - Non-existent", True, f"Correctly handled deletion of non-existent cookies for {service_name} user {user_identifier}")
                return True
            else:
                self.log_test("Cookie Session Delete - Non-existent", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Cookie Session Delete - Non-existent", False, f"Error: {str(e)}")
            return False

    def test_cookie_cleanup_expired(self):
        """Test 4: Cleanup expired cookies"""
        try:
            response = requests.post(f"{BACKEND_URL}/cookie-sessions/cleanup", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["success", "message", "cleaned_count"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Cookie Cleanup - Expired", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                # Should return success=True
                success = data.get("success")
                if success != True:
                    self.log_test("Cookie Cleanup - Expired", False, f"Expected success=True, got {success}", data)
                    return False
                
                # Cleaned count should be a number
                cleaned_count = data.get("cleaned_count")
                if not isinstance(cleaned_count, int) or cleaned_count < 0:
                    self.log_test("Cookie Cleanup - Expired", False, f"Invalid cleaned_count: {cleaned_count}", data)
                    return False
                
                # Message should contain cleaned count
                message = data.get("message", "")
                if str(cleaned_count) not in message:
                    self.log_test("Cookie Cleanup - Expired", False, f"Message doesn't contain cleaned count: {message}", data)
                    return False
                
                self.log_test("Cookie Cleanup - Expired", True, f"Successfully cleaned up {cleaned_count} expired cookie sessions")
                return True
            else:
                self.log_test("Cookie Cleanup - Expired", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Cookie Cleanup - Expired", False, f"Error: {str(e)}")
            return False

    def test_health_endpoint_cookie_management(self):
        """Test 5: Health endpoint includes cookie management info"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if cookie_management section exists
                if "cookie_management" not in data:
                    self.log_test("Health Endpoint - Cookie Management", False, "No cookie_management section in health response", data)
                    return False
                
                cookie_management = data.get("cookie_management", {})
                
                # Check required cookie management fields
                required_fields = ["total_sessions", "valid_sessions", "services_with_cookies", "encryption"]
                missing_fields = [field for field in required_fields if field not in cookie_management]
                
                if missing_fields:
                    self.log_test("Health Endpoint - Cookie Management", False, f"Missing cookie management fields: {missing_fields}", cookie_management)
                    return False
                
                # Check field types
                total_sessions = cookie_management.get("total_sessions")
                if not isinstance(total_sessions, int) or total_sessions < 0:
                    self.log_test("Health Endpoint - Cookie Management", False, f"Invalid total_sessions: {total_sessions}", cookie_management)
                    return False
                
                valid_sessions = cookie_management.get("valid_sessions")
                if not isinstance(valid_sessions, int) or valid_sessions < 0:
                    self.log_test("Health Endpoint - Cookie Management", False, f"Invalid valid_sessions: {valid_sessions}", cookie_management)
                    return False
                
                services_with_cookies = cookie_management.get("services_with_cookies")
                if not isinstance(services_with_cookies, list):
                    self.log_test("Health Endpoint - Cookie Management", False, f"services_with_cookies is not a list: {services_with_cookies}", cookie_management)
                    return False
                
                encryption = cookie_management.get("encryption")
                if encryption != "enabled":
                    self.log_test("Health Endpoint - Cookie Management", False, f"Expected encryption=enabled, got {encryption}", cookie_management)
                    return False
                
                self.log_test("Health Endpoint - Cookie Management", True, f"Cookie management info present: {total_sessions} total sessions, {valid_sessions} valid, encryption enabled")
                return True
            else:
                self.log_test("Health Endpoint - Cookie Management", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Health Endpoint - Cookie Management", False, f"Error: {str(e)}")
            return False

    def test_linkedin_automation_missing_user_email(self):
        """Test 6: LinkedIn automation endpoint with missing user_email"""
        try:
            payload = {
                "insight_type": "notifications"
            }
            
            response = requests.post(f"{BACKEND_URL}/automation/linkedin-insights", json=payload, timeout=10)
            
            if response.status_code == 400:
                data = response.json()
                
                # Check error message mentions user_email is required
                detail = data.get("detail", "")
                if "user_email is required" not in detail:
                    self.log_test("LinkedIn Automation - Missing user_email", False, f"Error message doesn't mention user_email requirement: {detail}", data)
                    return False
                
                self.log_test("LinkedIn Automation - Missing user_email", True, "Correctly returned 400 error for missing user_email")
                return True
            else:
                self.log_test("LinkedIn Automation - Missing user_email", False, f"Expected 400, got {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("LinkedIn Automation - Missing user_email", False, f"Error: {str(e)}")
            return False

    def test_linkedin_automation_no_cookies(self):
        """Test 7: LinkedIn automation with no saved cookies"""
        try:
            payload = {
                "user_email": "test@example.com",
                "insight_type": "notifications"
            }
            
            response = requests.post(f"{BACKEND_URL}/automation/linkedin-insights", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["success", "message"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("LinkedIn Automation - No Cookies", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                # Should return success=False when no cookies found
                success = data.get("success")
                if success != False:
                    self.log_test("LinkedIn Automation - No Cookies", False, f"Expected success=False when no cookies found, got {success}", data)
                    return False
                
                # Message should indicate no cookies found and guide user
                message = data.get("message", "")
                if "No valid LinkedIn cookies found" not in message:
                    self.log_test("LinkedIn Automation - No Cookies", False, f"Message doesn't indicate no cookies found: {message}", data)
                    return False
                
                if "manual cookie capture" not in message:
                    self.log_test("LinkedIn Automation - No Cookies", False, f"Message doesn't guide user to capture cookies: {message}", data)
                    return False
                
                # Should have needs_login flag
                needs_login = data.get("needs_login")
                if needs_login != True:
                    self.log_test("LinkedIn Automation - No Cookies", False, f"Expected needs_login=True, got {needs_login}", data)
                    return False
                
                self.log_test("LinkedIn Automation - No Cookies", True, "Correctly handled missing LinkedIn cookies with user guidance")
                return True
            else:
                self.log_test("LinkedIn Automation - No Cookies", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("LinkedIn Automation - No Cookies", False, f"Error: {str(e)}")
            return False

    def test_email_automation_missing_parameters(self):
        """Test 8: Email automation endpoint with missing parameters"""
        try:
            # Test missing user_email
            payload = {
                "provider": "gmail",
                "action": "check_inbox"
            }
            
            response = requests.post(f"{BACKEND_URL}/automation/email-check", json=payload, timeout=10)
            
            if response.status_code == 400:
                data = response.json()
                
                # Check error message mentions required parameters
                detail = data.get("detail", "")
                if "user_email and provider are required" not in detail:
                    self.log_test("Email Automation - Missing Parameters", False, f"Error message doesn't mention required parameters: {detail}", data)
                    return False
                
                self.log_test("Email Automation - Missing Parameters", True, "Correctly returned 400 error for missing parameters")
                return True
            else:
                self.log_test("Email Automation - Missing Parameters", False, f"Expected 400, got {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Email Automation - Missing Parameters", False, f"Error: {str(e)}")
            return False

    def test_email_automation_no_cookies(self):
        """Test 9: Email automation with no saved cookies"""
        try:
            payload = {
                "user_email": "test@example.com",
                "provider": "outlook",
                "action": "check_inbox"
            }
            
            response = requests.post(f"{BACKEND_URL}/automation/email-check", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["success", "message"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Email Automation - No Cookies", False, f"Missing fields: {missing_fields}", data)
                    return False
                
                # Should return success=False when no cookies found
                success = data.get("success")
                if success != False:
                    self.log_test("Email Automation - No Cookies", False, f"Expected success=False when no cookies found, got {success}", data)
                    return False
                
                # Message should indicate no cookies found and guide user
                message = data.get("message", "")
                if "No valid outlook cookies found" not in message:
                    self.log_test("Email Automation - No Cookies", False, f"Message doesn't indicate no cookies found: {message}", data)
                    return False
                
                if "manual cookie capture" not in message:
                    self.log_test("Email Automation - No Cookies", False, f"Message doesn't guide user to capture cookies: {message}", data)
                    return False
                
                # Should have needs_login flag
                needs_login = data.get("needs_login")
                if needs_login != True:
                    self.log_test("Email Automation - No Cookies", False, f"Expected needs_login=True, got {needs_login}", data)
                    return False
                
                self.log_test("Email Automation - No Cookies", True, "Correctly handled missing email cookies with user guidance")
                return True
            else:
                self.log_test("Email Automation - No Cookies", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Email Automation - No Cookies", False, f"Error: {str(e)}")
            return False

    def run_cookie_tests(self):
        """Run all cookie-based authentication tests"""
        print("🍪 Starting Cookie-Based Authentication System Testing for Elva AI")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print()
        
        # Cookie management tests
        tests = [
            self.test_cookie_sessions_list,
            self.test_cookie_session_status_check,
            self.test_cookie_session_delete_non_existent,
            self.test_cookie_cleanup_expired,
            self.test_health_endpoint_cookie_management,
            self.test_linkedin_automation_missing_user_email,
            self.test_linkedin_automation_no_cookies,
            self.test_email_automation_missing_parameters,
            self.test_email_automation_no_cookies
        ]
        
        passed = 0
        failed = 0
        
        for test_method in tests:
            try:
                if test_method():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL - {test_method.__name__}")
                print(f"    Unexpected error: {str(e)}")
                failed += 1
        
        print("=" * 80)
        print(f"🎯 COOKIE AUTHENTICATION SYSTEM TEST RESULTS:")
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        
        if failed == 0:
            print("🎉 ALL COOKIE AUTHENTICATION TESTS PASSED!")
        else:
            print(f"⚠️  {failed} tests failed - check implementation")
        
        return passed, failed

if __name__ == "__main__":
    tester = CookieSystemTester()
    tester.run_cookie_tests()