import requests
import json
import os
import jwt
import datetime
from dotenv import load_dotenv
import time

# 加载环境变量
load_dotenv()

def test_streaming():
    print("=== 测试流式输出 ===")
    
    # 创建一个测试用的JWT令牌
    secret_key = "asdf#FGSgvasgf$5$WGT"  # 与main.py中的SECRET_KEY相同
    token_payload = {
        "sub": 1,  # 用户ID
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        "fresh": True,
        "iat": datetime.datetime.utcnow(),
        "jti": "unique-id-123",
        "type": "access",
        "nbf": datetime.datetime.utcnow(),
        "identity": 1
    }
    token = jwt.encode(token_payload, secret_key, algorithm="HS256")
    
    # 构建请求头
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 构建URL
    params = {
        "message": "如何提高学习效率？",
        "stream": "true"
    }
    
    url = "http://localhost:5001/api/rag/chat"
    
    try:
        # 发送请求
        print("发送流式请求...")
        with requests.get(url, headers=headers, params=params, stream=True) as response:
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 处理流式响应
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            line_json = line_text[6:]  # 移除 'data: ' 前缀
                            try:
                                data = json.loads(line_json)
                                if 'content' in data:
                                    content = data['content']
                                    full_response += content
                                    print(content, end="", flush=True)
                                if 'status' in data and data['status'] == 'done':
                                    print("\n\n=== 流式响应完成 ===")
                                    print(f"对话ID: {data.get('conversation_id')}")
                            except json.JSONDecodeError:
                                print(f"无法解析JSON: {line_json}")
                
                print("\n\n=== 完整响应 ===")
                print(full_response)
            else:
                print("响应错误:")
                print(response.text)
    
    except Exception as e:
        print(f"请求出错: {str(e)}")

if __name__ == "__main__":
    test_streaming() 