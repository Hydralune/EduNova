# AI助手知识图谱集成说明

## 功能概述

本项目已成功集成了AI助手功能，支持两种模式：

1. **普通AI问答模式** - 基本的AI对话功能
2. **知识库增强模式** - 基于RAG（检索增强生成）的智能问答

## 技术架构

### 后端架构
- **RAG模块**: `backend/rag/rag_query.py` - 核心RAG查询逻辑
- **知识图谱**: `backend/rag/knowledge_graph.py` - 知识图谱构建和查询
- **API接口**: `backend/api/rag_ai.py` - RESTful API接口
- **向量数据库**: Chroma + 自定义EmbeddingFunction

### 前端架构
- **组件**: `frontend/src/components/ai/AIAssistant.vue` - 主要聊天界面
- **API**: `frontend/src/api.ts` - API调用封装
- **路由**: 支持独立访问和课程内嵌

## 功能特性

### 1. 模式选择
- 用户可以在聊天界面选择使用普通模式或RAG模式
- 普通模式：快速响应，适合一般性问题
- RAG模式：基于知识库，提供更准确的课程相关回答

### 2. 课程集成
- 在RAG模式下，用户需要选择特定课程
- 系统会自动检索该课程的知识库
- 支持向量检索和知识图谱检索

### 3. 流式响应
- 支持实时流式输出，提升用户体验
- 支持Markdown渲染，包括代码高亮
- 支持消息复制功能

### 4. 对话管理
- 支持对话历史记录
- 支持多轮对话上下文
- 支持新建对话功能

### 5. 引用来源
- RAG模式下会显示回答的参考来源
- 支持点击查看原始文档

## 使用方法

### 1. 普通AI问答
1. 在聊天界面选择"普通AI问答"模式
2. 直接输入问题即可获得回答
3. 适合一般性学习问题

### 2. 知识库增强问答
1. 在聊天界面选择"知识库增强"模式
2. 选择要查询的课程
3. 输入与课程相关的问题
4. 系统会基于课程知识库提供准确回答

### 3. 测试页面
访问 `/test-ai-assistant` 可以同时测试两种模式

## API接口

### 主要接口
- `POST /api/rag/chat` - 聊天接口
- `GET /api/rag/status` - 获取模块状态
- `GET /api/rag/conversations` - 获取对话列表
- `GET /api/rag/history` - 获取对话历史

### 请求参数
```json
{
  "message": "用户问题",
  "course_id": "课程ID（可选）",
  "conversation_id": "对话ID（可选）",
  "stream": true,
  "use_rag": true
}
```

## 配置要求

### 环境变量
```env
LLM_API_KEY=your_api_key
LLM_API_BASE=https://api.siliconflow.cn/v1
LLM_MODEL=Qwen/Qwen3-32B
```

### 知识库准备
1. 上传课程文档到知识库
2. 运行知识图谱构建脚本
3. 确保向量数据库已创建

## 部署说明

### 后端部署
1. 确保Python环境已安装所需依赖
2. 配置环境变量
3. 启动Flask应用

### 前端部署
1. 安装Node.js依赖
2. 构建生产版本
3. 部署到Web服务器

## 故障排除

### 常见问题
1. **API密钥未配置** - 检查环境变量设置
2. **知识库不存在** - 确保已为课程创建知识库
3. **模型响应慢** - 检查网络连接和API配额
4. **前端无法连接** - 检查CORS配置和后端服务状态

### 调试方法
1. 查看浏览器控制台错误信息
2. 检查后端日志输出
3. 使用测试页面验证功能
4. 检查网络请求状态

## 扩展功能

### 未来计划
1. 支持更多文件格式
2. 增加多模态输入（图片、音频）
3. 优化知识图谱构建算法
4. 增加个性化推荐功能
5. 支持多语言问答

## 技术栈

- **后端**: Python, Flask, LangChain, Chroma, NetworkX
- **前端**: Vue 3, TypeScript, Tailwind CSS
- **AI模型**: Qwen系列模型
- **向量数据库**: Chroma
- **知识图谱**: NetworkX

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

## 许可证

本项目采用MIT许可证。 