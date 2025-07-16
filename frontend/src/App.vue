<template>
  <div id="app" class="min-h-screen bg-gray-50 flex flex-col">
    <!-- 全局加载指示器 -->
    <div v-if="isInitializing" class="fixed inset-0 bg-white flex items-center justify-center z-50">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">正在加载...</p>
      </div>
    </div>

    <!-- 主要内容 -->
    <div v-else class="flex flex-col flex-grow">
      <!-- 导航栏 -->
      <nav v-if="showNavigation" class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between h-16">
            <div class="flex items-center">
              <router-link to="/" class="flex items-center">
                <div class="flex-shrink-0 flex items-center">
                  <img src="@/assets/images/atom.png" alt="Atom Icon" class="h-8 w-8 mr-2" />
                  <h1 class="text-xl font-bold text-primary-600">智能教学系统</h1>
                </div>
              </router-link>
              
              <!-- 导航链接 -->
              <div v-if="authStore.user" class="ml-6 flex space-x-4">
                <!-- 智能助手链接已移除 -->
              </div>
            </div>

            <div class="flex items-center space-x-4">
              <template v-if="authStore.user">
                <!-- 用户菜单 -->
                <div class="relative">
                  <button
                    @click="toggleUserMenu"
                    class="flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    <div class="h-8 w-8 rounded-full overflow-hidden flex items-center justify-center">
                      <img 
                        v-if="authStore.user?.avatar_url" 
                        :src="`http://localhost:5001${authStore.user.avatar_url}`" 
                        alt="用户头像" 
                        class="h-full w-full object-cover"
                      />
                      <div v-else class="h-full w-full bg-primary-600 flex items-center justify-center">
                        <span class="text-white text-sm font-medium">
                          {{ authStore.user?.full_name?.charAt(0) || authStore.user?.username?.charAt(0) || 'U' }}
                        </span>
                      </div>
                    </div>
                    <span class="ml-2 text-gray-700">{{ authStore.user?.full_name || authStore.user?.username }}</span>
                  </button>

                  <!-- 下拉菜单 -->
                  <div
                    v-if="userMenuOpen"
                    @click="toggleUserMenu"
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

      <!-- 页脚 -->
      <footer v-if="showNavigation" class="bg-white border-t border-gray-200 py-4 mt-auto">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="text-center text-xs text-gray-500">
            <a href="https://www.flaticon.com/free-icons/atom" title="atom icons" class="hover:text-primary-600">
              Atom icons created by Freepik - Flaticon
            </a>
          </div>
        </div>
      </footer>
    </div>
    
    <!-- 全局通知容器 -->
    <NotificationContainer />
    
    <!-- 全局确认对话框 -->
    <ConfirmDialog
      :show="dialogState.visible.value"
      :title="dialogState.options.value.title"
      :message="dialogState.options.value.message"
      :confirm-text="dialogState.options.value.confirmText || '确定'"
      :cancel-text="dialogState.options.value.cancelText || '取消'"
      :type="dialogState.options.value.type || 'info'"
      @confirm="handleDialogConfirm"
      @cancel="handleDialogCancel"
      @update:show="(val) => dialogState.visible.value = val"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, provide } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { courseAPI, materialAPI } from './api'
import NotificationContainer from './components/NotificationContainer.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'
import notificationService from './services/notificationService'
import dialogService from './services/dialogService'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 状态
const isInitializing = ref(true)
const userMenuOpen = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)

// 全局数据
const globalCourses = ref<any[]>([]);
const globalMaterials = ref<any[]>([]);
const isDataLoaded = ref(false);
const isDataLoading = ref(false);

// 提供全局数据给组件使用
provide('courses', globalCourses);
provide('materials', globalMaterials);
provide('isDataLoaded', isDataLoaded);
provide('isDataLoading', isDataLoading);

// 计算属性
const showNavigation = computed(() => {
  const hideNavRoutes = ['/login', '/register']
  return !hideNavRoutes.includes(route.path)
})

// 方法
const handleLogout = async () => {
  try {
    authStore.logout()
    notificationService.success('退出成功', '您已成功退出登录')
    router.push('/login')
  } catch (error) {
    notificationService.error('退出失败', '退出登录时发生错误')
  }
}

// 提供通知服务给所有组件使用
provide('showNotification', (type: 'success' | 'error' | 'warning' | 'info', title: string, message?: string) => {
  notificationService.show(type, title, message);
});

