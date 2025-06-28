#!/usr/bin/env python3
"""
详细的课件上传调试脚本
"""

import requests
import os
import json

# API基础URL
BASE_URL = 'http://localhost:5001/api'

def debug_upload():
    """调试上传功能"""
    
    print("=== 课件上传调试 ===\n")
    
    # 1. 登录获取token
    print("1. 登录获取token...")
    login_data = {
        'username': 'teacher',
        'password': 'teacher123'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
        print(f"登录响应状态码: {response.status_code}")
        print(f"登录响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"✓ 登录成功，获取到token: {token[:20]}...")
            
            # 解析token（仅用于调试）
            import jwt
            try:
                decoded = jwt.decode(token, options={"verify_signature": False})
                print(f"Token内容: {json.dumps(decoded, indent=2)}")
            except:
                print("无法解析token")
        else:
            print(f"✗ 登录失败: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"✗ 登录异常: {e}")
        return
    
    print()
    
    # 2. 测试token有效性
    print("2. 测试token有效性...")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f'{BASE_URL}/learning/courses', headers=headers)
        print(f"课程列表响应状态码: {response.status_code}")
        if response.status_code == 200:
            print("✓ Token有效，可以访问课程列表")
        else:
            print(f"✗ Token无效: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"✗ 测试token异常: {e}")
        return
    
    print()
    
    # 3. 创建测试文件
    print("3. 创建测试文件...")
    test_file_path = 'debug_test.txt'
    test_content = "这是一个调试测试文件\n用于测试上传功能\n"
    
    try:
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print(f"✓ 测试文件创建成功: {test_file_path}")
    except Exception as e:
        print(f"✗ 创建测试文件失败: {e}")
        return
    
    print()
    
    # 4. 测试上传（详细调试）
    print("4. 测试上传（详细调试）...")
    upload_data = {
        'course_id': '1',
        'title': '调试测试课件',
        'description': '这是一个调试测试课件'
    }
    
    files = {
        'file': ('debug_test.txt', open(test_file_path, 'rb'), 'text/plain')
    }
    
    upload_headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        print(f"上传URL: {BASE_URL}/material/upload")
        print(f"上传数据: {upload_data}")
        print(f"上传headers: {upload_headers}")
        
        response = requests.post(
            f'{BASE_URL}/material/upload',
            data=upload_data,
            files=files,
            headers=upload_headers
        )
        
        print(f"上传响应状态码: {response.status_code}")
        print(f"上传响应headers: {dict(response.headers)}")
        print(f"上传响应内容: {response.text}")
        
        if response.status_code == 201:
            data = response.json()
            material_id = data['material']['id']
            print(f"✓ 课件上传成功，材料ID: {material_id}")
        else:
            print(f"✗ 课件上传失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"✗ 课件上传异常: {e}")
    finally:
        # 清理测试文件
        try:
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
        except:
            pass
    
    print("\n=== 调试完成 ===")

if __name__ == '__main__':
    debug_upload() 