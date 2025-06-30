"""
RAG (Retrieval-Augmented Generation) module for EduNova

This module provides functionality for:
1. Processing documents and adding them to a vector database
2. Retrieving relevant documents based on a query
3. Using retrieved documents to enhance AI responses
"""

# Import key functions for external use
from backend.rag.create_db import process_document_with_progress
from backend.rag.embedding_util import get_embedding

# 导出主要函数
from .rag_query import hybrid_retriever, initialize_resources, format_docs

__all__ = ['hybrid_retriever', 'initialize_resources', 'format_docs'] 