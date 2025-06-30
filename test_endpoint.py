import requests

# Test the RAG knowledge add endpoint
try:
    response = requests.post(
        'http://localhost:5001/api/rag/knowledge/add',
        json={'course_id': 1, 'file_path': 'test.pdf'}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 401:
        print("✓ Endpoint exists but requires authentication (expected)")
    elif response.status_code == 404:
        print("✗ Endpoint not found (404 error)")
    else:
        print(f"Unexpected status code: {response.status_code}")
        
except Exception as e:
    print(f"Request failed: {e}") 