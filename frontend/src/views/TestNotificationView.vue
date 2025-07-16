<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-6">通知系统测试</h1>
    
    <div class="flex space-x-4 mb-8">
      <button @click="showSuccess" class="px-4 py-2 bg-green-500 text-white rounded">
        显示成功通知
      </button>
      <button @click="showError" class="px-4 py-2 bg-red-500 text-white rounded">
        显示错误通知
      </button>
      <button @click="showWarning" class="px-4 py-2 bg-yellow-500 text-white rounded">
        显示警告通知
      </button>
      <button @click="showInfo" class="px-4 py-2 bg-blue-500 text-white rounded">
        显示信息通知
      </button>
    </div>
    
    <div class="mb-4">
      <p>当前通知数量: {{ notificationCount }}</p>
    </div>
    
    <div>
      <button @click="clearAll" class="px-4 py-2 bg-gray-500 text-white rounded">
        清除所有通知
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import notificationService from '@/services/notificationService';

const notificationCount = computed(() => {
  return notificationService.getNotifications().value.length;
});

function showSuccess() {
  notificationService.success('成功', '操作已成功完成');
  console.log('显示成功通知，当前通知数量:', notificationCount.value);
}

function showError() {
  notificationService.error('错误', '操作失败，请重试');
  console.log('显示错误通知，当前通知数量:', notificationCount.value);
}

function showWarning() {
  notificationService.warning('警告', '此操作可能导致数据丢失');
  console.log('显示警告通知，当前通知数量:', notificationCount.value);
}

function showInfo() {
  notificationService.info('信息', '系统将于今晚23:00进行维护');
  console.log('显示信息通知，当前通知数量:', notificationCount.value);
}

function clearAll() {
  notificationService.clear();
  console.log('清除所有通知');
}
</script> 