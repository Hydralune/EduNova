

## 核心功能总结

### 1. 教师侧
*   **备课与设计**: 根据课程大纲、知识库文档自动设计教学内容（知识讲解、实训练习、时间分布）。
*   **考核内容生成**: 根据教学内容自动生成考核题目及参考答案，支持多样化题型（如编程题）。
*   **学情数据分析**: 自动化检测学生答案，提供错误定位与修正建议；分析学生整体数据，总结知识掌握情况与教学建议。

### 2. 学生侧
*   **在线学习助手**: 结合教学内容解答学生问题。
*   **实时练习评测助手**: 根据历史练习和要求生成题目，并进行纠错。

### 3. 管理侧
*   **用户管理**: 管理员/教师/学生等用户的基本管理。
*   **课件资源管理**: 管理教师备课产生的课件、练习等资源，支持导出。
*   **大屏概览**: 统计教师/学生使用次数、活跃板块；教学效率指数（备课/修正耗时、课程优化方向）；学生学习效果（平均正确率、知识点掌握、高频错误知识点）。

## 技术栈与非功能性要求
*   **后端**: Python + Flask
*   **前端**: Vue.js，现代化风格，动态交互，美观整洁。
*   **数据库**: SQLite，统一存放于backend文件夹下特定位置。
*   **RAG**: 已有Chroma向量数据库，无需实现RAG部分，但需预留接口。
*   **AI**: 预留AI功能模块接口（作业批改、成绩分析等）。
*   **用户**: 登录模块，不同用户角色（管理员、教师、学生）的功能模块。
*   **文档**: 完整的代码和文档，方便后续添加模块。
*   **大模型**: 至少1个开源大模型作为核心技术组件，本地知识库资料总量不大于100M。




## 系统架构设计

### 1. 整体架构
本系统采用前后端分离的架构，前端使用Vue.js框架，后端使用Python Flask框架。数据存储采用SQLite数据库。

```
+-----------------+
|     Frontend    |
|   (Vue.js App)  |
+--------+--------+
         |
         | RESTful API
         |
+--------+--------+
|      Backend    |
|   (Flask App)   |
+--------+--------+
         |
         | SQLAlchemy ORM
         |
+--------+--------+
|    SQLite DB    |
+-----------------+
```

### 2. 后端模块设计 (Flask)

*   **`backend/`**
    *   `app.py`: Flask应用主文件，负责路由注册、应用初始化等。
    *   `config.py`: 配置文件，包含数据库路径、密钥等。
    *   `models.py`: 数据库模型定义，使用SQLAlchemy。
    *   `auth.py`: 用户认证和授权相关逻辑。
    *   `routes/`: API路由定义。
        *   `user_routes.py`: 用户管理相关API。
        *   `course_routes.py`: 课程管理相关API。
        *   `assessment_routes.py`: 考核内容生成、学情分析相关API。
        *   `student_routes.py`: 学生学习助手、练习评测相关API。
        *   `admin_routes.py`: 管理员大屏概览、资源管理相关API。
        *   `rag_ai_routes.py`: RAG和AI功能预留接口。
    *   `services/`: 业务逻辑层，处理具体业务操作。
    *   `utils/`: 工具函数，如密码哈希、JWT生成等。
    *   `database/`: 存放SQLite数据库文件。

### 3. 前端模块设计 (Vue.js)

*   **`frontend/`**
    *   `public/`: 静态资源。
    *   `src/`:
        *   `main.js`: Vue应用入口文件。
        *   `App.vue`: 根组件。
        *   `router/index.js`: Vue Router配置，定义前端路由。
        *   `components/`: 可复用UI组件。
        *   `views/`: 页面组件。
            *   `Auth/`: 登录、注册页面。
            *   `Teacher/`: 教师端页面（备课、考核、学情分析）。
            *   `Student/`: 学生端页面（学习助手、练习评测）。
            *   `Admin/`: 管理员页面（用户管理、资源管理、大屏概览）。
            *   `NotFound.vue`: 404页面。
        *   `api/index.js`: 前后端API接口封装。
        *   `store/index.js`: Vuex状态管理（可选，根据复杂度决定是否使用）。
        *   `assets/`: 样式、图片等资源。

### 4. 数据库设计 (SQLite)

*   **`User` 表**: 用户信息，包含 `id`, `username`, `password_hash`, `role` (admin, teacher, student)。
*   **`Course` 表**: 课程信息，包含 `id`, `name`, `description`, `teacher_id`。
*   **`Material` 表**: 课件资源，包含 `id`, `title`, `file_path`, `course_id`, `upload_date`。
*   **`Assessment` 表**: 考核题目，包含 `id`, `course_id`, `question`, `answer`, `type`。
*   **`StudentAnswer` 表**: 学生提交的答案，包含 `id`, `student_id`, `assessment_id`, `answer_content`, `score`, `feedback`。
*   **`LearningRecord` 表**: 学生学习记录，包含 `id`, `student_id`, `course_id`, `activity_type`, `timestamp`。

（后续会根据具体需求细化数据库字段和关系）


