import os
import sys
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_initialize_rag():
    """测试初始化RAG模块"""
    try:
        # 导入初始化函数
        from backend.api.rag_ai import initialize_rag
        
        # 调用初始化函数
        logger.info("开始初始化RAG模块")
        result = initialize_rag()
        
        if result:
            logger.info("RAG模块初始化成功")
        else:
            logger.error("RAG模块初始化失败")
            
        # 尝试导入并使用RAG查询函数
        try:
            from backend.rag.rag_query import hybrid_retriever
            
            # 测试查询
            course_id = "1"
            query = "数字电路的基本概念是什么？"
            
            logger.info(f"执行RAG查询，课程ID: {course_id}, 查询: '{query}'")
            
            # 尝试查询
            docs = hybrid_retriever(query, course_id)
            
            if docs:
                logger.info(f"查询成功，找到 {len(docs)} 个相关文档")
                # 打印第一个文档的内容
                if len(docs) > 0:
                    logger.info(f"第一个文档内容: {docs[0].page_content[:100]}...")
            else:
                logger.warning("查询成功，但没有找到相关文档")
                
        except Exception as e:
            logger.error(f"使用RAG查询失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
    except ImportError as e:
        logger.error(f"导入初始化函数失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    logger.info("开始测试RAG初始化")
    test_initialize_rag() 