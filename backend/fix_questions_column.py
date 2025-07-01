import sqlite3
import os
import json

def fix_questions_column():
    """修复assessments表中的questions列，确保不为NULL"""
    # 获取数据库文件路径
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'edunova.db')
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查questions列的约束
        cursor.execute("PRAGMA table_info(assessments)")
        columns = cursor.fetchall()
        questions_column = None
        
        for column in columns:
            if column[1] == 'questions':
                questions_column = column
                break
        
        if questions_column:
            # 检查是否是NOT NULL约束
            is_not_null = questions_column[3] == 1  # 第4个元素表示是否NOT NULL
            
            print(f"questions列信息: {questions_column}")
            print(f"NOT NULL约束: {'是' if is_not_null else '否'}")
            
            # 更新所有NULL值为空数组
            cursor.execute("UPDATE assessments SET questions = '[]' WHERE questions IS NULL")
            rows_updated = cursor.rowcount
            print(f"已更新 {rows_updated} 行NULL值为空数组")
            
            conn.commit()
            print("questions列修复完成")
        else:
            print("未找到questions列")
        
    except Exception as e:
        print(f"错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_questions_column() 