<template>
  <div class="min-h-screen bg-gray-50 py-6">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">课件管理</h1>
        <p class="mt-2 text-sm text-gray-500">
          管理课程课件，支持上传、下载、编辑和删除操作
        </p>
      </div>

      <!-- 课程选择 -->
      <div class="mb-6">
        <label for="course-select" class="block text-sm font-medium text-gray-700 mb-2">
          选择课程
        </label>
        <select
          id="course-select"
          v-model="selectedCourseId"
          @change="onCourseChange"
          class="block w-full max-w-xs rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        >
          <option value="">请选择课程</option>
          <option v-for="course in courses" :key="course.id" :value="course.id">
            {{ course.name }}
          </option>
        </select>
      </div>

      <!-- 主要内容区域 -->
      <div v-if="selectedCourseId" class="space-y-6">
        <!-- 上传区域 -->
        <div v-if="showUploadForm">
          <MaterialUpload
            :course-id="selectedCourseId"
            @success="onUploadSuccess"
            @cancel="showUploadForm = false"
          />
        </div>

        <!-- 课件列表 -->
        <MaterialList
          :course-id="selectedCourseId"
          @upload="showUploadForm = true"
          @edit="onEditMaterial"
          @delete="onDeleteMaterial"
        />
      </div>

      <!-- 未选择课程时的提示 -->
      <div v-else class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">请选择课程</h3>
        <p class="mt-1 text-sm text-gray-500">选择一个课程来管理其课件</p>
      </div>
    </div>

    <!-- 编辑模态框 -->
    <div v-if="showEditModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-medium text-gray-900">编辑课件</h3>
            <button @click="closeEditModal" class="text-gray-400 hover:text-gray-600">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form @submit.prevent="handleEditSubmit" class="space-y-4">
            <div>
              <label for="edit-title" class="block text-sm font-medium text-gray-700">课件标题</label>
              <input
                type="text"
                id="edit-title"
                v-model="editForm.title"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
            </div>

            <div>
              <label for="edit-description" class="block text-sm font-medium text-gray-700">课件描述</label>
              <textarea
                id="edit-description"
                v-model="editForm.content"
                rows="3"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
            </div>

            <div class="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                @click="closeEditModal"
                class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                取消
              </button>
              <button
                type="submit"
                :disabled="editing"
                class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {{ editing ? '保存中...' : '保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import MaterialUpload from '@/components/material/MaterialUpload.vue'
import MaterialList from '@/components/material/MaterialList.vue'

// 响应式数据
const courses = ref([])
const selectedCourseId = ref('')
const showUploadForm = ref(false)
const showEditModal = ref(false)
const editing = ref(false)
const editingMaterial = ref(null)

const editForm = ref({
  title: '',
  content: ''
})

// 方法
const loadCourses = async () => {
  try {
    const response = await axios.get('/api/learning/courses', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    courses.value = response.data.courses || []
  } catch (err) {
    console.error('加载课程失败:', err)
  }
}

const onCourseChange = () => {
  showUploadForm.value = false
}

const onUploadSuccess = (material: any) => {
  showUploadForm.value = false
  // 可以在这里显示成功消息
  alert('课件上传成功！')
}

const onEditMaterial = (material: any) => {
  editingMaterial.value = material
  editForm.value = {
    title: material.title,
    content: material.content || ''
  }
  showEditModal.value = true
}

const onDeleteMaterial = (material: any) => {
  // 删除成功后的处理
  alert('课件删除成功！')
}

const closeEditModal = () => {
  showEditModal.value = false
  editingMaterial.value = null
  editForm.value = {
    title: '',
    content: ''
  }
}

const handleEditSubmit = async () => {
  if (!editingMaterial.value) return
  
  editing.value = true
  try {
    await axios.put(`/api/material/${editingMaterial.value.id}`, editForm.value, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    closeEditModal()
    alert('课件更新成功！')
  } catch (err) {
    console.error('更新失败:', err)
    alert('更新失败，请重试')
  } finally {
    editing.value = false
  }
}

// 生命周期
onMounted(() => {
  loadCourses()
})
</script> 