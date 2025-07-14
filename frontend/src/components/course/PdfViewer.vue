<template>
  <div class="pdf-viewer">
    <div v-if="loading" class="flex flex-col justify-center items-center h-[600px] bg-white rounded-md">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
      <p class="text-gray-500">{{ loadingProgress > 0 ? `加载中... ${loadingProgress}%` : '加载中...' }}</p>
    </div>

    <div v-else-if="error" class="flex flex-col items-center justify-center h-[600px] bg-white rounded-md">
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

    <!-- 正常渲染 -->
    <div v-else class="pdf-doc overflow-y-auto max-h-[600px]">
      <VuePdf
        v-for="page in numPages"
        :key="page"
        :src="pdfSrc"
        :page="page"
        class="mb-4 rounded-md shadow"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, defineEmits } from 'vue'
import { VuePdf, createLoadingTask } from 'vue3-pdfjs/esm'
import type { PDFDocumentProxy } from 'pdfjs-dist/types/src/display/api'

const props = defineProps({
  pdfUrl: {
    type: String,
    required: true
  }
})

defineEmits(['download'])

const loading = ref(true)
const error = ref<string | null>(null)
const loadingProgress = ref(0)
const numPages = ref(0)
const pdfSrc = ref(props.pdfUrl)

function loadPdf(url: string) {
  if (!url) return
  loading.value = true
  error.value = null
  loadingProgress.value = 0
  numPages.value = 0

  const task = createLoadingTask(url)
  task.onProgress = (progressData: { loaded: number; total: number }) => {
    if (progressData && progressData.total) {
      loadingProgress.value = Math.floor((progressData.loaded / progressData.total) * 100)
    }
  }

  task.promise
    .then((pdf: PDFDocumentProxy) => {
      numPages.value = pdf.numPages
      loading.value = false
    })
    .catch(() => {
      error.value = '无法加载PDF文件，请尝试直接查看或下载'
      loading.value = false
    })
}

watch(
  () => props.pdfUrl,
  (newUrl) => {
    pdfSrc.value = newUrl
    if (newUrl) {
      loadPdf(newUrl)
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.pdf-viewer {
  width: 100%;
}

.pdf-doc {
  width: 100%;
}
</style> 