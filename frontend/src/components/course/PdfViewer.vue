<template>
  <div class="pdf-viewer">
    <div v-if="loading" class="flex flex-col justify-center items-center h-[900px] bg-white rounded-md">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
      <p class="text-gray-500">{{ loadingProgress > 0 ? `加载中... ${loadingProgress}%` : '加载中...' }}</p>
    </div>
    <div v-else-if="error" class="flex flex-col items-center justify-center h-[900px] bg-white rounded-md">
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
    <div v-else class="relative">
      <!-- 顶部控制栏 -->
      <div class="absolute top-0 left-0 right-0 z-10 bg-gray-100 bg-opacity-90 p-2 flex justify-between items-center">
        <div class="flex space-x-2">
          <button 
            @click="$emit('download')" 
            class="px-3 py-1 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors text-sm flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            下载
          </button>
          <a 
            :href="pdfUrl" 
            target="_blank" 
            class="px-3 py-1 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors text-sm flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            新窗口打开
          </a>
        </div>
        <div class="flex space-x-2">
          <button 
            @click="toggleViewMode" 
            class="px-3 py-1 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors text-sm flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path v-if="viewMode === 'single'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2" />
            </svg>
            {{ viewMode === 'single' ? '双页视图' : '单页视图' }}
          </button>
          <button 
            @click="toggleFullscreen" 
            class="px-3 py-1 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors text-sm flex items-center"
          >
            <svg v-if="!isFullscreen" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5v-4m0 4h-4m4 0l-5-5" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            {{ isFullscreen ? '退出全屏' : '全屏' }}
          </button>
        </div>
      </div>

      <!-- 使用iframe嵌入PDF，让浏览器使用内置PDF查看器 -->
      <iframe
        ref="pdfFrame"
        :src="pdfViewerUrl"
        class="pdf-object"
        :class="{ 'fullscreen': isFullscreen }"
        allow="fullscreen"
        allowfullscreen
      ></iframe>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, defineProps, defineEmits, computed } from 'vue';

const props = defineProps({
  pdfUrl: {
    type: String,
    required: true
  }
});

// 视图模式：单页或双页
const viewMode = ref<'single' | 'double'>('single');

// 根据视图模式和URL生成PDF查看器URL
const pdfViewerUrl = computed(() => {
  if (!props.pdfUrl) return '';
  
  // 添加PDF查看参数
  let url = props.pdfUrl + '#toolbar=0';
  
  // 如果是双页模式，添加相应参数
  if (viewMode.value === 'double') {
    // 添加双页视图参数
    url += '&view=FitH&page=1&pagemode=thumbs&view=Fit';
  }
  
  return url;
});

const emit = defineEmits(['download']);

const loading = ref(true);
const error = ref<string | null>(null);
const loadingProgress = ref(0);
const isFullscreen = ref(false);
const pdfFrame = ref<HTMLIFrameElement | null>(null);

// 切换视图模式
function toggleViewMode() {
  viewMode.value = viewMode.value === 'single' ? 'double' : 'single';
  
  // 当切换视图模式时，需要重新加载PDF以应用新的参数
  if (pdfFrame.value) {
    pdfFrame.value.src = pdfViewerUrl.value;
  }
}

// 监听URL变化
watch(() => props.pdfUrl, (newUrl) => {
  if (newUrl) {
    loadPdf();
  }
}, { immediate: true });

// 监听窗口大小变化，自动切换视图模式
function handleResize() {
  // 如果窗口宽度大于1400px，自动切换到双页模式
  if (window.innerWidth > 1400 && viewMode.value === 'single') {
    viewMode.value = 'double';
    if (pdfFrame.value) {
      pdfFrame.value.src = pdfViewerUrl.value;
    }
  } 
  // 如果窗口宽度小于1400px，自动切换到单页模式
  else if (window.innerWidth <= 1400 && viewMode.value === 'double') {
    viewMode.value = 'single';
    if (pdfFrame.value) {
      pdfFrame.value.src = pdfViewerUrl.value;
    }
  }
}

onMounted(() => {
  if (props.pdfUrl) {
    loadPdf();
  }
  
  // 监听全屏变化事件
  document.addEventListener('fullscreenchange', handleFullscreenChange);
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize);
  
  // 初始检查窗口大小
  handleResize();
});

function handleFullscreenChange() {
  isFullscreen.value = Boolean(document.fullscreenElement);
}

function toggleFullscreen() {
  if (!pdfFrame.value) return;
  
  if (!isFullscreen.value) {
    // 进入全屏
    pdfFrame.value.requestFullscreen().catch(err => {
      console.error('无法进入全屏模式:', err);
    });
  } else {
    // 退出全屏
    if (document.exitFullscreen) {
      document.exitFullscreen().catch(err => {
        console.error('无法退出全屏模式:', err);
      });
    }
  }
}

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
  height: 900px;
  border-radius: 0.375rem;
  background-color: white;
  border: none;
}

.pdf-object.fullscreen {
  height: 100vh;
  border-radius: 0;
}

/* 全屏时隐藏控制栏 */
:fullscreen .pdf-object {
  height: 100vh;
}
</style> 