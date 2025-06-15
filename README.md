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

- **前端 (Frontend)**：基于现代 Web 框架构建，为不同角色提供直观、易用的用户界面。
- **后端 (Backend)**：使用 Flask 框架，通过统一的 RESTful API 提供服务。
- **核心引擎 (Core Engine)**：
  - **LLM 服务模块**: 封装了对大语言模型（如 DeepSeek）的调用。
  - **知识库与 RAG 模块**: 负责知识的存储、向量化和检索，为 LLM 提供生成所需的核心上下文。
- **数据库 (Database)**：持久化存储所有关键数据，如用户信息、课程资料、考核结果等。

## 🚀 本地开发指南

本指南将引导您在本地计算机上设置并运行 EduNova 项目。

### 1. 环境准备
- **Git**: 用于克隆项目代码。
- **Node.js**: 用于运行前端项目 (推荐 v18 或更高版本)。
- **Conda**: 用于管理后端的 Python 环境。

### 2. 后端设置 (Backend)

进入 `backend` 目录，所有后续的后端命令都在此目录下执行。
```bash
cd backend
```

#### a. 创建并激活 Conda 环境
我们推荐使用 Conda 创建一个独立的环境，以避免与其他项目的依赖冲突。
```bash
# 创建一个名为 edunova 的新环境 (使用 Python 3.9)
conda create --name edunova python=3.9 -y

# 激活环境
conda activate edunova
```

#### b. 安装 Python 依赖
```bash
pip install -r requirements.txt
```

#### c. 配置环境变量
在 `backend` 目录下，创建一个名为 `.env` 的文件。这个文件用于存放敏感信息，如 API 密钥。复制以下内容到 `.env` 文件中，并根据需要修改。
```
# .env 文件内容

# Flask 和 JWT 的安全密钥，推荐修改为随机字符串
SECRET_KEY='a-hard-to-guess-string'
JWT_SECRET_KEY='another-super-secret-key'

# DeepSeek 大模型的 API Key
DEEPSEEK_API_KEY='your-deepseek-api-key'

# 数据库连接URI，默认使用 backend 目录下的 app.db 文件
DATABASE_URL='sqlite:///app.db'
```

#### d. 初始化数据库
这是项目首次运行时**必须执行**的步骤。
```bash
# 1. 设置 FLASK_APP 环境变量，告诉 Flask 应用的入口在哪里
#    (Windows PowerShell)
$env:FLASK_APP = "run.py"
#    (Windows CMD)
#    set FLASK_APP=run.py
#    (macOS / Linux)
#    export FLASK_APP=run.py

# 2. 初始化数据库迁移功能 (只需在项目开始时运行一次)
flask db init

# 3. 生成数据库迁移脚本
flask db migrate -m "Initial migration"

# 4. 将迁移应用到数据库，创建数据表
flask db upgrade
```

#### e. 运行后端服务器
```bash
python run.py
```
后端服务将会在 `http://127.0.0.1:5000` 上运行。

---

### 3. 前端设置 (Frontend)

打开一个**新的终端窗口**，进入 `frontend` 目录。
```bash
cd frontend
```

#### a. 安装 Node.js 依赖（已安装则不需要）
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

## 📁 项目结构

```
EduNova/
├── backend/
│   ├── app/
│   │   ├── api/          # API 蓝图 (按功能划分)
│   │   │   ├── auth.py   # 认证 API
│   │   │   ├── admin.py
│   │   │   ├── student.py
│   │   │   └── teacher.py
│   │   ├── models/       # SQLAlchemy 数据模型
│   │   │   └── user.py
│   │   ├── services/     # 核心服务 (如 LLM 调用)
│   │   ├── __init__.py   # 应用工厂
│   │   ├── config.py     # 配置文件
│   │   └── extensions.py # Flask 扩展实例化
│   ├── migrations/       # 数据库迁移脚本
│   ├── tests/            # 测试目录
│   ├── .env.example      # 环境变量示例 (可选)
│   ├── requirements.txt  # Python 依赖
│   └── run.py            # 应用启动脚本
│
├── frontend/
│   ├── src/
│   │   ├── assets/       # 静态资源
│   │   ├── components/   # 可复用组件
│   │   ├── router/       # Vue Router 配置
│   │   ├── services/     # API 服务
│   │   ├── stores/       # Pinia 状态管理
│   │   └── views/        # 页面视图
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── documents/            # 项目文档
└── README.md             # 本文档
```
