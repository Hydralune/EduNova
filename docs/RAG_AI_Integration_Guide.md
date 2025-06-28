# RAG和AI模块集成指南

本文档说明如何在智能教学系统中集成和使用RAG（检索增强生成）和AI功能模块。

## 目录结构

```
backend/
├── rag_module/
│   ├── __init__.py          # RAG模块主接口
│   ├── vector_db/           # 向量数据库相关
│   ├── embeddings/          # 文本嵌入相关
│   └── retrieval/           # 检索相关
├── ai_module/
│   ├── __init__.py          # AI模块主接口
│   ├── grading/             # 自动批改相关
│   └── content_generation/  # 内容生成相关
├── module_config.py         # 模块配置管理
└── config.json             # 配置文件（用户创建）
```

## 快速开始

### 1. 启用RAG模块

#### 安装依赖
```bash
pip install chromadb sentence-transformers
```

#### 配置Chroma向量数据库
```python
# 在 rag_module/__init__.py 中取消注释相关代码
import chromadb
from sentence_transformers import SentenceTransformer

# 实现ChromaVectorStore类
class ChromaVectorStore(VectorStoreInterface):
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection("education_system")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        texts = [doc['content'] for doc in documents]
        metadatas = [doc.get('metadata', {}) for doc in documents]
        ids = [str(doc['id']) for doc in documents]
        embeddings = self.embedding_model.encode(texts).tolist()
        
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
        return True
```

#### 启用RAG功能
```python
from module_config import enable_rag_module

# 启用RAG模块
enable_rag_module('chroma')
```

### 2. 启用AI模块

#### 集成OpenAI API（可选）
```python
# 安装依赖
pip install openai

# 在 ai_module/__init__.py 中实现OpenAI集成
import openai

class OpenAIGradingModel(GradingInterface):
    def __init__(self, api_key: str):
        openai.api_key = api_key
    
    def grade_assignment(self, assignment: Dict[str, Any], student_answer: str) -> Dict[str, Any]:
        prompt = f"""
        作业题目: {assignment.get('title', '')}
        学生答案: {student_answer}
        
        请对这个答案进行评分（0-100分）并提供详细分析。
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # 解析AI响应并返回评分结果
        return self._parse_grading_response(response.choices[0].message.content)
```

#### 启用AI功能
```python
from module_config import enable_ai_module

# 启用AI模块
enable_ai_module()
```

### 3. 配置文件示例

创建 `backend/config.json`：

```json
{
  "rag": {
    "enabled": true,
    "vector_store_type": "chroma",
    "knowledge_base_path": "./knowledge_base",
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "top_k_results": 5
  },
  "ai": {
    "enabled": true,
    "grading": {
      "model_type": "openai",
      "api_key": "your-openai-api-key",
      "model_name": "gpt-3.5-turbo"
    },
    "analytics": {
      "model_type": "local",
      "enable_insights": true,
      "enable_recommendations": true
    },
    "content_generation": {
      "model_type": "openai",
      "max_questions_per_quiz": 20,
      "supported_difficulties": ["easy", "medium", "hard"]
    }
  }
}
```

## API使用示例

### RAG功能使用

```python
from rag_module import get_rag_service

# 获取RAG服务
rag_service = get_rag_service()

# 初始化知识库
course_materials = [
    {
        'id': 1,
        'content': '人工智能是计算机科学的一个分支...',
        'title': 'AI基础概念',
        'course_id': 1,
        'metadata': {'chapter': 1, 'difficulty': 'basic'}
    }
]
rag_service.initialize_knowledge_base(course_materials)

# 检索相关内容
context = rag_service.retrieve_context("什么是人工智能？", course_id=1)

# 生成答案
answer = rag_service.generate_answer("什么是人工智能？", context)
```

### AI功能使用

```python
from ai_module import get_ai_services

# 获取AI服务
ai_services = get_ai_services()

# 自动批改作业
grading_service = ai_services['grading']
result = grading_service.grade_submission(
    assignment_id=1,
    student_id=123,
    answer="人工智能是让机器模拟人类智能的技术..."
)

# 学习分析
analytics_service = ai_services['analytics']
analysis = analytics_service.analyze_student_progress(student_id=123, course_id=1)

# 内容生成
content_service = ai_services['content']
quiz = content_service.create_quiz(
    topic="人工智能基础",
    difficulty="medium",
    question_count=10
)
```

## 在Flask路由中使用

已经在 `src/routes/rag_ai.py` 中预留了相关API端点：

- `POST /api/rag/query` - RAG查询
- `POST /api/ai/grade` - 自动批改
- `GET /api/ai/analytics/{student_id}` - 学习分析
- `POST /api/ai/generate-quiz` - 生成测验

## 扩展和自定义

### 添加新的向量数据库支持

1. 实现 `VectorStoreInterface` 接口
2. 在 `rag_module/__init__.py` 中注册新的实现
3. 更新配置文件

### 添加新的AI模型

1. 实现相应的接口（`GradingInterface`、`AnalyticsInterface`等）
2. 在 `ai_module/__init__.py` 中注册新的实现
3. 更新配置文件

### 自定义评分标准

```python
class CustomGradingModel(GradingInterface):
    def __init__(self, rubric: Dict[str, Any]):
        self.rubric = rubric
    
    def grade_assignment(self, assignment: Dict[str, Any], student_answer: str) -> Dict[str, Any]:
        # 根据自定义评分标准进行评分
        pass
```

## 注意事项

1. **安全性**: 确保API密钥等敏感信息不要提交到版本控制系统
2. **性能**: 大量文档的向量化可能需要较长时间，建议异步处理
3. **成本**: 使用商业AI API时注意控制调用频率和成本
4. **数据隐私**: 确保学生数据的隐私和安全
5. **模型更新**: 定期更新AI模型以获得更好的性能

## 故障排除

### 常见问题

1. **Chroma数据库连接失败**
   - 检查persist_directory路径是否正确
   - 确保有足够的磁盘空间

2. **AI API调用失败**
   - 检查API密钥是否正确
   - 确认网络连接正常
   - 检查API配额是否用完

3. **模块初始化失败**
   - 检查依赖是否正确安装
   - 查看错误日志获取详细信息

### 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 启用详细日志
from module_config import module_config
module_config.set('system.log_level', 'DEBUG')
```

## 贡献和支持

如果您在使用过程中遇到问题或有改进建议，请：

1. 查看本文档和代码注释
2. 检查配置文件是否正确
3. 查看系统日志获取错误信息
4. 参考示例代码进行调试

本模块设计为可扩展和可定制的，您可以根据具体需求进行修改和扩展。

