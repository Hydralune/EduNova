import os
import sys
import json
import time
import requests
import shutil
import argparse
import sqlite3
from pathlib import Path

# 配置参数
API_BASE_URL = "http://localhost:5001/api"
PDF_FILE_PATH = "example\python.pdf"
USERNAME = "admin"
PASSWORD = "admin123"
COURSE_ID = None  # 将在脚本中获取或创建课程
UPLOAD_FOLDER = Path("backend/uploads")  # 上传文件夹路径
QUEUE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rag_queue.db")

def login():
    """登录并获取令牌"""
    print("正在登录...")
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={"username": USERNAME, "password": PASSWORD}
    )
    
    if response.status_code != 200:
        print(f"登录失败: {response.text}")
        sys.exit(1)
    
    token = response.json().get("token")
    print("登录成功!")
    return token

def get_headers(token):
    """获取带有授权令牌的请求头"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def get_or_create_course(token):
    """获取现有课程或创建新课程"""
    global COURSE_ID
    
    # 获取课程列表
    print("正在获取课程列表...")
    response = requests.get(
        f"{API_BASE_URL}/courses",
        headers=get_headers(token)
    )
    
    if response.status_code != 200:
        print(f"获取课程列表失败: {response.text}")
        sys.exit(1)
    
    courses = response.json().get("courses", [])
    
    # 如果有课程，使用第一个
    if courses:
        COURSE_ID = courses[0]["id"]
        print(f"使用现有课程: ID={COURSE_ID}, 名称={courses[0]['name']}")
        return COURSE_ID
    
    # 如果没有课程，创建一个新课程
    print("没有找到课程，正在创建新课程...")
    response = requests.post(
        f"{API_BASE_URL}/courses",
        headers=get_headers(token),
        json={
            "name": "量子计算测试课程",
            "description": "用于测试RAG功能的课程",
            "category": "计算机科学",
            "difficulty": "中级"
        }
    )
    
    if response.status_code != 201:
        print(f"创建课程失败: {response.text}")
        sys.exit(1)
    
    COURSE_ID = response.json().get("id")
    print(f"成功创建新课程: ID={COURSE_ID}")
    return COURSE_ID

def upload_pdf_to_course(token, course_id):
    """将PDF文件上传到课程"""
    print(f"正在上传PDF文件到课程 {course_id}...")
    
    # 检查文件是否存在
    if not os.path.exists(PDF_FILE_PATH):
        print(f"文件不存在: {PDF_FILE_PATH}")
        sys.exit(1)
    
    print(f"文件存在，大小: {os.path.getsize(PDF_FILE_PATH)} 字节")
    
    # 准备文件上传
    with open(PDF_FILE_PATH, "rb") as file:
        files = {"file": (os.path.basename(PDF_FILE_PATH), file)}
        response = requests.post(
            f"{API_BASE_URL}/courses/{course_id}/materials",
            headers={"Authorization": f"Bearer {token}"},
            files=files
        )
    
    if response.status_code != 201:
        print(f"上传文件失败: {response.text}")
        sys.exit(1)
    
    material = response.json()
    print(f"文件上传成功: ID={material.get('id')}, 路径={material.get('file_path')}")
    
    # 列出课程材料目录中的文件
    materials_dir = UPLOAD_FOLDER / f"materials/{course_id}"
    if materials_dir.exists():
        print(f"课程材料目录内容:")
        for item in materials_dir.iterdir():
            print(f"  - {item.name} ({item.stat().st_size} 字节)")
            
            # 如果找到了我们上传的文件，使用它的路径
            if item.name == os.path.basename(PDF_FILE_PATH):
                print(f"找到了上传的文件: {item}")
                material['actual_file_path'] = str(item)
    
    return material

def add_to_knowledge_base(token, course_id, file_path):
    """将文件添加到知识库"""
    print(f"正在将文件添加到知识库... 文件路径: {file_path}")
    
    # 确保文件路径格式正确
    if file_path.startswith('/'):
        file_path = file_path[1:]  # 移除开头的斜杠
    
    # 移除可能的 'uploads/' 前缀
    if file_path.startswith('uploads/'):
        file_path = file_path[8:]  # 移除 'uploads/' 前缀
    
    # 使用上传的文件路径
    correct_path = file_path
    print(f"使用文件路径: {correct_path}")
    
    # 检查文件是否存在
    server_file_path = UPLOAD_FOLDER / correct_path
    print(f"检查知识库文件路径: {server_file_path}")
    
    if not server_file_path.exists():
        print(f"错误: 文件在服务器上不存在: {server_file_path}")
        sys.exit(1)
    
    # 修改API端点，使用立即处理的接口而不是队列
    response = requests.post(
        f"{API_BASE_URL}/rag/knowledge/process_now",  # 新的API端点
        headers=get_headers(token),
        json={
            "course_id": course_id,
            "file_path": correct_path
        }
    )
    
    print(f"服务器响应: {response.status_code} - {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("status") == "success":
            print(f"文件处理成功: {result.get('message', '')}")
            return True
        else:
            print(f"处理失败: {result.get('message', '未知错误')}")
            return False
    else:
        print(f"API请求失败，状态码: {response.status_code}")
        return False

def get_queue_status_from_db(queue_id):
    """从本地数据库获取队列状态"""
    if not os.path.exists(QUEUE_DB_PATH):
        return None
        
    try:
        conn = sqlite3.connect(QUEUE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取队列状态
        cursor.execute("SELECT * FROM queue_status WHERE id = ?", (queue_id,))
        item = cursor.fetchone()
        
        if not item:
            return None
            
        # 获取最近的处理日志
        cursor.execute("""
            SELECT * FROM processing_log 
            WHERE queue_id = ? 
            ORDER BY timestamp DESC LIMIT 5
        """, (queue_id,))
        logs = cursor.fetchall()
        
        result = dict(item)
        result['logs'] = [dict(log) for log in logs]
        
        conn.close()
        return result
    except Exception as e:
        print(f"获取队列状态出错: {str(e)}")
        return None

def monitor_processing(token, course_id, queue_id):
    """监控知识库处理进度"""
    print("开始监控处理进度...")
    
    last_progress = -1
    last_status = None
    start_time = time.time()
    check_interval = 2  # 每2秒检查一次
    max_wait_time = 300  # 最长等待5分钟
    
    while time.time() - start_time < max_wait_time:
        # 首先尝试从本地数据库获取状态
        db_status = get_queue_status_from_db(queue_id)
        
        if db_status:
            status = db_status['status']
            progress = db_status['progress']
            
            # 如果状态或进度发生变化，则打印
            if status != last_status or abs(progress - last_progress) >= 1.0:
                last_status = status
                last_progress = progress
                elapsed_time = time.time() - start_time
                
                # 打印状态信息
                print(f"[{elapsed_time:.1f}秒] 处理状态: {status}, 进度: {progress:.1f}%")
                
                # 如果有日志，打印最新的日志
                if db_status.get('logs'):
                    latest_log = db_status['logs'][0]  # 最新的日志
                    print(f"  详情: [{latest_log['stage']}] {latest_log['message']}")
                
                # 如果处理完成或失败，退出循环
                if status == 'completed':
                    print("处理完成!")
                    return True
                elif status == 'failed':
                    error_message = db_status.get('error_message', '未知错误')
                    print(f"处理失败: {error_message}")
                    return False
        
        # 如果本地数据库没有状态信息，则从API获取
        response = requests.get(
            f"{API_BASE_URL}/rag/knowledge/status?course_id={course_id}",
            headers=get_headers(token)
        )
        
        if response.status_code != 200:
            print(f"获取状态失败: {response.text}")
            time.sleep(check_interval)
            continue
        
        items = response.json().get("items", [])
        queue_item = next((item for item in items if item["id"] == queue_id), None)
        
        if not queue_item:
            print("找不到队列项，可能已被删除")
            break
        
        status = queue_item.get("status")
        progress = queue_item.get("progress", 0)
        
        # 如果状态或进度发生变化，则打印
        if status != last_status or abs(progress - last_progress) >= 1.0:
            last_status = status
            last_progress = progress
            elapsed_time = time.time() - start_time
            
            # 打印状态信息
            print(f"[{elapsed_time:.1f}秒] 处理状态: {status}, 进度: {progress:.1f}%")
            
            # 如果有进度详情，打印详情
            if queue_item.get("progress_detail"):
                detail = queue_item["progress_detail"]
                if detail and isinstance(detail, dict):
                    print(f"  详情: [{detail.get('stage', 'unknown')}] {detail.get('message', '')}")
            
            # 如果处理完成或失败，退出循环
            if status == 'completed':
                print("处理完成!")
                return True
            elif status == 'failed':
                error_message = queue_item.get("error_message", "未知错误")
                print(f"处理失败: {error_message}")
                return False
            elif status == 'pending' and elapsed_time > 30:
                print("\n文件仍在等待处理中。您可能需要运行以下命令来处理队列：")
                print("python process_queue.py --process-id", queue_id)
                print("\n继续监控...")
        
        time.sleep(check_interval)
    
    print("监控超时，请手动检查处理状态")
    return False

def test_rag_chat(token, course_id):
    """测试使用知识库进行聊天"""
    print("测试与知识库聊天...")
    
    # 使用与Python相关的问题
    test_questions = [
        "Python编程有哪些基本概念？",
        "什么是Python的变量和数据类型？",
        "Python中如何定义函数？",
        "Python编程有什么特点？"
    ]
    
    for question in test_questions:
        print(f"\n问题: {question}")
        
        response = requests.post(
            f"{API_BASE_URL}/rag/chat",
            headers=get_headers(token),
            json={
                "message": question,
                "course_id": course_id,
                "use_rag": True
            }
        )
        
        if response.status_code != 200:
            print(f"聊天请求失败: {response.text}")
            continue
        
        result = response.json()
        print(f"回复: {result.get('message', '无回复')}")
        print("-" * 50)

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='测试RAG文件上传和处理')
    parser.add_argument('--chat-only', action='store_true', help='只进行聊天测试，不上传文件')
    parser.add_argument('--auto-process', action='store_true', help='自动处理队列')
    parser.add_argument('--queue-id', type=int, help='指定要处理的队列ID')
    args = parser.parse_args()
    
    # 登录获取token
    token = login()
    
    if args.chat_only:
        # 只进行聊天测试
        test_rag_chat(token, 1)
        return
    
    # 上传文件并添加到知识库
    course_id = get_or_create_course(token)
    material = upload_pdf_to_course(token, course_id)
    success = add_to_knowledge_base(token, course_id, material.get("file_path"))
    
    if not success:
        print("文件处理失败，无法继续测试")
        return
    
    # 如果处理成功，测试聊天
    print("文件处理成功，开始测试聊天...")
    test_rag_chat(token, course_id)

if __name__ == "__main__":
    main() 