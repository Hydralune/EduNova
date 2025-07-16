<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- 背景遮罩 -->
    <div class="absolute inset-0 bg-black bg-opacity-50" @click="cancel"></div>
    
    <!-- 对话框 -->
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md mx-4 z-10 overflow-hidden">
      <!-- 标题区域 - 根据类型使用不同颜色 -->
      <div class="px-6 py-4 border-b" :class="headerClass">
        <h3 class="text-lg font-semibold flex items-center">
          <!-- 图标 -->
          <svg v-if="type === 'success'" class="w-5 h-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          
          <svg v-else-if="type === 'error'" class="w-5 h-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
          
          <svg v-else-if="type === 'warning'" class="w-5 h-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          
          <svg v-else class="w-5 h-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
          </svg>
          
          {{ title }}
        </h3>
      </div>
      
      <!-- 内容区域 -->
      <div class="px-6 py-4">
        <p class="text-gray-700 leading-relaxed">{{ message }}</p>
      </div>
      
      <!-- 按钮区域 -->
      <div class="px-6 py-4 bg-gray-50 flex justify-end space-x-3">
        <button 
          @click="cancel" 
          class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400"
        >
          {{ cancelText }}
        </button>
        <button 
          @click="confirm" 
          :class="[
            'px-4 py-2 border rounded-md text-white focus:outline-none focus:ring-2 focus:ring-offset-2',
            buttonClass
          ]"
        >
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, computed } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '确认'
  },
  message: {
    type: String,
    default: '您确定要执行此操作吗？'
  },
  confirmText: {
    type: String,
    default: '确定'
  },
  cancelText: {
    type: String,
    default: '取消'
  },
  type: {
    type: String,
    default: 'info',
    validator: (value: string) => ['info', 'success', 'warning', 'error'].includes(value)
  }
});

const emit = defineEmits(['confirm', 'cancel', 'update:show']);

const confirm = () => {
  emit('confirm');
  emit('update:show', false);
};

const cancel = () => {
  emit('cancel');
  emit('update:show', false);
};

// 根据类型计算样式
const headerClass = computed(() => {
  switch (props.type) {
    case 'success':
      return 'bg-green-50 text-gray-800 border-green-100';
    case 'error':
      return 'bg-red-50 text-gray-800 border-red-100';
    case 'warning':
      return 'bg-blue-50 text-gray-800 border-blue-100';
    default:
      return 'bg-blue-50 text-gray-800 border-blue-100';
  }
});

const buttonClass = computed(() => {
  switch (props.type) {
    case 'success':
      return 'bg-green-600 hover:bg-green-700 border-transparent focus:ring-green-500';
    case 'error':
      return 'bg-red-600 hover:bg-red-700 border-transparent focus:ring-red-500';
    case 'warning':
      return 'bg-blue-600 hover:bg-blue-700 border-transparent focus:ring-blue-500';
    default:
      return 'bg-blue-600 hover:bg-blue-700 border-transparent focus:ring-blue-500';
  }
});
</script>

<style scoped>
/* 没有动画，保持简洁 */
</style> 