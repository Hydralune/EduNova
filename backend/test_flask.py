import requests
import json

def test_api():
    """Test the Flask API"""
    print("Testing API...")
    
    # Test direct backend
    base_url = 'http://localhost:5001/api'
    print(f"Testing direct backend: {base_url}")
    
    # Test health endpoint
    try:
        response = requests.get(f'{base_url}/health')
        print(f"Health check: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test through proxy
    proxy_url = 'http://localhost:8080/api'
    print(f"\nTesting through proxy: {proxy_url}")
    
    # Test health endpoint through proxy
    try:
        response = requests.get(f'{proxy_url}/health')
        print(f"Health check through proxy: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Health check through proxy failed: {e}")
    
    # Test users endpoint through proxy
    try:
        response = requests.get(f'{proxy_url}/admin/users', params={'page': 1, 'per_page': 10})
        print(f"\nUsers endpoint through proxy: {response.status_code}")
        print("Response headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        print("\nResponse body:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Users endpoint through proxy failed: {e}")
    
    # Test with direct fetch from JavaScript
    print("\nTest code for browser console:")
    print("""
    // Test through proxy
    fetch('http://localhost:8080/api/admin/users?page=1&per_page=10', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
    """)

if __name__ == "__main__":
    test_api()
