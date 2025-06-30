#!/usr/bin/env python3
"""
测试知识库管理功能
"""
import os
import sys
import requests
import json
import time

# 添加后端目录到Python路径
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

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
            return data.get('token')
        else:
            print(f"登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"登录错误: {e}")
        return None

def test_knowledge_base_management():
    """测试知识库管理功能"""
    base_url = "http://localhost:5001"
    
    # 获取token
    token = login_and_get_token()
    if not token:
        print("无法获取认证token，退出测试")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("=== 测试知识库管理功能 ===\n")
    
    # 1. 测试获取支持的文件类型
    print("1. 测试获取支持的文件类型")
    try:
        response = requests.get(f"{base_url}/api/rag/knowledge/supported-types", headers=headers)
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
        response = requests.get(f"{base_url}/api/courses", headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            courses = data.get('courses', [])
            print(f"课程数量: {len(courses)}")
            for course in courses[:3]:  # 只显示前3个
                print(f"  - {course['name']} (ID: {course['id']})")
        else:
            print(f"响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 3. 测试获取知识库状态
    print("\n3. 测试获取知识库状态")
    try:
        # 获取第一个课程的知识库状态
        response = requests.get(f"{base_url}/api/courses", headers=headers)
        if response.status_code == 200:
            courses = response.json().get('courses', [])
            if courses:
                course_id = courses[0]['id']
                kb_response = requests.get(f"{base_url}/api/rag/knowledge/status?course_id={course_id}", headers=headers)
                print(f"课程 {course_id} 知识库状态码: {kb_response.status_code}")
                if kb_response.status_code == 200:
                    kb_data = kb_response.json()
                    print(f"知识库状态: {kb_data}")
                else:
                    print(f"知识库状态响应: {kb_response.text}")
            else:
                print("没有找到课程")
        else:
            print("获取课程列表失败")
    except Exception as e:
        print(f"错误: {e}")
    
    # 4. 测试添加文件到知识库（模拟）
    print("\n4. 测试添加文件到知识库（模拟）")
    try:
        # 这里只是测试API调用，不实际添加文件
        test_data = {
            'course_id': 1,
            'file_path': '/test/path/document.pdf'
        }
        response = requests.post(f"{base_url}/api/rag/knowledge/add", json=test_data, headers=headers)
        print(f"添加文件状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"添加结果: {data}")
        else:
            print(f"添加响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 5. 测试删除文件（模拟）
    print("\n5. 测试删除文件（模拟）")
    try:
        # 这里只是测试API调用，不实际删除文件
        test_data = {
            'queue_id': 999  # 不存在的ID
        }
        response = requests.delete(f"{base_url}/api/rag/knowledge/remove", json=test_data, headers=headers)
        print(f"删除文件状态码: {response.status_code}")
        if response.status_code == 404:  # 应该返回404，因为ID不存在
            print("删除API正常工作（返回404，因为ID不存在）")
        else:
            print(f"删除响应: {response.text}")
    except Exception as e:
        print(f"错误: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_knowledge_base_management() 