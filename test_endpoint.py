#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script for the LLM Analysis Quiz endpoint.

Usage:
    python test_endpoint.py
"""

import json
import sys
import os
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

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Install it with: pip install requests")
    sys.exit(1)


def test_endpoint(
    endpoint_url: str,
    email: str,
    secret: str,
    quiz_url: str = "https://tds-llm-analysis.s-anand.net/demo",
) -> None:
    """Test the quiz endpoint with a POST request."""
    
    payload: Dict[str, Any] = {
        "email": email,
        "secret": secret,
        "url": quiz_url,
    }
    
    print(f"Testing endpoint: {endpoint_url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(
            endpoint_url,
            json=payload,
            timeout=5.0,  # Short timeout for initial response
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✓ Endpoint is working! Quiz processing started in background.")
        elif response.status_code == 400:
            print("\n✗ Invalid JSON format")
        elif response.status_code == 403:
            print("\n✗ Invalid secret")
        else:
            print(f"\n✗ Unexpected status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Connection error: Is the server running?")
    except requests.exceptions.Timeout:
        print("\n✗ Request timeout")
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    # Get values from command line, environment, or defaults
    ENDPOINT_URL = sys.argv[1] if len(sys.argv) > 1 else os.getenv("ENDPOINT_URL", "http://localhost:8000/")
    EMAIL = sys.argv[2] if len(sys.argv) > 2 else os.getenv("EMAIL", "test@example.com")
    SECRET = sys.argv[3] if len(sys.argv) > 3 else os.getenv("SECRET", "test-secret")
    QUIZ_URL = sys.argv[4] if len(sys.argv) > 4 else "https://tds-llm-analysis.s-anand.net/demo"
    
    test_endpoint(ENDPOINT_URL, EMAIL, SECRET, QUIZ_URL)

