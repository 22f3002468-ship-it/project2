#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test suite for LLM Analysis Quiz endpoint.

Tests all cases to ensure full score:
1. Invalid JSON → 400
2. Invalid secret → 403
3. Valid request → 200
4. Missing fields → 400
5. Health check → 200
"""

import json
import sys
import time
from typing import Dict, Any, Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Install it with: pip install requests")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_test(name: str):
    """Print test header."""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}TEST: {name}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")


def print_pass(message: str):
    """Print pass message."""
    print(f"{Colors.GREEN}✓ PASS: {message}{Colors.RESET}")


def print_fail(message: str):
    """Print fail message."""
    print(f"{Colors.RED}✗ FAIL: {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message."""
    print(f"{Colors.YELLOW}ℹ INFO: {message}{Colors.RESET}")


class EndpointTester:
    """Comprehensive endpoint tester."""
    
    def __init__(self, base_url: str, email: str, secret: str):
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.secret = secret
        self.passed = 0
        self.failed = 0
    
    def test_health_check(self) -> bool:
        """Test health check endpoint."""
        print_test("Health Check")
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                if "status" in data and data["status"] == "ok":
                    print_pass("Health check returns 200 with status='ok'")
                    return True
                else:
                    print_fail(f"Health check response missing 'status': {data}")
                    return False
            else:
                print_fail(f"Health check returned {resp.status_code}, expected 200")
                return False
        except Exception as e:
            print_fail(f"Health check failed: {e}")
            return False
    
    def test_invalid_json(self) -> bool:
        """Test invalid JSON → 400."""
        print_test("Invalid JSON → 400")
        try:
            # Send malformed JSON
            resp = requests.post(
                f"{self.base_url}/",
                data="this is not json",
                headers={"Content-Type": "application/json"},
                timeout=5.0
            )
            if resp.status_code == 400:
                print_pass("Invalid JSON correctly returns 400")
                return True
            else:
                print_fail(f"Expected 400, got {resp.status_code}: {resp.text[:200]}")
                return False
        except Exception as e:
            print_fail(f"Test failed: {e}")
            return False
    
    def test_missing_fields(self) -> bool:
        """Test missing required fields → 400."""
        print_test("Missing Required Fields → 400")
        test_cases = [
            ({}, "Empty payload"),
            ({"email": self.email}, "Missing secret and url"),
            ({"secret": self.secret}, "Missing email and url"),
            ({"url": "https://example.com"}, "Missing email and secret"),
            ({"email": self.email, "secret": self.secret}, "Missing url"),
            ({"email": self.email, "url": "https://example.com"}, "Missing secret"),
            ({"secret": self.secret, "url": "https://example.com"}, "Missing email"),
        ]
        
        all_passed = True
        for payload, description in test_cases:
            try:
                resp = requests.post(
                    f"{self.base_url}/",
                    json=payload,
                    timeout=5.0
                )
                if resp.status_code == 400:
                    print_pass(f"{description} → 400")
                else:
                    print_fail(f"{description} → {resp.status_code} (expected 400)")
                    all_passed = False
            except Exception as e:
                print_fail(f"{description} test failed: {e}")
                all_passed = False
        
        return all_passed
    
    def test_invalid_secret(self) -> bool:
        """Test invalid secret → 403."""
        print_test("Invalid Secret → 403")
        test_cases = [
            ("wrong-secret", "Wrong secret"),
            ("", "Empty secret"),
            (" " * 10, "Whitespace secret"),
        ]
        
        all_passed = True
        for wrong_secret, description in test_cases:
            try:
                payload = {
                    "email": self.email,
                    "secret": wrong_secret,
                    "url": "https://example.com/quiz-123"
                }
                resp = requests.post(
                    f"{self.base_url}/",
                    json=payload,
                    timeout=5.0
                )
                if resp.status_code == 403:
                    print_pass(f"{description} → 403")
                else:
                    print_fail(f"{description} → {resp.status_code} (expected 403)")
                    all_passed = False
            except Exception as e:
                print_fail(f"{description} test failed: {e}")
                all_passed = False
        
        return all_passed
    
    def test_invalid_url_format(self) -> bool:
        """Test invalid URL format → 400."""
        print_test("Invalid URL Format → 400")
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "just-text",
            "",
        ]
        
        all_passed = True
        for invalid_url in invalid_urls:
            try:
                payload = {
                    "email": self.email,
                    "secret": self.secret,
                    "url": invalid_url
                }
                resp = requests.post(
                    f"{self.base_url}/",
                    json=payload,
                    timeout=5.0
                )
                if resp.status_code == 400:
                    print_pass(f"Invalid URL '{invalid_url}' → 400")
                else:
                    print_fail(f"Invalid URL '{invalid_url}' → {resp.status_code} (expected 400)")
                    all_passed = False
            except Exception as e:
                print_fail(f"Invalid URL test failed: {e}")
                all_passed = False
        
        return all_passed
    
    def test_valid_request(self) -> bool:
        """Test valid request → 200."""
        print_test("Valid Request → 200")
        try:
            payload = {
                "email": self.email,
                "secret": self.secret,
                "url": "https://tds-llm-analysis.s-anand.net/demo"
            }
            resp = requests.post(
                f"{self.base_url}/",
                json=payload,
                timeout=5.0
            )
            
            if resp.status_code == 200:
                data = resp.json()
                required_fields = ["status", "message", "started_at", "deadline"]
                missing = [f for f in required_fields if f not in data]
                
                if not missing:
                    print_pass("Valid request returns 200 with all required fields")
                    print_info(f"Response: {json.dumps(data, indent=2)}")
                    return True
                else:
                    print_fail(f"Missing fields in response: {missing}")
                    return False
            else:
                print_fail(f"Expected 200, got {resp.status_code}: {resp.text[:200]}")
                return False
        except Exception as e:
            print_fail(f"Test failed: {e}")
            return False
    
    def test_response_structure(self) -> bool:
        """Test response structure for valid request."""
        print_test("Response Structure Validation")
        try:
            payload = {
                "email": self.email,
                "secret": self.secret,
                "url": "https://tds-llm-analysis.s-anand.net/demo"
            }
            resp = requests.post(
                f"{self.base_url}/",
                json=payload,
                timeout=5.0
            )
            
            if resp.status_code != 200:
                print_fail(f"Expected 200, got {resp.status_code}")
                return False
            
            data = resp.json()
            
            # Check status field
            if "status" in data:
                if data["status"] == "ok":
                    print_pass("Response has 'status' field with value 'ok'")
                else:
                    print_fail(f"Response 'status' is '{data['status']}', expected 'ok'")
                    return False
            else:
                print_fail("Response missing 'status' field")
                return False
            
            # Check message field
            if "message" in data and isinstance(data["message"], str):
                print_pass("Response has 'message' field (string)")
            else:
                print_fail("Response missing or invalid 'message' field")
                return False
            
            # Check started_at field
            if "started_at" in data:
                print_pass("Response has 'started_at' field")
            else:
                print_fail("Response missing 'started_at' field")
                return False
            
            # Check deadline field
            if "deadline" in data:
                print_pass("Response has 'deadline' field")
            else:
                print_fail("Response missing 'deadline' field")
                return False
            
            return True
        except Exception as e:
            print_fail(f"Test failed: {e}")
            return False
    
    def test_deadline_calculation(self) -> bool:
        """Test that deadline is approximately 3 minutes from start."""
        print_test("Deadline Calculation (3 minutes)")
        try:
            payload = {
                "email": self.email,
                "secret": self.secret,
                "url": "https://tds-llm-analysis.s-anand.net/demo"
            }
            
            start_time = time.time()
            resp = requests.post(
                f"{self.base_url}/",
                json=payload,
                timeout=5.0
            )
            end_time = time.time()
            
            if resp.status_code != 200:
                print_fail(f"Expected 200, got {resp.status_code}")
                return False
            
            data = resp.json()
            
            # Parse ISO datetime strings
            from datetime import datetime
            started_at = datetime.fromisoformat(data["started_at"].replace('Z', '+00:00'))
            deadline = datetime.fromisoformat(data["deadline"].replace('Z', '+00:00'))
            
            # Calculate difference
            diff = (deadline - started_at).total_seconds()
            expected = 3 * 60  # 3 minutes in seconds
            
            # Allow 5 second tolerance
            if abs(diff - expected) <= 5:
                print_pass(f"Deadline is approximately 3 minutes from start (diff: {diff:.1f}s)")
                return True
            else:
                print_fail(f"Deadline difference is {diff:.1f}s, expected ~{expected}s")
                return False
        except Exception as e:
            print_fail(f"Test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}COMPREHENSIVE ENDPOINT TEST SUITE{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"\nTesting endpoint: {self.base_url}")
        print(f"Email: {self.email}")
        print(f"Secret: {'*' * len(self.secret)}")
        
        results = {}
        
        # Run all tests
        results["health_check"] = self.test_health_check()
        results["invalid_json"] = self.test_invalid_json()
        results["missing_fields"] = self.test_missing_fields()
        results["invalid_secret"] = self.test_invalid_secret()
        results["invalid_url"] = self.test_invalid_url_format()
        results["valid_request"] = self.test_valid_request()
        results["response_structure"] = self.test_response_structure()
        results["deadline_calculation"] = self.test_deadline_calculation()
        
        # Summary
        self.passed = sum(1 for v in results.values() if v)
        self.failed = sum(1 for v in results.values() if not v)
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.RESET}")
        print(f"Total: {len(results)}")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.RESET}")
            print("\nFailed tests:")
            for test_name, passed in results.items():
                if not passed:
                    print(f"  - {test_name}")
        
        return results


def main():
    """Main test runner."""
    import os
    
    # Get configuration from environment or command line
    if len(sys.argv) >= 4:
        base_url = sys.argv[1]
        email = sys.argv[2]
        secret = sys.argv[3]
    else:
        # Try to get from environment
        base_url = os.getenv("ENDPOINT_URL", "http://localhost:8000")
        email = os.getenv("EMAIL", "test@example.com")
        secret = os.getenv("SECRET", "test-secret")
        
        if email == "test@example.com" or secret == "test-secret":
            print(f"{Colors.YELLOW}Warning: Using default test credentials.{Colors.RESET}")
            print(f"Usage: python {sys.argv[0]} <endpoint_url> <email> <secret>")
            print(f"Or set ENDPOINT_URL, EMAIL, and SECRET environment variables.\n")
    
    tester = EndpointTester(base_url, email, secret)
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if tester.failed == 0 else 1)


if __name__ == "__main__":
    main()

