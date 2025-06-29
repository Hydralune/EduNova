import requests
import json

def test_auth_api():
    """测试认证API"""
    base_url = "http://localhost:5001/api"
    
    # 1. 登录获取令牌
    login_data = {
        "username": "admin",  # 替换为实际用户名
        "password": "admin123"  # 替换为实际密码
    }
    
    try:
        print("尝试登录...")
        login_response = requests.post(f"{base_url}/auth/login", json=login_data)
        login_response.raise_for_status()
        
        login_data = login_response.json()
        token = login_data.get("token")
        
        if not token:
            print("登录失败，未获取到令牌")
            print(f"响应内容: {json.dumps(login_data, indent=2, ensure_ascii=False)}")
            return
            
        print(f"登录成功，获取到令牌: {token[:10]}...")
        
        # 2. 获取用户资料
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n尝试获取用户资料...")
        profile_response = requests.get(f"{base_url}/auth/profile", headers=headers)
        profile_response.raise_for_status()
        
        profile_data = profile_response.json()
        print(f"用户资料: {json.dumps(profile_data, indent=2, ensure_ascii=False)}")
        
        # 3. 检查RAG状态
        print("\n尝试获取RAG状态...")
        rag_response = requests.get(f"{base_url}/rag/status", headers=headers)
        rag_response.raise_for_status()
        
        rag_data = rag_response.json()
        print(f"RAG状态: {json.dumps(rag_data, indent=2, ensure_ascii=False)}")
        
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"状态码: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"错误内容: {e.response.text}")

if __name__ == "__main__":
    test_auth_api() 