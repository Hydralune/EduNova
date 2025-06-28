<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- 全局加载指示器 -->
    <div v-if="isInitializing" class="fixed inset-0 bg-white flex items-center justify-center z-50">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">正在加载...</p>
      </div>
    </div>

    <!-- 主要内容 -->
    <div v-else>
      <!-- 导航栏 -->
      <nav v-if="showNavigation" class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between h-16">
            <div class="flex items-center">
              <router-link to="/" class="flex items-center">
                <div class="flex-shrink-0">
                  <h1 class="text-xl font-bold text-primary-600">智能教学系统</h1>
                </div>
              </router-link>
            </div>

            <div class="flex items-center space-x-4">
              <template v-if="authStore.isAuthenticated">
                <!-- 用户菜单 -->
                <div class="relative">
                  <button
                    @click="showUserMenu = !showUserMenu"
                    class="flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    <div class="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center">
                      <span class="text-white text-sm font-medium">
                        {{ authStore.user?.full_name?.charAt(0) || 'U' }}
                      </span>
                    </div>
                    <span class="ml-2 text-gray-700">{{ authStore.user?.full_name }}</span>
                  </button>

                  <!-- 下拉菜单 -->
                  <div
                    v-if="showUserMenu"
                    @click="showUserMenu = false"
                    class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50"
                  >
                    <div class="py-1">
                      <router-link
                        to="/profile"
                        class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        个人资料
                      </router-link>
                      <button
                        @click="handleLogout"
                        class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        退出登录
                      </button>
                    </div>
                  </div>
                </div>
              </template>
              <template v-else>
                <router-link
                  to="/login"
                  class="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
                >
                  登录
                </router-link>
                <router-link
                  to="/register"
                  class="btn btn-primary"
                >
                  注册
                </router-link>
              </template>
            </div>
          </div>
        </div>
      </nav>

      <!-- 路由视图 -->
      <main class="flex-1">
        <router-view />
      </main>

      <!-- 全局通知 -->
      <div
        v-if="notification.show"
        class="fixed top-4 right-4 z-50 max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden"
      >
        <div class="p-4">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <div
                :class="{
                  'text-green-400': notification.type === 'success',
                  'text-red-400': notification.type === 'error',
                  'text-yellow-400': notification.type === 'warning',
                  'text-blue-400': notification.type === 'info'
                }"
              >
                <!-- 图标 -->
                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    v-if="notification.type === 'success'"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                  <path
                    v-else-if="notification.type === 'error'"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                  <path
                    v-else
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>
            <div class="ml-3 w-0 flex-1 pt-0.5">
              <p class="text-sm font-medium text-gray-900">{{ notification.title }}</p>
              <p v-if="notification.message" class="mt-1 text-sm text-gray-500">
                {{ notification.message }}
              </p>
            </div>
            <div class="ml-4 flex-shrink-0 flex">
              <button
                @click="hideNotification"
                class="bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <span class="sr-only">关闭</span>
                <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fill-rule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clip-rule="evenodd"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 状态
const isInitializing = ref(true)
const showUserMenu = ref(false)
const notification = ref({
  show: false,
  type: 'info' as 'success' | 'error' | 'warning' | 'info',
  title: '',
  message: ''
})

// 计算属性
const showNavigation = computed(() => {
  const hideNavRoutes = ['/login', '/register']
  return !hideNavRoutes.includes(route.path)
})

// 方法
const handleLogout = async () => {
  try {
    authStore.logout()
    showNotification('success', '退出成功', '您已成功退出登录')
    router.push('/login')
  } catch (error) {
    showNotification('error', '退出失败', '退出登录时发生错误')
  }
}

const showNotification = (
  type: 'success' | 'error' | 'warning' | 'info',
  title: string,
  message?: string
) => {
  notification.value = {
    show: true,
    type,
    title,
    message: message || ''
  }
  
  // 3秒后自动隐藏
  setTimeout(() => {
    hideNotification()
  }, 3000)
}

const hideNotification = () => {
  notification.value.show = false
}

// 点击外部关闭用户菜单
const handleClickOutside = (event: Event) => {
  const target = event.target as Element
  if (!target.closest('.relative')) {
    showUserMenu.value = false
  }
}

// 生命周期
onMounted(async () => {
  // 初始化认证状态
  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchProfile()
    } catch (error) {
      console.error('Failed to fetch profile:', error)
      authStore.logout()
    }
  }
  
  isInitializing.value = false
  
  // 添加点击外部事件监听
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 全局错误处理
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason)
  showNotification('error', '系统错误', '发生了未预期的错误，请刷新页面重试')
})
</script>

<style scoped>
/* 组件特定样式 */
</style>

