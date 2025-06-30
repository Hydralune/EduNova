<template>
  <div class="navigation-controls">
    <button 
      @click="goBack" 
      class="px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-md flex items-center"
      :disabled="!canGoBack"
      :class="{'opacity-50 cursor-not-allowed': !canGoBack}"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
      </svg>
      返回
    </button>
    <button 
      @click="goForward" 
      class="px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-md flex items-center ml-2"
      :disabled="!canGoForward"
      :class="{'opacity-50 cursor-not-allowed': !canGoForward}"
    >
      <span class="mr-1">前进</span>
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { navigationService } from '../../services/navigationService';

const canGoBack = ref(false);
const canGoForward = ref(false);

// 检查导航状态
function checkNavigationState() {
  canGoBack.value = navigationService.canGoBack();
  canGoForward.value = navigationService.canGoForward();
}

// 返回上一页
function goBack() {
  if (canGoBack.value) {
    navigationService.goBack();
  }
}

// 前进到下一页
function goForward() {
  if (canGoForward.value) {
    navigationService.goForward();
  }
}

onMounted(() => {
  checkNavigationState();
  
  // 每秒检查一次导航状态
  const interval = setInterval(checkNavigationState, 1000);
  
  // 组件卸载时清除定时器
  onUnmounted(() => {
    clearInterval(interval);
  });
});
</script>

<style scoped>
.navigation-controls {
  display: flex;
}
</style> 