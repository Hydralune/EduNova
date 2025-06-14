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

## 🚀 快速开始

### 1. 环境准备
- Python 3.8+
- Git

### 2. 克隆与安装

```bash
# 克隆项目到本地
git clone <your-repository-url>
cd EduNova

# 进入后端目录
cd backend

# (推荐) 创建并激活虚拟环境
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置
在 `backend/app/config.py` 文件中，你需要配置你的大模型 API 密钥。

```python
# backend/app/config.py

# 将 "your-deepseek-api-key" 替换为你的真实密钥
# 或者将其设置为环境变量 DEEPSEEK_API_KEY
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-deepseek-api-key")
```

## ⚙️ 使用说明

### 启动应用
确保你位于 `backend` 目录下，并已激活虚拟环境。

```bash
# 设置 Flask 应用入口
# Windows (cmd)
set FLASK_APP=app.main
# Windows (PowerShell)
$env:FLASK_APP = "app.main"
# macOS/Linux
export FLASK_APP=app.main

# 启动开发服务器
flask run
```
应用将在 `http://127.0.0.1:5000` 上运行。

### 运行测试
项目包含一套单元测试来确保核心功能的正确性。在 `backend` 目录下运行：

```bash
python -m unittest discover
```
这将自动发现并执行 `tests/` 目录下的所有测试用例。

## 📁 项目结构

```
EduNova/
├── backend/
│   ├── app/
│   │   ├── api/          # API 蓝图 (按角色划分)
│   │   │   ├── admin.py
│   │   │   ├── student.py
│   │   │   └── teacher.py
│   │   ├── services/     # 核心服务 (如 LLM 调用)
│   │   │   └── llm_service.py
│   │   ├── __init__.py
│   │   ├── config.py     # 配置文件
│   │   └── main.py       # Flask 应用入口
│   ├── tests/            # 测试目录
│   │   └── test_llm_service.py
│   └── requirements.txt  # Python 依赖
│
├── documents/            # 项目文档
│   ├── 模块设计.md
│   └── ...
│
└── README.md             # 本文档
```
