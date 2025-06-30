#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试RAG聊天功能

此脚本用于测试RAG系统与聊天功能的集成。
它将模拟一个简单的对话，并验证RAG检索和回答生成功能是否正常工作。
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入RAG模块
try:
    from rag_query import hybrid_retriever, format_docs, initialize_resources
except ImportError as e:
    print(f"导入RAG模块失败: {e}")
    sys.exit(1)

def test_rag_retrieval(course_id, query):
    """测试RAG检索功能"""
    print(f"\n=== 测试RAG检索功能 ===")
    print(f"课程ID: {course_id}")
    print(f"查询: {query}")
    
    try:
        # 获取检索结果
        docs = hybrid_retriever(query, course_id)
        
        print(f"\n找到 {len(docs)} 个相关文档片段:")
        
        for i, doc in enumerate(docs[:3], 1):  # 只显示前3个结果
            source = doc.metadata.get('source', '未知来源')
            print(f"\n--- 文档 {i} ---")
            print(f"来源: {os.path.basename(source)}")
            print(f"内容片段: {doc.page_content[:150]}...")
        
        if len(docs) > 3:
            print(f"\n... 还有 {len(docs) - 3} 个结果未显示 ...")
        
        return docs
    except Exception as e:
        print(f"检索失败: {e}")
        return []

def test_rag_chat(course_id, query):
    """测试完整的RAG聊天流程"""
    print(f"\n=== 测试RAG聊天流程 ===")
    print(f"课程ID: {course_id}")
    print(f"查询: {query}")
    
    try:
        # 初始化资源
        resources = initialize_resources(course_id)
        
        # 获取检索结果
        docs = hybrid_retriever(query, course_id)
        context = format_docs(docs)
        
        # 构建提示
        prompt = f"""你是一个智能教育助手，名为EduNova。你的任务是帮助学生解答问题、提供学习建议和解释复杂概念。
请基于以下参考资料回答用户的问题。如果参考资料中没有相关信息，请明确告知你无法从提供的资料中找到答案。
请保持回答友好、专业且易于理解。

参考资料:
{context}

问题: {query}

回答:"""
        
        # 调用LLM生成回答
        llm = resources['llm']
        response = llm.invoke(prompt)
        
        print("\n=== AI回答 ===")
        print(response.content)
        
        return response.content
    except Exception as e:
        print(f"生成回答失败: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="测试RAG聊天功能")
    parser.add_argument("--course_id", type=str, required=True, help="课程ID")
    parser.add_argument("--query", type=str, default="", help="测试查询")
    parser.add_argument("--mode", type=str, choices=["retrieval", "chat", "both"], default="both", 
                      help="测试模式: retrieval=仅测试检索, chat=测试完整聊天, both=两者都测试")
    args = parser.parse_args()
    
    # 如果没有提供查询，使用默认查询
    query = args.query
    if not query:
        query = "这门课程的主要内容是什么？"
    
    # 根据模式执行测试
    if args.mode in ["retrieval", "both"]:
        docs = test_rag_retrieval(args.course_id, query)
        if not docs and args.mode == "both":
            print("\n警告: 没有找到相关文档，无法继续测试聊天功能")
            return
    
    if args.mode in ["chat", "both"]:
        test_rag_chat(args.course_id, query)

if __name__ == "__main__":
    main() 