import os
import sys
import time
import logging
import json
import sqlite3
import argparse

# 设置环境变量
os.environ["LLM_API_KEY"] = "sk-dfthbfklqzgxhhrfiwukmgfakpcfuletjjvapquirwwcuteh"  # 替换为实际的API密钥
os.environ["LLM_API_BASE"] = "https://api.siliconflow.cn/v1"
os.environ["LLM_MODEL"] = "deepseek-chat"
os.environ["EMBEDDING_MODEL"] = "BAAI/bge-large-zh-v1.5"

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建一个单独的队列状态数据库
QUEUE_DB_PATH = os.path.join(current_dir, "rag_queue.db")

def init_queue_db():
    """初始化队列状态数据库"""
    conn = sqlite3.connect(QUEUE_DB_PATH)
    cursor = conn.cursor()
    
    # 创建队列状态表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS queue_status (
        id INTEGER PRIMARY KEY,
        course_id INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at INTEGER,
        updated_at INTEGER,
        completed_at INTEGER,
        error_message TEXT,
        progress REAL DEFAULT 0.0,
        progress_detail TEXT
    )
    ''')
    
    # 创建处理日志表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS processing_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        queue_id INTEGER,
        timestamp INTEGER,
        stage TEXT,
        message TEXT,
        progress REAL,
        FOREIGN KEY (queue_id) REFERENCES queue_status (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    logger.info(f"队列状态数据库初始化完成: {QUEUE_DB_PATH}")

def sync_with_flask_db():
    """从Flask数据库同步队列状态到本地数据库"""
    # 导入Flask应用和模型
    from backend.main import app
    from backend.models.learning import KnowledgeBaseQueue
    from backend.extensions import db
    
    # 连接到本地数据库
    conn = sqlite3.connect(QUEUE_DB_PATH)
    cursor = conn.cursor()
    
    with app.app_context():
        # 获取所有队列项
        queue_items = KnowledgeBaseQueue.query.all()
        
        for item in queue_items:
            # 检查本地数据库中是否存在此项
            cursor.execute("SELECT id FROM queue_status WHERE id = ?", (item.id,))
            exists = cursor.fetchone()
            
            progress_detail = item.progress_detail or '{}'
            
            if exists:
                # 更新现有项
                cursor.execute('''
                UPDATE queue_status
                SET status = ?, progress = ?, progress_detail = ?, updated_at = ?,
                    completed_at = ?, error_message = ?
                WHERE id = ?
                ''', (
                    item.status, item.progress, progress_detail,
                    item.last_updated, item.completed_at, item.error_message, item.id
                ))
            else:
                # 插入新项
                cursor.execute('''
                INSERT INTO queue_status (id, course_id, file_path, status, created_at, 
                                         updated_at, completed_at, error_message, progress, progress_detail)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.id, item.course_id, item.file_path, item.status,
                    item.created_at, item.last_updated, item.completed_at,
                    item.error_message, item.progress, progress_detail
                ))
                
            # 记录处理日志
            if item.progress_detail:
                try:
                    detail = json.loads(item.progress_detail)
                    cursor.execute('''
                    INSERT INTO processing_log (queue_id, timestamp, stage, message, progress)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (
                        item.id, detail.get('timestamp', int(time.time())),
                        detail.get('stage', 'unknown'), detail.get('message', ''),
                        detail.get('progress', item.progress)
                    ))
                except json.JSONDecodeError:
                    pass
    
    conn.commit()
    conn.close()
    logger.info("已同步队列状态到本地数据库")

def update_flask_db_from_local(queue_id, status, progress, message=None):
    """从本地数据库更新Flask数据库中的队列状态"""
    # 导入Flask应用和模型
    from backend.main import app
    from backend.models.learning import KnowledgeBaseQueue
    from backend.extensions import db
    
    with app.app_context():
        queue_item = db.session.get(KnowledgeBaseQueue, queue_id)
        if queue_item:
            queue_item.status = status
            queue_item.progress = progress
            
            if message:
                queue_item.error_message = message
                
            if status == 'completed':
                queue_item.completed_at = int(time.time())
                
            queue_item.last_updated = int(time.time())
            
            # 更新进度详情
            progress_detail = {
                "stage": status,
                "progress": progress,
                "message": message or f"处理进度: {progress:.1f}%",
                "timestamp": int(time.time())
            }
            queue_item.progress_detail = json.dumps(progress_detail)
            
            db.session.commit()
            logger.info(f"已更新队列项 {queue_id} 在Flask数据库中的状态: {status}, 进度: {progress:.1f}%")
            return True
        else:
            logger.error(f"在Flask数据库中找不到队列项 {queue_id}")
            return False

def process_knowledge_queue(queue_id):
    """处理知识库队列项"""
    # 导入Flask应用和模型
    from backend.main import app
    from backend.models.learning import KnowledgeBaseQueue
    from backend.extensions import db
    
    with app.app_context():
        # 获取队列项
        queue_item = db.session.get(KnowledgeBaseQueue, queue_id)
        if not queue_item:
            logger.error(f"队列项 {queue_id} 不存在")
            return False
        
        try:
            # 更新状态为处理中
            queue_item.status = 'processing'
            queue_item.last_updated = int(time.time())
            queue_item.progress_detail = json.dumps({
                "stage": "initializing",
                "message": "正在初始化处理",
                "timestamp": int(time.time())
            })
            db.session.commit()
            
            # 同步到本地数据库
            sync_with_flask_db()
            
            # 定义进度回调函数
            def progress_callback(progress, stage=None, message=None):
                with app.app_context():
                    # 获取最新的队列项
                    current_item = db.session.get(KnowledgeBaseQueue, queue_id)
                    if not current_item:
                        logger.error(f"在进度更新期间找不到队列项 {queue_id}")
                        return
                    
                    if progress < 0:
                        # 发生错误
                        current_item.status = 'failed'
                        current_item.error_message = message or "处理失败"
                        current_item.last_updated = int(time.time())
                    else:
                        current_item.progress = progress
                        
                        # 更新进度详情
                        progress_detail = {
                            "stage": stage or "processing",
                            "progress": progress,
                            "message": message or f"处理进度: {progress:.1f}%",
                            "timestamp": int(time.time())
                        }
                        current_item.progress_detail = json.dumps(progress_detail)
                        current_item.last_updated = int(time.time())
                        
                        logger.info(f"队列项 {queue_id}: {progress:.1f}% - {message or '处理中'}")
                    
                    db.session.commit()
                    
                    # 同步到本地数据库
                    sync_with_flask_db()
            
            # 获取文件的完整路径
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], queue_item.file_path.lstrip('/'))
            
            logger.info(f"处理文件: {file_path}, 课程ID: {queue_item.course_id}")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                progress_callback(-1, "error", f"文件不存在: {queue_item.file_path}")
                return False
            
            # 导入处理函数
            from backend.rag.create_db import process_document_with_progress
            
            # 处理文档
            success = process_document_with_progress(
                course_id=str(queue_item.course_id),
                file_path=file_path,
                progress_callback=progress_callback
            )
            
            # 根据结果更新状态
            queue_item = db.session.get(KnowledgeBaseQueue, queue_id)
            if not queue_item:
                logger.error(f"处理后找不到队列项 {queue_id}")
                return False
                
            if success:
                queue_item.status = 'completed'
                queue_item.completed_at = int(time.time())
                queue_item.progress = 100.0
                queue_item.progress_detail = json.dumps({
                    "stage": "completed",
                    "progress": 100.0,
                    "message": "处理完成",
                    "timestamp": int(time.time())
                })
                queue_item.last_updated = int(time.time())
                logger.info(f"成功处理队列项 {queue_id}")
            else:
                queue_item.status = 'failed'
                if not queue_item.error_message:
                    queue_item.error_message = "未知错误"
                queue_item.progress_detail = json.dumps({
                    "stage": "failed",
                    "message": queue_item.error_message,
                    "timestamp": int(time.time())
                })
                queue_item.last_updated = int(time.time())
                logger.error(f"处理队列项 {queue_id} 失败")
            
            db.session.commit()
            
            # 同步到本地数据库
            sync_with_flask_db()
            
            return success
            
        except Exception as e:
            logger.error(f"处理队列项 {queue_id} 时出错: {str(e)}")
            # 更新状态为失败
            try:
                with app.app_context():
                    queue_item = db.session.get(KnowledgeBaseQueue, queue_id)
                    if queue_item:
                        queue_item.status = 'failed'
                        queue_item.error_message = str(e)
                        queue_item.progress_detail = json.dumps({
                            "stage": "error",
                            "message": str(e),
                            "timestamp": int(time.time())
                        })
                        queue_item.last_updated = int(time.time())
                        db.session.commit()
                        
                        # 同步到本地数据库
                        sync_with_flask_db()
            except Exception as inner_e:
                logger.error(f"更新队列项状态失败: {str(inner_e)}")
            return False

def process_pending_queue_items():
    """处理所有待处理的队列项"""
    # 导入Flask应用和模型
    from backend.main import app
    from backend.models.learning import KnowledgeBaseQueue
    
    with app.app_context():
        # 获取所有待处理的队列项
        pending_items = KnowledgeBaseQueue.query.filter_by(status='pending').all()
        
        if not pending_items:
            logger.info("没有找到待处理的队列项。")
            return
        
        logger.info(f"找到 {len(pending_items)} 个待处理的队列项。")
        
        # 处理每个项
        for item in pending_items:
            logger.info(f"处理队列项 {item.id}, 课程ID: {item.course_id}, 文件: {item.file_path}")
            success = process_knowledge_queue(item.id)
            if success:
                logger.info(f"成功处理队列项 {item.id}。")
            else:
                logger.error(f"处理队列项 {item.id} 失败。")

def get_queue_status(queue_id=None, course_id=None):
    """获取队列状态"""
    # 连接到本地数据库
    conn = sqlite3.connect(QUEUE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if queue_id:
        # 获取特定队列项的状态
        cursor.execute('''
        SELECT * FROM queue_status WHERE id = ?
        ''', (queue_id,))
        item = cursor.fetchone()
        
        if item:
            # 获取处理日志
            cursor.execute('''
            SELECT * FROM processing_log WHERE queue_id = ? ORDER BY timestamp DESC LIMIT 10
            ''', (queue_id,))
            logs = cursor.fetchall()
            
            result = dict(item)
            result['logs'] = [dict(log) for log in logs]
            
            conn.close()
            return result
        else:
            conn.close()
            return None
    
    elif course_id:
        # 获取特定课程的所有队列项
        cursor.execute('''
        SELECT * FROM queue_status WHERE course_id = ? ORDER BY created_at DESC
        ''', (course_id,))
        items = cursor.fetchall()
        
        result = [dict(item) for item in items]
        conn.close()
        return result
    
    else:
        # 获取所有队列项
        cursor.execute('''
        SELECT * FROM queue_status ORDER BY created_at DESC
        ''')
        items = cursor.fetchall()
        
        result = [dict(item) for item in items]
        conn.close()
        return result

def display_queue_status(queue_id=None, course_id=None):
    """显示队列状态"""
    if queue_id:
        # 显示特定队列项的状态
        item = get_queue_status(queue_id=queue_id)
        if item:
            print(f"\n队列项 {item['id']} 状态:")
            print(f"  课程ID: {item['course_id']}")
            print(f"  文件路径: {item['file_path']}")
            print(f"  状态: {item['status']}")
            print(f"  进度: {item['progress']:.1f}%")
            print(f"  创建时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['created_at']))}")
            if item['completed_at']:
                print(f"  完成时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['completed_at']))}")
            if item['error_message']:
                print(f"  错误信息: {item['error_message']}")
            
            if item['logs']:
                print("\n处理日志:")
                for log in item['logs']:
                    log_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log['timestamp']))
                    print(f"  [{log_time}] {log['stage']}: {log['message']}")
        else:
            print(f"找不到队列项 {queue_id}")
    
    elif course_id:
        # 显示特定课程的所有队列项
        items = get_queue_status(course_id=course_id)
        if items:
            print(f"\n课程 {course_id} 的队列项:")
            for item in items:
                print(f"  ID: {item['id']}, 文件: {os.path.basename(item['file_path'])}, 状态: {item['status']}, 进度: {item['progress']:.1f}%")
        else:
            print(f"课程 {course_id} 没有队列项")
    
    else:
        # 显示所有队列项
        items = get_queue_status()
        if items:
            print("\n所有队列项:")
            for item in items:
                print(f"  ID: {item['id']}, 课程: {item['course_id']}, 文件: {os.path.basename(item['file_path'])}, 状态: {item['status']}, 进度: {item['progress']:.1f}%")
        else:
            print("没有队列项")

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="RAG知识库处理队列管理工具")
    parser.add_argument('--process', action='store_true', help='处理所有待处理的队列项')
    parser.add_argument('--process-id', type=int, help='处理特定ID的队列项')
    parser.add_argument('--status', action='store_true', help='显示所有队列项的状态')
    parser.add_argument('--status-id', type=int, help='显示特定ID的队列项状态')
    parser.add_argument('--status-course', type=int, help='显示特定课程的所有队列项状态')
    parser.add_argument('--sync', action='store_true', help='同步Flask数据库到本地数据库')
    
    args = parser.parse_args()
    
    # 初始化队列数据库
    init_queue_db()
    
    # 同步数据库
    if args.sync or args.status or args.status_id or args.status_course:
        sync_with_flask_db()
    
    # 处理队列项
    if args.process:
        try:
            process_pending_queue_items()
        except Exception as e:
            logger.error(f"处理队列时出错: {str(e)}")
            sys.exit(1)
    
    # 处理特定队列项
    if args.process_id:
        try:
            success = process_knowledge_queue(args.process_id)
            if success:
                print(f"成功处理队列项 {args.process_id}")
            else:
                print(f"处理队列项 {args.process_id} 失败")
        except Exception as e:
            logger.error(f"处理队列项 {args.process_id} 时出错: {str(e)}")
            sys.exit(1)
    
    # 显示队列状态
    if args.status:
        display_queue_status()
    
    if args.status_id:
        display_queue_status(queue_id=args.status_id)
    
    if args.status_course:
        display_queue_status(course_id=args.status_course)
    
    # 如果没有指定任何操作，默认处理所有待处理的队列项
    if not any(vars(args).values()):
        try:
            process_pending_queue_items()
        except Exception as e:
            logger.error(f"处理队列时出错: {str(e)}")
            sys.exit(1) 