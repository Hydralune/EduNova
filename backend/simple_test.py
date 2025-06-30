import os
import sys
import logging
from pathlib import Path
import networkx as nx

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_direct_rag_query():
    """直接测试RAG查询，使用正确的路径"""
    try:
        # 导入必要的库
        from langchain_community.document_loaders import PyMuPDFLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.docstore.document import Document
        from langchain_chroma import Chroma
        
        # 定义嵌入函数
        class SimpleEmbeddingFunction:
            def __init__(self):
                pass
                
            def embed_documents(self, texts):
                # 简单的嵌入函数，返回1024维的零向量
                return [[0.0] * 1024 for _ in texts]
                
            def embed_query(self, text):
                # 简单的嵌入函数，返回1024维的零向量
                return [0.0] * 1024
        
        # 设置路径
        course_id = "1"
        
        # 检查两种可能的路径
        paths = [
            os.path.join(project_root, "uploads", "knowledge_base", course_id, "vectordb"),
            os.path.join(project_root, "backend", "uploads", "knowledge_base", course_id, "vectordb")
        ]
        
        vectordb_path = None
        for path in paths:
            if os.path.exists(path):
                vectordb_path = path
                logger.info(f"找到向量数据库路径: {path}")
                break
        
        if not vectordb_path:
            logger.error("无法找到向量数据库路径")
            return
            
        # 尝试加载向量数据库
        try:
            logger.info(f"尝试加载向量数据库: {vectordb_path}")
            
            # 创建简单的嵌入函数
            embedding_function = SimpleEmbeddingFunction()
            
            # 加载向量数据库
            vectorstore = Chroma(
                persist_directory=vectordb_path,
                embedding_function=embedding_function
            )
            
            # 检查向量数据库是否包含文档
            collection = vectorstore.get()
            doc_count = len(collection['documents']) if collection and 'documents' in collection else 0
            
            logger.info(f"向量数据库中包含 {doc_count} 个文档")
            
            if doc_count > 0:
                # 尝试一个简单的查询
                query = "数字电路的基本概念"
                logger.info(f"执行查询: '{query}'")
                
                # 使用相似度搜索
                results = vectorstore.similarity_search(query, k=2)
                
                logger.info(f"查询结果: 找到 {len(results)} 个匹配文档")
                
                # 显示结果
                for i, doc in enumerate(results):
                    logger.info(f"结果 {i+1}:")
                    logger.info(f"  内容: {doc.page_content[:100]}...")
                    logger.info(f"  元数据: {doc.metadata}")
            
        except Exception as e:
            logger.error(f"加载向量数据库失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    except ImportError as e:
        logger.error(f"导入必要的库失败: {str(e)}")

if __name__ == "__main__":
    logger.info("开始直接测试RAG查询")
    test_direct_rag_query() 