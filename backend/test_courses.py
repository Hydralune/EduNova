#!/usr/bin/env python3
"""
测试课程数据的简单脚本
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from models.course import Course
from extensions import db

def test_courses():
    """测试课程数据"""
    with app.app_context():
        try:
            courses = Course.query.all()
            print(f"找到 {len(courses)} 个课程:")
            for course in courses:
                print(f"  - ID: {course.id}, 名称: {course.name}")
            
            if not courses:
                print("没有找到任何课程数据")
                return False
            return True
        except Exception as e:
            print(f"查询课程时出错: {e}")
            return False

if __name__ == "__main__":
    test_courses() 