# RAG 知识库模块实现说明

## 概述

RAG（检索增强生成）知识库模块是 EduNova 智能教育助手的核心功能之一，它通过将文档转换为向量数据库和知识图谱，为 AI 提供准确的上下文信息，从而实现基于课程内容的智能问答。

## 系统架构

RAG 知识库模块由以下几个主要部分组成：

1. **文档处理流水线**：负责文档的加载、分割、向量化和知识图谱构建
2. **向量数据库**：存储文档的向量表示，用于语义检索
3. **知识图谱**：存储文档中的实体和关系，用于结构化知识检索
4. **队列管理系统**：处理文档的异步处理和状态跟踪
5. **检索引擎**：结合向量检索和知识图谱查询，获取最相关的上下文信息
6. **AI 问答接口**：将检索到的上下文与用户问题一起发送给 LLM，生成回答

## 文件结构

```
EduNova/
├── backend/
│   ├── api/
│   │   └── rag_ai.py      # RAG API 接口
│   ├── models/
│   │   └── learning.py    # 包含 KnowledgeBaseQueue 模型
│   ├── rag/
│   │   ├── create_db.py   # 知识库创建
│   │   ├── embedding_util.py # 嵌入工具
│   │   └── rag_query.py   # 知识库查询
│   └── tasks/
│       └── rag_processor.py # RAG 处理器
├── process_queue.py       # 队列处理脚本
└── test_rag_upload.py     # 测试脚本
```

## 工作流程

### 1. 文档上传

用户通过前端界面或 API 上传文档，文档被保存到服务器的 `uploads/materials/{course_id}` 目录下。

### 2. 添加到处理队列

上传的文档被添加到 `KnowledgeBaseQueue` 表中，状态为 `pending`。

### 3. 异步处理

后台线程或独立进程处理队列中的文档：

1. 加载文档（PDF、Word、文本等）
2. 将文档分割成较小的块
3. 使用嵌入模型将文本块转换为向量
4. 构建知识图谱
5. 保存向量数据库和知识图谱
6. 更新队列状态为 `completed`

### 4. 状态跟踪

处理过程中，系统会实时更新队列项的状态和进度，用户可以通过前端界面或 API 查询处理进度。

### 5. 知识库查询

用户提问时，系统会：

1. 将问题转换为向量
2. 在向量数据库中检索最相关的文本块
3. 在知识图谱中查询相关实体和关系
4. 将检索到的上下文与用户问题一起发送给 LLM
5. 返回 LLM 生成的回答

## 队列管理系统

为了处理大量文档和长时间运行的任务，我们实现了一个队列管理系统：

1. **数据库表**：`KnowledgeBaseQueue` 存储队列项信息
2. **本地数据库**：`rag_queue.db` 存储队列状态和处理日志
3. **处理脚本**：`process_queue.py` 用于处理队列和查询状态
4. **后台线程**：`rag_processor.py` 中的处理函数

队列项可能处于以下状态：

- **pending**：等待处理
- **processing**：正在处理
- **completed**：处理完成
- **failed**：处理失败

## 使用方法

### 添加文档到知识库

```python
response = requests.post(
    "http://localhost:5001/api/rag/knowledge/add",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "course_id": course_id,
        "file_path": file_path
    }
)
```

### 处理队列

```bash
# 处理所有待处理的队列项
python process_queue.py

# 处理特定 ID 的队列项
python process_queue.py --process-id 5

# 显示队列状态
python process_queue.py --status
```

### 查询知识库

```python
response = requests.post(
    "http://localhost:5001/api/rag/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "message": "量子计算在人工智能中有哪些应用?",
        "course_id": course_id,
        "use_rag": True
    }
)
```

## 技术细节

### 向量化

文档向量化使用了 `BAAI/bge-large-zh-v1.5` 模型，该模型在中文语义表示方面表现优异。

### 知识图谱构建

知识图谱通过 LLM 从文档中提取实体和关系，使用 NetworkX 库存储为 GML 格式。

### 混合检索

查询时同时使用向量相似度检索和知识图谱查询，结合两者结果获得更全面的上下文信息。

## 故障排除

常见问题及解决方法：

1. **队列项状态一直是 "pending"**：运行 `python process_queue.py` 处理队列
2. **处理失败**：检查错误消息，可能是文件格式不支持或路径错误
3. **查询结果不准确**：检查文档是否成功处理，可能需要调整分割参数或向量化模型

更多详细信息请参阅 [RAG_Queue_Management.md](RAG_Queue_Management.md) 和 [RAG_AI_Integration_Guide.md](RAG_AI_Integration_Guide.md)。