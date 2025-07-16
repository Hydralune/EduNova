<template>
  <transition-group name="notification" tag="div" class="notification-container">
    <div
      v-for="notification in notifications"
      :key="notification.id"
      class="notification"
      :class="[`notification-${notification.type}`]"
    >
      <!-- 图标 -->
      <svg v-if="notification.type === 'success'" class="notification-icon success-icon" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
      </svg>
      
      <svg v-else-if="notification.type === 'error'" class="notification-icon error-icon" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
      </svg>
      
      <svg v-else-if="notification.type === 'warning'" class="notification-icon warning-icon" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      
      <svg v-else class="notification-icon info-icon" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
      </svg>
      
      <!-- 内容 -->
      <div class="notification-text">
        <div class="notification-title">{{ notification.title }}</div>
        <div v-if="notification.message" class="notification-message">{{ notification.message }}</div>
      </div>
      
      <!-- 关闭按钮 -->
      <button 
        @click="removeNotification(notification.id)" 
        class="notification-close"
      >
        <svg class="close-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
  </transition-group>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import notificationService from '../services/notificationService';

// Get notifications from the service
const notifications = computed(() => {
  return notificationService.getNotifications().value;
});

// Remove notification
const removeNotification = (id: number): void => {
  notificationService.remove(id);
};
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 1.5rem;
  right: 1.5rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  width: 400px;
  max-width: calc(100vw - 3rem);
  pointer-events: none;
}

.notification {
  display: flex;
  align-items: flex-start;
  padding: 1.25rem 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
  border-left-width: 5px;
  border-left-style: solid;
  background-color: white;
  position: relative;
  margin-bottom: 0.75rem;
  min-height: 4.5rem;
  width: 100%;
  pointer-events: auto;
  transform-origin: center right;
}

.notification-icon {
  flex-shrink: 0;
  margin-right: 0.875rem;
  height: 1.25rem;
  width: 1.25rem;
}

.notification-text {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 600;
  font-size: 0.9375rem;
  line-height: 1.25rem;
}

.notification-message {
  font-size: 0.8125rem;
  line-height: 1.25rem;
  margin-top: 0.25rem;
  opacity: 0.9;
}

.notification-close {
  flex-shrink: 0;
  margin-left: 0.75rem;
  color: #9ca3af;
  transition: color 0.15s;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
}

.close-icon {
  height: 1rem;
  width: 1rem;
}

.notification-close:hover {
  color: #6b7280;
}

/* Success notification */
.notification-success {
  border-left-color: #10b981;
  background-color: #f0fdf4;
}

.success-icon {
  color: #10b981;
}

.notification-success .notification-title {
  color: #065f46;
}

.notification-success .notification-message {
  color: #065f46;
}

/* Error notification */
.notification-error {
  border-left-color: #ef4444;
  background-color: #fef2f2;
}

.error-icon {
  color: #ef4444;
}

.notification-error .notification-title {
  color: #991b1b;
}

.notification-error .notification-message {
  color: #991b1b;
}

/* Warning notification */
.notification-warning {
  border-left-color: #f59e0b;
  background-color: #fffbeb;
}

.warning-icon {
  color: #f59e0b;
}

.notification-warning .notification-title {
  color: #92400e;
}

.notification-warning .notification-message {
  color: #92400e;
}

/* Info notification */
.notification-info {
  border-left-color: #3b82f6;
  background-color: #eff6ff;
}

.info-icon {
  color: #3b82f6;
}

.notification-info .notification-title {
  color: #1e40af;
}

.notification-info .notification-message {
  color: #1e40af;
}

/* Animations */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
  will-change: transform, opacity;
}

.notification-leave-active {
  position: absolute;
  width: 100%;
}

.notification-enter-from,
.notification-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.notification-move {
  transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
</style> 