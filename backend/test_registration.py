"""
Test registration endpoint with detailed error output
"""
import requests
import json

BASE_URL = "http://localhost:3000"

test_user = {
    "username": "newuser2",
    "email": "newuser2@example.com",
    "password": "TestPass123!",
    "fullName": "New User",
    "phone": "9801234567",
    "currency": "NPR",
    "nationality": "Nepal",
    "age": 28,
    "gender": "female"
}

try:
    print(f"Testing registration endpoint at {BASE_URL}/auth_login/register")
    print(f"Sending data: {json.dumps(test_user, indent=2)}\n")
    
    response = requests.post(
        f"{BASE_URL}/auth_login/register",
        json=test_user,
        timeout=15
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 201:
        print(f"\n✅ Registration successful!")
        print(f"Response JSON: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"\n❌ Registration failed with status {response.status_code}")
        try:
            print(f"Error details: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Error details: {response.text}")
            
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to backend at http://localhost:3000")
    print("   Make sure the backend server is running: python main.py")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
