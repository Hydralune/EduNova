<template>
  <div class="bg-white shadow rounded-lg">
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-medium text-gray-900">课件列表</h3>
        <button
          @click="$emit('upload')"
          class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          上传课件
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="px-6 py-8 text-center">
      <svg class="animate-spin mx-auto h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="mt-2 text-sm text-gray-500">加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="materials.length === 0" class="px-6 py-8 text-center">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">暂无课件</h3>
      <p class="mt-1 text-sm text-gray-500">开始上传第一个课件吧！</p>
      <div class="mt-6">
        <button
          @click="$emit('upload')"
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          上传课件
        </button>
      </div>
    </div>

    <!-- 课件列表 -->
    <div v-else class="divide-y divide-gray-200">
      <div
        v-for="material in materials"
        :key="material.id"
        class="px-6 py-4 hover:bg-gray-50"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <!-- 文件类型图标 -->
            <div class="flex-shrink-0">
              <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="getFileTypeColor(material.material_type)">
                <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>

            <!-- 课件信息 -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-2">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {{ material.title }}
                </p>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="getFileTypeBadgeColor(material.material_type)">
                  {{ getFileTypeText(material.material_type) }}
                </span>
              </div>
              <p v-if="material.content" class="text-sm text-gray-500 truncate">
                {{ material.content }}
              </p>
              <p class="text-xs text-gray-400">
                上传时间：{{ formatDate(material.created_at) }}
              </p>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="flex items-center space-x-2">
            <button
              @click="downloadMaterial(material)"
              class="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              下载
            </button>
            <button
              v-if="canEdit(material)"
              @click="editMaterial(material)"
              class="text-gray-600 hover:text-gray-800 text-sm font-medium"
            >
              编辑
            </button>
            <button
              v-if="canDelete(material)"
              @click="deleteMaterial(material)"
              class="text-red-600 hover:text-red-800 text-sm font-medium"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="total > perPage" class="px-6 py-4 border-t border-gray-200">
      <div class="flex items-center justify-between">
        <div class="text-sm text-gray-700">
          显示 {{ (currentPage - 1) * perPage + 1 }} 到 {{ Math.min(currentPage * perPage, total) }} 条，
          共 {{ total }} 条
        </div>
        <div class="flex space-x-2">
          <button
            @click="changePage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            上一页
          </button>
          <button
            @click="changePage(currentPage + 1)"
            :disabled="currentPage >= Math.ceil(total / perPage)"
            class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import api from '../../api'

// Props
interface Props {
  courseId: number
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  upload: []
  edit: [material: any]
  delete: [material: any]
}>()

// 响应式数据
const materials = ref([])
const loading = ref(false)
const currentPage = ref(1)
const perPage = ref(10)
const total = ref(0)

// 方法
const loadMaterials = async () => {
  loading.value = true
  try {
    const response = await api.get(`/material/list/${props.courseId}`, {
      params: {
        page: currentPage.value,
        per_page: perPage.value
      }
    })
    
    materials.value = response.materials || []
    total.value = response.total || 0
  } catch (err) {
    console.error('加载课件失败:', err)
  } finally {
    loading.value = false
  }
}

const changePage = (page: number) => {
  currentPage.value = page
  loadMaterials()
}

const downloadMaterial = async (material: any) => {
  try {
    const response = await api.get(`/material/download/${material.id}`, {
      responseType: 'blob'
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', material.title)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('下载失败:', err)
    alert('下载失败，请重试')
  }
}

const editMaterial = (material: any) => {
  emit('edit', material)
}

const deleteMaterial = async (material: any) => {
  if (!confirm(`确定要删除课件"${material.title}"吗？`)) {
    return
  }
  
  try {
    await api.delete(`/material/${material.id}`)
    emit('delete', material)
    loadMaterials() // 重新加载列表
  } catch (err) {
    console.error('删除失败:', err)
    alert('删除失败，请重试')
  }
}

const getFileTypeColor = (type: string) => {
  switch (type) {
    case 'pdf': return 'bg-red-500'
    case 'ppt': return 'bg-orange-500'
    case 'doc': return 'bg-blue-500'
    case 'text': return 'bg-green-500'
    default: return 'bg-gray-500'
  }
}

const getFileTypeBadgeColor = (type: string) => {
  switch (type) {
    case 'pdf': return 'bg-red-100 text-red-800'
    case 'ppt': return 'bg-orange-100 text-orange-800'
    case 'doc': return 'bg-blue-100 text-blue-800'
    case 'text': return 'bg-green-100 text-green-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getFileTypeText = (type: string) => {
  switch (type) {
    case 'pdf': return 'PDF'
    case 'ppt': return 'PPT'
    case 'doc': return 'Word'
    case 'text': return 'TXT'
    default: return '文件'
  }
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const canEdit = (material: any) => {
  // 这里可以根据用户权限判断是否可以编辑
  return true
}

const canDelete = (material: any) => {
  // 这里可以根据用户权限判断是否可以删除
  return true
}

// 监听课程ID变化
watch(() => props.courseId, () => {
  currentPage.value = 1
  loadMaterials()
})

// 生命周期
onMounted(() => {
  loadMaterials()
})
</script>