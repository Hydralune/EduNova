# EduNova - 智能实训教育助手

EduNova 是一个旨在利用大语言模型（LLM）和检索增强生成（RAG）技术，为教师和学生打造的智能化、一体化的实训教学平台。它致力于将人工智能深度融合于教学设计、实训辅导、考核评估和学情分析等核心环节，从而提升教学效率、激发学生潜能，并为教学管理提供数据驱动的决策支持。

## ✨ 主要功能

EduNova 的功能设计围绕三大核心用户群体：教师、学生和管理员。

### 👨‍🏫 **教师端**
- **智能备课与设计**：上传课程大纲或知识库，AI 自动设计教学内容、实训活动和时间安排。
- **智能考核内容生成**：根据知识点一键生成多样化的考核题目、参考答案及评分标准。
- **学情数据分析**：自动批改学生答案，提供错误定位和修正建议，并可视化分析学生知识掌握情况，生成教学改进建议。
- **知识库管理**：上传和管理课程资料，系统自动处理并构建知识库，支持智能问答。

### 👩‍🎓 **学生端**
- **在线学习助手**：随时随地提问，AI 结合教学内容进行精准、智能的问答。
- **实时练习与评测**：根据学习进度和个人需求生成练习题，并获得即时的评测反馈和纠错指导。
- **知识库检索**：基于课程知识库进行智能问答，获取精准的学习支持。

### ⚙️ **管理端**
- **用户与角色管理**：精细化的权限控制，确保系统安全。
- **课程与资源管理**：集中管理所有课程资源，方便查阅、修改和导出。
- **教学大屏概览**：实时统计分析平台使用情况、教学效率和学生学习效果，为教学管理提供宏观视角。
- **知识库监控**：监控知识库构建进度和状态，确保系统正常运行。

## 🏗️ 系统架构

项目采用前后端分离的现代 Web 架构，确保了系统的高内聚、低耦合和可扩展性。

- **前端 (Frontend)**：基于Vue 3和Tailwind CSS构建，为不同角色提供直观、易用的用户界面。
- **后端 (Backend)**：使用 Flask 框架，通过统一的 RESTful API 提供服务。
- **核心引擎 (Core Engine)**：
  - **LLM 服务模块**: 封装了对大语言模型的调用。
  - **知识库与 RAG 模块**: 负责知识的存储、向量化和检索，为 LLM 提供生成所需的核心上下文。
  - **队列管理系统**: 处理文档的异步处理和状态跟踪，确保大文件处理不阻塞主应用。
- **数据库 (Database)**：使用SQLite持久化存储所有关键数据，如用户信息、课程资料、考核结果等。

## 🚀 本地开发指南

本指南将引导您在本地计算机上设置并运行 EduNova 项目。

### 1. 环境准备
- **Git**: 用于克隆项目代码。
- **Node.js**: 用于运行前端项目 (推荐 v18 或更高版本)。
- **Python**: 用于运行后端项目 (推荐 v3.9 或更高版本)。

### 2. 快速安装与设置

您可以使用我们提供的安装脚本一键完成所有依赖安装和初始化：

```bash
# 在项目根目录执行
python setup.py
```

或者，您可以按照以下步骤手动安装：

详细的依赖说明和安装指南请参阅 [DEPENDENCIES.md](DEPENDENCIES.md)。

#### a. 安装 Python 依赖
```bash
# 在项目根目录执行
pip install -r requirements.txt
```

#### b. 安装 Node.js 依赖
```bash
# 在项目根目录执行
npm install
```

#### c. 初始化数据库
```bash
cd backend
python init_db.py
```

### 3. 运行应用

#### a. 运行后端服务器
```bash
# 在项目根目录执行
npm run start:backend
# 或者: cd backend && python run.py
```
后端服务将会在 `http://127.0.0.1:5001` 上运行。

#### b. 运行前端开发服务器
```bash
# 在项目根目录执行
npm run start:frontend
# 或者: cd frontend && npm run dev
```
前端应用将会在一个新端口上运行 (例如 `http://localhost:5173/`)，并会在终端中显示具体的地址。

