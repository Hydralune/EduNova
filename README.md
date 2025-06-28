# EduNova - 智能实训教育助手

EduNova 是一个旨在利用大语言模型（LLM）和检索增强生成（RAG）技术，为教师和学生打造的智能化、一体化的实训教学平台。它致力于将人工智能深度融合于教学设计、实训辅导、考核评估和学情分析等核心环节，从而提升教学效率、激发学生潜能，并为教学管理提供数据驱动的决策支持。

## ✨ 主要功能

EduNova 的功能设计围绕三大核心用户群体：教师、学生和管理员。

### 👨‍🏫 **教师端**
- **智能备课与设计**：上传课程大纲或知识库，AI 自动设计教学内容、实训活动和时间安排。
- **智能考核内容生成**：根据知识点一键生成多样化的考核题目、参考答案及评分标准。
- **学情数据分析**：自动批改学生答案，提供错误定位和修正建议，并可视化分析学生知识掌握情况，生成教学改进建议。

### 👩‍🎓 **学生端**
- **在线学习助手**：随时随地提问，AI 结合教学内容进行精准、智能的问答。
- **实时练习与评测**：根据学习进度和个人需求生成练习题，并获得即时的评测反馈和纠错指导。

### ⚙️ **管理端**
- **用户与角色管理**：精细化的权限控制，确保系统安全。
- **课程与资源管理**：集中管理所有课程资源，方便查阅、修改和导出。
- **教学大屏概览**：实时统计分析平台使用情况、教学效率和学生学习效果，为教学管理提供宏观视角。

## 🏗️ 系统架构

项目采用前后端分离的现代 Web 架构，确保了系统的高内聚、低耦合和可扩展性。

- **前端 (Frontend)**：基于Vue 3和Tailwind CSS构建，为不同角色提供直观、易用的用户界面。
- **后端 (Backend)**：使用 Flask 框架，通过统一的 RESTful API 提供服务。
- **核心引擎 (Core Engine)**：
  - **LLM 服务模块**: 封装了对大语言模型的调用。
  - **知识库与 RAG 模块**: 负责知识的存储、向量化和检索，为 LLM 提供生成所需的核心上下文。
- **数据库 (Database)**：使用SQLite持久化存储所有关键数据，如用户信息、课程资料、考核结果等。

## 🚀 本地开发指南

本指南将引导您在本地计算机上设置并运行 EduNova 项目。

### 1. 环境准备
- **Git**: 用于克隆项目代码。
- **Node.js**: 用于运行前端项目 (推荐 v18 或更高版本)。
- **Python**: 用于运行后端项目 (推荐 v3.9 或更高版本)。

### 2. 后端设置 (Backend)

进入 `backend` 目录，所有后续的后端命令都在此目录下执行。
```bash
cd backend
```

#### a. 安装 Python 依赖
```bash
pip install -r requirements.txt
```

#### b. 初始化数据库
```bash
python init_db.py
```

#### c. 运行后端服务器
```bash
python main.py
```
后端服务将会在 `http://127.0.0.1:5001` 上运行。

---

### 3. 前端设置 (Frontend)

打开一个**新的终端窗口**，进入 `frontend` 目录。
```bash
cd frontend
```

#### a. 安装 Node.js 依赖
```bash
npm install
```

#### b. 运行前端开发服务器
```bash
npm run dev
```
前端应用将会在一个新端口上运行 (例如 `http://localhost:5173/`)，并会在终端中显示具体的地址。

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
│   ├── utils/             # 工具函数
│   ├── extensions.py      # Flask扩展初始化
│   ├── init_db.py         # 数据库初始化脚本
│   ├── main.py            # 应用主入口
│   ├── requirements.txt   # Python依赖
│   └── run_server.py      # 服务器启动脚本
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
│   ├── package.json       # Node.js依赖
│   ├── tailwind.config.js # Tailwind CSS配置
│   └── vite.config.ts     # Vite配置
│
├── docs/                  # 项目文档
│   ├── 智能教学系统 - 完整项目文档.md
│   ├── RAG_AI_Integration_Guide.md
│   └── 需求分析.md
│
└── README.md              # 本文档
```

## 📝 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。
