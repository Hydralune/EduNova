import requests
import json

def test_auth():
    print("Testing authentication...")
    try:
        login_response = requests.post(
            'http://localhost:5001/api/auth/login',
            json={
                'username': 'admin',
                'password': 'admin123'
            }
        )
        
        if login_response.status_code == 200:
            response_data = login_response.json()
            token = response_data.get('token')
            if token:
                print(f"✓ Authentication successful")
                return token
            else:
                print("✗ No token in response")
                return None
        else:
            print(f"✗ Authentication failed: {login_response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Authentication request failed: {e}")
        return None

def test_status(token, course_id):
    if not token:
        print("No token available")
        return
    
    print(f"\nTesting knowledge base status for course {course_id}...")
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'http://localhost:5001/api/rag/knowledge/status?course_id={course_id}',
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                items = data.get('items', [])
                print(f"\nFound {len(items)} queue items:")
                for item in items:
                    print(f"  ID: {item['id']}, Status: {item['status']}, Progress: {item['progress']}%, File: {item['file_path']}")
                    if item.get('error_message'):
                        print(f"    Error: {item['error_message']}")
            else:
                print(f"API returned error: {data.get('message')}")
        else:
            print(f"Request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    token = test_auth()
    if token:
        # Test course 1 and 3
        test_status(token, 1)
        test_status(token, 3) 