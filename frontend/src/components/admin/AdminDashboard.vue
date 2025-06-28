<template>
  <div class="bg-white shadow overflow-hidden rounded-lg">
    <div class="px-4 py-5 sm:p-6">
      <!-- 用户管理 -->
      <div v-if="currentTab === 'users'" class="space-y-6">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-medium text-gray-900">用户管理</h3>
          <div class="flex space-x-2">
            <div class="relative">
              <input 
                type="text" 
                v-model="userSearchQuery" 
                placeholder="搜索用户..." 
                class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
              <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
            <button @click="showAddUserModal = true" class="btn btn-primary">
              添加用户
            </button>
          </div>
        </div>

        <!-- 用户列表 -->
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">邮箱</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">注册时间</th>
                <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-if="loading">
                <td colspan="6" class="px-6 py-4 text-center text-sm text-gray-500">加载中...</td>
              </tr>
              <tr v-else-if="!filteredUsers.length">
                <td colspan="6" class="px-6 py-4 text-center text-sm text-gray-500">没有找到用户</td>
              </tr>
              <tr v-else v-for="user in filteredUsers" :key="user.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                      <span class="text-gray-500 font-medium">{{ user.username.charAt(0).toUpperCase() }}</span>
                    </div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900">{{ user.full_name }}</div>
                      <div class="text-sm text-gray-500">@{{ user.username }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ user.email }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" 
                    :class="{
                      'bg-green-100 text-green-800': user.role === 'admin',
                      'bg-blue-100 text-blue-800': user.role === 'teacher',
                      'bg-yellow-100 text-yellow-800': user.role === 'student'
                    }">
                    {{ userRoleText(user.role) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" 
                    :class="{
                      'bg-green-100 text-green-800': user.is_active,
                      'bg-red-100 text-red-800': !user.is_active
                    }">
                    {{ user.is_active ? '已激活' : '未激活' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(user.created_at) }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button @click="editUser(user)" class="text-blue-600 hover:text-blue-900 mr-3">编辑</button>
                  <button @click="deleteUser(user)" class="text-red-600 hover:text-red-900">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分页 -->
        <div class="flex justify-between items-center">
          <div class="text-sm text-gray-700">
            显示 <span class="font-medium">{{ (currentPage - 1) * pageSize + 1 }}</span> 到 
            <span class="font-medium">{{ Math.min(currentPage * pageSize, totalUsers) }}</span> 条，
            共 <span class="font-medium">{{ totalUsers }}</span> 条
          </div>
          <div class="flex space-x-2">
            <button 
              @click="currentPage--" 
              :disabled="currentPage === 1"
              class="btn btn-outline"
              :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
            >
              上一页
            </button>
            <button 
              @click="currentPage++" 
              :disabled="currentPage * pageSize >= totalUsers"
              class="btn btn-outline"
              :class="{ 'opacity-50 cursor-not-allowed': currentPage * pageSize >= totalUsers }"
            >
              下一页
            </button>
          </div>
        </div>
      </div>

      <!-- 课程管理 -->
      <div v-if="currentTab === 'courses'" class="space-y-6">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-medium text-gray-900">课程管理</h3>
          <div class="flex space-x-2">
            <div class="relative">
              <input 
                type="text" 
                v-model="courseSearchQuery" 
                placeholder="搜索课程..." 
                class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
              <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
            <button class="btn btn-primary">
              添加课程
            </button>
          </div>
        </div>

        <!-- 课程列表 -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="course in filteredCourses" :key="course.id" class="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
            <div class="h-40 bg-blue-100 flex items-center justify-center">
              <svg class="h-20 w-20 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <div class="px-4 py-4">
              <h3 class="text-lg font-medium text-gray-900">{{ course.name }}</h3>
              <p class="mt-1 text-sm text-gray-500">{{ course.description }}</p>
              <div class="mt-4 flex items-center justify-between">
                <div class="flex items-center">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                    {{ course.category }}
                  </span>
                  <span class="ml-2 text-sm text-gray-500">
                    {{ course.student_count || 0 }} 名学生
                  </span>
                </div>
                <div class="flex space-x-2">
                  <button class="text-blue-600 hover:text-blue-900">
                    <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                    </svg>
                  </button>
                  <button class="text-red-600 hover:text-red-900">
                    <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 系统设置 -->
      <div v-if="currentTab === 'settings'" class="space-y-6">
        <h3 class="text-lg font-medium text-gray-900">系统设置</h3>
        
        <form @submit.prevent="saveSettings" class="space-y-6">
          <!-- 基本设置 -->
          <div class="bg-white shadow overflow-hidden rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <h4 class="text-base font-medium text-gray-900 mb-4">基本设置</h4>
              <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
                <div>
                  <label for="site-name" class="block text-sm font-medium text-gray-700">网站名称</label>
                  <input 
                    type="text" 
                    id="site-name" 
                    v-model="settings.siteName" 
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label for="site-description" class="block text-sm font-medium text-gray-700">网站描述</label>
                  <input 
                    type="text" 
                    id="site-description" 
                    v-model="settings.siteDescription" 
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label for="admin-email" class="block text-sm font-medium text-gray-700">管理员邮箱</label>
                  <input 
                    type="email" 
                    id="admin-email" 
                    v-model="settings.adminEmail" 
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label for="user-registration" class="block text-sm font-medium text-gray-700">用户注册</label>
                  <select 
                    id="user-registration" 
                    v-model="settings.allowRegistration" 
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  >
                    <option :value="true">允许</option>
                    <option :value="false">禁止</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- 文件上传设置 -->
          <div class="bg-white shadow overflow-hidden rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <h4 class="text-base font-medium text-gray-900 mb-4">文件上传设置</h4>
              <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
                <div>
                  <label for="max-file-size" class="block text-sm font-medium text-gray-700">最大文件大小 (MB)</label>
                  <input 
                    type="number" 
                    id="max-file-size" 
                    v-model="settings.maxFileSize" 
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label for="allowed-file-types" class="block text-sm font-medium text-gray-700">允许的文件类型</label>
                  <input 
                    type="text" 
                    id="allowed-file-types" 
                    v-model="settings.allowedFileTypes" 
                    placeholder="pdf,doc,docx,ppt,pptx,jpg,png"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- AI设置 -->
          <div class="bg-white shadow overflow-hidden rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <h4 class="text-base font-medium text-gray-900 mb-4">AI功能设置</h4>
              <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
                <div>
                  <label for="enable-ai" class="block text-sm font-medium text-gray-700">启用AI功能</label>
                  <select 
                    id="enable-ai" 
                    v-model="settings.enableAI" 
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  >
                    <option :value="true">启用</option>
                    <option :value="false">禁用</option>
                  </select>
                </div>
                <div>
                  <label for="ai-model" class="block text-sm font-medium text-gray-700">AI模型</label>
                  <select 
                    id="ai-model" 
                    v-model="settings.aiModel" 
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  >
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                    <option value="gpt-4">GPT-4</option>
                    <option value="claude-3-opus">Claude 3 Opus</option>
                  </select>
                </div>
                <div>
                  <label for="api-key" class="block text-sm font-medium text-gray-700">API密钥</label>
                  <input 
                    type="password" 
                    id="api-key" 
                    v-model="settings.apiKey" 
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>
              </div>
            </div>
          </div>

          <div class="flex justify-end">
            <button type="button" class="btn btn-outline mr-3">重置</button>
            <button type="submit" class="btn btn-primary">保存设置</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { adminAPI, userAPI, courseAPI } from '../../api';

// 定义类型接口
interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  is_active: boolean;
  created_at?: string;
  last_login?: string;
}

interface Course {
  id: number;
  name: string;
  description: string;
  category?: string;
  difficulty?: string;
  duration?: number;
  is_public?: boolean;
  cover_image?: string;
  teacher_id?: number;
  teacher?: string;
  student_count?: number;
}

interface ApiResponse<T> {
  [key: string]: any;
  total?: number;
}

// 接收从父组件传递的activeTab属性
const props = defineProps({
  activeTab: {
    type: String,
    default: 'users'
  }
});

// 当前显示的标签页
const currentTab = computed(() => props.activeTab);

// 用户管理
const users = ref<User[]>([]);
const userSearchQuery = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const totalUsers = ref(0);
const loading = ref(false);
const showAddUserModal = ref(false);

// 课程管理
const courses = ref<Course[]>([]);
const courseSearchQuery = ref('');
const courseLoading = ref(false);

// 系统设置
const settings = ref({
  siteName: '智能教学系统',
  siteDescription: '基于AI的智能教学平台',
  adminEmail: 'admin@example.com',
  allowRegistration: true,
  maxFileSize: 10,
  allowedFileTypes: 'pdf,doc,docx,ppt,pptx,jpg,png',
  enableAI: true,
  aiModel: 'gpt-3.5-turbo',
  apiKey: '********'
});

// 计算属性
const filteredUsers = computed(() => {
  if (!userSearchQuery.value) return users.value;
  const query = userSearchQuery.value.toLowerCase();
  return users.value.filter(user => 
    user.username.toLowerCase().includes(query) || 
    (user.full_name && user.full_name.toLowerCase().includes(query)) || 
    user.email.toLowerCase().includes(query)
  );
});

const filteredCourses = computed(() => {
  if (!courseSearchQuery.value) return courses.value;
  const query = courseSearchQuery.value.toLowerCase();
  return courses.value.filter(course => 
    course.name.toLowerCase().includes(query) || 
    course.description.toLowerCase().includes(query) || 
    (course.category && course.category.toLowerCase().includes(query))
  );
});

// 方法
const userRoleText = (role: string) => {
  switch (role) {
    case 'admin': return '管理员';
    case 'teacher': return '教师';
    case 'student': return '学生';
    default: return '未知';
  }
};

const formatDate = (dateString: string | undefined) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN');
};