#### c. 运行知识库处理队列
```bash
# 在项目根目录执行
python process_queue.py
```
这将处理所有待处理的知识库文档。更多选项请参阅 [RAG_Queue_Management.md](docs/RAG_Queue_Management.md)。

### 4. 访问应用

当后端和前端服务都成功运行后，在您的浏览器中打开前端应用的地址 (如 `http://localhost:5173/`)，即可开始使用 EduNova。

### 5. 默认用户账户

系统已预设以下默认用户，可用于测试：

- **管理员**：用户名 `admin`，密码 `admin123`
- **教师**：用户名 `teacher`，密码 `teacher123`
- **学生**：用户名 `student`，密码 `student123`

## 📁 项目结构

```
EduNova/
├── backend/               # 后端项目目录
│   ├── api/               # API 路由和控制器
│   │   ├── admin.py       # 管理员相关API
│   │   ├── auth.py        # 认证相关API
│   │   ├── learning.py    # 学习相关API
│   │   ├── rag_ai.py      # RAG AI相关API
│   │   └── user.py        # 用户相关API
│   ├── config/            # 配置文件
│   ├── database/          # 数据库文件
│   ├── models/            # 数据模型
│   │   ├── assessment.py  # 评估模型
│   │   ├── course.py      # 课程模型
│   │   ├── learning.py    # 学习记录模型
│   │   ├── material.py    # 课程资料模型
│   │   └── user.py        # 用户模型
│   ├── rag/               # RAG模块
│   │   ├── create_db.py   # 知识库创建
│   │   ├── embedding_util.py # 嵌入工具
│   │   └── rag_query.py   # 知识库查询
│   ├── tasks/             # 后台任务
│   │   └── rag_processor.py # RAG处理器
│   ├── utils/             # 工具函数
│   ├── extensions.py      # Flask扩展初始化
│   ├── init_db.py         # 数据库初始化脚本
│   ├── main.py            # 应用主入口
│   └── run.py             # 服务器启动脚本
│
├── frontend/              # 前端项目目录
│   ├── public/            # 静态资源
│   ├── src/               # 源代码
│   │   ├── api/           # API调用
│   │   ├── assets/        # 静态资源
│   │   ├── components/    # Vue组件
│   │   │   ├── admin/     # 管理员组件
│   │   │   ├── ai/        # AI助手组件
│   │   │   ├── analytics/ # 数据分析组件
│   │   │   ├── assessment/# 评估组件
│   │   │   ├── course/    # 课程组件
│   │   │   └── rag/       # RAG相关组件
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # 状态管理
│   │   └── views/         # 页面视图
│   ├── index.html         # HTML入口
│   ├── package.json       # 前端依赖
│   ├── tailwind.config.js # Tailwind CSS配置
│   └── vite.config.ts     # Vite配置
│
├── docs/                  # 项目文档
│   ├── 智能教学系统 - 完整项目文档.md
│   ├── RAG_AI_Integration_Guide.md
│   ├── RAG_Queue_Management.md # 队列管理文档
│   ├── 需求分析.md
│   └── DEPENDENCIES.md    # 依赖说明文档
│
├── process_queue.py       # 知识库队列处理脚本
├── test_rag_upload.py     # RAG上传测试脚本
├── requirements.txt       # 统一的Python依赖
├── package.json           # 项目根依赖和脚本
└── README.md              # 本文档
```

## 💡 RAG知识库系统

EduNova 的核心功能之一是基于 RAG (Retrieval-Augmented Generation) 的知识库系统，它允许：

1. **上传课程资料**：支持PDF、Word、文本等多种格式
2. **自动构建知识库**：系统自动处理文档，构建向量数据库和知识图谱
3. **智能问答**：学生可以针对课程内容提问，获得精准回答
4. **知识库管理**：教师可以管理知识库内容，添加或移除资料

详细的队列管理系统文档请参阅 [RAG_Queue_Management.md](docs/RAG_Queue_Management.md)。

## 📝 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。
