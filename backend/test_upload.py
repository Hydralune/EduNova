#!/usr/bin/env python3
"""
简单的课件上传测试脚本
"""

import requests
import os

# API基础URL
BASE_URL = 'http://localhost:5001/api'

def test_upload():
    """测试课件上传功能"""
    
    print("=== 课件上传测试 ===\n")
    
    # 1. 登录获取token
    print("1. 登录获取token...")
    login_data = {
        'username': 'teacher',
        'password': 'teacher123'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✓ 登录成功，获取到token")
        else:
            print(f"✗ 登录失败: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"✗ 登录异常: {e}")
        return
    
    print()
    
    # 2. 获取课程列表
    print("2. 获取课程列表...")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f'{BASE_URL}/learning/courses', headers=headers)
        if response.status_code == 200:
            data = response.json()
            courses = data.get('courses', [])
            print(f"✓ 成功获取课程列表，共 {len(courses)} 个课程")
            if courses:
                course_id = courses[0]['id']
                print(f"  使用课程ID: {course_id}")
            else:
                print("  没有找到课程，无法继续测试")
                return
        else:
            print(f"✗ 获取课程列表失败: {response.status_code}")
            return
    except Exception as e:
        print(f"✗ 获取课程列表异常: {e}")
        return
    
    print()
    
    # 3. 创建测试文件
    print("3. 创建测试文件...")
    test_file_path = 'test_upload.txt'
    test_content = "这是一个测试文件\n用于测试上传功能\n"
    
    try:
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print(f"✓ 测试文件创建成功: {test_file_path}")
    except Exception as e:
        print(f"✗ 创建测试文件失败: {e}")
        return
    
    print()
    
    # 4. 上传文件
    print("4. 测试上传文件...")
    upload_data = {
        'course_id': str(course_id),
        'title': '测试课件',
        'description': '这是一个测试课件'
    }
    
    files = {
        'file': ('test_upload.txt', open(test_file_path, 'rb'), 'text/plain')
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/material/upload',
            data=upload_data,
            files=files,
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 201:
            data = response.json()
            material_id = data['material']['id']
            print(f"✓ 课件上传成功，材料ID: {material_id}")
        else:
            print(f"✗ 课件上传失败: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"✗ 课件上传异常: {e}")
        return
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
    
    print("\n=== 测试完成 ===")

if __name__ == '__main__':
    test_upload() 