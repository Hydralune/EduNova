<template>
  <div class="profile-container">
    <h1>个人资料</h1>
    <div v-if="authStore.isLoading" class="loading">加载中...</div>
    <div v-else-if="authStore.error" class="error">{{ authStore.error }}</div>
    <div v-else-if="authStore.user" class="profile-card">
      <div class="profile-header">
        <div class="avatar-container">
          <img v-if="authStore.user.avatar" :src="authStore.user.avatar" alt="头像" class="avatar" />
          <div v-else class="avatar-placeholder">{{ authStore.user.username?.charAt(0).toUpperCase() }}</div>
        </div>
        <h2>{{ authStore.user.full_name || authStore.user.username }}</h2>
        <p class="role-badge">{{ translateRole(authStore.user.role) }}</p>
      </div>
      <div class="profile-details">
        <div class="detail-item">
          <span class="label">用户名:</span>
          <span class="value">{{ authStore.user.username }}</span>
        </div>
        <div class="detail-item">
          <span class="label">邮箱:</span>
          <span class="value">{{ authStore.user.email }}</span>
        </div>
        <div class="detail-item">
          <span class="label">姓名:</span>
          <span class="value">{{ authStore.user.full_name || '未提供' }}</span>
        </div>
        <div class="detail-item">
          <span class="label">角色:</span>
          <span class="value">{{ translateRole(authStore.user.role) }}</span>
        </div>
        <div v-if="authStore.user.created_at" class="detail-item">
          <span class="label">注册时间:</span>
          <span class="value">{{ formatDate(authStore.user.created_at) }}</span>
        </div>
      </div>
      
      <div class="profile-actions">
        <button class="btn btn-primary">修改资料</button>
        <button class="btn btn-outline">修改密码</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

// 角色翻译函数
const translateRole = (role: string) => {
  switch (role) {
    case 'admin': return '管理员';
    case 'teacher': return '教师';
    case 'student': return '学生';
    default: return role;
  }
};

// 格式化日期函数
const formatDate = (dateString: string | null) => {
  if (!dateString) return '未知';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

onMounted(async () => {
  // 检查用户是否已登录
  if (!authStore.isAuthenticated) {
    router.push('/login');
    return;
  }

  try {
    // 如果用户数据未加载，则获取用户资料
    if (!authStore.user) {
      await authStore.fetchProfile();
    }
  } catch (err: any) {
    console.error('加载个人资料失败:', err);
    // 如果未授权，重定向到登录页面
    if (err.status === 401) {
      authStore.logout();
      router.push('/login');
    }
  }
});
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 1rem;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
}

.error {
  color: #e53e3e;
}

.profile-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.profile-header {
  background-color: #4299e1;
  color: white;
  padding: 2rem;
  text-align: center;
}

.avatar-container {
  margin: 0 auto 1rem;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  background-color: #2b6cb0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 3rem;
  font-weight: bold;
}

.role-badge {
  display: inline-block;
  background-color: #2b6cb0;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.profile-details {
  padding: 2rem;
}

.detail-item {
  margin-bottom: 1rem;
  display: flex;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.5rem;
}

.label {
  font-weight: bold;
  min-width: 120px;
  color: #4a5568;
}

.value {
  flex: 1;
}

.profile-actions {
  padding: 0 2rem 2rem;
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #4299e1;
  color: white;
  border: none;
}

.btn-primary:hover {
  background-color: #3182ce;
}

.btn-outline {
  background-color: transparent;
  color: #4299e1;
  border: 1px solid #4299e1;
}

.btn-outline:hover {
  background-color: #ebf8ff;
}
</style> 