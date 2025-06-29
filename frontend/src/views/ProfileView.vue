<template>
  <div class="profile-container">
    <h1 class="text-2xl font-bold mb-6">个人资料</h1>
    <div v-if="loading" class="loading">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
      <p class="mt-4 text-gray-600 text-center">加载中...</p>
    </div>
    <div v-else-if="error" class="error bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
      {{ error }}
    </div>
    <div v-else-if="user" class="profile-card">
      <div class="profile-header">
        <div class="avatar-container" @click="isEditing && openAvatarUpload()">
          <img v-if="previewAvatar || user.avatar_url" :src="previewAvatar || (user.avatar_url ? `http://localhost:5001${user.avatar_url}` : '')" alt="头像" class="avatar" />
          <div v-else class="avatar-placeholder">{{ user.username?.charAt(0).toUpperCase() }}</div>
          <div v-if="isEditing" class="avatar-edit-overlay">
            <span>点击更换头像</span>
          </div>
        </div>
        <h2>{{ user.full_name || user.username }}</h2>
        <p class="role-badge">{{ translateRole(user.role) }}</p>
      </div>
      
      <!-- 查看模式 -->
      <div v-if="!isEditing" class="profile-details">
        <div class="detail-item">
          <span class="label">用户名:</span>
          <span class="value">{{ user.username }}</span>
        </div>
        <div class="detail-item">
          <span class="label">邮箱:</span>
          <span class="value">{{ user.email }}</span>
        </div>
        <div class="detail-item">
          <span class="label">姓名:</span>
          <span class="value">{{ user.full_name || '未提供' }}</span>
        </div>
        <div class="detail-item">
          <span class="label">角色:</span>
          <span class="value">{{ translateRole(user.role) }}</span>
        </div>
        <div v-if="user.created_at" class="detail-item">
          <span class="label">注册时间:</span>
          <span class="value">{{ formatDate(user.created_at) }}</span>
        </div>
      </div>
      
      <!-- 编辑模式 -->
      <div v-else class="profile-details">
        <form @submit.prevent="saveProfile">
          <div class="detail-item">
            <span class="label">用户名:</span>
            <span class="value">{{ user.username }}</span>
            <span class="text-gray-500 text-sm">(用户名不可更改)</span>
          </div>
          <div class="detail-item">
            <span class="label">邮箱:</span>
            <input v-model="editForm.email" type="email" required class="form-input" />
          </div>
          <div class="detail-item">
            <span class="label">姓名:</span>
            <input v-model="editForm.full_name" type="text" class="form-input" />
          </div>
          <div class="detail-item">
            <span class="label">角色:</span>
            <span class="value">{{ translateRole(user.role) }}</span>
            <span class="text-gray-500 text-sm">(角色不可更改)</span>
          </div>
          <div class="detail-item">
            <span class="label">头像:</span>
            <button type="button" @click="openAvatarUpload" class="btn btn-outline btn-sm">
              {{ previewAvatar ? '更换头像' : '上传头像' }}
            </button>
            <span v-if="previewAvatar" class="text-green-500 ml-2">
              (已选择新头像，保存后生效)
            </span>
          </div>
        </form>
      </div>
      
      <div class="profile-actions">
        <template v-if="!isEditing">
          <button @click="startEditing" class="btn btn-primary">修改资料</button>
          <button @click="showPasswordModal = true" class="btn btn-outline">修改密码</button>
        </template>
        <template v-else>
          <button @click="saveProfile" class="btn btn-primary">保存</button>
          <button @click="cancelEditing" class="btn btn-outline">取消</button>
        </template>
      </div>
    </div>
    
    <!-- 头像上传模态框 -->
    <div v-if="showAvatarModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-lg">
        <h3 class="text-xl font-bold mb-4">上传头像</h3>
        
        <div 
          class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:bg-gray-50"
          @click="triggerFileInput"
        >
          <div v-if="previewAvatar" class="mb-4">
            <img :src="previewAvatar" alt="预览" class="max-h-64 mx-auto rounded" />
          </div>
          <div v-else>
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            <p class="mt-2">点击选择图片</p>
            <p class="text-sm text-gray-500">支持 JPG, PNG 格式</p>
          </div>
        </div>
        <input 
          type="file" 
          ref="fileInput" 
          accept="image/*" 
          class="hidden" 
          @change="onFileChange" 
        />
        
        <div class="flex justify-end gap-2 mt-6">
          <button @click="closeAvatarModal" class="btn btn-outline">取消</button>
          <button @click="confirmAvatar" class="btn btn-primary" :disabled="!previewAvatar">确认</button>
        </div>
      </div>
    </div>
    
    <!-- 修改密码模态框 -->
    <div v-if="showPasswordModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-lg">
        <h3 class="text-xl font-bold mb-4">修改密码</h3>
        <form @submit.prevent="changePassword">
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">当前密码</label>
            <input 
              v-model="passwordForm.old_password" 
              type="password" 
              required 
              class="w-full px-3 py-2 border rounded-md" 
            />
          </div>
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">新密码</label>
            <input 
              v-model="passwordForm.new_password" 
              type="password" 
              required 
              class="w-full px-3 py-2 border rounded-md" 
            />
          </div>
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">确认新密码</label>
            <input 
              v-model="passwordForm.confirm_password" 
              type="password" 
              required 
              class="w-full px-3 py-2 border rounded-md" 
            />
            <p v-if="passwordError" class="text-red-500 text-sm mt-1">{{ passwordError }}</p>
          </div>
          
          <div class="flex justify-end gap-2 mt-6">
            <button type="button" @click="showPasswordModal = false" class="btn btn-outline">取消</button>
            <button type="submit" class="btn btn-primary">确认修改</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, inject } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import * as authAPI from '@/api/auth';

