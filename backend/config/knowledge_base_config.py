"""
知识库配置文件
统一管理知识库相关的路径和配置
"""

import os

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 知识库相关路径配置
class KnowledgeBaseConfig:
    """知识库配置类"""
    
    # 基础路径
    UPLOADS_DIR = os.path.join(PROJECT_ROOT, "uploads")
    
    # 材料存储路径（用户上传的原始文件）
    MATERIALS_DIR = os.path.join(UPLOADS_DIR, "materials")
    
    # 知识库存储路径（处理后的文件）
    KNOWLEDGE_BASE_DIR = os.path.join(UPLOADS_DIR, "knowledge_base")
    
    # 向量数据库存储路径
    VECTOR_DB_DIR = os.path.join(KNOWLEDGE_BASE_DIR, "{course_id}", "vectordb")
    
    # 元数据文件路径
    PROCESSING_STATUS_FILE = os.path.join(KNOWLEDGE_BASE_DIR, "{course_id}", "processing_status.json")
    PROCESSED_FILES_FILE = os.path.join(KNOWLEDGE_BASE_DIR, "{course_id}", "processed_files.json")
    
    # 支持的文件类型
    SUPPORTED_FILE_TYPES = {
        '.pdf': 'PDF文档',
        '.docx': 'Word文档',
        '.doc': 'Word文档',
        '.txt': '文本文件',
        '.md': 'Markdown文件',
        '.markdown': 'Markdown文件'
    }
    
    # 文档处理配置
    CHUNK_SIZE = 300  # 文本块大小
    CHUNK_OVERLAP = 50  # 文本块重叠大小
    
    @classmethod
    def get_materials_path(cls, course_id: str) -> str:
        """获取课程材料路径"""
        return os.path.join(cls.MATERIALS_DIR, str(course_id))
    
    @classmethod
    def get_knowledge_base_path(cls, course_id: str) -> str:
        """获取知识库路径"""
        return os.path.join(cls.KNOWLEDGE_BASE_DIR, str(course_id))
    
    @classmethod
    def get_vector_db_path(cls, course_id: str) -> str:
        """获取向量数据库路径"""
        return cls.VECTOR_DB_DIR.format(course_id=str(course_id))
    
    @classmethod
    def get_processing_status_path(cls, course_id: str) -> str:
        """获取处理状态文件路径"""
        return cls.PROCESSING_STATUS_FILE.format(course_id=str(course_id))
    
    @classmethod
    def get_processed_files_path(cls, course_id: str) -> str:
        """获取已处理文件信息路径"""
        return cls.PROCESSED_FILES_FILE.format(course_id=str(course_id))
    
    @classmethod
    def ensure_directories_exist(cls, course_id: str):
        """确保所有必要的目录都存在"""
        directories = [
            cls.get_materials_path(course_id),
            cls.get_knowledge_base_path(course_id),
            cls.get_vector_db_path(course_id)
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def is_file_supported(cls, filename: str) -> bool:
        """检查文件类型是否支持"""
        _, ext = os.path.splitext(filename)
        return ext.lower() in cls.SUPPORTED_FILE_TYPES
    
    @classmethod
    def get_file_type_description(cls, filename: str) -> str:
        """获取文件类型描述"""
        _, ext = os.path.splitext(filename)
        return cls.SUPPORTED_FILE_TYPES.get(ext.lower(), '未知文件类型')

# 创建全局配置实例
kb_config = KnowledgeBaseConfig()

# 导出常用函数
def get_materials_path(course_id: str) -> str:
    """获取课程材料路径"""
    return kb_config.get_materials_path(course_id)

def get_knowledge_base_path(course_id: str) -> str:
    """获取知识库路径"""
    return kb_config.get_knowledge_base_path(course_id)

def get_vector_db_path(course_id: str) -> str:
    """获取向量数据库路径"""
    return kb_config.get_vector_db_path(course_id)

def is_file_supported(filename: str) -> bool:
    """检查文件类型是否支持"""
    return kb_config.is_file_supported(filename) 