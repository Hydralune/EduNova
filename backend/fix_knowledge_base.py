#!/usr/bin/env python3
"""
知识库路径修复脚本
统一所有课程的知识库存储路径为 backend/uploads/knowledge_base/{course_id}/
"""

import os
import sys
import shutil
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def fix_knowledge_base_paths():
    """修复知识库路径，确保所有课程使用统一的路径"""
    
    # 定义路径
    materials_dir = os.path.join(project_root, "backend", "uploads", "materials")
    knowledge_base_dir = os.path.join(project_root, "backend", "uploads", "knowledge_base")
    
    print("=== 知识库路径修复工具 ===")
    print(f"材料目录: {materials_dir}")
    print(f"知识库目录: {knowledge_base_dir}")
    
    # 确保知识库目录存在
    os.makedirs(knowledge_base_dir, exist_ok=True)
    
    # 获取所有课程目录
    if not os.path.exists(materials_dir):
        print(f"❌ 材料目录不存在: {materials_dir}")
        return False
    
    course_dirs = []
    for item in os.listdir(materials_dir):
        item_path = os.path.join(materials_dir, item)
        if os.path.isdir(item_path) and item.isdigit():
            course_dirs.append(item)
    
    print(f"发现课程目录: {course_dirs}")
    
    # 处理每个课程
    for course_id in course_dirs:
        print(f"\n--- 处理课程 {course_id} ---")
        
        # 源目录（材料）
        source_dir = os.path.join(materials_dir, course_id)
        # 目标目录（知识库）
        target_dir = os.path.join(knowledge_base_dir, course_id)
        
        print(f"源目录: {source_dir}")
        print(f"目标目录: {target_dir}")
        
        # 检查源目录是否存在
        if not os.path.exists(source_dir):
            print(f"❌ 源目录不存在: {source_dir}")
            continue
        
        # 检查目标目录是否已存在
        if os.path.exists(target_dir):
            print(f"⚠️  目标目录已存在: {target_dir}")
            response = input("是否覆盖？(y/N): ").strip().lower()
            if response != 'y':
                print("跳过此课程")
                continue
        
        # 创建目标目录
        os.makedirs(target_dir, exist_ok=True)
        
        # 复制文件到知识库目录
        copied_files = []
        for filename in os.listdir(source_dir):
            source_file = os.path.join(source_dir, filename)
            target_file = os.path.join(target_dir, filename)
            
            if os.path.isfile(source_file):
                try:
                    shutil.copy2(source_file, target_file)
                    copied_files.append(filename)
                    print(f"✓ 复制文件: {filename}")
                except Exception as e:
                    print(f"❌ 复制文件失败 {filename}: {e}")
        
        print(f"✓ 课程 {course_id} 处理完成，复制了 {len(copied_files)} 个文件")
        
        # 创建处理状态文件
        status_file = os.path.join(target_dir, "processing_status.json")
        status_data = {
            "course_id": course_id,
            "source_dir": source_dir,
            "target_dir": target_dir,
            "copied_files": copied_files,
            "processed_at": int(time.time()),
            "status": "ready_for_processing"
        }
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 状态文件已创建: {status_file}")
    
    print("\n=== 修复完成 ===")
    print("现在你可以运行以下命令来创建向量数据库:")
    print("python backend/rag/create_db.py --course_id <课程ID>")
    return True

def create_vector_databases():
    """为所有课程创建向量数据库"""
    
    knowledge_base_dir = os.path.join(project_root, "backend", "uploads", "knowledge_base")
    
    if not os.path.exists(knowledge_base_dir):
        print(f"❌ 知识库目录不存在: {knowledge_base_dir}")
        return False
    
    # 获取所有课程目录
    course_dirs = []
    for item in os.listdir(knowledge_base_dir):
        item_path = os.path.join(knowledge_base_dir, item)
        if os.path.isdir(item_path) and item.isdigit():
            course_dirs.append(item)
    
    print(f"发现需要创建向量数据库的课程: {course_dirs}")
    
    for course_id in course_dirs:
        print(f"\n--- 为课程 {course_id} 创建向量数据库 ---")
        
        # 运行create_db.py
        import subprocess
        cmd = [sys.executable, "backend/rag/create_db.py", "--course_id", course_id]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
            if result.returncode == 0:
                print(f"✓ 课程 {course_id} 向量数据库创建成功")
            else:
                print(f"❌ 课程 {course_id} 向量数据库创建失败:")
                print(result.stderr)
        except Exception as e:
            print(f"❌ 执行命令失败: {e}")
    
    return True

if __name__ == "__main__":
    import time
    
    print("知识库路径修复工具")
    print("1. 修复知识库路径")
    print("2. 创建向量数据库")
    print("3. 执行完整流程")
    
    choice = input("请选择操作 (1/2/3): ").strip()
    
    if choice == "1":
        fix_knowledge_base_paths()
    elif choice == "2":
        create_vector_databases()
    elif choice == "3":
        if fix_knowledge_base_paths():
            create_vector_databases()
    else:
        print("无效选择") 