import os
import argparse
from dotenv import load_dotenv
import networkx as nx
from typing import List, Dict, Any, Optional
import random
import time
import openai
import sys
import json
import logging
import requests
from pathlib import Path

# 禁用 ChromaDB telemetry 以防止错误信息
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

# 设置日志级别为ERROR，减少不必要的日志输出
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("backend.rag.embedding_util").setLevel(logging.WARNING)
logging.getLogger("posthog").setLevel(logging.ERROR)

# 完全禁用 posthog (ChromaDB使用的遥测库)
try:
    import posthog
    # 正确禁用posthog的方式
    posthog.disabled = True
    # 替换capture方法以避免参数错误
    original_capture = posthog.capture
    def safe_capture(*args, **kwargs):
        try:
            if len(args) <= 1:
                return original_capture(*args, **kwargs)
            else:
                # 忽略多余的参数
                return original_capture(args[0])
        except Exception:
            pass
    posthog.capture = safe_capture
except:
    pass

# Import query expansion module
# from backend.rag.query_expansion import expand_query, multi_query_expansion

"""
RAG查询模块 - 包含向量检索和重排序功能

此模块实现了检索增强生成(RAG)的核心功能:
1. 向量检索: 使用ChromaDB和embedding API进行语义相似性搜索
2. 重排序: 使用Silicon Flow的重排序API对检索结果进行优化排序
3. 知识图谱增强: (可选功能) 使用知识图谱提供额外的上下文信息

配置参数:
- LLM_API_KEY: API密钥
- LLM_API_BASE: API基础URL (默认: https://api.siliconflow.cn/v1)
- LLM_MODEL: 大语言模型名称 (默认: Qwen/Qwen3-32B)
- RERANK_MODEL: 重排序模型名称 (默认: BAAI/bge-reranker-v2-m3)

使用方法:
1. 向量检索和重排序:
   docs = hybrid_retriever(query, course_id)
   
2. 重排序API:
   rerank_results = rerank_documents(query, documents, max_results)
   
3. 完整RAG查询:
   response = rag_query(query, course_id)
   
4. 流式RAG查询:
   for chunk in rag_query_stream(query, course_id):
       print(chunk, end="")

注意:
- 本模块使用了类型忽略注释(# type: ignore)来解决与LangChain库版本不匹配导致的类型检查问题
- EmbeddingFunction类实现了langchain_core.embeddings.Embeddings接口
"""

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings  # 导入Embeddings接口
from backend.rag.embedding_util import get_embedding

# 导入自定义的EmbeddingFunction，避免从create_db导入
class EmbeddingFunction(Embeddings):  # 实现Embeddings接口
    """Custom embedding function for use with Chroma."""
    def __init__(self):
        self.get_embedding = get_embedding
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        embeddings = []
        for text in texts:
            try:
                result = self.get_embedding(text)
                embeddings.append(result["data"][0]["embedding"])
            except Exception as e:
                print(f"Error embedding document: {e}")
                # 返回1024维零向量作为后备
                embeddings.append([0.0] * 1024)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        try:
            result = self.get_embedding(text)
            return result["data"][0]["embedding"]
        except Exception as e:
            print(f"Error embedding query: {e}")
            # 返回1024维零向量作为后备
            return [0.0] * 1024

# 添加缺失的函数
def load_knowledge_graph(course_id: str) -> nx.Graph:
    """加载知识图谱"""
    try:
        graph_path = os.path.join("uploads/knowledge_base", course_id, 'knowledge_graph.gml')
        if os.path.exists(graph_path):
            return nx.read_gml(graph_path)
        else:
            return nx.Graph()
    except Exception as e:
        print(f"加载知识图谱失败: {e}")
        return nx.Graph()

def search_knowledge_graph(graph: nx.Graph, query: str, all_chunks: dict) -> List[Document]:
    """在知识图谱中搜索相关内容"""
    try:
        # 简单的关键词搜索
        query_upper = query.upper()
        related_chunk_ids = set()
        
        for node in graph.nodes():
            if query_upper in node:
                related_chunk_ids.update(graph.nodes[node].get('source_chunks', []))
        
        # 返回相关文档
        return [all_chunks[chunk_id] for chunk_id in related_chunk_ids if chunk_id in all_chunks]
    except Exception as e:
        print(f"知识图谱搜索失败: {e}")
        return []