function toggleUserMenu() {
  userMenuOpen.value = !userMenuOpen.value
}

function handleClickOutside(event: MouseEvent) {
  if (userMenuRef.value && !(userMenuRef.value as HTMLElement).contains(event.target as HTMLElement)) {
    userMenuOpen.value = false
  }
}

// 对话框状态
const dialogState = dialogService.getDialogState();

// 对话框确认和取消处理
const handleDialogConfirm = () => {
  if (dialogState.options.value.onConfirm) {
    dialogState.options.value.onConfirm();
  }
};

const handleDialogCancel = () => {
  if (dialogState.options.value.onCancel) {
    dialogState.options.value.onCancel();
  }
};

// 提供对话框服务给所有组件使用
provide('confirm', async (message: string, title?: string) => {
  return await dialogService.confirm({
    title: title || '确认',
    message
  });
});

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

  // 如果用户已登录，预加载课程和材料数据
  if (authStore.user) {
    await loadGlobalData();
  }
  
  // 初始化导航历史记录
  initNavigationHistory();
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 初始化导航历史记录
function initNavigationHistory() {
  // 监听路由变化，记录导航历史
  router.afterEach((to, from) => {
    // 记录当前路由到历史记录
    const navigationHistory = JSON.parse(sessionStorage.getItem('navigationHistory') || '[]');
    
    // 避免重复记录相同路径
    if (navigationHistory.length === 0 || navigationHistory[navigationHistory.length - 1] !== from.fullPath) {
      navigationHistory.push(from.fullPath);
      // 限制历史记录长度，避免过长
      if (navigationHistory.length > 20) {
        navigationHistory.shift();
      }
      sessionStorage.setItem('navigationHistory', JSON.stringify(navigationHistory));
    }
  });
}

// 全局错误处理
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason)
  notificationService.error('系统错误', '发生了未预期的错误，请刷新页面重试')
})

// 监听登录状态变化
authStore.$subscribe((mutation, state) => {
  if (state.user && !isDataLoaded.value && !isDataLoading.value) {
    loadGlobalData();
  }
});

async function loadGlobalData() {
  if (isDataLoading.value) return;
  
  isDataLoading.value = true;
  try {
    // 加载课程数据
    const courseResponse = await courseAPI.getCourses();
    const courses = courseResponse && typeof courseResponse === 'object' ? (courseResponse as any).courses || [] : [];
    
    if (Array.isArray(courses)) {
      globalCourses.value = courses;
      
      // 加载每个课程的材料
      const allMaterials: any[] = [];
      for (const course of globalCourses.value) {
        try {
          const materialResponse = await materialAPI.getMaterials(course.id);
          const materials = materialResponse && typeof materialResponse === 'object' ? (materialResponse as any).materials || [] : [];
          
          if (Array.isArray(materials)) {
            allMaterials.push(...materials);
          }
        } catch (error) {
          console.error(`加载课程 ${course.id} 的材料失败:`, error);
        }
      }
      
      globalMaterials.value = allMaterials;
    }
    
    isDataLoaded.value = true;
  } catch (error) {
    console.error('加载全局数据失败:', error);
  } finally {
    isDataLoading.value = false;
  }
}
</script>

<style>
/* 主色调 */
:root {
  --color-primary-50: #eef2ff;
  --color-primary-100: #e0e7ff;
  --color-primary-200: #c7d2fe;
  --color-primary-300: #a5b4fc;
  --color-primary-400: #818cf8;
  --color-primary-500: #6366f1;
  --color-primary-600: #4f46e5;
  --color-primary-700: #4338ca;
  --color-primary-800: #3730a3;
  --color-primary-900: #312e81;
}

/* 全局样式 */
.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  outline: none;
  transition: all 0.2s;
}

.btn:focus {
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.5);
}

.btn-primary {
  background-color: var(--color-primary-600);
  color: white;
}

.btn-primary:hover {
  background-color: var(--color-primary-700);
}

.btn-outline {
  border: 1px solid #d1d5db;
  color: #374151;
  background-color: white;
}

.btn-outline:hover {
  background-color: #f9fafb;
}

.text-primary-600 {
  color: var(--color-primary-600);
}

.bg-primary-600 {
  background-color: var(--color-primary-600);
}

/* 通知容器样式 */
.notification-wrapper {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 9999;
  pointer-events: none;
}

.notification-wrapper > * {
  pointer-events: auto;
}
</style> 