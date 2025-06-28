#!/usr/bin/env python3
import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 导入main.py中的Flask应用
from backend.main import app, create_tables

if __name__ == '__main__':
    # 初始化数据库
    create_tables()
    
    # 运行应用
    app.run(host='0.0.0.0', port=5001, debug=True)