# Load environment variables
load_dotenv()

def format_docs(docs: List[Document]) -> str:
    """Helper function to format retrieved documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)

def get_query_entities_chain(llm):
    """Creates a chain for extracting entities from the user's query."""
    prompt = ChatPromptTemplate.from_template("""
Extract the names of key concepts or entities from the following question.
Return them as a JSON list of strings.

Question:
---
{question}
---
    """)
    return prompt | llm | JsonOutputParser()

def get_graph_context(question: str, graph: nx.Graph, all_chunks: dict, llm) -> List[Document]:
    """
    Retrieves context from the knowledge graph by finding paths between entities in the query.
    """
    print("--- Identifying entities in query for graph search ---")
    query_entities_chain = get_query_entities_chain(llm)
    try:
        entities = query_entities_chain.invoke({"question": question})
        # Filter out any non-string or empty string results from the parser
        entities = [e.strip().upper() for e in entities if isinstance(e, str) and e.strip()]
        print(f"--- Found entities: {entities} ---")
    except Exception:
        print("--- Could not extract entities from query, skipping graph search. ---")
        return []

    if not entities:
        return []

    related_chunk_ids = set()
    path_docs = []

    # First, gather chunks directly related to each entity
    for entity_name in entities:
        if entity_name in graph:
            related_chunk_ids.update(graph.nodes[entity_name].get('source_chunks', []))

    # If multiple entities are found, find paths between them
    if len(entities) > 1:
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                source = entities[i]
                target = entities[j]
                if source in graph and target in graph:
                    try:
                        paths = list(nx.all_shortest_paths(graph, source=source, target=target))
                        print(f"--- Found {len(paths)} shortest path(s) between {source} and {target} ---")
                        for path in paths:
                            path_str = " -> ".join(path)
                            path_doc = Document(
                                page_content=f"Found a reasoning path: {path_str}",
                                metadata={"source": "knowledge_graph_path"}
                            )
                            path_docs.append(path_doc)
                            # Add chunks from all nodes in the path
                            for node_name in path:
                                related_chunk_ids.update(graph.nodes[node_name].get('source_chunks', []))
                    except nx.NetworkXNoPath:
                        print(f"--- No path found between {source} and {target} ---")
                        pass

    # Retrieve the unique documents from the collected chunk IDs
    graph_docs = [all_chunks[chunk_id] for chunk_id in related_chunk_ids if chunk_id in all_chunks]
    
    # Combine path descriptions with the text chunks
    final_graph_docs = path_docs + graph_docs
    print(f"--- Retrieved {len(final_graph_docs)} total documents (including paths) from the knowledge graph ---")
    return final_graph_docs

