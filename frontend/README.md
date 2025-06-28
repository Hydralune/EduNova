# 智能教学系统前端

这是智能教学系统的前端部分，使用Vue 3 + TypeScript + Tailwind CSS构建。

## 开发环境设置

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

## 项目结构

- `src/` - 源代码
  - `api/` - API请求函数
  - `assets/` - 静态资源（CSS, 图片等）
  - `components/` - Vue组件
  - `router/` - Vue Router配置
  - `stores/` - Pinia状态管理
  - `views/` - 页面视图
  - `App.vue` - 主应用组件
  - `main.ts` - 应用入口

## 后端接口

前端默认连接到 `http://localhost:5001/api` 的后端接口。你可以在 `vite.config.ts` 文件中修改代理配置。 