<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-6">通知系统测试页面</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- 简单页面内通知 -->
      <div class="p-6 bg-white rounded-lg shadow-md">
        <h2 class="text-xl font-bold mb-4">页面内通知</h2>
        
        <div class="space-y-4">
          <button @click="addPageNotification('success')" class="w-full p-3 bg-green-100 text-green-800 rounded">
            添加成功通知
          </button>
          
          <button @click="addPageNotification('error')" class="w-full p-3 bg-red-100 text-red-800 rounded">
            添加错误通知
          </button>
          
          <button @click="addPageNotification('warning')" class="w-full p-3 bg-yellow-100 text-yellow-800 rounded">
            添加警告通知
          </button>
          
          <button @click="addPageNotification('info')" class="w-full p-3 bg-blue-100 text-blue-800 rounded">
            添加信息通知
          </button>
        </div>
        
        <!-- 页面内通知列表 -->
        <div class="mt-6 space-y-3">
          <div v-if="pageNotifications.length === 0" class="text-gray-500 italic">
            暂无通知
          </div>
          
          <div v-for="notification in pageNotifications" :key="notification.id"
               :class="[
                 'p-3 rounded flex justify-between items-start',
                 {
                   'bg-green-50 text-green-800': notification.type === 'success',
                   'bg-red-50 text-red-800': notification.type === 'error',
                   'bg-yellow-50 text-yellow-800': notification.type === 'warning',
                   'bg-blue-50 text-blue-800': notification.type === 'info'
                 }
               ]">
            <div>
              <div class="font-medium">{{ getNotificationTitle(notification.type) }}</div>
              <div class="text-sm">{{ getNotificationMessage(notification.type) }}</div>
            </div>
            <button @click="removePageNotification(notification.id)" class="text-gray-500 hover:text-gray-700">
              &times;
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 全局通知容器 -->
    <div class="mt-8 p-6 bg-white rounded-lg shadow-md">
      <h2 class="text-xl font-bold mb-4">全局通知容器</h2>
      <p class="text-gray-600">这个容器用于展示全局通知系统中的通知。</p>
      
      <div class="mt-4">
        <NotificationContainer />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import NotificationContainer from '../components/NotificationContainer.vue';

// 页面内通知
const pageNotifications = ref([]);
let notificationId = 0;

function addPageNotification(type) {
  pageNotifications.value.push({
    id: notificationId++,
    type
  });
  
  // 5秒后自动移除
  setTimeout(() => {
    const index = pageNotifications.value.findIndex(n => n.id === notificationId - 1);
    if (index !== -1) {
      pageNotifications.value.splice(index, 1);
    }
  }, 5000);
}

function removePageNotification(id) {
  const index = pageNotifications.value.findIndex(n => n.id === id);
  if (index !== -1) {
    pageNotifications.value.splice(index, 1);
  }
}

function getNotificationTitle(type) {
  switch (type) {
    case 'success': return '操作成功';
    case 'error': return '操作失败';
    case 'warning': return '警告';
    case 'info': return '信息';
    default: return '通知';
  }
}

function getNotificationMessage(type) {
  switch (type) {
    case 'success': return '您的操作已成功完成';
    case 'error': return '操作失败，请重试';
    case 'warning': return '此操作可能导致数据丢失';
    case 'info': return '系统将于今晚23:00进行维护';
    default: return '';
  }
}
</script> 