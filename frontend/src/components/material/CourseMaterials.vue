<template>
  <div class="course-materials">
    <!-- 操作按钮 -->
    <div class="flex justify-end mb-6">
      <button 
        v-if="canUpload" 
        @click="showUploadModal = true"
        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        上传课件
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-8">
      <svg class="animate-spin h-8 w-8 text-blue-500 mx-auto" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="mt-2 text-sm text-gray-500">加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="materials.length === 0" class="text-center py-8">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">暂无课件</h3>
      <p class="mt-1 text-sm text-gray-500">还没有上传任何课件</p>
      <div v-if="canUpload" class="mt-6">
        <button
          @click="showUploadModal = true"
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          上传第一个课件
        </button>
      </div>
    </div>

    <!-- 课件列表 -->
    <div v-else class="space-y-4">
      <div
        v-for="material in materials"
        :key="material.id"
        class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
      >
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
            <p v-if="material.content" class="text-sm text-gray-500 truncate mt-1">
              {{ material.content }}
            </p>
            <p class="text-xs text-gray-400 mt-1">
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

    <!-- 上传模态框 -->
    <MaterialUploadModal
      :show="showUploadModal"
      :course-id="courseId"
      @close="showUploadModal = false"
      @success="onUploadSuccess"
    />

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
import { ref, onMounted, watch } from 'vue'
import api from '../../api'
import MaterialUploadModal from './MaterialUploadModal.vue'

// Props
interface Props {
  courseId: number
  canUpload?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  canUpload: false
})

// Emits
const emit = defineEmits<{
  refresh: []
}>()

// 响应式数据
const materials = ref([])
const loading = ref(false)
const showUploadModal = ref(false)
const showEditModal = ref(false)
const editing = ref(false)
const editingMaterial = ref(null)

const editForm = ref({
  title: '',
  content: ''
})

// 方法
const loadMaterials = async () => {
  loading.value = true
  try {
    const response = await api.get(`/material/list/${props.courseId}`)
    materials.value = response.materials || []
    total.value = response.total || 0
  } catch (err) {
    console.error('加载课件失败:', err)
  } finally {
    loading.value = false
  }
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
  editingMaterial.value = material
  editForm.value = {
    title: material.title,
    content: material.content || ''
  }
  showEditModal.value = true
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

const onUploadSuccess = (material: any) => {
  loadMaterials() // 重新加载列表
  emit('refresh')
  alert('课件上传成功！')
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
    await api.put(`/material/${editingMaterial.value.id}`, editForm.value)
    editing.value = false
    editingMaterial.value = null
    loadMaterials() // 重新加载列表
    alert('课件更新成功！')
  } catch (err) {
    console.error('保存失败:', err)
    alert('保存失败，请重试')
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
  return props.canUpload
}

const canDelete = (material: any) => {
  // 这里可以根据用户权限判断是否可以删除
  return props.canUpload
}

// 监听课程ID变化
watch(() => props.courseId, () => {
  loadMaterials()
})

// 生命周期
onMounted(() => {
  loadMaterials()
})
</script> 