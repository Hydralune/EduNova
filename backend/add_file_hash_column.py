#!/usr/bin/env python3
"""
为Material表添加file_hash字段的简单脚本
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
import hashlib
from sqlalchemy import text

from backend.main import app
from backend.extensions import db
from backend.models.material import Material

def add_file_hash_column():
    """为Material表添加file_hash字段"""
    try:
        with app.app_context():
            print("=== 添加file_hash字段 ===")
            
            # 检查字段是否已存在
            try:
                result = db.session.execute(text("SELECT file_hash FROM material LIMIT 1"))
                print("✅ file_hash字段已存在")
                return
            except Exception:
                print("📝 需要添加file_hash字段")
            
            # 添加file_hash字段
            try:
                db.session.execute(text("ALTER TABLE material ADD COLUMN file_hash VARCHAR(64)"))
                db.session.commit()
                print("✅ 成功添加file_hash字段")
            except Exception as e:
                print(f"❌ 添加file_hash字段失败: {e}")
                db.session.rollback()
                return
            
            # 为现有文件计算哈希值
            print("🔄 为现有文件计算哈希值...")
            materials = Material.query.filter(Material.file_path.isnot(None)).all()
            
            for material in materials:
                try:
                    # 构建完整的文件路径
                    file_path = os.path.join(project_root, "backend", "uploads", material.file_path.lstrip('/'))
                    
                    if os.path.exists(file_path):
                        # 计算文件哈希
                        hash_sha256 = hashlib.sha256()
                        with open(file_path, "rb") as f:
                            for chunk in iter(lambda: f.read(4096), b""):
                                hash_sha256.update(chunk)
                        file_hash = hash_sha256.hexdigest()
                        
                        material.file_hash = file_hash
                        print(f"✅ 计算哈希: {material.title} -> {file_hash[:8]}...")
                    else:
                        print(f"⚠️  文件不存在: {file_path}")
                        
                except Exception as e:
                    print(f"❌ 处理文件失败 {material.title}: {e}")
            
            # 提交更改
            try:
                db.session.commit()
                print("✅ 所有文件哈希值计算完成")
            except Exception as e:
                print(f"❌ 提交更改失败: {e}")
                db.session.rollback()
                
    except Exception as e:
        print(f"❌ 执行失败: {e}")

if __name__ == "__main__":
    add_file_hash_column() 