#!/usr/bin/env python3
"""
简单的课件上传测试脚本 - 直接测试后端API
"""

import requests
import os

# API基础URL
BASE_URL = 'http://localhost:5001/api'

def test_upload_direct():
    """直接测试上传功能"""
    
    print("=== 直接测试上传功能 ===\n")
    
    # 1. 创建测试文件
    print("1. 创建测试文件...")
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
    
    # 2. 测试上传API（不带认证）
    print("2. 测试上传API（不带认证）...")
    upload_data = {
        'course_id': '1',
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
            files=files
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 401:
            print("✓ 正确返回401未认证错误")
        else:
            print(f"✗ 意外的响应: {response.status_code}")
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")
    finally:
        # 清理测试文件
        try:
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
        except:
            pass
    
    print()
    
    # 3. 测试健康检查
    print("3. 测试健康检查...")
    try:
        response = requests.get(f'{BASE_URL}/health')
        print(f"健康检查状态码: {response.status_code}")
        print(f"健康检查内容: {response.text}")
    except Exception as e:
        print(f"✗ 健康检查异常: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == '__main__':
    test_upload_direct() 