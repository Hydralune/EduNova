import sqlite3
import os

def add_created_by_column():
    """向assessments表添加created_by列"""
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
        # 检查created_by列是否已存在
        cursor.execute("PRAGMA table_info(assessments)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'created_by' not in columns:
            print("添加created_by列...")
            # 添加created_by列
            cursor.execute("ALTER TABLE assessments ADD COLUMN created_by INTEGER REFERENCES user(id)")
            
            # 设置默认值为1（假设ID为1的用户是管理员）
            cursor.execute("UPDATE assessments SET created_by = 1")
            
            conn.commit()
            print("created_by列添加成功")
        else:
            print("created_by列已存在")
        
    except Exception as e:
        print(f"错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_created_by_column() 