import threading
import time
import os
import json
from flask import current_app
import logging

from backend.models.learning import KnowledgeBaseQueue
from backend.extensions import db
from backend.rag.create_db import process_document_with_progress

# Setup logging
logger = logging.getLogger(__name__)

def process_knowledge_queue(queue_id):
    """Process a knowledge base queue item in a background thread"""
    # 导入app对象
    from backend.main import app
    
    # 在应用上下文中执行所有操作
    with app.app_context():
        # Get the queue item
        queue_item = db.session.get(KnowledgeBaseQueue, queue_id)
        if not queue_item:
            logger.error(f"Queue item {queue_id} not found")
            return
        
        try:
            # Update status to processing
            queue_item.status = 'processing'
            queue_item.last_updated = int(time.time())
            queue_item.progress_detail = json.dumps({
                "stage": "initializing",
                "message": "正在初始化处理",
                "timestamp": int(time.time())
            })
            db.session.commit()
            
            # Define progress callback function
            def progress_callback(progress, stage=None, message=None):
                # 在应用上下文中执行进度更新
                with app.app_context():
                    # Get a fresh instance of the queue item
                    current_item = db.session.get(KnowledgeBaseQueue, queue_id)
                    if not current_item:
                        logger.error(f"Queue item {queue_id} not found during progress update")
                        return
                    
                    if progress < 0:
                        # Error occurred
                        current_item.status = 'failed'
                        current_item.error_message = message or "Processing failed"
                        current_item.last_updated = int(time.time())
                    else:
                        current_item.progress = progress
                        
                        # Update progress detail
                        progress_detail = {
                            "stage": stage or "processing",
                            "progress": progress,
                            "message": message or f"处理进度: {progress:.1f}%",
                            "timestamp": int(time.time())
                        }
                        current_item.progress_detail = json.dumps(progress_detail)
                        current_item.last_updated = int(time.time())
                        
                        logger.info(f"Queue item {queue_id}: {progress:.1f}% - {message or 'Processing'}")
                    
                    db.session.commit()
            
            # Get the full path to the file
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], queue_item.file_path.lstrip('/'))
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                progress_callback(-1, "error", f"文件不存在: {queue_item.file_path}")
                return False
                
            # Process the document
            success = process_document_with_progress(
                course_id=str(queue_item.course_id),
                file_path=file_path,
                progress_callback=progress_callback,
                purpose=queue_item.purpose or 'general'  # 传递文件用途参数
            )
            
            # Update status based on result
            queue_item = db.session.get(KnowledgeBaseQueue, queue_id)
            if not queue_item:
                logger.error(f"Queue item {queue_id} not found after processing")
                return False
                
            if success:
                queue_item.status = 'completed'
                queue_item.completed_at = int(time.time())
                queue_item.progress = 100.0
                queue_item.error_message = None  # 清除错误信息
                queue_item.progress_detail = json.dumps({
                    "stage": "completed",
                    "progress": 100.0,
                    "message": "处理完成",
                    "timestamp": int(time.time())
                })
                queue_item.last_updated = int(time.time())
                logger.info(f"Successfully processed queue item {queue_id}")
            else:
                queue_item.status = 'failed'
                if not queue_item.error_message:
                    queue_item.error_message = "Unknown error occurred"
                queue_item.progress_detail = json.dumps({
                    "stage": "failed",
                    "message": queue_item.error_message,
                    "timestamp": int(time.time())
                })
                queue_item.last_updated = int(time.time())
                logger.error(f"Failed to process queue item {queue_id}")
            
            db.session.commit()
            return success
            
        except Exception as e:
            logger.error(f"Error processing queue item {queue_id}: {str(e)}")
            # Update status to failed
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
            except Exception as inner_e:
                logger.error(f"Failed to update queue item status: {str(inner_e)}")
            return False

def start_processing_queue_item(queue_id):
    """Start processing a queue item in a background thread"""
    thread = threading.Thread(target=process_knowledge_queue, args=(queue_id,))
    thread.daemon = True
    thread.start()
    return thread 