// 注入通知服务
const showNotification = inject('showNotification') as (type: 'success' | 'error' | 'warning' | 'info', title: string, message?: string) => void;

const router = useRouter();
const authStore = useAuthStore();
const fileInput = ref<HTMLInputElement | null>(null);

// 状态变量
const loading = ref(false);
const error = ref('');
const isEditing = ref(false);
const showAvatarModal = ref(false);
const showPasswordModal = ref(false);
const previewAvatar = ref('');
const passwordError = ref('');
const selectedFile = ref<File | null>(null);

// 用户数据
const user = computed(() => authStore.user);

// 编辑表单
const editForm = reactive({
  email: '',
  full_name: ''
});

// 密码表单
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
});

// 角色翻译函数
const translateRole = (role: string) => {
  switch (role) {
    case 'admin': return '管理员';
    case 'teacher': return '教师';
    case 'student': return '学生';
    default: return role;
  }
};

// 格式化日期函数
const formatDate = (dateString: string | null) => {
  if (!dateString) return '未知';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

// 开始编辑
const startEditing = () => {
  if (user.value) {
    console.log('开始编辑，当前用户:', user.value);
    // 确保表单数据被正确初始化
    editForm.email = user.value.email || '';
    editForm.full_name = user.value.full_name || '';
    console.log('编辑表单初始化为:', editForm);
    isEditing.value = true;
  }
};

// 取消编辑
const cancelEditing = () => {
  isEditing.value = false;
  previewAvatar.value = '';
};

// 保存个人资料
const saveProfile = async () => {
  error.value = '';
  loading.value = true;
  
  try {
    // 更新用户资料
    await authStore.updateProfile({
      email: editForm.email,
      full_name: editForm.full_name
    });
    
    // 如果有选择头像，上传头像
    if (selectedFile.value) {
      try {
        const avatarResponse = await authStore.simpleUploadUserAvatar(selectedFile.value);
        console.log('头像上传成功:', avatarResponse);
      } catch (avatarErr: any) {
        console.error('头像上传失败:', avatarErr);
        showNotification('error', '头像上传失败', (avatarErr.error || avatarErr.message || '未知错误'));
        // 继续执行，不要因为头像上传失败而中断整个流程
      }
    }
    
    // 更新成功
    isEditing.value = false;
    previewAvatar.value = ''; // 清除预览头像
    selectedFile.value = null; // 清除选择的文件
    showNotification('success', '个人资料更新成功');
    
    // 刷新页面显示
    if (authStore.user) {
      editForm.email = authStore.user.email || '';
      editForm.full_name = authStore.user.full_name || '';
    }
  } catch (err: any) {
    console.error('更新个人资料失败:', err);
    error.value = typeof err === 'string' ? err : (err.error || '更新个人资料失败，请重试');
  } finally {
    loading.value = false;
  }
};

// 修改密码
const changePassword = async () => {
  passwordError.value = '';
  
  // 验证两次输入的密码是否一致
  if (passwordForm.old_password !== passwordForm.new_password) {
    passwordError.value = '两次输入的新密码不一致';
    return;
  }
  
  loading.value = true;
  
  try {
    await authAPI.changeUserPassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    });
    
    // 重置表单
    passwordForm.old_password = '';
    passwordForm.new_password = '';
    passwordForm.confirm_password = '';
    
    // 关闭模态框
    showPasswordModal.value = false;
    
    showNotification('success', '密码修改成功');
  } catch (err: any) {
    console.error('修改密码失败:', err);
    passwordError.value = typeof err === 'string' ? err : (err.error || '修改密码失败，请检查当前密码是否正确');
  } finally {
    loading.value = false;
  }
};

