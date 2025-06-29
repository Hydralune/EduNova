import requests
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 测试直接使用SiliconFlow API
def test_direct_api():
    print("=== 测试直接调用API ===")
    
    # 从环境变量获取API配置
    api_key = os.getenv("LLM_API_KEY")
    api_base = os.getenv("LLM_API_BASE")
    model_name = os.getenv("LLM_MODEL")
    
    if not api_key or not api_base:
        print("错误: 未找到API密钥或基础URL")
        return
    
    print(f"API基础URL: {api_base}")
    print(f"模型名称: {model_name}")
    
    # 构建请求
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model_name or "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个智能教育助手，名为EduNova。"},
            {"role": "user", "content": "你好，请介绍一下自己。"}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        # 发送请求
        print("发送API请求...")
        response = requests.post(f"{api_base}/chat/completions", headers=headers, json=data)
        
        # 打印响应
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("API响应成功:")
            print(result["choices"][0]["message"]["content"])
        else:
            print("API响应错误:")
            print(response.text)
    
    except Exception as e:
        print(f"请求出错: {str(e)}")

if __name__ == "__main__":
    test_direct_api() 