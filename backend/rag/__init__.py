"""
RAG (Retrieval-Augmented Generation) module for EduNova

This module provides functionality for:
1. Processing documents and adding them to a vector database
2. Retrieving relevant documents based on a query
3. Using retrieved documents to enhance AI responses
"""

# 导出主要函数
from .rag_query import hybrid_retriever, initialize_resources, format_docs
from .segmentor import segment_text
from .query_expansion import expand_query, multi_query_expansion

# 避免循环导入，延迟导入
def get_process_document_with_progress():
    from backend.rag.create_db import process_document_with_progress
    return process_document_with_progress

def get_embedding_function():
    from backend.rag.embedding_util import get_embedding
    return get_embedding

def get_query_expansion():
    from backend.rag.query_expansion import expand_query, multi_query_expansion
    return expand_query, multi_query_expansion

__all__ = ['hybrid_retriever', 'initialize_resources', 'format_docs', 'segment_text', 'get_process_document_with_progress', 'get_embedding_function', 'get_query_expansion'] 