// 打开头像上传模态框
const openAvatarUpload = () => {
  console.log('打开头像上传模态框');
  showAvatarModal.value = true;
};

// 关闭头像上传模态框
const closeAvatarModal = () => {
  console.log('关闭头像上传模态框');
  showAvatarModal.value = false;
};

// 触发文件选择
const triggerFileInput = () => {
  console.log('触发文件选择');
  if (fileInput.value) {
    fileInput.value.click();
  }
};

// 处理文件选择
const onFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    const file = target.files[0];
    
    // 检查文件类型和大小
    if (!file.type.match('image.*')) {
      showNotification('error', '文件类型错误', '请选择图片文件');
      return;
    }
    
    if (file.size > 5 * 1024 * 1024) { // 5MB限制
      showNotification('error', '文件过大', '图片大小不能超过5MB');
      return;
    }
    
    console.log('选择了文件:', file.name, file.type, file.size);
    
    // 保存文件对象以便后续上传
    selectedFile.value = file;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      console.log('文件读取完成');
      previewAvatar.value = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
};

// 确认头像
const confirmAvatar = () => {
  console.log('确认头像');
  showAvatarModal.value = false;
};

onMounted(async () => {
  // 检查用户是否已登录
  if (!authStore.isAuthenticated) {
    router.push('/login');
    return;
  }

  loading.value = true;
  try {
    // 如果用户数据未加载，则获取用户资料
    if (!authStore.user) {
      await authStore.fetchProfile();
    }
    
    // 初始化编辑表单
    if (authStore.user) {
      editForm.email = authStore.user.email || '';
      editForm.full_name = authStore.user.full_name || '';
    }
  } catch (err: any) {
    console.error('加载个人资料失败:', err);
    error.value = typeof err === 'string' ? err : (err.error || '加载个人资料失败');
    // 如果未授权，重定向到登录页面
    if (err.status === 401) {
      authStore.logout();
      router.push('/login');
    }
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 1rem;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
}

.error {
  color: #e53e3e;
}

.profile-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.profile-header {
  background-color: #4299e1;
  color: white;
  padding: 2rem;
  text-align: center;
}

.avatar-container {
  margin: 0 auto 1rem;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  background-color: #2b6cb0;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  cursor: pointer;
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 3rem;
  font-weight: bold;
}

.avatar-edit-overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.avatar-container:hover .avatar-edit-overlay {
  opacity: 1;
}

.role-badge {
  display: inline-block;
  background-color: #2b6cb0;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.profile-details {
  padding: 2rem;
}

.detail-item {
  margin-bottom: 1rem;
  display: flex;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.5rem;
  align-items: center;
}

.label {
  font-weight: bold;
  min-width: 120px;
  color: #4a5568;
}

.value {
  flex: 1;
}

.profile-actions {
  padding: 0 2rem 2rem;
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #4299e1;
  color: white;
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background-color: #3182ce;
}

.btn-outline {
  background-color: transparent;
  color: #4299e1;
  border: 1px solid #4299e1;
}

.btn-outline:hover:not(:disabled) {
  background-color: #ebf8ff;
}

.form-input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.25rem;
  outline: none;
}

.form-input:focus {
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
}
</style> 