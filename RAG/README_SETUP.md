# RAG模块设置指南

本指南将帮助您正确设置和配置RAG（检索增强生成）模块，以便与EduNova系统集成。

## 1. 环境配置

### 创建环境变量文件

1. 在`RAG`目录下创建一个`.env`文件（注意：此文件已被添加到`.gitignore`中，不会被提交到仓库）
2. 参考`templates/.env.example`文件的格式，添加以下必要配置：

```
# LLM API Configuration
LLM_API_KEY='your-actual-api-key'
LLM_API_BASE='https://api.siliconflow.cn/v1'
LLM_MODEL='Qwen/Qwen3-32B'

# 其他配置项...
```

### 安装依赖

在`RAG`目录下运行：

```bash
pip install -r requirements.txt
```

## 2. 数据准备

### 文档存储

1. 将教学文档放入`RAG/documents`目录
2. 私有或敏感文档应放在`RAG/documents/private`目录（此目录已被添加到`.gitignore`中）

### 创建向量数据库

运行以下命令创建向量数据库：

```bash
python create_db.py --doc_dir ./documents --db_dir ./data
```

注意：生成的向量数据库将保存在`./data`目录中，该目录已被添加到`.gitignore`中，不会被提交到仓库。

## 3. 安全注意事项

为确保API密钥和敏感数据的安全，请遵循以下准则：

1. **不要**将包含实际API密钥的`.env`文件提交到仓库
2. **不要**将`data`目录（包含向量数据库）提交到仓库
3. **不要**将`documents/private`目录中的敏感文档提交到仓库
4. **不要**修改`.gitignore`文件中关于RAG模块的忽略规则

## 4. 与EduNova系统集成

目前，RAG模块尚未完全集成到EduNova系统中。在完成集成前，您可以独立使用此模块进行以下操作：

### 生成考试题目

```bash
python generate_exam.py --subject "计算机网络" --difficulty "中等" --count 5
```

### 查询知识库

```bash
python rag_query.py --query "什么是TCP协议" --db_dir ./data
```

## 5. 故障排除

如果遇到以下问题，请尝试相应的解决方案：

1. **API密钥错误**：确保`.env`文件中的`LLM_API_KEY`值正确
2. **向量数据库错误**：删除`./data`目录并重新运行`create_db.py`
3. **内存不足**：减小`CHUNK_SIZE`或`EMBEDDING_BATCH_SIZE`的值

## 6. 后续开发计划

- 完成与EduNova后端API的集成
- 添加更多文档处理功能
- 优化检索算法
- 实现用户反馈机制 