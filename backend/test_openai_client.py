import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

def test_openai_client():
    print("=== 测试OpenAI客户端初始化 ===")
    
    # 从环境变量获取API配置
    api_key = os.getenv("LLM_API_KEY")
    api_base = os.getenv("LLM_API_BASE")
    model_name = os.getenv("LLM_MODEL")
    
    if not api_key or not api_base:
        print("错误: 未找到API密钥或基础URL")
        return
    
    print(f"API密钥: {api_key[:5]}...{api_key[-5:] if len(api_key) > 10 else ''}")
    print(f"API基础URL: {api_base}")
    print(f"模型名称: {model_name}")
    
    try:
        # 尝试初始化客户端
        print("尝试初始化OpenAI客户端...")
        client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        
        print("客户端初始化成功!")
        
        # 尝试发送一个简单的请求
        print("尝试发送一个简单的请求...")
        response = client.chat.completions.create(
            model=model_name or "deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个智能教育助手，名为EduNova。"},
                {"role": "user", "content": "你好，请介绍一下自己。"}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        print("请求成功!")
        print("AI回复:")
        print(response.choices[0].message.content)
        
    except Exception as e:
        print(f"错误: {str(e)}")
        print(f"错误类型: {type(e)}")
        
        # 尝试不同的初始化方式
        print("\n尝试不同的初始化方式...")
        try:
            client = OpenAI(api_key=api_key)
            if api_base:
                client.base_url = api_base
            
            print("替代初始化方式成功!")
            
            # 尝试发送一个简单的请求
            print("尝试发送一个简单的请求...")
            response = client.chat.completions.create(
                model=model_name or "deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个智能教育助手，名为EduNova。"},
                    {"role": "user", "content": "你好，请介绍一下自己。"}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            print("请求成功!")
            print("AI回复:")
            print(response.choices[0].message.content)
            
        except Exception as e2:
            print(f"替代初始化方式也失败: {str(e2)}")
            print(f"错误类型: {type(e2)}")

if __name__ == "__main__":
    test_openai_client() 