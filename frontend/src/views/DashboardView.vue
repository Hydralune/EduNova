<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <!-- 页面标题 -->
      <div class="px-4 py-6 sm:px-0">
        <div class="border-4 border-dashed border-gray-200 rounded-lg p-8 text-center">
          <div class="flex items-center justify-center mb-4">
            <img src="@/assets/images/atom.png" alt="Atom Icon" class="h-10 w-10 mr-3" />
            <h1 class="text-3xl font-bold text-gray-900">
              欢迎使用智能教学系统
            </h1>
          </div>
          <p class="text-lg text-gray-600 mb-8">
            您好，{{ authStore.user?.full_name }}！请根据您的角色选择相应的功能模块。
          </p>
          
          <!-- 角色导航卡片 -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <!-- 学生模块 -->
            <div v-if="authStore.isStudent || authStore.isAdmin" class="card hover:shadow-lg transition-shadow duration-200">
              <div class="text-center">
                <div class="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-blue-100 mb-4">
                  <svg class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <h3 class="text-lg font-medium text-gray-900 mb-2">学生模块</h3>
                <p class="text-sm text-gray-500 mb-4">
                  在线学习助手、练习评测、课程资源
                </p>
                <router-link
                  to="/student"
                  class="btn btn-primary w-full"
                >
                  进入学习
                </router-link>
              </div>
            </div>
            
            <!-- 教师模块 -->
            <div v-if="authStore.isTeacher || authStore.isAdmin" class="card hover:shadow-lg transition-shadow duration-200">
              <div class="text-center">
                <div class="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-green-100 mb-4">
                  <svg class="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 class="text-lg font-medium text-gray-900 mb-2">教师模块</h3>
                <p class="text-sm text-gray-500 mb-4">
                  智能备课、考核生成、学情分析
                </p>
                <router-link
                  to="/teacher"
                  class="btn btn-primary w-full"
                >
                  进入教学
                </router-link>
              </div>
            </div>
            
            <!-- 管理员模块 -->
            <div v-if="authStore.isAdmin" class="card hover:shadow-lg transition-shadow duration-200">
              <div class="text-center">
                <div class="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-purple-100 mb-4">
                  <svg class="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 class="text-lg font-medium text-gray-900 mb-2">管理员模块</h3>
                <p class="text-sm text-gray-500 mb-4">
                  用户管理、系统监控、数据分析
                </p>
                <router-link
                  to="/admin"
                  class="btn btn-primary w-full"
                >
                  进入管理
                </router-link>
              </div>
            </div>
          </div>
          
          <!-- 快速操作 -->
          <div class="mt-12">
            <h2 class="text-xl font-semibold text-gray-900 mb-6">快速操作</h2>
            <div class="flex flex-wrap justify-center gap-4">
              <router-link
                to="/profile"
                class="btn btn-outline"
              >
                个人资料
              </router-link>
              <button
                @click="checkSystemHealth"
                class="btn btn-outline"
                :disabled="isCheckingHealth"
              >
                {{ isCheckingHealth ? '检查中...' : '系统状态' }}
              </button>
            </div>
          </div>
          
          <!-- 系统状态 -->
          <div v-if="systemHealth" class="mt-6 p-4 bg-green-50 rounded-lg">
            <p class="text-green-800">
              <svg class="inline h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              {{ systemHealth.message }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
// import { healthAPI } from '@/services/api'

const authStore = useAuthStore()

const isCheckingHealth = ref(false)
const systemHealth = ref<any>(null)

const checkSystemHealth = async () => {
  try {
    isCheckingHealth.value = true
    // 临时禁用健康检查功能，等待API实现
    // const response = await healthAPI.check()
    systemHealth.value = { message: '系统正常运行中' }
  } catch (error) {
    console.error('Health check failed:', error)
    systemHealth.value = { message: '系统检查失败，请稍后重试' }
  } finally {
    isCheckingHealth.value = false
  }
}
</script>