// 加载用户数据
const loadUsers = async () => {
  loading.value = true;
  try {
    console.log('Fetching users from API...');
    const response = await userAPI.getUsers({
      page: currentPage.value,
      per_page: pageSize.value
    }) as ApiResponse<User[]>;
    
    console.log('API response:', response);
    users.value = response.users || [];
    totalUsers.value = response.total || 0;
  } catch (error) {
    console.error('获取用户列表失败:', error);
    // 使用模拟数据作为备用
    console.log('使用模拟数据作为备用');
    users.value = [
      {
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        full_name: '系统管理员',
        role: 'admin',
        is_active: true,
        created_at: '2025-06-24T10:00:00.000000'
      },
      {
        id: 2,
        username: 'teacher',
        email: 'teacher@example.com',
        full_name: '示例教师',
        role: 'teacher',
        is_active: true,
        created_at: '2025-06-24T10:00:00.000000'
      },
      {
        id: 3,
        username: 'student',
        email: 'student@example.com',
        full_name: '示例学生',
        role: 'student',
        is_active: true,
        created_at: '2025-06-24T10:00:00.000000'
      }
    ];
    totalUsers.value = users.value.length;
  } finally {
    loading.value = false;
  }
};

// 加载课程数据
const loadCourses = async () => {
  courseLoading.value = true;
  try {
    console.log('Fetching courses from API...');
    const response = await courseAPI.getCourses() as ApiResponse<Course[]>;
    console.log('API response:', response);
    courses.value = response.courses || [];
  } catch (error) {
    console.error('获取课程列表失败:', error);
    // 使用模拟数据作为备用
    console.log('使用模拟数据作为备用');
    courses.value = [
      {
        id: 1,
        name: 'Python编程基础',
        description: '学习Python编程的基本概念和语法',
        category: '计算机科学',
        difficulty: 'beginner',
        teacher_id: 2,
        student_count: 15
      },
      {
        id: 2,
        name: '数据结构与算法',
        description: '掌握常见数据结构和算法',
        category: '计算机科学',
        difficulty: 'intermediate',
        teacher_id: 2,
        student_count: 8
      },
      {
        id: 3,
        name: '机器学习入门',
        description: '了解机器学习的基本原理和应用',
        category: '人工智能',
        difficulty: 'advanced',
        teacher_id: 2,
        student_count: 12
      }
    ];
  } finally {
    courseLoading.value = false;
  }
};

