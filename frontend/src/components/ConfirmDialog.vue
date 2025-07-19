<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- 背景遮罩 -->
    <div class="absolute inset-0 bg-black bg-opacity-30" @click="cancel"></div>
    
    <!-- 对话框 -->
    <div class="bg-white rounded-md shadow-lg w-full max-w-sm mx-4 z-10 overflow-hidden">
      <!-- 标题区域 - 简洁的白色背景 -->
      <div class="px-5 py-3 border-b border-gray-100">
        <h3 class="text-base font-medium text-gray-800">
          {{ title }}
        </h3>
      </div>
      
      <!-- 内容区域 -->
      <div class="px-5 py-3">
        <p class="text-sm text-gray-600 leading-relaxed">{{ message }}</p>
      </div>
      
      <!-- 按钮区域 -->
      <div class="px-5 py-3 flex justify-end space-x-2">
        <button 
          @click="cancel" 
          class="px-3 py-1.5 text-xs border border-gray-200 rounded text-gray-600 bg-white hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-gray-200"
        >
          {{ cancelText }}
        </button>
        <button 
          @click="confirm" 
          class="px-3 py-1.5 text-xs rounded text-white bg-blue-500 hover:bg-blue-600 focus:outline-none focus:ring-1 focus:ring-blue-300"
        >
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';

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
</script>

<style scoped>
/* 没有动画，保持简洁 */
</style> 