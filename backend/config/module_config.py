"""
模块集成配置

本文件用于配置和管理RAG和AI模块的集成。
用户可以根据需要启用或禁用特定功能，并配置相关参数。
"""

import os
from typing import Dict, Any, Optional

class ModuleConfig:
    """模块配置类"""
    
    def __init__(self):
        self.config = {
            # RAG模块配置
            'rag': {
                'enabled': False,  # 用户需要手动启用
                'vector_store_type': 'chroma',
                'embedding_model': None,  # 用户需要配置
                'knowledge_base_path': './knowledge_base',
                'chunk_size': 1000,
                'chunk_overlap': 200,
                'top_k_results': 5
            },
            
            # AI模块配置
            'ai': {
                'enabled': False,  # 用户需要手动启用
                'grading': {
                    'model_type': 'mock',  # 'mock', 'openai', 'local'
                    'api_key': None,
                    'model_name': None
                },
                'analytics': {
                    'model_type': 'mock',
                    'enable_insights': True,
                    'enable_recommendations': True
                },
                'content_generation': {
                    'model_type': 'mock',
                    'max_questions_per_quiz': 20,
                    'supported_difficulties': ['easy', 'medium', 'hard']
                }
            },
            
            # 系统配置
            'system': {
                'log_level': 'INFO',
                'cache_enabled': True,
                'cache_ttl': 3600,  # 1小时
                'max_concurrent_requests': 10
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def is_rag_enabled(self) -> bool:
        """检查RAG模块是否启用"""
        return self.get('rag.enabled', False)
    
    def is_ai_enabled(self) -> bool:
        """检查AI模块是否启用"""
        return self.get('ai.enabled', False)
    
    def load_from_file(self, config_path: str) -> None:
        """从文件加载配置"""
        if os.path.exists(config_path):
            import json
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                self._merge_config(self.config, file_config)
    
    def save_to_file(self, config_path: str) -> None:
        """保存配置到文件"""
        import json
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def _merge_config(self, base: Dict, update: Dict) -> None:
        """合并配置"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

# 全局配置实例
module_config = ModuleConfig()

def initialize_modules() -> Dict[str, Any]:
    """初始化所有模块"""
    result = {
        'rag': None,
        'ai': None,
        'status': 'initialized'
    }
    
    try:
        # 加载配置文件（如果存在）
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        module_config.load_from_file(config_path)
        
        # 初始化RAG模块
        if module_config.is_rag_enabled():
            try:
                from rag_module import initialize_rag_service
                rag_service = initialize_rag_service()
                result['rag'] = rag_service
                print("RAG模块初始化成功")
            except Exception as e:
                print(f"RAG模块初始化失败: {e}")
                result['rag_error'] = str(e)
        
        # 初始化AI模块
        if module_config.is_ai_enabled():
            try:
                from ai_module import initialize_ai_services
                ai_services = initialize_ai_services()
                result['ai'] = ai_services
                print("AI模块初始化成功")
            except Exception as e:
                print(f"AI模块初始化失败: {e}")
                result['ai_error'] = str(e)
        
        return result
        
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
        return result

def get_module_status() -> Dict[str, Any]:
    """获取模块状态"""
    return {
        'rag_enabled': module_config.is_rag_enabled(),
        'ai_enabled': module_config.is_ai_enabled(),
        'config': module_config.config
    }

def enable_rag_module(vector_store_type: str = 'chroma') -> bool:
    """启用RAG模块"""
    try:
        module_config.set('rag.enabled', True)
        module_config.set('rag.vector_store_type', vector_store_type)
        
        # 重新初始化模块
        initialize_modules()
        return True
    except Exception as e:
        print(f"启用RAG模块失败: {e}")
        return False

def enable_ai_module() -> bool:
    """启用AI模块"""
    try:
        module_config.set('ai.enabled', True)
        
        # 重新初始化模块
        initialize_modules()
        return True
    except Exception as e:
        print(f"启用AI模块失败: {e}")
        return False