// 加载系统设置
const loadSettings = async () => {
  try {
    console.log('Fetching system settings from API...');
    const response = await adminAPI.getSystemStats() as ApiResponse<any>;
    console.log('API response:', response);
    // 如果后端返回了系统设置，则更新本地设置
    if (response && response.config) {
      settings.value = {
        ...settings.value,
        ...response.config
      };
    }
  } catch (error) {
    console.error('获取系统设置失败:', error);
    // 使用默认设置
    console.log('使用默认系统设置');
  }
};

const editUser = async (user: User) => {
  // 实现编辑用户的逻辑
  console.log('编辑用户', user);
  // 这里可以打开一个编辑用户的模态框
};

const deleteUser = async (user: User) => {
  if (confirm(`确定要删除用户 ${user.full_name || user.username} 吗？`)) {
    try {
      await userAPI.deleteUser(user.id);
      alert('用户删除成功');
      // 重新加载用户列表
      loadUsers();
    } catch (error) {
      console.error('删除用户失败:', error);
      alert('删除用户失败，请重试');
    }
  }
};

const saveSettings = async () => {
  try {
    // 使用adminAPI.updateConfig方法保存设置
    await adminAPI.updateConfig(settings.value);
    alert('设置已保存');
  } catch (error) {
    console.error('保存设置失败:', error);
    alert('保存设置失败，请重试');
  }
};

// 监听页码变化，重新加载用户数据
watch(currentPage, () => {
  loadUsers();
});

// 监听标签页变化，加载相应数据
watch(() => props.activeTab, (newTab) => {
  if (newTab === 'users') {
    loadUsers();
  } else if (newTab === 'courses') {
    loadCourses();
  } else if (newTab === 'settings') {
    loadSettings();
  }
});

// 生命周期钩子
onMounted(() => {
  // 根据当前活动的标签页加载数据
  if (currentTab.value === 'users') {
    loadUsers();
  } else if (currentTab.value === 'courses') {
    loadCourses();
  } else if (currentTab.value === 'settings') {
    loadSettings();
  }
});
</script>

<style scoped>
.btn {
  @apply px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2;
}

.btn-primary {
  @apply text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500;
}

.btn-outline {
  @apply text-gray-700 bg-white border-gray-300 hover:bg-gray-50 focus:ring-blue-500;
}
</style> 