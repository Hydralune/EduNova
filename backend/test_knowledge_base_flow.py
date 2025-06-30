#!/usr/bin/env python3
"""
测试知识库处理流程
"""
import os
import sys
import requests
import json
import time
import logging
from pathlib import Path

# 添加后端目录到Python路径
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def login_and_get_token():
    """登录并获取token"""
    base_url = "http://localhost:5001"
    
    # 尝试登录
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"登录错误: {e}")
        return None

def test_knowledge_base_flow():
    """测试完整的知识库处理流程"""
    base_url = "http://localhost:5001"
    
    print("=== 测试知识库处理流程 ===")
    
    # 获取认证token
    print("\n0. 获取认证token")
    token = login_and_get_token()
    if not token:
        print("无法获取认证token，跳过需要认证的测试")
        headers = {}
    else:
        print("认证成功")
        headers = {'Authorization': f'Bearer {token}'}
    
    # 1. 测试获取支持的文件类型
    print("\n1. 测试获取支持的文件类型")
    try:
        response = requests.get(f"{base_url}/api/rag/knowledge/supported-types")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"支持的文件类型: {data}")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 2. 测试获取课程列表
    print("\n2. 测试获取课程列表")
    try:
        response = requests.get(f"{base_url}/api/courses")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            courses = data.get('courses', [])
            print(f"找到 {len(courses)} 个课程")
            for course in courses:
                print(f"  - {course['name']} (ID: {course['id']})")
            
            # 选择第一个课程进行测试
            if courses:
                test_course_id = courses[0]['id']
                print(f"选择课程 ID: {test_course_id} 进行测试")
            else:
                print("没有找到课程，无法继续测试")
                return
        else:
            print(f"响应: {response.text}")
            return
    except Exception as e:
        print(f"错误: {e}")
        return
    
    # 3. 测试获取课程材料
    print(f"\n3. 测试获取课程 {test_course_id} 的材料")
    try:
        response = requests.get(f"{base_url}/api/courses/{test_course_id}/materials")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            materials = data.get('materials', [])
            print(f"找到 {len(materials)} 个材料")
            
            # 查找支持知识库的材料
            supported_materials = []
            for material in materials:
                if material.get('file_path'):
                    file_ext = os.path.splitext(material['file_path'])[1].lower()
                    if file_ext in ['.pdf', '.docx', '.doc', '.txt', '.md']:
                        supported_materials.append(material)
            
            print(f"其中 {len(supported_materials)} 个材料支持知识库")
            for material in supported_materials:
                print(f"  - {material['title']} ({material['file_path']})")
            
            if supported_materials:
                test_material = supported_materials[0]
                print(f"选择材料: {test_material['title']} 进行测试")
            else:
                print("没有找到支持知识库的材料，无法继续测试")
                return
        else:
            print(f"响应: {response.text}")
            return
    except Exception as e:
        print(f"错误: {e}")
        return
    
    # 4. 测试添加到知识库（需要认证）
    if token:
        print(f"\n4. 测试添加材料到知识库")
        try:
            data = {
                'course_id': test_course_id,
                'file_path': test_material['file_path']
            }
            response = requests.post(f"{base_url}/api/rag/knowledge/add", json=data, headers=headers)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"添加成功: {result}")
                queue_id = result.get('queue_id')
            else:
                print(f"响应: {response.text}")
                return
        except Exception as e:
            print(f"错误: {e}")
            return
        
        # 5. 测试获取知识库状态（需要认证）
        print(f"\n5. 测试获取知识库状态")
        try:
            response = requests.get(f"{base_url}/api/rag/knowledge/status?course_id={test_course_id}", headers=headers)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                print(f"队列中有 {len(items)} 个项目")
                for item in items:
                    print(f"  - {item['file_path']}: {item['status']} ({item.get('progress', 0)}%)")
            else:
                print(f"响应: {response.text}")
        except Exception as e:
            print(f"错误: {e}")
        
        # 6. 测试RAG聊天（需要认证）
        print(f"\n6. 测试RAG聊天")
        try:
            data = {
                'message': '请介绍一下这个课程的主要内容',
                'course_id': test_course_id,
                'use_rag': True,
                'stream': False
            }
            response = requests.post(f"{base_url}/api/rag/chat", json=data, headers=headers)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"聊天响应: {result.get('message', '无响应')[:100]}...")
            else:
                print(f"响应: {response.text}")
        except Exception as e:
            print(f"错误: {e}")
    else:
        print("\n跳过需要认证的测试（4-6）")

def check_knowledge_base_paths():
    """检查知识库路径和文件是否存在"""
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 检查可能的知识库路径
    possible_paths = [
        os.path.join(project_root, "uploads", "knowledge_base", "1"),
        os.path.join(project_root, "backend", "uploads", "knowledge_base", "1"),
        os.path.join(project_root, "backend", "backend", "uploads", "knowledge_base", "1")
    ]
    
    for path in possible_paths:
        vectordb_path = os.path.join(path, "vectordb")
        logger.info(f"检查路径: {path}")
        logger.info(f"  - 目录存在: {os.path.exists(path)}")
        
        logger.info(f"检查向量数据库: {vectordb_path}")
        logger.info(f"  - 向量数据库存在: {os.path.exists(vectordb_path)}")
        
        if os.path.exists(vectordb_path):
            # 列出向量数据库中的文件
            files = os.listdir(vectordb_path)
            logger.info(f"  - 向量数据库文件: {files}")
    
    # 检查配置文件中的路径设置
    try:
        from backend.config.knowledge_base_config import KnowledgeBaseConfig
        logger.info(f"配置文件中的知识库路径: {KnowledgeBaseConfig.KNOWLEDGE_BASE_DIR}")
        
        # 获取课程1的知识库路径
        kb_path = KnowledgeBaseConfig.get_knowledge_base_path("1")
        vector_db_path = KnowledgeBaseConfig.get_vector_db_path("1")
        
        logger.info(f"配置的知识库路径: {kb_path}")
        logger.info(f"  - 目录存在: {os.path.exists(kb_path)}")
        
        logger.info(f"配置的向量数据库路径: {vector_db_path}")
        logger.info(f"  - 向量数据库存在: {os.path.exists(vector_db_path)}")
    except ImportError:
        logger.error("无法导入知识库配置")

def test_rag_query():
    """测试RAG查询功能"""
    try:
        # 导入RAG查询函数
        from backend.rag.rag_query import hybrid_retriever, format_docs
        
        # 测试查询
        course_id = "1"
        query = "数字电路的基本概念是什么？"
        
        logger.info(f"执行RAG查询，课程ID: {course_id}, 查询: '{query}'")
        
        try:
            # 尝试查询
            docs = hybrid_retriever(query, course_id)
            
            if docs:
                logger.info(f"查询成功，找到 {len(docs)} 个相关文档")
                # 打印第一个文档的内容
                if len(docs) > 0:
                    logger.info(f"第一个文档内容: {docs[0].page_content[:100]}...")
                    logger.info(f"第一个文档元数据: {docs[0].metadata}")
            else:
                logger.warning("查询成功，但没有找到相关文档")
                
        except Exception as e:
            logger.error(f"查询失败: {str(e)}")
            # 打印详细错误信息
            import traceback
            logger.error(traceback.format_exc())
    except ImportError:
        logger.error("无法导入RAG查询模块")

if __name__ == "__main__":
    logger.info("开始检查知识库路径")
    check_knowledge_base_paths()
    
    logger.info("\n开始测试RAG查询")
    test_rag_query()

    test_knowledge_base_flow() 