# New function to initialize resources for external use
def initialize_resources(course_id):
    """Initialize and return resources for a specific course."""
    # --- Load API Keys ---
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE", "https://api.siliconflow.cn/v1")
    model_name = os.getenv("LLM_MODEL", "Qwen/Qwen3-32B")

    if not api_key:
        raise ValueError("LLM_API_KEY not found in .env file.")
    if not base_url:
        raise ValueError("LLM_API_BASE not found in .env file.")
    if not model_name:
        raise ValueError("LLM_MODEL not found in .env file.")

    # --- Initialize LLM ---
    # 使用类型忽略注释解决类型检查问题
    # 直接使用type: ignore跳过类型检查
    from pydantic import SecretStr
    llm = ChatOpenAI(  # type: ignore
        api_key=SecretStr(api_key) if api_key else None,
        base_url=base_url,
        model=model_name,
        temperature=0,
        max_retries=6
    )

    # --- Load Vectorstore ---
    # 检查多个可能的知识库路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    possible_paths = [
        os.path.join(project_root, "uploads", "knowledge_base", course_id),
        os.path.join(project_root, "backend", "uploads", "knowledge_base", course_id),
        # 添加绝对路径支持
        r"C:\Users\Ylon\Desktop\EduNova\backend\uploads\knowledge_base\test_course_f84787f9"
    ]
    
    persist_dir = None
    for path in possible_paths:
        if os.path.exists(path):
            print(f"找到知识库路径: {path}")
            
            # 检查向量数据库目录
            vectordb_path = os.path.join(path, "vectordb")
            if os.path.exists(vectordb_path):
                print(f"找到向量数据库路径: {vectordb_path}")
                persist_dir = vectordb_path
                break
            else:
                # 如果没有vectordb子目录，使用主目录
                persist_dir = path
                break
    
    if not persist_dir:
        raise FileNotFoundError(f"No database found for course '{course_id}'. Please run create_db.py first.")
    
    # 创建嵌入函数和向量存储
    embedding_function = EmbeddingFunction()
    
    # 使用类型忽略注释解决类型检查问题
    # 添加telemetry_impl=None参数禁用遥测
    try:
        from chromadb.config import Settings
        # 确保完全禁用遥测
        client_settings = Settings(
            anonymized_telemetry=False,
            allow_reset=True,
            telemetry_enabled=False
        )
        
        # 在初始化前确保环境变量设置正确
        os.environ["ANONYMIZED_TELEMETRY"] = "False"
        os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"
        
        print(f"正在初始化Chroma，使用路径: {persist_dir}")
        vectorstore = Chroma(  # type: ignore
            persist_directory=persist_dir,
            embedding_function=embedding_function,
            client_settings=client_settings
        )
    except Exception as e:
        print(f"使用自定义设置初始化Chroma失败: {e}，尝试使用默认设置")
        # 在回退方案中也禁用遥测
        os.environ["ANONYMIZED_TELEMETRY"] = "False"
        os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"
        
        vectorstore = Chroma(  # type: ignore
            persist_directory=persist_dir,
            embedding_function=embedding_function
        )
    
    # 创建检索器
    vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    return {
        'llm': llm,
        'vector_retriever': vector_retriever
    }

# Expose hybrid_retriever for external use
def hybrid_retriever(query: str, course_id: str):
    """Retrieves relevant documents using vector search and reranking for a given query and course."""
    resources = initialize_resources(course_id)
    
    # 完全跳过知识图谱检索
    # graph_docs = get_graph_context(query, resources['graph'], resources['all_chunks_map'], resources['llm'])
    
    # 只使用向量检索
    print("--- Performing vector search ---")
    vector_docs = resources['vector_retriever'].invoke(query)
    print(f"--- Retrieved {len(vector_docs)} chunks from vector search ---")

    # 如果找到足够的文档，执行重排序
    if len(vector_docs) > 1:
        print("--- Performing reranking ---")
        # 提取文档内容
        documents = [doc.page_content for doc in vector_docs]
        # 执行重排序
        rerank_results = rerank_documents(query, documents)
        
        if rerank_results:
            # 根据重排序结果重新排列文档
            reranked_docs = []
            for item in rerank_results:
                doc_idx = item.get('index')
                if doc_idx is not None and isinstance(doc_idx, int) and 0 <= doc_idx < len(vector_docs):
                    reranked_docs.append(vector_docs[doc_idx])
            
            print(f"--- Reranking successful, returned {len(reranked_docs)} documents ---")
            return reranked_docs

    # 如果重排序失败或文档不足，直接返回向量检索结果
    return vector_docs

