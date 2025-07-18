#!/usr/bin/env python3
"""
数据库迁移脚本 - 为Material表添加file_hash字段
"""

import sqlite3
import os
import sys

# 获取当前脚本的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
project_root = os.path.dirname(current_dir)

# 数据库路径
db_path = os.path.join(current_dir, 'eduNova.sqlite')  # 使用eduNova.sqlite文件

def migrate_knowledge_base_queue():
    """为KnowledgeBaseQueue表添加file_hash和purpose字段"""
    print(f"正在迁移数据库: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return False
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_base_queue'")
        if not cursor.fetchone():
            print("knowledge_base_queue表不存在，无需迁移")
            return True
        
        # 检查file_hash列是否存在
        cursor.execute("PRAGMA table_info(knowledge_base_queue)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'file_hash' not in columns:
            print("添加file_hash列...")
            cursor.execute("ALTER TABLE knowledge_base_queue ADD COLUMN file_hash TEXT")
            print("创建file_hash索引...")
            cursor.execute("CREATE INDEX idx_knowledge_base_queue_file_hash ON knowledge_base_queue(file_hash)")
        else:
            print("file_hash列已存在")
        
        if 'purpose' not in columns:
            print("添加purpose列...")
            cursor.execute("ALTER TABLE knowledge_base_queue ADD COLUMN purpose TEXT DEFAULT 'general'")
        else:
            print("purpose列已存在")
        
        conn.commit()
        print("迁移完成!")
        return True
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = migrate_knowledge_base_queue()
    sys.exit(0 if success else 1) 