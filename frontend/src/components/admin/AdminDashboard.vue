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
            <button @click="showAddCourseModal = true" class="btn btn-primary">
              添加课程
            </button>
          </div>
        </div>

        <!-- 课程列表 -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="course in filteredCourses" :key="course.id" class="bg-white overflow-hidden shadow rounded-lg border border-gray-200">
            <div class="h-40 bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center relative">
              <img v-if="course.cover_image" :src="'http://localhost:5001' + course.cover_image" alt="课程封面" class="h-full w-full object-cover" />
              <div v-else class="absolute inset-0 flex items-center justify-center bg-opacity-80 bg-gradient-to-r from-blue-500 to-indigo-600">
                <h3 class="text-xl font-bold text-white text-center px-4">{{ course.name }}</h3>
              </div>
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
                  <button @click="editCourse(course)" class="text-blue-600 hover:text-blue-900">
                    <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                    </svg>
                  </button>
                  <button @click="deleteCourse(course)" class="text-red-600 hover:text-red-900">
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

    <!-- 添加课程模态框 -->
    <div v-if="showAddCourseModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-lg">
        <h3 class="text-xl font-bold mb-4">{{ isEditingCourse ? '编辑课程' : '添加课程' }}</h3>
        <div class="max-h-[70vh] overflow-y-auto">
          <form @submit.prevent="saveCourse">
            <div class="space-y-4">
              <div>
                <label for="course-name" class="block text-sm font-medium text-gray-700">课程名称</label>
                <input 
                  type="text" 
                  id="course-name" 
                  v-model="newCourse.name" 
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  required
                />
              </div>
              <div>
                <label for="course-description" class="block text-sm font-medium text-gray-700">课程描述</label>
                <textarea 
                  id="course-description" 
                  v-model="newCourse.description" 
                  rows="3"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  required
                ></textarea>
              </div>
              <div>
                <label for="course-cover" class="block text-sm font-medium text-gray-700">课程封面图片</label>
                <div class="mt-1 flex items-center">
                  <div v-if="coverImagePreview" class="relative w-full h-32 mb-2">
                    <img :src="coverImagePreview" alt="封面预览" class="w-full h-full object-cover rounded-md" />
                    <button 
                      type="button" 
                      @click="removeCoverImage" 
                      class="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1"
                    >
                      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  <input 
                    type="file" 
                    id="course-cover" 
                    @change="handleCoverImageChange" 
                    accept="image/*"
                    class="hidden"
                    ref="coverImageInput"
                  />
                  <button 
                    type="button" 
                    @click="triggerFileInput()" 
                    class="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    {{ coverImagePreview ? '更换图片' : '上传封面图片' }}
                  </button>
                </div>
              </div>
              <div>
                <label for="course-category" class="block text-sm font-medium text-gray-700">课程类别</label>
                <select 
                  id="course-category" 
                  v-model="newCourse.category" 
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                >
                  <option value="计算机科学">计算机科学</option>
                  <option value="数学">数学</option>
                  <option value="物理">物理</option>
                  <option value="化学">化学</option>
                  <option value="生物">生物</option>
                  <option value="语言">语言</option>
                  <option value="人文">人文</option>
                  <option value="艺术">艺术</option>
                  <option value="其他">其他</option>
                </select>
              </div>
              <div>
                <label for="course-difficulty" class="block text-sm font-medium text-gray-700">难度级别</label>
                <select 
                  id="course-difficulty" 
                  v-model="newCourse.difficulty" 
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                >
                  <option value="beginner">初级</option>
                  <option value="intermediate">中级</option>
                  <option value="advanced">高级</option>
                </select>
              </div>
              <div class="flex items-center">
                <input 
                  type="checkbox" 
                  id="course-public" 
                  v-model="newCourse.is_public" 
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="course-public" class="ml-2 block text-sm text-gray-900">公开课程</label>
              </div>
            </div>
            <div class="mt-5 flex justify-end space-x-3">
              <button 
                type="button" 
                @click="closeModal" 
                class="btn btn-outline"
              >
                取消
              </button>
              <button type="submit" class="btn btn-primary">
                {{ isEditingCourse ? '保存' : '创建' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- 添加/编辑用户模态框 -->
    <div v-if="showAddUserModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-lg">
        <h3 class="text-xl font-bold mb-4">{{ isEditingUser ? '编辑用户' : '添加用户' }}</h3>
        <div class="max-h-[70vh] overflow-y-auto">
          <form @submit.prevent="isEditingUser ? updateUserData() : createUser()">
            <div class="space-y-4">
              <div>
                <label for="user-username" class="block text-sm font-medium text-gray-700">用户名</label>
                <input 
                  type="text" 
                  id="user-username" 
                  v-model="newUser.username" 
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  :disabled="isEditingUser"
                  required
                />
              </div>
              <div>
                <label for="user-email" class="block text-sm font-medium text-gray-700">邮箱</label>
                <input 
                  type="email" 
                  id="user-email" 
                  v-model="newUser.email" 
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  required
                />
              </div>
              <div>
                <label for="user-full-name" class="block text-sm font-medium text-gray-700">姓名</label>
                <input 
                  type="text" 
                  id="user-full-name" 
                  v-model="newUser.full_name" 
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                />
              </div>
              <div>
                <label for="user-password" class="block text-sm font-medium text-gray-700">
                  {{ isEditingUser ? '密码（留空表示不修改）' : '密码' }}
                </label>
                <input 
                  type="password" 
                  id="user-password" 
                  v-model="newUser.password" 
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  :required="!isEditingUser"
                />
              </div>
              <div>
                <label for="user-role" class="block text-sm font-medium text-gray-700">角色</label>
                <select 
                  id="user-role" 
                  v-model="newUser.role" 
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                >
                  <option value="admin">管理员</option>
                  <option value="teacher">教师</option>
                  <option value="student">学生</option>
                </select>
              </div>
              <div class="flex items-center">
                <input 
                  type="checkbox" 
                  id="user-active" 
                  v-model="newUser.is_active" 
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label for="user-active" class="ml-2 block text-sm text-gray-900">账户已激活</label>
              </div>
            </div>
            <div class="mt-5 flex justify-end space-x-3">
              <button 
                type="button" 
                @click="closeUserModal" 
                class="btn btn-outline"
              >
                取消
              </button>
              <button type="submit" class="btn btn-primary">
                {{ isEditingUser ? '保存' : '创建' }}
              </button>
            </div>
          </form>
        </div>
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
const newUser = ref({
  username: '',
  email: '',
  password: '',
  full_name: '',
  role: 'student',
  is_active: true
});
const isEditingUser = ref(false);
const currentEditingUserId = ref<number | null>(null);

// 课程管理
const courses = ref<Course[]>([]);
const courseSearchQuery = ref('');
const courseLoading = ref(false);
const showAddCourseModal = ref(false);
const newCourse = ref({
  name: '',
  description: '',
  category: '计算机科学',
  difficulty: 'beginner',
  is_public: true
});
const coverImageFile = ref<File | null>(null);
const coverImagePreview = ref<string | null>(null);

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

// 添加新的状态变量
const currentEditingCourseId = ref<number | null>(null);
const isEditingCourse = ref(false);

// 计算属性
const filteredUsers = computed(() => {
  if (!users.value || users.value.length === 0) {
    console.log('No users available for filtering');
    return [];
  }
  
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
  console.log('开始加载用户数据...');
  loading.value = true;
  
  try {
    console.log('尝试从API获取用户数据, 当前页面:', currentPage.value);
    const response = await userAPI.getUsers({
      page: currentPage.value,
      per_page: pageSize.value
    }) as ApiResponse<User[]>;
    
    console.log('API响应成功:', response);
    
    if (response && response.users && Array.isArray(response.users)) {
      users.value = response.users;
      totalUsers.value = response.total || users.value.length;
      console.log(`成功加载 ${users.value.length} 个用户`);
    } else {
      console.warn('API返回的用户数据格式不符合预期', response);
      // 如果API返回的数据格式不符合预期，使用模拟数据
      useMockData();
    }
  } catch (error) {
    console.error('获取用户列表失败:', error);
    // 使用模拟数据作为备用
    useMockData();
  } finally {
    loading.value = false;
    console.log('用户数据加载完成，当前用户列表长度:', users.value.length);
  }
};

// 使用模拟数据的辅助函数
const useMockData = () => {
  console.log('使用模拟数据');
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
};

// 加载课程数据
const loadCourses = async () => {
  courseLoading.value = true;
  try {
    console.log('Fetching courses from API...');
    
    // 只使用一种API调用方式
    const response = await courseAPI.getCourses();
    console.log('API response:', response);
    
    // 处理API响应数据
    const responseData = response as any; // 类型断言为any以避免TypeScript错误
    if (responseData && responseData.courses) {
      courses.value = responseData.courses;
      console.log('成功加载课程数据:', courses.value);
    } else {
      console.warn('API返回格式不符合预期:', response);
      courses.value = [];
    }
  } catch (error) {
    console.error('获取课程列表失败:', error);
    courses.value = [];
    alert('获取课程列表失败，请检查网络连接或联系管理员');
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
  
  // 将当前用户数据设置到表单中
  newUser.value = {
    username: user.username,
    email: user.email,
    password: '', // 密码留空，表示不修改
    full_name: user.full_name || '',
    role: user.role,
    is_active: user.is_active
  };
  
  // 存储当前编辑的用户ID
  currentEditingUserId.value = user.id;
  
  // 打开模态框，使用编辑模式
  isEditingUser.value = true;
  showAddUserModal.value = true;
};

const updateUserData = async () => {
  try {
    if (!currentEditingUserId.value) {
      alert('用户ID无效');
      return;
    }
    
    // 准备更新数据
    const updateData: any = {
      email: newUser.value.email,
      full_name: newUser.value.full_name,
      role: newUser.value.role,
      is_active: newUser.value.is_active
    };
    
    // 如果提供了密码，则更新密码
    if (newUser.value.password) {
      updateData.password = newUser.value.password;
    }
    
    // 调用API更新用户
    await userAPI.updateUser(currentEditingUserId.value, updateData);
    alert('用户更新成功');
    
    // 重置表单和状态
    resetUserForm();
    
    // 关闭模态框
    showAddUserModal.value = false;
    
    // 重新加载用户列表
    loadUsers();
  } catch (error) {
    console.error('更新用户失败:', error);
    alert('更新用户失败，请重试');
  }
};

const closeUserModal = () => {
  showAddUserModal.value = false;
  // 重置编辑状态
  resetUserForm();
};

const resetUserForm = () => {
  isEditingUser.value = false;
  currentEditingUserId.value = null;
  // 重置表单
  newUser.value = {
    username: '',
    email: '',
    password: '',
    full_name: '',
    role: 'student',
    is_active: true
  };
};

const deleteUser = async (user: User) => {
  if (confirm(`确定要删除用户 ${user.full_name || user.username} 吗？`)) {
    try {
      await userAPI.deleteUser(user.id);
      alert('用户删除成功');
      // 重新加载用户列表
      loadUsers();
    } catch (error: any) {
      console.error('删除用户失败:', error);
      
      // 检查是否是教师有关联课程的错误
      if (error.response && error.response.data && error.response.data.error) {
        if (error.response.data.error.includes('该教师仍有关联的课程')) {
          alert('删除失败: 该教师仍有关联的课程。请先将课程重新分配给其他教师或删除这些课程。');
        } else {
          alert(`删除用户失败: ${error.response.data.error}`);
        }
      } else {
        alert('删除用户失败，请重试');
      }
    }
  }
};

const createUser = async () => {
  try {
    if (!newUser.value.username || !newUser.value.email) {
      alert('用户名和邮箱为必填项');
      return;
    }
    
    await userAPI.createUser(newUser.value);
    alert('用户创建成功');
    
    // 重置表单
    newUser.value = {
      username: '',
      email: '',
      password: '',
      full_name: '',
      role: 'student',
      is_active: true
    };
    
    // 关闭模态框
    showAddUserModal.value = false;
    
    // 重新加载用户列表
    loadUsers();
  } catch (error) {
    console.error('创建用户失败:', error);
    alert('创建用户失败，请重试');
  }
};

const editCourse = async (course: Course) => {
  // 将当前课程数据设置到表单中
  newCourse.value = {
    name: course.name,
    description: course.description,
    category: course.category || '计算机科学',
    difficulty: course.difficulty || 'beginner',
    is_public: course.is_public !== false
  };
  
  // 如果有封面图片，设置预览
  if (course.cover_image) {
    coverImagePreview.value = 'http://localhost:5001' + course.cover_image;
  } else {
    coverImagePreview.value = null;
  }
  coverImageFile.value = null;
  
  // 存储当前编辑的课程ID
  currentEditingCourseId.value = course.id;
  
  // 打开模态框，但使用编辑模式
  isEditingCourse.value = true;
  showAddCourseModal.value = true;
};

const deleteCourse = async (course: Course) => {
  if (confirm(`确定要删除课程 "${course.name}" 吗？`)) {
    try {
      await courseAPI.deleteCourse(course.id);
      alert('课程删除成功');
      // 重新加载课程列表
      loadCourses();
    } catch (error) {
      console.error('删除课程失败:', error);
      alert('删除课程失败，请重试');
    }
  }
};

const handleCoverImageChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    coverImageFile.value = target.files[0];
    coverImagePreview.value = URL.createObjectURL(target.files[0]);
  }
};

const removeCoverImage = () => {
  coverImageFile.value = null;
  coverImagePreview.value = null;
  const input = document.getElementById('course-cover') as HTMLInputElement;
  if (input) {
    input.value = '';
  }
};

const triggerFileInput = () => {
  const input = document.getElementById('course-cover') as HTMLInputElement;
  if (input) {
    input.click();
  }
};

const saveCourse = async () => {
  console.log("saveCourse函数被调用");
  try {
    if (!newCourse.value.name || !newCourse.value.description) {
      alert('课程名称和描述为必填项');
      return;
    }
    
    console.log("准备发送请求，数据:", newCourse.value);
    console.log("封面图片:", coverImageFile.value);
    
    let response: any; // 使用any类型避免TypeScript错误
    if (isEditingCourse.value && currentEditingCourseId.value) {
      console.log("更新现有课程, ID:", currentEditingCourseId.value);
      // 更新现有课程
      response = await courseAPI.updateCourse(
        currentEditingCourseId.value, 
        newCourse.value, 
        coverImageFile.value || undefined
      );
      console.log("课程更新响应:", response);
      alert('课程更新成功');
    } else {
      console.log("创建新课程");
      // 创建新课程
      response = await courseAPI.createCourse(
        newCourse.value, 
        coverImageFile.value || undefined
      );
      console.log("课程创建响应:", response);
      alert('课程创建成功');
    }
    
    // 重置表单
    newCourse.value = {
      name: '',
      description: '',
      category: '计算机科学',
      difficulty: 'beginner',
      is_public: true
    };
    coverImageFile.value = null;
    coverImagePreview.value = null;
    currentEditingCourseId.value = null;
    isEditingCourse.value = false;
    
    // 关闭模态框
    showAddCourseModal.value = false;
    
    // 重新加载课程列表
    loadCourses();
  } catch (error) {
    console.error('保存课程失败:', error);
    alert('保存课程失败，请重试');
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

const closeModal = () => {
  showAddCourseModal.value = false;
  // 重置编辑状态
  isEditingCourse.value = false;
  currentEditingCourseId.value = null;
  // 重置表单
  newCourse.value = {
    name: '',
    description: '',
    category: '计算机科学',
    difficulty: 'beginner',
    is_public: true
  };
  coverImageFile.value = null;
  coverImagePreview.value = null;
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
  padding: 0.5rem 1rem;
  border: 1px solid transparent;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.375rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}
.btn:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

.btn-primary {
  color: white;
  background-color: #2563eb;
}
.btn-primary:hover {
  background-color: #1d4ed8;
}
.btn-primary:focus {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}

.btn-outline {
  color: #374151;
  background-color: white;
  border-color: #d1d5db;
}
.btn-outline:hover {
  background-color: #f9fafb;
}
.btn-outline:focus {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}
</style> 