def upload_file_to_api(file_path: str, api_key: str) -> Optional[str]:
    """上传文件到API并返回文件ID"""
    try:
        url = "https://api.siliconflow.cn/v1/files"
        
        with open(file_path, 'rb') as f:
            files = {
                'file': (os.path.basename(file_path), f, 'application/octet-stream')
            }
            data = {
                'purpose': 'assistants'
            }
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            response = requests.post(url, files=files, data=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('id')
            else:
                print(f"文件上传失败: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        print(f"上传文件时出错: {e}")
        return None

def rerank_documents(query: str, documents: List[str], max_results: int = 5) -> List[Dict[str, Any]]:
    """
    使用重排序API对文档列表进行重排序
    
    Args:
        query: 查询文本
        documents: 要重排序的文档列表
        max_results: 返回的最大结果数
        
    Returns:
        重排序后的结果列表，每个结果包含索引和相关性分数
    """
    try:
        # 获取API配置
        api_key = os.getenv("LLM_API_KEY")
        api_base = os.getenv("LLM_API_BASE", "https://api.siliconflow.cn/v1")
        rerank_model = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3")
        
        if not api_key or not documents:
            print("未找到API密钥或文档列表为空，跳过重排序")
            return []
            
        print(f"--- 使用模型 {rerank_model} 进行重排序，共 {len(documents)} 个文档 ---")
        
        # 构建重排序请求
        url = f"{api_base}/rerank"
        payload = {
            "query": query,
            "documents": documents,
            "return_documents": False,  # 我们只需要索引和分数
            "model": rerank_model
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 发送重排序请求
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            rerank_result = response.json()
            print(f"--- 重排序成功 ---")
            
            # 返回排序结果（限制数量）
            results = rerank_result.get('results', [])[:max_results]
            return results
        else:
            print(f"重排序API请求失败: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"重排序请求失败: {e}")
        return []

def query_knowledge_base(query: str, course_id: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    查询知识库，返回相关文档片段
    使用向量搜索检索候选文档，然后使用重排序API优化结果
    """
    try:
        # 检查多个可能的知识库路径
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        possible_paths = [
            os.path.join(project_root, "uploads", "knowledge_base", str(course_id)),
            os.path.join(project_root, "backend", "uploads", "knowledge_base", str(course_id))
        ]
        
        persist_dir = None
        for path in possible_paths:
            vectordb_path = os.path.join(path, "vectordb")
            if os.path.exists(vectordb_path):
                print(f"找到向量数据库路径: {vectordb_path}")
                persist_dir = vectordb_path
                break
        
        if not persist_dir:
            print(f"向量数据库不存在，检查了以下路径: {possible_paths}")
            return []
        
        # 创建向量存储
        embedding_function = EmbeddingFunction()
        # 使用类型忽略注释来解决类型检查问题
        vectorstore = Chroma(  # type: ignore
            persist_directory=persist_dir,
            embedding_function=embedding_function
        )
        
        # 执行向量搜索 - 检索更多候选文档用于重排序
        print("--- 执行向量搜索 ---")
        candidate_count = max(max_results * 3, 15)  # 检索更多候选文档以供重排序
        docs = vectorstore.similarity_search(query, k=candidate_count)
        
        if not docs:
            print("--- 向量搜索未找到结果 ---")
            return []
            
        print(f"--- 向量搜索找到 {len(docs)} 个候选文档 ---")
        
        # 提取文档内容用于重排序
        documents = [doc.page_content for doc in docs]
        
        # 使用重排序API
        rerank_results = rerank_documents(query, documents, max_results)
        
        if rerank_results:
            # 处理重排序结果
            results = []
            for item in rerank_results:
                # 安全地获取索引和分数，确保它们是有效值
                doc_idx = item.get('index')
                score = item.get('relevance_score', 0.0)
                
                # 类型安全的索引检查
                if doc_idx is not None and isinstance(doc_idx, int) and 0 <= doc_idx < len(docs):
                    doc = docs[doc_idx]
                    results.append({
                        'content': doc.page_content,
                        'metadata': doc.metadata,
                        'score': score
                    })
            
            print(f"--- 返回 {len(results)} 个重排序后的文档片段 ---")
            return results
        else:
            # 回退到向量搜索结果
            print("--- 重排序失败，使用向量搜索结果 ---")
            results = []
            for i, doc in enumerate(docs[:max_results]):
                results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': 1.0 - (i * 0.1)  # 简单的相似度分数
                })
            return results
        
    except Exception as e:
        print(f"查询知识库时出错: {e}")
        return []

def build_rag_context(query: str, course_id: str, max_tokens: int = 8000) -> str:
    """
    构建RAG上下文，简化版本
    """
    try:
        # 查询知识库
        relevant_docs = query_knowledge_base(query, course_id, max_results=10)
        
        if not relevant_docs:
            print("未找到相关文档")
            return ""
        
        # 构建上下文
        context_parts = []
        current_tokens = 0
        
        for doc in relevant_docs:
            content = doc['content']
            # 简单估算token数量（中文字符约等于token数）
            estimated_tokens = len(content)
            
            if current_tokens + estimated_tokens > max_tokens:
                break
                
            context_parts.append(f"文档片段:\n{content}\n")
            current_tokens += estimated_tokens
        
        context = "\n".join(context_parts)
        print(f"--- 构建了包含 {len(context_parts)} 个文档片段的上下文 ---")
        return context
        
    except Exception as e:
        print(f"构建RAG上下文时出错: {e}")
        return ""

def get_llm_response(query: str, context: str = "", max_tokens: int = 4000) -> str:
    """
    获取LLM响应，支持文件上传处理大文件
    """
    try:
        # 获取API配置
        api_key = os.getenv("LLM_API_KEY")
        api_base = os.getenv("LLM_API_BASE", "https://api.siliconflow.cn/v1")
        model = os.getenv("LLM_MODEL", "Qwen/Qwen3-32B")
        
        if not api_key:
            raise ValueError("LLM_API_KEY not found in .env file.")
        
        # 构建提示词
        if context:
            prompt = f"""基于以下上下文信息回答问题：\n\n上下文信息：\n{context}\n\n问题：{query}\n\n请基于上下文信息提供准确、详细的回答。如果上下文中没有相关信息，请说明无法从提供的信息中找到答案。"""
        else:
            prompt = f"请回答以下问题：{query}"
        
        # 检查是否需要文件上传（如果上下文太长）
        if len(prompt) > 32000:  # 如果超过32k字符，考虑文件上传
            print("--- 上下文过长，考虑使用文件上传 ---")
            # 这里可以添加文件上传逻辑
            # 暂时截断上下文
            prompt = prompt[:32000] + "\n\n[上下文已截断]"
        
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
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        print(f"--- 发送LLM请求，模型: {model} ---")
        response = requests.post(
            f"{api_base}/chat/completions",
            headers=headers,
            json=data,
            timeout=120  # 增加超时时间到120秒
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            print(f"LLM请求失败: {response.status_code} - {response.text}")
            return f"抱歉，处理请求时出现错误：{response.text}"
            
    except requests.exceptions.Timeout:
        print("LLM请求超时")
        return "抱歉，请求超时，请稍后重试。"
    except requests.exceptions.ConnectionError:
        print("LLM连接错误")
        return "抱歉，网络连接错误，请检查网络连接。"
    except Exception as e:
        print(f"获取LLM响应时出错: {e}")
        return f"抱歉，处理请求时出现错误：{str(e)}"

def rag_query(query: str, course_id: str) -> str:
    """
    简化的RAG查询函数
    """
    try:
        print(f"--- 开始RAG查询，课程ID: {course_id} ---")
        
        # 构建RAG上下文
        print("--- 使用向量检索构建上下文 ---")
        context = build_rag_context(query, course_id, max_tokens=6000)
        
        if not context:
            return "抱歉，未找到相关的文档信息。"
        
        # 获取LLM响应
        response = get_llm_response(query, context, max_tokens=4000)
        
        print("--- RAG查询完成 ---")
        return response
        
    except Exception as e:
        print(f"RAG查询失败: {e}")
        return f"抱歉，RAG查询失败：{str(e)}"

def rag_query_stream(query: str, course_id: str):
    """
    支持流式响应的RAG查询函数
    """
    try:
        print(f"--- 开始RAG查询，课程ID: {course_id} ---")
        
        # 构建RAG上下文
        print("--- 使用向量检索构建上下文 ---")
        context = build_rag_context(query, course_id, max_tokens=6000)
        
        if not context:
            yield "抱歉，未找到相关的文档信息。"
            return
        
        # 获取LLM流式响应
        for chunk in get_llm_response_stream(query, context, max_tokens=4000):
            yield chunk
        
        print("--- RAG查询完成 ---")
        
    except Exception as e:
        print(f"RAG查询失败: {e}")
        yield f"抱歉，RAG查询失败：{str(e)}"

def get_llm_response_stream(query: str, context: str = "", max_tokens: int = 4000):
    """
    获取LLM流式响应
    """
    try:
        # 获取API配置
        api_key = os.getenv("LLM_API_KEY")
        api_base = os.getenv("LLM_API_BASE", "https://api.siliconflow.cn/v1")
        model = os.getenv("LLM_MODEL", "Qwen/Qwen3-32B")
        
        if not api_key:
            raise ValueError("LLM_API_KEY not found in .env file.")
        
        # 构建提示词
        if context:
            prompt = f"""基于以下上下文信息回答问题：

上下文信息：
{context}

问题：{query}

请基于上下文信息提供准确、详细的回答。回答要自然流畅，不要提及"基于上下文信息"等字眼。如果上下文中没有相关信息，请说明无法从提供的信息中找到答案。"""
        else:
            prompt = f"请回答以下问题：{query}"
        
        # 检查是否需要文件上传（如果上下文太长）
        if len(prompt) > 32000:  # 如果超过32k字符，考虑文件上传
            print("--- 上下文过长，考虑使用文件上传 ---")
            # 这里可以添加文件上传逻辑
            # 暂时截断上下文
            prompt = prompt[:32000] + "\n\n[上下文已截断]"
        
        # 发送流式请求
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "stream": True
        }
        
        print(f"--- 发送LLM请求，模型: {model} ---")
        response = requests.post(
            f"{api_base}/chat/completions",
            headers=headers,
            json=data,
            timeout=120,
            stream=True
        )
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            data_json = json.loads(data_str)
                            if 'choices' in data_json and len(data_json['choices']) > 0:
                                delta = data_json['choices'][0].get('delta', {})
                                if 'content' in delta and delta['content'] is not None:
                                    yield delta['content']
                        except json.JSONDecodeError:
                            continue
        else:
            print(f"LLM请求失败: {response.status_code} - {response.text}")
            yield f"抱歉，处理请求时出现错误：{response.text}"
            
    except requests.exceptions.Timeout:
        print("LLM请求超时")
        yield "抱歉，请求超时，请稍后重试。"
    except requests.exceptions.ConnectionError:
        print("LLM连接错误")
        yield "抱歉，网络连接错误，请检查网络连接。"
    except Exception as e:
        print(f"获取LLM响应时出错: {e}")
        yield f"抱歉，处理请求时出现错误：{str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Query a course-specific vector database.")
    parser.add_argument("--course_id", type=str, required=True, help="ID of the course to query.")
    args = parser.parse_args()

    # --- Initialize Resources ---
    try:
        resources = initialize_resources(args.course_id)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {str(e)}")
        return

    # --- Display Sample Entities ---
    G = resources['graph']
    if G.number_of_nodes() > 0:
        print("\n--- Sample of Extracted Entities ---")
        sample_nodes = random.sample(list(G.nodes()), min(10, G.number_of_nodes()))
        for node in sample_nodes:
            print(f"- {node} (Type: {G.nodes[node].get('type', 'N/A')})")
    else:
        print("\n--- Knowledge graph is empty or could not be loaded. ---")

    # --- Define RAG Chain ---
    template = """You are a helpful and knowledgeable AI assistant.
Use the following retrieved context as your primary source to answer the user's question.
If the context is incomplete or lacks sufficient detail, supplement it with your own general knowledge to provide a thorough and accurate answer.
If the context includes code snippets, display them clearly in a code block.
When you provide actual (non-pseudocode) code, ensure it is complete and runnable. If the context does not include enough information, fill in the missing parts using your own knowledge.
When appropriate, combine the context and your own expertise to generate extended outputs, such as lesson plans, assignments, examples, or detailed explanations.
Always aim for clarity, correctness, and relevance.
If you genuinely do not know the answer, say "I don't know" instead of guessing.

Question: {question}

Context: {context}

Answer:"""
    prompt = PromptTemplate.from_template(template)

    rag_chain = (
        {"context": RunnablePassthrough() | (lambda query: hybrid_retriever(query, args.course_id)) | format_docs, "question": RunnablePassthrough()}
        | prompt
        | resources['llm']
        | StrOutputParser()
    )

    # --- Conversation Loop ---
    print("\n--- Starting Conversation Loop ---")
    while True:
        try:
            query = input("\n[You]: ")
            if query.lower() in ["exit", "quit"]:
                break
            
            print("\n[AI]:")
            
            # Add a more patient retry loop for the whole chain
            for attempt in range(3): # Retry up to 3 times
                try:
                    for chunk in rag_chain.stream(query):
                        print(chunk, end="", flush=True)
                    print() # for newline after streaming
                    break # Success, exit retry loop
                except openai.RateLimitError as e:
                    wait_time = (attempt + 1) * 5 # Wait 5s, then 10s
                    print(f"\n[System]: API rate limit reached. Waiting for {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
            else: # If all retries fail
                print("\n[System]: Could not get a response after multiple retries due to persistent rate limiting.")


        except (KeyboardInterrupt, EOFError):
            break
    print("\n--- Exiting ---")

if __name__ == "__main__":
    main()