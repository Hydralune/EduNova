import { ref } from 'vue';

// Notification type definition
export interface Notification {
  id: number;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration: number;
  timestamp: number;
  timeoutId?: number;
}

// Store for notifications
const notifications = ref<Notification[]>([]);
let notificationId = 0;

/**
 * Notification service to manage notifications across the application
 */
const notificationService = {
  /**
   * Show a notification
   * @param type - Type of notification: 'success', 'error', 'warning', 'info'
   * @param title - Title of the notification
   * @param message - Optional message for the notification
   * @param duration - Duration in milliseconds, default is 5000ms
   * @returns - ID of the notification for later reference
   */
  show(type: 'success' | 'error' | 'warning' | 'info', title: string, message = '', duration = 5000): number {
    const id = notificationId++;
    
    // Create notification object
    const notification: Notification = {
      id,
      type,
      title,
      message,
      duration,
      timestamp: Date.now()
    };
    
    // Auto-remove after duration
    if (duration > 0) {
      notification.timeoutId = window.setTimeout(() => {
        this.remove(id);
      }, duration);
    }
    
    notifications.value.push(notification);
    return id;
  },
  
  /**
   * Show a success notification
   */
  success(title: string, message = '', duration = 5000): number {
    return this.show('success', title, message, duration);
  },
  
  /**
   * Show an error notification
   */
  error(title: string, message = '', duration = 8000): number {
    return this.show('error', title, message, duration);
  },
  
  /**
   * Show a warning notification
   */
  warning(title: string, message = '', duration = 7000): number {
    return this.show('warning', title, message, duration);
  },
  
  /**
   * Show an info notification
   */
  info(title: string, message = '', duration = 5000): number {
    return this.show('info', title, message, duration);
  },
  
  /**
   * Remove a notification by ID
   */
  remove(id: number): void {
    const index = notifications.value.findIndex(n => n.id === id);
    if (index !== -1) {
      const notification = notifications.value[index];
      // Clear timeout if exists
      if (notification.timeoutId) {
        clearTimeout(notification.timeoutId);
      }
      notifications.value.splice(index, 1);
    }
  },
  
  /**
   * Clear all notifications
   */
  clear(): void {
    // Clear all timeouts
    notifications.value.forEach(notification => {
      if (notification.timeoutId) {
        clearTimeout(notification.timeoutId);
      }
    });
    notifications.value = [];
  },
  
  /**
   * Get all active notifications
   */
  getNotifications() {
    return notifications;
  }
};

export default notificationService; 