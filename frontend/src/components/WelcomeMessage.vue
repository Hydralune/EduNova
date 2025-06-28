<template>
  <div class="bg-white shadow overflow-hidden rounded-lg">
    <div class="px-4 py-5 sm:p-6">
      <div class="flex items-center">
        <div class="flex-shrink-0 h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
          <svg class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path v-if="userRole === 'admin'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path v-if="userRole === 'teacher'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            <path v-if="userRole === 'student'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <div class="ml-5">
          <h3 class="text-lg leading-6 font-medium text-gray-900">
            欢迎使用智能教学系统
          </h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">
            您好，{{ userName }}！请根据您的角色选择相应的功能模块。
          </p>
        </div>
      </div>
    </div>
    
    <!-- 快速操作 -->
    <div class="border-t border-gray-200 px-4 py-5 sm:p-6">
      <h4 class="text-base font-medium text-gray-900 mb-4">快速操作</h4>
      
      <!-- 管理员快速操作 -->
      <div v-if="userRole === 'admin'" class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button @click="navigate('users')" class="btn btn-outline flex items-center justify-center">
          <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          用户管理
        </button>
        <button @click="navigate('courses')" class="btn btn-outline flex items-center justify-center">
          <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          课程管理
        </button>
        <button @click="navigate('settings')" class="btn btn-outline flex items-center justify-center">
          <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          系统设置
        </button>
      </div>
      
      <!-- 教师快速操作 -->
      <div v-if="userRole === 'teacher'" class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button @click="navigate('ai-assistant')" class="btn btn-outline flex items-center justify-center">
          <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          智能备课
        </button>
        <button @click="navigate('courses')" class="btn btn-outline flex items-center justify-center">
          <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          考核生成
        </button>
        <button @click="navigate('analytics')" class="btn btn-outline flex items-center justify-center">
          <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          学情分析
        </button>
      </div>
      
      <!-- 学生快速操作 -->
      <div v-if="userRole === 'student'" class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button @click="navigate('courses')" class="btn btn-outline flex items-center justify-center">
          <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          我的课程
        </button>
        <button @click="navigate('ai-assistant')" class="btn btn-outline flex items-center justify-center">
          <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          智能助手
        </button>
        <button @click="navigate('analytics')" class="btn btn-outline flex items-center justify-center">
          <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          学习分析
        </button>
      </div>
    </div>
    
    <!-- 系统状态 -->
    <div class="border-t border-gray-200 px-4 py-5 sm:p-6">
      <h4 class="text-base font-medium text-gray-900 mb-4">系统状态</h4>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="p-3 bg-blue-50 rounded-lg">
          <div class="flex items-center">
            <div class="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
              <svg class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-3">
              <div class="text-sm font-medium text-blue-800">最近登录</div>
              <div class="text-xs text-blue-600">{{ formatDate(lastLogin) }}</div>
            </div>
          </div>
        </div>
        <div class="p-3 bg-green-50 rounded-lg">
          <div class="flex items-center">
            <div class="flex-shrink-0 h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
              <svg class="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-3">
              <div class="text-sm font-medium text-green-800">系统状态</div>
              <div class="text-xs text-green-600">正常运行</div>
            </div>
          </div>
        </div>
        <div class="p-3 bg-purple-50 rounded-lg">
          <div class="flex items-center">
            <div class="flex-shrink-0 h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center">
              <svg class="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <div class="ml-3">
              <div class="text-sm font-medium text-purple-800">AI模块</div>
              <div class="text-xs text-purple-600">已启用</div>
            </div>
          </div>
        </div>
        <div class="p-3 bg-yellow-50 rounded-lg">
          <div class="flex items-center">
            <div class="flex-shrink-0 h-10 w-10 rounded-full bg-yellow-100 flex items-center justify-center">
              <svg class="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-3">
              <div class="text-sm font-medium text-yellow-800">通知</div>
              <div class="text-xs text-yellow-600">{{ notificationCount }} 条未读</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 个人资料 -->
    <div class="border-t border-gray-200 px-4 py-5 sm:p-6">
      <div class="flex items-center justify-between">
        <h4 class="text-base font-medium text-gray-900">个人资料</h4>
        <router-link to="/profile" class="text-sm font-medium text-blue-600 hover:text-blue-500">
          编辑资料
        </router-link>
      </div>
      <div class="mt-4 flex items-center">
        <div class="flex-shrink-0 h-16 w-16 rounded-full bg-gray-200 flex items-center justify-center text-xl font-medium text-gray-600">
          {{ userInitials }}
        </div>
        <div class="ml-4">
          <div class="text-lg font-medium text-gray-900">{{ userName }}</div>
          <div class="text-sm text-gray-500">{{ userEmail }}</div>
          <div class="mt-1 text-sm">
            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" 
              :class="{
                'bg-green-100 text-green-800': userRole === 'admin',
                'bg-blue-100 text-blue-800': userRole === 'teacher',
                'bg-yellow-100 text-yellow-800': userRole === 'student'
              }">
              {{ userRoleText }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineProps, defineEmits } from 'vue';
import { useAuthStore } from '@/stores/auth';

const props = defineProps({
  activeTab: {
    type: String,
    default: 'dashboard'
  }
});

const emit = defineEmits(['update:activeTab']);

const authStore = useAuthStore();

// 用户信息
const userName = computed(() => authStore.user?.full_name || '用户');
const userEmail = computed(() => authStore.user?.email || '');
const userRole = computed(() => authStore.user?.role || '');
const userRoleText = computed(() => {
  switch (userRole.value) {
    case 'admin': return '管理员';
    case 'teacher': return '教师';
    case 'student': return '学生';
    default: return '用户';
  }
});
const userInitials = computed(() => {
  if (!authStore.user?.full_name) return '?';
  return authStore.user.full_name
    .split(' ')
    .map(name => name.charAt(0))
    .join('')
    .toUpperCase();
});

// 系统状态信息
const lastLogin = computed(() => authStore.user?.last_login || new Date().toISOString());
const notificationCount = computed(() => 3); // 示例数据

// 格式化日期
const formatDate = (dateString: string) => {
  try {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (error) {
    return '未知';
  }
};

// 导航方法
const navigate = (tab: string) => {
  emit('update:activeTab', tab);
};
</script>

<style scoped>
.btn {
  @apply px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2;
}

.btn-outline {
  @apply text-gray-700 bg-white border-gray-300 hover:bg-gray-50 focus:ring-blue-500;
}
</style> 