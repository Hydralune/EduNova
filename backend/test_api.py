import requests
import json

def test_api():
    base_url = "http://localhost:5001"
    
    # 测试状态API
    print("=== 测试状态API ===")
    try:
        response = requests.get(f"{base_url}/api/status")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"状态API错误: {e}")
    
    # 测试课程API
    print("\n=== 测试课程API ===")
    try:
        response = requests.get(f"{base_url}/api/courses")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"课程API错误: {e}")
    
    # 测试RAG状态API
    print("\n=== 测试RAG状态API ===")
    try:
        response = requests.get(f"{base_url}/api/rag/status")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"RAG状态API错误: {e}")

if __name__ == "__main__":
    test_api() 