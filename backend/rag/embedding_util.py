import os
import requests
import json
import time
import logging
from typing import List, Union, Dict, Any
from dotenv import load_dotenv

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()  # First try to load from backend/.env
rag_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'RAG', '.env')
if os.path.exists(rag_env_path):
    load_dotenv(rag_env_path)  # If exists, load from RAG/.env

def get_embedding(texts: Union[str, List[str]], max_retries: int = 3) -> Dict[str, Any]:
    """
    Get embeddings for text or list of texts using the Silicon Flow API.
    
    Args:
        texts: A string or list of strings to get embeddings for
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dictionary containing the embedding results
    """
    # 使用Silicon Flow API配置
    api_key = "sk-dfthbfklqzgxhhrfiwukmgfakpcfuletjjvapquirwwcuteh"
    api_base = "https://api.siliconflow.cn/v1"
    embedding_model = "BAAI/bge-large-zh-v1.5"
    
    # Ensure texts is a list
    if isinstance(texts, str):
        texts = [texts]
    
    # 过滤空文本
    texts = [text.strip() for text in texts if text and text.strip()]
    if not texts:
        logger.warning("没有有效的文本进行向量化")
        # 返回空的embedding结果
        return {
            "data": [{"embedding": [0.0] * 1024}],
            "model": embedding_model,
            "usage": {"prompt_tokens": 0, "total_tokens": 0}
        }
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Prepare request data
    data = {
        "model": embedding_model,
        "input": texts,
        "encoding_format": "float"
    }
    
    # 重试机制
    for attempt in range(max_retries):
        try:
            logger.info(f"向量化请求 (尝试 {attempt + 1}/{max_retries}): {len(texts)} 个文本")
            
            # Make the API request
            response = requests.post(
                f"{api_base}/embeddings",
                headers=headers,
                json=data,
                timeout=30  # 30秒超时
            )
            
            # Check for errors
            if response.status_code != 200:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # 递增等待时间
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(error_msg)
            
            # 解析响应
            result = response.json()
            
            # 验证响应格式
            if 'data' not in result:
                raise Exception("API响应格式错误：缺少 'data' 字段")
            
            # 验证每个embedding的维度
            for i, item in enumerate(result['data']):
                if 'embedding' not in item:
                    raise Exception(f"API响应格式错误：第 {i} 个结果缺少 'embedding' 字段")
                
                embedding = item['embedding']
                if not isinstance(embedding, list) or len(embedding) != 1024:
                    raise Exception(f"API响应格式错误：第 {i} 个embedding维度不正确，期望1024，实际{len(embedding)}")
            
            logger.info(f"向量化成功: {len(result['data'])} 个embedding")
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"API请求超时 (尝试 {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
                continue
            else:
                raise Exception("API请求超时，已达到最大重试次数")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求异常 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
                continue
            else:
                raise Exception(f"API请求失败: {e}")
                
        except Exception as e:
            logger.error(f"向量化过程中出现未知错误 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
                continue
            else:
                raise Exception(f"向量化失败: {e}")
    
    # 如果所有重试都失败了，返回占位符embedding
    logger.warning("所有重试都失败了，返回占位符embedding")
    return {
        "data": [{"embedding": [0.0] * 1024} for _ in texts],
        "model": embedding_model,
        "usage": {"prompt_tokens": 0, "total_tokens": 0}
    }