# RAG 知识库队列管理系统

## 概述

RAG（检索增强生成）知识库队列管理系统用于管理文档处理队列，将上传的文档转换为向量数据库和知识图谱。本系统提供了以下功能：

1. 将文档添加到处理队列
2. 实时监控处理进度
3. 处理队列中的文档
4. 查询队列状态
5. 处理失败的重试机制

## 系统组件

系统由以下几个主要组件组成：

1. **数据模型** (`backend/models/learning.py`): 定义了 `KnowledgeBaseQueue` 模型，存储队列项信息
2. **处理器** (`backend/tasks/rag_processor.py`): 负责在后台线程中处理队列项
3. **队列处理脚本** (`process_queue.py`): 独立脚本，用于处理队列和查询状态
4. **本地数据库** (`rag_queue.db`): SQLite 数据库，用于存储队列状态和处理日志
5. **测试脚本** (`test_rag_upload.py`): 用于测试上传文档并添加到知识库

## 使用方法

### 1. 迁移数据库

首次使用前，需要迁移数据库以添加新字段：

```bash
python backend/database/migrate_queue_db.py
```

### 2. 添加文档到知识库

通过 API 或前端界面上传文档并添加到知识库。系统会自动将文档添加到处理队列。

### 3. 处理队列

有两种方式处理队列：

#### 方式一：使用 `process_queue.py` 脚本

```bash
# 处理所有待处理的队列项
python process_queue.py

# 处理特定 ID 的队列项
python process_queue.py --process-id 5

# 显示所有队列项的状态
python process_queue.py --status

# 显示特定 ID 的队列项状态
python process_queue.py --status-id 5

# 显示特定课程的所有队列项状态
python process_queue.py --status-course 1

# 同步 Flask 数据库到本地数据库
python process_queue.py --sync
```

#### 方式二：通过 Web API

通过 Web API 添加文档到知识库后，系统会自动启动后台线程处理队列项。

### 4. 监控处理进度

使用 `test_rag_upload.py` 脚本监控处理进度：

```bash
# 上传文档并监控处理进度
python test_rag_upload.py

# 监控特定 ID 的队列项
python test_rag_upload.py --queue-id 5

# 仅测试聊天功能
python test_rag_upload.py --chat-only
```

## 队列状态说明

队列项可能处于以下状态：

- **pending**: 等待处理
- **processing**: 正在处理
- **completed**: 处理完成
- **failed**: 处理失败

## 处理阶段

文档处理分为以下几个阶段：

1. **initializing**: 初始化处理
2. **loading**: 加载文档
3. **splitting**: 分割文档
4. **vectorizing**: 向量化文档
5. **graph_extraction**: 提取知识图谱
6. **saving**: 保存结果
7. **completed**: 处理完成
8. **failed**: 处理失败

## 故障排除

### 问题：队列项状态一直是 "pending"

可能原因：
- 后台线程未启动或已退出
- 处理进程未运行

解决方法：
```bash
python process_queue.py --process-id <队列ID>
```

### 问题：处理失败

可能原因：
- 文件格式不支持
- 文件路径错误
- 内存不足

解决方法：
1. 检查错误消息：
```bash
python process_queue.py --status-id <队列ID>
```
2. 修复问题后重新添加到队列

## 系统架构

```
+----------------+     +-------------------+     +----------------+
| Web API        |---->| KnowledgeBaseQueue|---->| 后台处理线程   |
| (rag_ai.py)    |     | (数据库表)        |     | (rag_processor)|
+----------------+     +-------------------+     +----------------+
                              |
                              v
+----------------+     +-------------------+
| process_queue.py|---->| rag_queue.db     |
| (独立脚本)      |     | (本地数据库)      |
+----------------+     +-------------------+
```

## 技术细节

- 使用 SQLite 数据库存储队列状态和处理日志
- 使用 JSON 格式存储详细进度信息
- 使用线程池处理队列项
- 实时更新处理进度 