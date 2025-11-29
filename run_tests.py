#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test runner for LLM Analysis Quiz endpoint.

This script runs comprehensive tests to ensure your endpoint meets all requirements.
"""

import subprocess
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not required if env vars are set manually

def main():
    """Run comprehensive tests."""
    print("=" * 60)
    print("LLM Analysis Quiz - Comprehensive Test Suite")
    print("=" * 60)
    print()
    
    # Check if server is running
    import requests
    try:
        base_url = os.getenv("ENDPOINT_URL", "http://localhost:8000")
        resp = requests.get(f"{base_url}/health", timeout=2.0)
        if resp.status_code == 200:
            print("✓ Server is running")
        else:
            print("✗ Server health check failed")
            return 1
    except Exception as e:
        print(f"✗ Cannot connect to server at {base_url}")
        print(f"  Error: {e}")
        print("\nPlease start the server first:")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return 1
    
    # Get credentials
    email = os.getenv("EMAIL")
    secret = os.getenv("SECRET")
    
    if not email or not secret:
        print("✗ EMAIL and SECRET environment variables not set")
        print("\nPlease set them in your .env file or environment:")
        print("  export EMAIL=your-email@example.com")
        print("  export SECRET=your-secret")
        return 1
    
    print(f"✓ Using email: {email}")
    print(f"✓ Using secret: {'*' * len(secret)}")
    print()
    
    # Run comprehensive tests
    try:
        result = subprocess.run(
            [sys.executable, "test_comprehensive.py", base_url, email, secret],
            check=False
        )
        return result.returncode
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n✗ Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

