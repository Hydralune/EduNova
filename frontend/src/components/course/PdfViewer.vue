<template>
  <div class="pdf-viewer">
    <div v-if="loading" class="flex flex-col justify-center items-center h-[600px] bg-white border rounded-md">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
      <p class="text-gray-500">{{ loadingProgress > 0 ? `加载中... ${loadingProgress}%` : '加载中...' }}</p>
    </div>
    <div v-else-if="error" class="flex flex-col items-center justify-center h-[600px] bg-white border rounded-md">
      <div class="text-red-500 mb-4">{{ error }}</div>
      <div class="flex space-x-4">
        <a 
          :href="pdfUrl" 
          target="_blank" 
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          直接查看
        </a>
        <button 
          @click="$emit('download')" 
          class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
        >
          下载PDF
        </button>
      </div>
    </div>
    <div v-else>
      <!-- 使用object标签直接嵌入PDF，让浏览器使用内置PDF查看器 -->
      <object
        :data="pdfUrl"
        type="application/pdf"
        class="pdf-object"
      >
        <div class="flex flex-col items-center justify-center h-full bg-white">
          <p class="text-red-500 mb-4">您的浏览器不支持直接查看PDF</p>
          <div class="flex space-x-4">
            <a 
              :href="pdfUrl" 
              target="_blank" 
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              直接查看
            </a>
            <button 
              @click="$emit('download')" 
              class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
            >
              下载PDF
            </button>
          </div>
        </div>
      </object>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, defineProps, defineEmits } from 'vue';

const props = defineProps({
  pdfUrl: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['download']);

const loading = ref(true);
const error = ref<string | null>(null);
const loadingProgress = ref(0);

// 监听URL变化
watch(() => props.pdfUrl, (newUrl) => {
  if (newUrl) {
    loadPdf();
  }
}, { immediate: true });

onMounted(() => {
  if (props.pdfUrl) {
    loadPdf();
  }
});

function loadPdf() {
  if (!props.pdfUrl) return;
  
  loading.value = true;
  error.value = null;
  
  // 简单检查URL是否有效
  fetch(props.pdfUrl, { method: 'HEAD' })
    .then(response => {
      if (response.ok) {
        // URL有效，显示PDF
        loading.value = false;
      } else {
        // URL无效，显示错误
        error.value = 'PDF文件不存在或无法访问';
        loading.value = false;
      }
    })
    .catch(() => {
      // 请求失败，显示错误
      error.value = '无法加载PDF文件，请尝试直接查看或下载';
      loading.value = false;
    });
}
</script>

<style scoped>
.pdf-viewer {
  width: 100%;
}

.pdf-object {
  width: 100%;
  height: 600px;
  border-radius: 0.375rem;
  border: 1px solid #e5e7eb;
  background-color: white;
}

/* 尝试通过CSS变量覆盖PDF查看器的主题色 */
:deep(object) {
  --viewer-bg-color: white;
  --viewer-text-color: black;
  --viewer-toolbar-bg-color: #f9fafb;
  --viewer-toolbar-color: #4b5563;
}
</style> 