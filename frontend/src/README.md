# 智能教学系统前端

## 通知系统使用指南

本项目实现了一个统一的通知系统，可以在整个应用程序中使用。

### 基本用法

通知系统有两种使用方式：

#### 1. 通过注入的 showNotification 函数使用

在组件中可以通过注入的 `showNotification` 函数来显示通知：

```vue
<script setup>
import { inject } from 'vue';

// 注入通知函数
const showNotification = inject('showNotification');

// 使用方法
function handleSuccess() {
  showNotification('success', '操作成功', '数据已保存');
}

function handleError() {
  showNotification('error', '操作失败', '请检查网络连接');
}
</script>
```

#### 2. 直接导入 notificationService 使用

也可以直接导入 `notificationService` 服务来显示通知：

```vue
<script setup>
import notificationService from '@/services/notificationService';

// 使用方法
function handleSuccess() {
  notificationService.success('操作成功', '数据已保存');
}

function handleError() {
  notificationService.error('操作失败', '请检查网络连接');
}

function handleWarning() {
  notificationService.warning('警告', '此操作可能有风险');
}

function handleInfo() {
  notificationService.info('提示', '请注意查看最新公告');
}
</script>
```

### API 参考

#### notificationService

notificationService 提供以下方法：

- `success(title, message?, duration?)`: 显示成功通知
- `error(title, message?, duration?)`: 显示错误通知
- `warning(title, message?, duration?)`: 显示警告通知
- `info(title, message?, duration?)`: 显示信息通知
- `show(type, title, message?, duration?)`: 显示指定类型的通知
- `remove(id)`: 移除指定 ID 的通知
- `clear()`: 清除所有通知

参数说明：
- `title`: 通知标题（必填）
- `message`: 通知内容（可选）
- `duration`: 显示时长，单位为毫秒，默认为 5000ms（可选）
- `type`: 通知类型，可选值为 'success'、'error'、'warning'、'info'

### 示例

```vue
<template>
  <div>
    <button @click="showSuccessNotification">显示成功通知</button>
    <button @click="showErrorNotification">显示错误通知</button>
    <button @click="showWarningNotification">显示警告通知</button>
    <button @click="showInfoNotification">显示信息通知</button>
  </div>
</template>

<script setup>
import notificationService from '@/services/notificationService';

const showSuccessNotification = () => {
  notificationService.success('操作成功', '数据已保存');
};

const showErrorNotification = () => {
  notificationService.error('操作失败', '请检查网络连接');
};

const showWarningNotification = () => {
  notificationService.warning('警告', '此操作可能有风险');
};

const showInfoNotification = () => {
  notificationService.info('提示', '请注意查看最新公告');
};
</script>
``` 