import requests
import json
import os
import jwt
import datetime
from dotenv import load_dotenv
import time

# 加载环境变量
load_dotenv()

def test_conversation():
    print("=== 测试多轮对话 ===")
    
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
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # 第一轮对话
    print("\n--- 第一轮对话 ---")
    first_message = "你好"
    
    try:
        print(f"发送消息: {first_message}")
        response = requests.post("http://localhost:5001/api/rag/chat", 
                                headers=headers, 
                                json={"message": first_message})
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("AI回复:")
            print(result["response"]["content"])
            
            # 保存对话ID用于后续对话
            conversation_id = result["response"]["conversation_id"]
            print(f"对话ID: {conversation_id}")
        else:
            print("响应错误:")
            print(response.text)
            return
    
    except Exception as e:
        print(f"请求出错: {str(e)}")
        return
    
    # 暂停一下
    time.sleep(2)
    
    # 第二轮对话
    print("\n--- 第二轮对话 ---")
    second_message = "如何提高学习效率？"
    
    try:
        print(f"发送消息: {second_message}")
        print(f"使用对话ID: {conversation_id}")
        
        response = requests.post("http://localhost:5001/api/rag/chat", 
                                headers=headers, 
                                json={
                                    "message": second_message,
                                    "conversation_id": conversation_id
                                })
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("AI回复:")
            print(result["response"]["content"])
        else:
            print("响应错误:")
            print(response.text)
    
    except Exception as e:
        print(f"请求出错: {str(e)}")

if __name__ == "__main__":
    test_conversation() 