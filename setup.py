#!/usr/bin/env python
"""
EduNova Setup Script
This script helps set up the EduNova project by installing dependencies and initializing the database.
"""

import os
import sys
from setuptools import setup, find_packages

# 确保PyInstaller在路径中
try:
    import PyInstaller
except ImportError:
    print("PyInstaller未安装，请先运行: pip install pyinstaller")
    sys.exit(1)

# 项目元数据
setup(
    name="EduNova",
    version="1.0.0",
    description="智能教学系统",
    author="EduNova Team",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
        "flask-cors",
        "pyinstaller"
    ],
)

# PyInstaller配置
if "build_exe" in sys.argv:
    import PyInstaller.__main__
    
    # 前端构建目录
    frontend_dist = os.path.join("frontend", "dist")
    
    # 确保前端已构建
    if not os.path.exists(frontend_dist):
        print("错误: 前端尚未构建。请先运行: cd frontend && npm run build")
        sys.exit(1)
    
    # PyInstaller参数
    PyInstaller.__main__.run([
        "backend/main.py",  # 入口文件
        "--name=EduNova",   # 可执行文件名称
        "--onefile",        # 单文件模式
        "--windowed",       # 无控制台窗口
        "--icon=frontend/public/favicon.ico",  # 应用图标
        # 添加数据文件
        "--add-data=frontend/dist;frontend/dist",  # 前端构建文件
        "--add-data=backend/templates;backend/templates",  # 后端模板
        "--add-data=backend/instance;backend/instance",  # 实例文件夹
        # 排除不需要的模块
        "--exclude-module=matplotlib",
        "--exclude-module=notebook",
        "--exclude-module=jupyter",
    ]) 