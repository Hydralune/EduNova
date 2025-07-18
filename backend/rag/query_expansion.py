import os
import requests
import logging
from typing import Optional
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

def expand_query(query: str, use_cache: bool = True) -> str:
    """
    使用小型语言模型扩展用户查询，添加相关关键词和同义词
    
    Args:
        query: 原始用户查询
        use_cache: 是否使用缓存结果（如果相同查询已处理过）
    
    Returns:
        扩展后的查询
    """
    # 简单的缓存机制
    if use_cache:
        # 检查是否有缓存
        cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "query_cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        # 创建缓存文件名（使用查询的哈希值）
        import hashlib
        query_hash = hashlib.md5(query.encode()).hexdigest()
        cache_file = os.path.join(cache_dir, f"{query_hash}.txt")
        
        # 检查缓存是否存在
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_result = f.read().strip()
                    logger.info(f"使用缓存的查询扩展结果: {cached_result}")
                    return cached_result
            except Exception as e:
                logger.warning(f"读取缓存失败: {e}")
    
    try:
        # 获取API配置
        api_key = os.getenv("LLM_API_KEY")
        api_base = os.getenv("LLM_API_BASE", "https://api.siliconflow.cn/v1")
        # 使用指定的模型
        model = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
        
        if not api_key:
            logger.warning("未找到API密钥，跳过查询扩展")
            return query
            
        # 构建提示词
        prompt = f"""请分析并扩展以下查询，添加相关关键词、术语和同义词，使其更加详细和全面。
        目标是提高信息检索的效果，所以请添加可能出现在相关文档中的专业术语。
        保持扩展后的查询与原始查询的语义一致，但更加丰富。
        
        原始查询: {query}
        
        扩展查询:"""
        
        # 发送请求
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 300,
            "temperature": 0.3  # 低温度保持扩展的相关性
        }
        
        logger.info(f"扩展查询，使用模型: {model}")
        response = requests.post(
            f"{api_base}/chat/completions",
            headers=headers,
            json=data,
            timeout=60  # 增加超时时间到60秒
        )
        
        if response.status_code == 200:
            result = response.json()
            expanded_query = result["choices"][0]["message"]["content"].strip()
            logger.info(f"原始查询: {query}")
            logger.info(f"扩展查询: {expanded_query}")
            
            # 保存到缓存
            if use_cache and expanded_query:
                try:
                    with open(cache_file, "w", encoding="utf-8") as f:
                        f.write(expanded_query)
                except Exception as e:
                    logger.warning(f"写入缓存失败: {e}")
                    
            return expanded_query
        else:
            logger.error(f"查询扩展请求失败: {response.status_code} - {response.text}")
            return query
            
    except Exception as e:
        logger.error(f"查询扩展时出错: {e}")
        return query  # 出错时返回原始查询

def multi_query_expansion(query: str, num_variations: int = 3) -> list:
    """
    生成多个查询变体
    
    Args:
        query: 原始查询
        num_variations: 要生成的变体数量
    
    Returns:
        查询变体列表
    """
    try:
        # 获取API配置
        api_key = os.getenv("LLM_API_KEY")
        api_base = os.getenv("LLM_API_BASE", "https://api.siliconflow.cn/v1")
        model = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
        
        if not api_key:
            logger.warning("未找到API密钥，跳过多查询扩展")
            return [query]
            
        # 构建提示词
        prompt = f"""请为以下查询生成{num_variations}个不同的变体，每个变体都应该表达相同的意思，但使用不同的词汇和表达方式。
        目标是提高信息检索的效果，所以请使用可能出现在相关文档中的不同术语和表达。
        
        原始查询: {query}
        
        请以JSON格式返回结果，格式如下:
        {{
            "variants": [
                "变体1",
                "变体2",
                "变体3"
            ]
        }}
        """
        
        # 发送请求
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.5  # 稍高的温度以获得更多样化的变体
        }
        
        logger.info(f"生成多查询变体，使用模型: {model}")
        response = requests.post(
            f"{api_base}/chat/completions",
            headers=headers,
            json=data,
            timeout=60  # 增加超时时间到60秒
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            
            # 解析JSON响应
            import json
            try:
                # 提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    variants_data = json.loads(json_str)
                    variants = variants_data.get("variants", [])
                    
                    if variants:
                        logger.info(f"生成了 {len(variants)} 个查询变体")
                        return variants
                    else:
                        logger.warning("未能解析查询变体")
                        return [query]
                else:
                    logger.warning("未找到JSON格式的响应")
                    return [query]
            except json.JSONDecodeError:
                logger.warning("JSON解析失败")
                return [query]
        else:
            logger.error(f"多查询扩展请求失败: {response.status_code}")
            return [query]
            
    except Exception as e:
        logger.error(f"多查询扩展时出错: {e}")
        return [query]  # 出错时返回原始查询

if __name__ == "__main__":
    # 测试查询扩展
    test_query = "TensorFlow.js有什么优点？"
    expanded = expand_query(test_query)
    print(f"扩展查询: {expanded}")
    
    # 测试多查询扩展
    variants = multi_query_expansion(test_query, 2)
    print("查询变体:")
    for i, variant in enumerate(variants):
        print(f"{i+1}. {variant}") 