<template>
  <div class="bg-white shadow rounded-lg p-6">
    <div class="mb-6">
      <h3 class="text-lg font-medium text-gray-900">上传课件</h3>
      <p class="mt-1 text-sm text-gray-500">
        支持 PDF、PPT、Word 等格式文件，最大文件大小 50MB
      </p>
    </div>

    <!-- 上传表单 -->
    <form @submit.prevent="handleUpload" class="space-y-6">
      <!-- 课程选择 -->
      <div>
        <label for="course" class="block text-sm font-medium text-gray-700">选择课程</label>
        <select
          id="course"
          v-model="form.course_id"
          required
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        >
          <option value="">请选择课程</option>
          <option v-for="course in courses" :key="course.id" :value="course.id">
            {{ course.name }}
          </option>
        </select>
      </div>

      <!-- 文件上传 -->
      <div>
        <label class="block text-sm font-medium text-gray-700">选择文件</label>
        <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
          <div class="space-y-1 text-center">
            <svg
              class="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
              aria-hidden="true"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            <div class="flex text-sm text-gray-600">
              <label
                for="file-upload"
                class="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
              >
                <span>上传文件</span>
                <input
                  id="file-upload"
                  ref="fileInput"
                  type="file"
                  class="sr-only"
                  @change="handleFileSelect"
                  accept=".pdf,.ppt,.pptx,.doc,.docx,.txt"
                />
              </label>
              <p class="pl-1">或拖拽文件到此处</p>
            </div>
            <p class="text-xs text-gray-500">PDF, PPT, Word, TXT 格式，最大 50MB</p>
          </div>
        </div>
        
        <!-- 文件预览 -->
        <div v-if="selectedFile" class="mt-4 p-4 bg-gray-50 rounded-md">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <svg class="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-900">{{ selectedFile.name }}</p>
                <p class="text-sm text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
              </div>
            </div>
            <button
              type="button"
              @click="removeFile"
              class="text-red-600 hover:text-red-800"
            >
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- 标题 -->
      <div>
        <label for="title" class="block text-sm font-medium text-gray-700">课件标题</label>
        <input
          type="text"
          id="title"
          v-model="form.title"
          required
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          placeholder="请输入课件标题"
        />
      </div>

      <!-- 描述 -->
      <div>
        <label for="description" class="block text-sm font-medium text-gray-700">课件描述</label>
        <textarea
          id="description"
          v-model="form.description"
          rows="3"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          placeholder="请输入课件描述（可选）"
        />
      </div>

      <!-- 上传按钮 -->
      <div class="flex justify-end">
        <button
          type="button"
          @click="$emit('cancel')"
          class="mr-3 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          取消
        </button>
        <button
          type="submit"
          :disabled="uploading || !canUpload"
          class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="uploading" class="flex items-center">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            上传中...
          </span>
          <span v-else>上传课件</span>
        </button>
      </div>
    </form>

    <!-- 错误提示 -->
    <div v-if="error" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
      <div class="flex">
        <svg class="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div class="ml-3">
          <p class="text-sm text-red-800">{{ error }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../../api'

// Props
interface Props {
  courseId?: number
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  success: [material: any]
  cancel: []
}>()

// 响应式数据
const courses = ref([])
const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const error = ref('')

const form = ref({
  course_id: props.courseId || '',
  title: '',
  description: ''
})

// 计算属性
const canUpload = computed(() => {
  return form.value.course_id && selectedFile.value && form.value.title && !uploading.value
})

// 方法
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    
    // 检查文件大小（50MB限制）
    if (file.size > 50 * 1024 * 1024) {
      error.value = '文件大小不能超过50MB'
      return
    }
    
    // 检查文件类型
    const allowedTypes = ['.pdf', '.ppt', '.pptx', '.doc', '.docx', '.txt']
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!allowedTypes.includes(fileExtension)) {
      error.value = '不支持的文件类型，请选择PDF、PPT、Word或TXT文件'
      return
    }
    
    selectedFile.value = file
    error.value = ''
    
    // 如果标题为空，使用文件名作为标题
    if (!form.value.title) {
      form.value.title = file.name.replace(/\.[^/.]+$/, '') // 移除文件扩展名
    }
  }
}

const removeFile = () => {
  selectedFile.value = null
  if (this.$refs.fileInput) {
    this.$refs.fileInput.value = ''
  }
}

const loadCourses = async () => {
  try {
    const response = await api.get('/learning/courses')
    courses.value = response.courses || []
  } catch (err) {
    console.error('加载课程失败:', err)
  }
}

const handleUpload = async () => {
  if (!canUpload.value) return
  
  uploading.value = true
  error.value = ''
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value!)
    formData.append('course_id', form.value.course_id.toString())
    formData.append('title', form.value.title)
    formData.append('description', form.value.description)
    
    const response = await api.post('/material/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    emit('success', response.material)
    
    // 重置表单
    form.value = {
      course_id: props.courseId || '',
      title: '',
      description: ''
    }
    selectedFile.value = null
    if (this.$refs.fileInput) {
      this.$refs.fileInput.value = ''
    }
    
  } catch (err: any) {
    console.error('上传失败:', err)
    error.value = err.error || '上传失败，请重试'
  } finally {
    uploading.value = false
  }
}

// 生命周期
onMounted(() => {
  loadCourses()
})
</script> 