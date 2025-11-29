#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the endpoint with the demo quiz URL and monitor the process.
"""

import json
import sys
import os
import time
import requests

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

def main():
    """Test the demo quiz URL."""
    endpoint_url = os.getenv("ENDPOINT_URL", "http://localhost:8000/")
    email = os.getenv("EMAIL", "test@example.com")
    secret = os.getenv("SECRET", "test-secret")
    demo_url = "https://tds-llm-analysis.s-anand.net/demo"
    
    print("=" * 60)
    print("Testing Demo Quiz URL")
    print("=" * 60)
    print(f"Endpoint: {endpoint_url}")
    print(f"Email: {email}")
    print(f"Demo URL: {demo_url}")
    print()
    
    payload = {
        "email": email,
        "secret": secret,
        "url": demo_url
    }
    
    print("Sending POST request...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        response = requests.post(
            endpoint_url,
            json=payload,
            timeout=10.0
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Request accepted!")
            print(f"Response: {json.dumps(data, indent=2)}")
            print()
            print("=" * 60)
            print("Quiz Processing Status")
            print("=" * 60)
            print("✓ Quiz processing has started in the background")
            print(f"✓ Started at: {data.get('started_at', 'N/A')}")
            print(f"✓ Deadline: {data.get('deadline', 'N/A')}")
            print()
            print("NOTE: The quiz is being solved in the background.")
            print("Check your server logs to see the progress:")
            print("  - Page rendering")
            print("  - File downloads")
            print("  - LLM analysis")
            print("  - Answer submissions")
            print("  - Quiz chain following")
            print()
            print("The server will process the quiz automatically.")
            print("You should see log messages indicating:")
            print("  - 'Starting quiz for email=...'")
            print("  - 'Solving quiz URL: ...'")
            print("  - 'Submit result for ...: correct=...'")
            return 0
        elif response.status_code == 400:
            print("✗ Invalid JSON or missing fields")
            print(f"Response: {response.text}")
            return 1
        elif response.status_code == 403:
            print("✗ Invalid secret")
            print(f"Response: {response.text}")
            print()
            print("Make sure your SECRET in .env matches the one you submitted in the Google Form.")
            return 1
        else:
            print(f"✗ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return 1
            
    except requests.exceptions.ConnectionError:
        print("✗ Connection error: Is the server running?")
        print()
        print("Start the server with:")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return 1
    except requests.exceptions.Timeout:
        print("✗ Request timeout")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

