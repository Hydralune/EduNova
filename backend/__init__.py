"""
RAG (Retrieval-Augmented Generation) 模块接口

本模块为智能教学系统提供基于检索增强生成的功能支持。
用户可以在此基础上集成Chroma向量数据库和其他RAG组件。

主要功能：
1. 文档向量化和存储
2. 语义检索
3. 上下文增强生成
4. 知识库管理
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os

class VectorStoreInterface(ABC):
    """向量数据库接口"""
    
    @abstractmethod
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """添加文档到向量数据库"""
        pass
    
    @abstractmethod
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """语义相似度搜索"""
        pass
    
    @abstractmethod
    def delete_documents(self, document_ids: List[str]) -> bool:
        """删除文档"""
        pass

class EmbeddingInterface(ABC):
    """文本嵌入接口"""
    
    @abstractmethod
    def encode_text(self, text: str) -> List[float]:
        """将文本转换为向量"""
        pass
    
    @abstractmethod
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """批量文本向量化"""
        pass

class RAGService:
    """RAG服务主类"""
    
    def __init__(self, vector_store: VectorStoreInterface, embedding_model: EmbeddingInterface):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.knowledge_base_path = os.path.join(os.path.dirname(__file__), 'knowledge_base')
        
    def initialize_knowledge_base(self, course_materials: List[Dict[str, Any]]) -> bool:
        """初始化知识库"""
        try:
            # 处理课程材料并添加到向量数据库
            processed_docs = []
            for material in course_materials:
                doc = {
                    'id': material.get('id'),
                    'content': material.get('content', ''),
                    'title': material.get('title', ''),
                    'course_id': material.get('course_id'),
                    'metadata': material.get('metadata', {})
                }
                processed_docs.append(doc)
            
            return self.vector_store.add_documents(processed_docs)
        except Exception as e:
            print(f"初始化知识库失败: {e}")
            return False
    
    def retrieve_context(self, query: str, course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """检索相关上下文"""
        try:
            # 执行语义搜索
            results = self.vector_store.search_similar(query, top_k=5)
            
            # 如果指定了课程ID，过滤结果
            if course_id:
                results = [r for r in results if r.get('course_id') == course_id]
            
            return results
        except Exception as e:
            print(f"检索上下文失败: {e}")
            return []
    
    def generate_answer(self, question: str, context: List[Dict[str, Any]]) -> str:
        """基于上下文生成答案"""
        # 这里是预留接口，用户可以集成具体的生成模型
        # 例如：OpenAI GPT、本地LLM等
        
        if not context:
            return "抱歉，我没有找到相关的学习资料来回答您的问题。"
        
        # 构建上下文字符串
        context_text = "\n".join([doc.get('content', '') for doc in context[:3]])
        
        # 这里应该调用实际的生成模型
        # 目前返回一个模拟回答
        return f"基于课程资料，我为您找到了相关信息。请注意这是一个预留接口，需要集成具体的AI模型来生成详细回答。\n\n相关内容摘要：{context_text[:200]}..."

# 预留的Chroma集成示例
class ChromaVectorStore(VectorStoreInterface):
    """Chroma向量数据库实现示例"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        # 这里用户需要安装并导入chromadb
        # import chromadb
        # self.client = chromadb.PersistentClient(path=persist_directory)
        # self.collection = self.client.get_or_create_collection("education_system")
        
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """添加文档到Chroma数据库"""
        try:
            # 示例代码，需要用户实现
            # texts = [doc['content'] for doc in documents]
            # metadatas = [doc.get('metadata', {}) for doc in documents]
            # ids = [str(doc['id']) for doc in documents]
            # self.collection.add(documents=texts, metadatas=metadatas, ids=ids)
            return True
        except Exception as e:
            print(f"添加文档失败: {e}")
            return False
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """在Chroma中搜索相似文档"""
        try:
            # 示例代码，需要用户实现
            # results = self.collection.query(query_texts=[query], n_results=top_k)
            # return [{'content': doc, 'metadata': meta} for doc, meta in zip(results['documents'][0], results['metadatas'][0])]
            return []
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def delete_documents(self, document_ids: List[str]) -> bool:
        """删除文档"""
        try:
            # self.collection.delete(ids=document_ids)
            return True
        except Exception as e:
            print(f"删除文档失败: {e}")
            return False

# 全局RAG服务实例（需要用户初始化）
rag_service = None

def initialize_rag_service(vector_store_type: str = "chroma") -> RAGService:
    """初始化RAG服务"""
    global rag_service
    
    if vector_store_type == "chroma":
        vector_store = ChromaVectorStore()
    else:
        raise ValueError(f"不支持的向量数据库类型: {vector_store_type}")
    
    # 这里需要用户提供嵌入模型
    # embedding_model = YourEmbeddingModel()
    embedding_model = None  # 预留接口
    
    rag_service = RAGService(vector_store, embedding_model)
    return rag_service

def get_rag_service() -> Optional[RAGService]:
    """获取RAG服务实例"""
    return rag_service

