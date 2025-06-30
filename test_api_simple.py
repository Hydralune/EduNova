import requests
import json

def test_api():
    url = 'http://localhost:5001/api/rag/knowledge/add'
    data = {
        'course_id': 1,
        'file_path': 'test.pdf'
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 401:
            print("✓ Endpoint exists but requires authentication (expected)")
        elif response.status_code == 404:
            print("✗ Endpoint not found (404 error)")
        else:
            print(f"Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_api() 