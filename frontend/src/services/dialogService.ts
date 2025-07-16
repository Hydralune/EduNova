import { ref } from 'vue';

// 对话框状态
export interface DialogOptions {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'info' | 'success' | 'warning' | 'error';
  onConfirm?: () => void;
  onCancel?: () => void;
}

// 默认对话框状态
const defaultDialogOptions: DialogOptions = {
  title: '确认',
  message: '您确定要执行此操作吗？',
  confirmText: '确定',
  cancelText: '取消',
  type: 'info'
};

// 对话框状态
const dialogVisible = ref(false);
const dialogOptions = ref<DialogOptions>({ ...defaultDialogOptions });

/**
 * 对话框服务
 */
const dialogService = {
  /**
   * 显示确认对话框
   * @param options 对话框选项
   */
  confirm(options: DialogOptions | string): Promise<boolean> {
    return new Promise((resolve) => {
      // 如果传入的是字符串，则将其作为消息内容
      if (typeof options === 'string') {
        dialogOptions.value = {
          ...defaultDialogOptions,
          message: options
        };
      } else {
        dialogOptions.value = {
          ...defaultDialogOptions,
          ...options
        };
      }

      // 设置确认和取消回调
      const originalConfirm = dialogOptions.value.onConfirm;
      const originalCancel = dialogOptions.value.onCancel;

      dialogOptions.value.onConfirm = () => {
        if (originalConfirm) originalConfirm();
        resolve(true);
      };

      dialogOptions.value.onCancel = () => {
        if (originalCancel) originalCancel();
        resolve(false);
      };

      // 显示对话框
      dialogVisible.value = true;
    });
  },

  /**
   * 显示成功确认对话框
   */
  success(options: DialogOptions | string): Promise<boolean> {
    if (typeof options === 'string') {
      return this.confirm({
        title: '成功',
        message: options,
        type: 'success'
      });
    }
    return this.confirm({
      ...options,
      type: 'success'
    });
  },

  /**
   * 显示错误确认对话框
   */
  error(options: DialogOptions | string): Promise<boolean> {
    if (typeof options === 'string') {
      return this.confirm({
        title: '错误',
        message: options,
        type: 'error'
      });
    }
    return this.confirm({
      ...options,
      type: 'error'
    });
  },

  /**
   * 显示警告确认对话框
   */
  warning(options: DialogOptions | string): Promise<boolean> {
    if (typeof options === 'string') {
      return this.confirm({
        title: '警告',
        message: options,
        type: 'warning'
      });
    }
    return this.confirm({
      ...options,
      type: 'warning'
    });
  },

  /**
   * 关闭对话框
   */
  close() {
    dialogVisible.value = false;
  },

  /**
   * 获取对话框状态
   */
  getDialogState() {
    return {
      visible: dialogVisible,
      options: dialogOptions
    };
  }
};

export default dialogService; 