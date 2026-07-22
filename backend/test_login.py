"""
Test login endpoint
"""
import requests
import json

BASE_URL = "http://localhost:3000"

test_login = {
    "username": "newuser2@example.com",  # Can use email or username
    "password": "TestPass123!"
}

try:
    print(f"Testing login endpoint at {BASE_URL}/auth_login/login")
    print(f"Login with: {test_login['username']}\n")
    
    # Use form data for OAuth2PasswordRequestForm
    response = requests.post(
        f"{BASE_URL}/auth_login/login",
        data=test_login,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful!")
        print(f"Token: {data['access_token'][:50]}...")
        print(f"Token Type: {data['token_type']}")
    else:
        print(f"❌ Login failed")
        print(f"Response: {response.text}")
            
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
