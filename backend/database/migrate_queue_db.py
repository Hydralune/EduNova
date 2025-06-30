#!/usr/bin/env python3
"""
数据库迁移脚本 - 为Material表添加file_hash字段
"""

import os
import sys
import hashlib

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.extensions import db
from backend.models.material import Material
from backend.main import create_app

def calculate_file_hash(file_path):
    """计算文件的SHA256哈希值"""
    if not os.path.exists(file_path):
        return None
    
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def migrate_material_table():
    """迁移Material表，添加file_hash字段"""
    app = create_app()
    
    with app.app_context():
        print("=== 开始数据库迁移 ===")
        
        # 检查file_hash字段是否存在
        try:
            # 尝试查询file_hash字段
            result = db.session.execute("SELECT file_hash FROM material LIMIT 1")
            print("✅ file_hash字段已存在")
            return
        except Exception as e:
            print("📝 需要添加file_hash字段")
        
        # 添加file_hash字段
        try:
            db.session.execute("ALTER TABLE material ADD COLUMN file_hash VARCHAR(64)")
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
                file_path = os.path.join(project_root, "backend", material.file_path.lstrip('/'))
                
                if os.path.exists(file_path):
                    # 计算文件哈希
                    file_hash = calculate_file_hash(file_path)
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

if __name__ == "__main__":
    migrate_material_table() 