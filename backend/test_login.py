import requests
import json

def test_login():
    """Test the login API"""
    print("Testing login API...")
    
    url = 'http://localhost:5001/api/auth/login'
    headers = {'Content-Type': 'application/json'}
    data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    # Test OPTIONS request
    try:
        options_headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        response = requests.options(url, headers=options_headers)
        print(f"OPTIONS request: {response.status_code}")
        print("Response headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"OPTIONS request failed: {e}")
    
    # Test login request
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(f"\nLogin request: {response.status_code}")
        if response.status_code == 200:
            print("Login successful!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Login failed: {response.text}")
    except Exception as e:
        print(f"Login request failed: {e}")
    
    # Test with fetch from JavaScript
    print("\nTest code for browser console:")
    print("""
    fetch('http://localhost:5001/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: 'admin',
        password: 'admin123'
      })
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
    """)

if __name__ == "__main__":
    test_login() 