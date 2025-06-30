<template>
  <div class="simple-test">
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-8 text-center">AI助手功能测试</h1>
      
      <div class="bg-white rounded-lg shadow-md p-6">
        <!-- API状态测试 -->
        <div class="mb-6 p-4 border rounded-lg">
          <h3 class="text-lg font-semibold mb-3">1. API状态检查</h3>
          <button 
            @click="checkAPIStatus" 
            :disabled="loading"
            class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {{ loading ? '检查中...' : '检查API状态' }}
          </button>
          <div v-if="apiStatus" class="mt-3 p-3 bg-gray-100 rounded text-sm">
            <pre>{{ JSON.stringify(apiStatus, null, 2) }}</pre>
          </div>
        </div>

        <!-- 课程列表测试 -->
        <div class="mb-6 p-4 border rounded-lg">
          <h3 class="text-lg font-semibold mb-3">2. 课程列表获取</h3>
          <button 
            @click="fetchCourses" 
            :disabled="loading"
            class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:bg-gray-400"
          >
            {{ loading ? '获取中...' : '获取课程列表' }}
          </button>
          <div v-if="courses.length > 0" class="mt-3 p-3 bg-green-50 rounded">
            <p class="font-medium text-green-800">找到 {{ courses.length }} 个课程:</p>
            <ul class="mt-2 space-y-1">
              <li v-for="course in courses" :key="course.id" class="text-sm">
                <span class="font-medium">ID: {{ course.id }}</span> - {{ course.name }}
              </li>
            </ul>
          </div>
          <div v-else-if="coursesError" class="mt-3 p-3 bg-red-50 rounded text-red-800">
            {{ coursesError }}
          </div>
        </div>

        <!-- 聊天测试 -->
        <div class="mb-6 p-4 border rounded-lg">
          <h3 class="text-lg font-semibold mb-3">3. 聊天功能测试</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-sm font-medium mb-1">聊天模式:</label>
              <select v-model="chatMode" class="w-full p-2 border rounded">
                <option value="general">普通AI问答</option>
                <option value="rag">知识库增强</option>
              </select>
            </div>
            
            <div v-if="chatMode === 'rag'">
              <label class="block text-sm font-medium mb-1">选择课程:</label>
              <select v-model="selectedCourseId" class="w-full p-2 border rounded">
                <option value="">请选择课程</option>
                <option v-for="course in courses" :key="course.id" :value="course.id">
                  {{ course.name }} (ID: {{ course.id }})
                </option>
              </select>
            </div>
          </div>
          
          <div class="mb-4">
            <label class="block text-sm font-medium mb-1">输入问题:</label>
            <input 
              v-model="testMessage" 
              placeholder="输入测试问题..." 
              class="w-full p-2 border rounded"
            />
          </div>
          
          <button 
            @click="testChat" 
            :disabled="loading || !testMessage.trim() || (chatMode === 'rag' && !selectedCourseId)"
            class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 disabled:bg-gray-400"
          >
            {{ loading ? '发送中...' : '发送测试消息' }}
          </button>
          
          <div v-if="chatResponse" class="mt-3 p-3 bg-gray-100 rounded">
            <h4 class="font-medium mb-2">响应结果:</h4>
            <pre class="text-sm">{{ JSON.stringify(chatResponse, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ragAiAPI, courseAPI } from '../api'

const loading = ref(false)
const apiStatus = ref(null)
const courses = ref([])
const coursesError = ref(null)
const chatMode = ref('general')
const selectedCourseId = ref('')
const testMessage = ref('你好，请介绍一下你自己')
const chatResponse = ref(null)

const checkAPIStatus = async () => {
  loading.value = true
  try {
    const response = await ragAiAPI.getStatus()
    apiStatus.value = {
      success: true,
      data: response.data
    }
  } catch (error) {
    apiStatus.value = {
      success: false,
      error: error.message,
      details: error.response?.data
    }
  } finally {
    loading.value = false
  }
}

const fetchCourses = async () => {
  loading.value = true
  coursesError.value = null
  try {
    const response = await courseAPI.getCourses()
    courses.value = response.data?.courses || []
    console.log('课程数据:', courses.value)
  } catch (error) {
    coursesError.value = `获取课程失败: ${error.message}`
    console.error('获取课程失败:', error)
  } finally {
    loading.value = false
  }
}

const testChat = async () => {
  loading.value = true
  chatResponse.value = null
  
  try {
    const params = {
      message: testMessage.value,
      stream: false
    }
    
    if (chatMode.value === 'rag' && selectedCourseId.value) {
      params.course_id = selectedCourseId.value
      params.use_rag = true
    } else {
      params.use_rag = false
    }
    
    console.log('发送聊天请求:', params)
    
    const response = await ragAiAPI.chat(params)
    
    chatResponse.value = {
      success: true,
      data: response.data
    }
  } catch (error) {
    chatResponse.value = {
      success: false,
      error: error.message,
      details: error.response?.data
    }
    console.error('聊天测试失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.simple-test {
  min-height: 100vh;
  background-color: #f8fafc;
}
</style> 