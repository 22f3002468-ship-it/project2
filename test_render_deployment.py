#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Render deployment.

Usage:
    python test_render_deployment.py <render-url>
    
Example:
    python test_render_deployment.py https://llm-analysis-quiz.onrender.com
"""

import json
import sys
import os
import requests
from typing import Dict, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(message: str):
    """Print success message."""
    print(f"✓ {message}")


def print_error(message: str):
    """Print error message."""
    print(f"✗ {message}")


def print_info(message: str):
    """Print info message."""
    print(f"ℹ {message}")


def test_health_check(base_url: str) -> bool:
    """Test health check endpoint."""
    print_header("Health Check Test")
    
    try:
        url = f"{base_url}/health"
        print_info(f"Testing: {url}")
        
        response = requests.get(url, timeout=10.0)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check passed (Status: {response.status_code})")
            print_info(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Health check failed (Status: {response.status_code})")
            print_info(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timeout - service may be starting up")
        print_info("Render free tier may take 30-60 seconds on first request")
        return False
    except requests.exceptions.ConnectionError:
        print_error("Connection error - check if URL is correct")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_invalid_json(base_url: str) -> bool:
    """Test invalid JSON handling."""
    print_header("Invalid JSON Test (Should return 400)")
    
    try:
        url = f"{base_url}/"
        print_info(f"Testing: {url}")
        
        response = requests.post(
            url,
            data="this is not json",
            headers={"Content-Type": "application/json"},
            timeout=10.0
        )
        
        if response.status_code == 400:
            print_success(f"Invalid JSON correctly returns 400")
            return True
        else:
            print_error(f"Expected 400, got {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_invalid_secret(base_url: str, email: str) -> bool:
    """Test invalid secret handling."""
    print_header("Invalid Secret Test (Should return 403)")
    
    try:
        url = f"{base_url}/"
        payload = {
            "email": email,
            "secret": "wrong-secret",
            "url": "https://example.com"
        }
        print_info(f"Testing with wrong secret")
        
        response = requests.post(url, json=payload, timeout=10.0)
        
        if response.status_code == 403:
            print_success(f"Invalid secret correctly returns 403")
            return True
        else:
            print_error(f"Expected 403, got {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_valid_request(base_url: str, email: str, secret: str) -> bool:
    """Test valid request."""
    print_header("Valid Request Test (Should return 200)")
    
    try:
        url = f"{base_url}/"
        payload = {
            "email": email,
            "secret": secret,
            "url": "https://tds-llm-analysis.s-anand.net/demo"
        }
        print_info(f"Testing with demo quiz URL")
        print_info(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=15.0)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Valid request returns 200")
            print_info(f"Response: {json.dumps(data, indent=2)}")
            
            # Validate response structure
            required_fields = ["status", "message", "started_at", "deadline"]
            missing = [f for f in required_fields if f not in data]
            
            if not missing:
                print_success("Response has all required fields")
                if data.get("status") == "ok":
                    print_success("Status is 'ok'")
                else:
                    print_error(f"Status is '{data.get('status')}', expected 'ok'")
                    return False
                return True
            else:
                print_error(f"Missing fields: {missing}")
                return False
        else:
            print_error(f"Expected 200, got {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timeout")
        print_info("This might be normal for first request on Render free tier")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def main():
    """Main test function."""
    print("=" * 60)
    print("  Render Deployment Test Suite")
    print("=" * 60)
    
    # Get Render URL
    if len(sys.argv) > 1:
        render_url = sys.argv[1].rstrip('/')
    else:
        render_url = os.getenv("RENDER_URL", "")
        if not render_url:
            print_error("Please provide Render URL as argument or set RENDER_URL env var")
            print_info("Usage: python test_render_deployment.py <render-url>")
            print_info("Example: python test_render_deployment.py https://llm-analysis-quiz.onrender.com")
            sys.exit(1)
    
    # Get credentials
    email = os.getenv("EMAIL", "22f3002468@ds.study.iitm.ac.in")
    secret = os.getenv("SECRET", "")
    
    if not secret:
        print_error("SECRET environment variable not set")
        print_info("Set it in .env file or environment")
        sys.exit(1)
    
    print(f"\nTesting endpoint: {render_url}")
    print(f"Email: {email}")
    print(f"Secret: {'*' * len(secret)}")
    
    results = {}
    
    # Run tests
    results["health"] = test_health_check(render_url)
    
    if results["health"]:
        results["invalid_json"] = test_invalid_json(render_url)
        results["invalid_secret"] = test_invalid_secret(render_url, email)
        results["valid_request"] = test_valid_request(render_url, email, secret)
    else:
        print_error("\nSkipping other tests - health check failed")
        print_info("Service may still be starting up. Wait a minute and try again.")
        results["invalid_json"] = False
        results["invalid_secret"] = False
        results["valid_request"] = False
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print_success("\n🎉 All tests passed! Your deployment is working correctly!")
        print_info("\nYour endpoint is ready for evaluation!")
        print_info(f"Endpoint URL: {render_url}/")
        print_info("Use this URL in your Google Form submission.")
    else:
        print_error(f"\n⚠️  {total - passed} test(s) failed")
        if not results["health"]:
            print_info("\nIf health check failed, the service may still be starting.")
            print_info("Render free tier can take 30-60 seconds on first request.")
            print_info("Wait a minute and run the tests again.")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

