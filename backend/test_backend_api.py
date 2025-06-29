import requests
import json
import os
from dotenv import load_dotenv
import jwt
import datetime

# 加载环境变量
load_dotenv()

# 测试后端API
def test_backend_api():
    print("=== 测试后端API ===")
    
    # 创建一个测试用的JWT令牌
    secret_key = os.getenv("JWT_SECRET_KEY", "test_secret_key")
    token_payload = {
        "sub": 1,  # 用户ID
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    token = jwt.encode(token_payload, secret_key, algorithm="HS256")
    
    # 构建请求
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "message": "你好，请介绍一下自己。"
    }
    
    try:
        # 发送请求
        print("发送后端API请求...")
        response = requests.post("http://localhost:3000/api/rag/chat", headers=headers, json=data)
        
        # 打印响应
        print(f"状态码: {response.status_code}")
        print("响应内容:")
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    
    except Exception as e:
        print(f"请求出错: {str(e)}")

if __name__ == "__main__":
    test_backend_api() 