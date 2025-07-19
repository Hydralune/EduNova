<template>
  <div class="knowledge-base">
    <div class="mb-6 flex justify-between items-center">
      <h2 class="text-2xl font-bold">知识库管理</h2>
      <div class="flex gap-2">
        <button 
          @click="showUploadModal = true"
          class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
        >
          直接上传到知识库
        </button>
        <button 
          @click="showImportModal = true"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          从课件导入
        </button>
      </div>
    </div>

    <!-- 知识库状态概览 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white p-4 rounded-lg shadow-md border">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-gray-500">总文件数</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.totalFiles }}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white p-4 rounded-lg shadow-md border">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-gray-500">已处理</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.completedFiles }}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white p-4 rounded-lg shadow-md border">
        <div class="flex items-center">
          <div class="p-2 bg-yellow-100 rounded-lg">
            <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-gray-500">处理中</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.processingFiles }}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white p-4 rounded-lg shadow-md border">
        <div class="flex items-center">
          <div class="p-2 bg-red-100 rounded-lg">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-gray-500">失败</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.failedFiles }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="bg-white p-4 rounded-lg shadow-md border mb-6">
      <div class="flex flex-wrap gap-4 items-end">
        <div class="flex-1 min-w-64">
          <label class="block text-sm font-medium text-gray-700 mb-1">搜索文件</label>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索文件名或课程名..."
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div class="min-w-48">
          <label class="block text-sm font-medium text-gray-700 mb-1">课程</label>
          <select 
            v-model="filterCourseId" 
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">所有课程</option>
            <option v-for="course in courses" :key="course.id" :value="course.id">
              {{ course.name }}
            </option>
          </select>
        </div>
        
        <div class="min-w-48">
          <label class="block text-sm font-medium text-gray-700 mb-1">状态</label>
          <select 
            v-model="filterStatus" 
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">所有状态</option>
            <option value="pending">等待处理</option>
            <option value="processing">处理中</option>
            <option value="completed">已完成</option>
            <option value="failed">处理失败</option>
          </select>
        </div>
        
        <button 
          @click="refreshKnowledgeBase"
          class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
          :disabled="refreshing"
        >
          <svg v-if="refreshing" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span v-else>刷新</span>
        </button>
      </div>
      
      <!-- 批量操作 -->
      <div class="mt-4 flex items-center gap-4">
        <div class="flex items-center gap-2">
          <input 
            type="checkbox" 
            v-model="selectAll"
            @change="toggleSelectAll"
            class="rounded border-gray-300"
          />
          <span class="text-sm text-gray-600">全选</span>
        </div>
        
        <div class="flex gap-2">
          <button 
            v-if="selectedItems.length > 0"
            @click="batchDelete"
            class="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
            :disabled="batchDeleting"
          >
            <span v-if="!batchDeleting">批量删除 ({{ selectedItems.length }})</span>
            <span v-else class="flex items-center">
              <svg class="animate-spin h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              删除中
            </span>
          </button>
          
          <button 
            v-if="hasProcessingItems"
            @click="clearQueue"
            class="px-3 py-1 bg-orange-600 text-white text-sm rounded hover:bg-orange-700"
            :disabled="clearingQueue"
          >
            <span v-if="!clearingQueue">清空队列</span>
            <span v-else class="flex items-center">
              <svg class="animate-spin h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              清空中
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- 知识库文件列表 -->
    <div class="bg-white rounded-lg shadow-md border">
      <div class="p-4 border-b">
        <h3 class="text-lg font-semibold">知识库文件</h3>
      </div>
      
      <div v-if="loading" class="flex justify-center py-10">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
      
      <div v-else-if="filteredKnowledgeItems.length === 0" class="p-10 text-center">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        <p class="mt-2 text-gray-500">暂无知识库文件</p>
        <button 
          @click="showUploadModal = true"
          class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          上传第一个文件
        </button>
      </div>
      
      <div v-else class="divide-y">
        <div 
          v-for="item in filteredKnowledgeItems" 
          :key="item.id" 
          class="p-4 hover:bg-gray-50"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center flex-1">
              <!-- 选择框 -->
              <div class="mr-3">
                <input 
                  type="checkbox" 
                  :value="item.id"
                  v-model="selectedItemIds"
                  class="rounded border-gray-300"
                />
              </div>
              
              <!-- 文件图标 -->
              <div class="mr-4">
                <span v-html="getFileIcon(item.file_path)"></span>
              </div>
              
              <!-- 文件信息 -->
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <h4 class="font-medium text-gray-900">{{ getFileName(item.file_path) }}</h4>
                  <span :class="getStatusBadgeClass(item.status)">
                    {{ getStatusText(item.status) }}
                  </span>
                </div>
                
                <div class="mt-1 flex items-center text-sm text-gray-500 gap-4">
                  <span>{{ getCourseName(item.course_id) }}</span>
                  <span>{{ getFileSize(item.file_path) }}</span>
                  <span>{{ formatDate(item.created_at) }}</span>
                </div>
                
                <!-- 处理进度 -->
                <div v-if="item.status === 'processing' && item.progress !== undefined" class="mt-2">
                  <div class="flex items-center gap-2">
                    <div class="flex-1 bg-gray-200 rounded-full h-2">
                      <div 
                        class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        :style="`width: ${item.progress}%`"
                      ></div>
                    </div>
                    <span class="text-sm text-gray-600">{{ item.progress.toFixed(1) }}%</span>
                  </div>
                </div>
                
                <!-- 错误信息 -->
                <div v-if="item.status === 'failed' && item.error_message" class="mt-2">
                  <p class="text-sm text-red-600">{{ item.error_message }}</p>
                </div>
              </div>
            </div>
            
            <!-- 操作按钮 -->
            <div class="flex items-center gap-2">
              <button 
                v-if="item.status === 'completed'"
                @click="searchInFile(item)"
                class="text-blue-600 hover:text-blue-800 text-sm"
              >
                搜索
              </button>
              
              <button 
                v-if="item.status === 'failed'"
                @click="retryProcessing(item)"
                class="text-yellow-600 hover:text-yellow-800 text-sm"
              >
                重试
              </button>
              
              <button 
                @click="removeFromKnowledgeBase(item)"
                class="text-red-600 hover:text-red-800 text-sm"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 直接上传到知识库模态框 -->
    <div v-if="showUploadModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-lg">
        <h3 class="text-xl font-bold mb-4">直接上传到知识库</h3>
        
        <form @submit.prevent="uploadToKnowledgeBase" class="space-y-4">
          <div>
            <label class="block text-gray-700 text-sm font-bold mb-2">选择课程 <span class="text-red-500">*</span></label>
            <select 
              v-model="uploadForm.courseId" 
              required
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">请选择课程</option>
              <option v-for="course in courses" :key="course.id" :value="course.id">
                {{ course.name }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="block text-gray-700 text-sm font-bold mb-2">选择文件 <span class="text-red-500">*</span></label>
            <div class="border-2 border-dashed border-gray-300 rounded-md p-6">
              <div class="text-center">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="mt-1 text-sm text-gray-600">
                  拖放文件到这里，或者
                  <label for="direct-upload" class="text-blue-600 hover:text-blue-500 cursor-pointer">浏览文件</label>
                </p>
                <p class="mt-1 text-xs text-gray-500">
                  支持 PDF, DOCX, DOC, TXT, MD 格式
                </p>
              </div>
              <input 
                id="direct-upload" 
                type="file" 
                class="hidden" 
                @change="handleDirectFileChange" 
                accept=".pdf,.docx,.doc,.txt,.md"
                required 
              />
            </div>
            <p v-if="uploadForm.file" class="mt-2 text-sm text-gray-500">
              已选择: {{ uploadForm.file.name }} ({{ (uploadForm.file.size / 1024).toFixed(1) }}KB)
            </p>
          </div>
          
          <div v-if="uploadProgress > 0 && uploadProgress < 100" class="mb-4">
            <div class="w-full bg-gray-200 rounded-full h-2.5">
              <div class="bg-blue-600 h-2.5 rounded-full" :style="`width: ${uploadProgress}%`"></div>
            </div>
            <p class="text-sm text-gray-500 mt-1">上传中... {{ uploadProgress }}%</p>
          </div>
          
          <p v-if="uploadError" class="text-red-500 mb-4">{{ uploadError }}</p>
          
          <div class="flex justify-end gap-2 mt-6">
            <button 
              type="button"
              @click="showUploadModal = false"
              class="px-4 py-2 border rounded-md"
            >
              取消
            </button>
            <button 
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-md"
              :disabled="uploading"
            >
              <span v-if="!uploading">上传</span>
              <span v-else class="flex items-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                上传中
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 从课件导入模态框 -->
    <div v-if="showImportModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[80vh] overflow-y-auto">
        <h3 class="text-xl font-bold mb-4">从课件导入到知识库</h3>
        
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">选择课程</label>
          <select 
            v-model="importForm.courseId" 
            @change="fetchCourseMaterials"
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">请选择课程</option>
            <option v-for="course in courses" :key="course.id" :value="course.id">
              {{ course.name }}
            </option>
          </select>
        </div>
        
        <div v-if="courseMaterials.length > 0" class="space-y-4">
          <h4 class="font-medium">可导入的课件文件</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div 
              v-for="material in courseMaterials" 
              :key="material.id"
              class="border rounded-md p-4 hover:bg-gray-50"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <span class="mr-3" v-html="getFileIcon(material.file_path)"></span>
                  <div>
                    <p class="font-medium">{{ material.title }}</p>
                    <p class="text-sm text-gray-500">{{ material.material_type }} · {{ material.size }}</p>
                  </div>
                </div>
                <button 
                  v-if="isSupportedForKnowledgeBase(material)"
                  @click="importToKnowledgeBase(material)"
                  class="text-blue-600 hover:text-blue-800 text-sm"
                  :disabled="isProcessingKnowledgeBase(material)"
                >
                  {{ getImportButtonText(material) }}
                </button>
                <span v-else class="text-sm text-gray-400">不支持</span>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else-if="importForm.courseId" class="text-center py-10">
          <p class="text-gray-500">该课程暂无课件文件</p>
        </div>
        
        <div class="flex justify-end mt-6">
          <button 
            @click="showImportModal = false"
            class="px-4 py-2 border rounded-md"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue';
import { ragAiAPI, materialAPI, courseAPI, knowledgeBaseAPI } from '../../api';
import notificationService from '../../services/notificationService';
import dialogService from '../../services/dialogService';

// 类型定义
interface Course {
  id: number;
  name: string;
}

interface KnowledgeItem {
  id: number;
  course_id: number;
  file_path: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  progress_detail?: {
    stage: string;
    message?: string;
  };
  error_message?: string;
  created_at: string | number;
}

interface Material {
  id: number;
  title: string;
  file_path: string;
  material_type: string;
  size: string;
}

interface ApiResponse<T = any> {
  status: string;
  message?: string;
  data?: T;
}

interface CoursesResponse extends ApiResponse {
  courses?: Course[];
}

interface KnowledgeBaseResponse extends ApiResponse {
  items?: KnowledgeItem[];
}

interface MaterialsResponse extends ApiResponse {
  materials?: Material[];
}

interface UploadResponse extends ApiResponse {
  id?: number;
}

interface MaterialDetailResponse extends ApiResponse {
  file_path?: string;
}

// 搜索和筛选
const searchQuery = ref('');
const filterCourseId = ref('');
const filterStatus = ref('');
const refreshing = ref(false);

// 批量操作
const selectedItemIds = ref<number[]>([]);
const selectAll = ref(false);
const batchDeleting = ref(false);
const clearingQueue = ref(false);

// 模态框状态
const showUploadModal = ref(false);
const showImportModal = ref(false);

// 上传相关
const uploading = ref(false);
const uploadProgress = ref(0);
const uploadError = ref('');
const uploadForm = reactive({
  courseId: '',
  file: null as File | null
});

// 导入相关
const importForm = reactive({
  courseId: ''
});

// 数据
const courses = ref<Course[]>([]);
const knowledgeItems = ref<KnowledgeItem[]>([]);
const courseMaterials = ref<Material[]>([]);
const loading = ref(false);

// 统计
const stats = reactive({
  totalFiles: 0,
  completedFiles: 0,
  processingFiles: 0,
  failedFiles: 0
});

const hasProcessing = computed(() =>
  knowledgeItems.value.some(item => item.status === 'pending' || item.status === 'processing')
);

// 批量操作相关计算属性
const selectedItems = computed(() => 
  knowledgeItems.value.filter(item => selectedItemIds.value.includes(item.id))
);

const hasProcessingItems = computed(() =>
  knowledgeItems.value.some(item => item.status === 'pending' || item.status === 'processing')
);

// 轮询控制
let refreshTimer: number | null = null;
let lastRefreshTime = 0;
const REFRESH_INTERVAL = 10000; // 10秒间隔
const MIN_REFRESH_INTERVAL = 5000; // 最小5秒间隔

// 计算属性
const filteredKnowledgeItems = computed(() => {
  let items = knowledgeItems.value;
  console.log('filteredKnowledgeItems计算开始，原始项目数:', items.length);
  console.log('搜索查询:', searchQuery.value);
  console.log('课程筛选:', filterCourseId.value);
  console.log('状态筛选:', filterStatus.value);
  
  // 按搜索查询过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    items = items.filter(item => 
      getFileName(item.file_path).toLowerCase().includes(query) ||
      getCourseName(item.course_id).toLowerCase().includes(query)
    );
    console.log('搜索过滤后项目数:', items.length);
  }
  
  // 按课程过滤
  if (filterCourseId.value) {
    items = items.filter(item => item.course_id === Number(filterCourseId.value));
    console.log('课程过滤后项目数:', items.length);
  }
  
  // 按状态过滤
  if (filterStatus.value) {
    items = items.filter(item => item.status === filterStatus.value);
    console.log('状态过滤后项目数:', items.length);
  }
  
  console.log('最终过滤后项目数:', items.length);
  return items;
});

onMounted(async () => {
  console.log('KnowledgeBase组件开始加载...');
  
  // 先获取课程列表
  await fetchCourses();
  console.log('课程列表获取完成，课程数量:', courses.value.length);
  
  // 再获取知识库状态
  await fetchKnowledgeBaseStatus();
  console.log('知识库状态获取完成，知识库项目数量:', knowledgeItems.value.length);
});

watch(hasProcessing, (val) => {
  if (val) {
    // 只有在没有定时器且距离上次刷新超过最小间隔时才启动轮询
    if (!refreshTimer && (Date.now() - lastRefreshTime) > MIN_REFRESH_INTERVAL) {
      refreshTimer = window.setInterval(() => {
        // 检查是否还有处理中的项目
        if (hasProcessing.value) {
          fetchKnowledgeBaseStatus();
        } else {
          // 如果没有处理中的项目，停止轮询
          if (refreshTimer) {
            clearInterval(refreshTimer);
            refreshTimer = null;
          }
        }
      }, REFRESH_INTERVAL);
    }
  } else {
    // 没有处理中的项目，停止轮询
    if (refreshTimer) {
      clearInterval(refreshTimer);
      refreshTimer = null;
    }
  }
}, { immediate: true });

// 获取课程列表
async function fetchCourses() {
  try {
    console.log('开始获取课程列表...');
    const response = await courseAPI.getCourses();
    console.log('课程API响应:', response);
    
    // 检查响应格式 - Axios响应
    if (response && typeof response === 'object' && 'data' in response) {
      const data = response.data as CoursesResponse;
      courses.value = data.courses || [];
    } else if (response && typeof response === 'object' && 'courses' in response) {
      // 直接响应格式
      courses.value = (response as CoursesResponse).courses || [];
    } else {
      courses.value = [];
    }
    
    console.log('课程列表设置完成:', courses.value);
  } catch (error) {
    console.error('获取课程列表失败:', error);
    courses.value = [];
  }
}

// 获取知识库状态
async function fetchKnowledgeBaseStatus() {
  // 防抖：如果距离上次请求时间太短，跳过
  const now = Date.now();
  if (now - lastRefreshTime < MIN_REFRESH_INTERVAL) {
    console.log('跳过频繁请求，距离上次请求时间:', now - lastRefreshTime, 'ms');
    return;
  }
  
  lastRefreshTime = now;
  loading.value = true;
  
  try {
    console.log('开始获取知识库状态，当前课程数量:', courses.value.length);
    
    // 获取所有课程的知识库状态
    const allItems: KnowledgeItem[] = [];
    for (const course of courses.value) {
      try {
        console.log(`获取课程 ${course.id} (${course.name}) 的知识库状态...`);
        const response = await knowledgeBaseAPI.getKnowledgeBaseStatus(course.id);
        console.log(`课程 ${course.id} 知识库状态响应:`, response);
        
        // 检查响应格式 - Axios响应
        if (response && typeof response === 'object' && 'data' in response) {
          const data = response.data as KnowledgeBaseResponse;
          if (data && data.status === 'success' && data.items) {
            allItems.push(...data.items);
            console.log(`课程 ${course.id} 添加了 ${data.items.length} 个项目`);
          }
        } else if (response && typeof response === 'object' && 'status' in response) {
          // 直接响应格式
          const kbResponse = response as KnowledgeBaseResponse;
          if (kbResponse.status === 'success' && kbResponse.items) {
            allItems.push(...kbResponse.items);
            console.log(`课程 ${course.id} 添加了 ${kbResponse.items.length} 个项目`);
          }
        }
      } catch (error) {
        console.error(`获取课程 ${course.id} 知识库状态失败:`, error);
      }
    }
    
    console.log('所有课程知识库状态获取完成，总项目数:', allItems.length);
    knowledgeItems.value = allItems;
    updateStats();
    console.log('统计更新完成:', stats);
    
    // 检查是否还有处理中的项目，如果没有则停止轮询
    if (!hasProcessing.value && refreshTimer) {
      console.log('所有项目处理完成，停止轮询');
      clearInterval(refreshTimer);
      refreshTimer = null;
    }
  } catch (error) {
    console.error('获取知识库状态失败:', error);
  } finally {
    loading.value = false;
  }
}

// 刷新知识库
async function refreshKnowledgeBase() {
  refreshing.value = true;
  await fetchKnowledgeBaseStatus();
  refreshing.value = false;
}

// 更新统计
function updateStats() {
  const items = knowledgeItems.value;
  stats.totalFiles = items.length;
  stats.completedFiles = items.filter(item => item.status === 'completed').length;
  stats.processingFiles = items.filter(item => item.status === 'processing').length;
  stats.failedFiles = items.filter(item => item.status === 'failed').length;
}

// 直接上传到知识库
async function uploadToKnowledgeBase() {
  if (!uploadForm.courseId || !uploadForm.file) {
    notificationService.warning('操作提示', '请选择课程和文件');
    return;
  }

  uploading.value = true;
  uploadError.value = '';
  uploadProgress.value = 0;

  try {
    // 先上传文件到课件系统
    const formData = new FormData();
    formData.append('file', uploadForm.file);
    formData.append('title', uploadForm.file.name);
    
    uploadProgress.value = 30;
    
    const uploadResponse = await materialAPI.uploadMaterial(Number(uploadForm.courseId), formData);
    
    uploadProgress.value = 60;
    
    // 检查上传响应
    let materialId: number;
    let isDuplicate = false;
    let duplicateMessage = '';
    
    if (uploadResponse && typeof uploadResponse === 'object' && 'data' in uploadResponse) {
      const data = uploadResponse.data as any;
      if (data.status === 'duplicate') {
        // 处理重复文件
        isDuplicate = true;
        duplicateMessage = data.message || '文件已存在';
        materialId = data.material?.id || 0;
      } else {
        materialId = data.material?.id || 0;
      }
    } else if (uploadResponse && typeof uploadResponse === 'object' && 'status' in uploadResponse) {
      const response = uploadResponse as any;
      if (response.status === 'duplicate') {
        isDuplicate = true;
        duplicateMessage = response.message || '文件已存在';
        materialId = response.material?.id || 0;
      } else {
        materialId = response.material?.id || 0;
      }
    } else {
      throw new Error('无法获取上传的文件ID');
    }
    
    // 如果是重复文件，显示提示信息
    if (isDuplicate) {
      console.log('检测到重复文件:', duplicateMessage);
      // 可以选择继续处理或停止
      const continueProcessing = await dialogService.confirm({
        title: '重复文件提示',
        message: `${duplicateMessage}\n\n是否继续将该文件添加到知识库？`,
        type: 'info'
      });
      if (!continueProcessing) {
        uploadProgress.value = 0;
        return;
      }
    }
    
    const materialResponse = await materialAPI.getMaterial(materialId);
    let filePath: string;
    
    if (materialResponse && typeof materialResponse === 'object' && 'data' in materialResponse) {
      const data = materialResponse.data as MaterialDetailResponse;
      filePath = data.file_path || '';
    } else if (materialResponse && typeof materialResponse === 'object' && 'file_path' in materialResponse) {
      filePath = (materialResponse as MaterialDetailResponse).file_path || '';
    } else {
      throw new Error('无法获取文件路径');
    }
    
    // 修正 filePath 格式，确保不带 /uploads/ 前缀
    filePath = filePath.replace(/^\/?uploads\//, '');
    // 再确保以 materials/{courseId}/ 开头
    if (!filePath.startsWith('materials/')) {
      const fileName = uploadForm.file.name;
      filePath = `materials/${uploadForm.courseId}/${fileName}`;
    }
    uploadProgress.value = 80;
    
    // 添加到知识库
    const kbResponse = await knowledgeBaseAPI.addToKnowledgeBase(Number(uploadForm.courseId), filePath);
    
    uploadProgress.value = 100;
    
    // 检查响应格式
    let success = false;
    let message = '';
    
    if (kbResponse && typeof kbResponse === 'object' && 'data' in kbResponse) {
      const data = kbResponse.data as ApiResponse;
      success = data.status === 'success';
      message = data.message || '';
    } else if (kbResponse && typeof kbResponse === 'object' && 'status' in kbResponse) {
      const response = kbResponse as ApiResponse;
      success = response.status === 'success';
      message = response.message || '';
    }
    
    if (success) {
      // 清空表单
      uploadForm.courseId = '';
      uploadForm.file = null;
      showUploadModal.value = false;
      
      // 刷新知识库状态
      await fetchKnowledgeBaseStatus();
      
      const successMessage = isDuplicate 
        ? '重复文件已添加到知识库处理队列' 
        : '文件已成功上传并添加到知识库处理队列';
      notificationService.success('上传成功', successMessage);
    } else {
      throw new Error(message || '添加到知识库失败');
    }
  } catch (error) {
    console.error('上传到知识库失败:', error);
    uploadError.value = error instanceof Error ? error.message : '上传失败';
  } finally {
    uploading.value = false;
    uploadProgress.value = 0;
  }
}

// 处理直接文件选择
function handleDirectFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    uploadForm.file = target.files[0];
  }
}

// 获取课程材料
async function fetchCourseMaterials() {
  if (!importForm.courseId) {
    courseMaterials.value = [];
    return;
  }
  
  try {
    const response = await materialAPI.getMaterials(Number(importForm.courseId));
    
    // 检查响应格式
    if (response && typeof response === 'object' && 'data' in response) {
      const data = response.data as MaterialsResponse;
      courseMaterials.value = data.materials || [];
    } else if (response && typeof response === 'object' && 'materials' in response) {
      courseMaterials.value = (response as MaterialsResponse).materials || [];
    } else {
      courseMaterials.value = [];
    }
  } catch (error) {
    console.error('获取课程材料失败:', error);
    courseMaterials.value = [];
  }
}

// 从课件导入到知识库
async function importToKnowledgeBase(material: Material) {
  if (!material.file_path) {
    notificationService.warning('操作提示', '该材料没有文件路径，无法导入到知识库');
    return;
  }
  // 修正 file_path 路径，去掉 /uploads/ 前缀
  let filePath = material.file_path.replace(/^\/?uploads\//, '');
  try {
    const response = await knowledgeBaseAPI.addToKnowledgeBase(Number(importForm.courseId), filePath);
    
    // 检查响应格式
    let success = false;
    let message = '';
    
    if (response && typeof response === 'object' && 'data' in response) {
      const data = response.data as ApiResponse;
      success = data.status === 'success';
      message = data.message || '';
    } else if (response && typeof response === 'object' && 'status' in response) {
      const apiResponse = response as ApiResponse;
      success = apiResponse.status === 'success';
      message = apiResponse.message || '';
    }
    
    if (success) {
      await fetchKnowledgeBaseStatus();
      notificationService.success('导入成功', '文件已添加到知识库处理队列');
    } else {
      throw new Error(message || '添加到知识库失败');
    }
  } catch (error) {
    console.error('导入到知识库失败:', error);
    notificationService.error('导入失败', error instanceof Error ? error.message : '未知错误');
  }
}

// 检查文件是否支持知识库
function isSupportedForKnowledgeBase(material: Material) {
  if (!material.file_path) return false;
  
  const fileExtension = material.file_path.substring(material.file_path.lastIndexOf('.')).toLowerCase();
  return ['.pdf', '.docx', '.doc', '.txt', '.md'].includes(fileExtension);
}

// 检查文件是否正在处理中
function isProcessingKnowledgeBase(material: Material) {
  if (!material.file_path) return false;
  
  const queueItem = knowledgeItems.value.find(item => 
    item.file_path === material.file_path && 
    (item.status === 'pending' || item.status === 'processing')
  );
  
  return !!queueItem;
}

// 获取导入按钮文本
function getImportButtonText(material: Material) {
  if (!material.file_path) return '导入';
  
  const queueItem = knowledgeItems.value.find(item => item.file_path === material.file_path);
  
  if (!queueItem) return '导入';
  
  switch (queueItem.status) {
    case 'pending':
      return '等待处理';
    case 'processing':
      return `处理中 ${queueItem.progress ? queueItem.progress.toFixed(1) : 0}%`;
    case 'completed':
      return '已导入';
    case 'failed':
      return '处理失败';
    default:
      return '导入';
  }
}

// 重试处理
async function retryProcessing(item: KnowledgeItem) {
  try {
    const result = await dialogService.confirm({
      title: '重试处理',
      message: `确定要重新处理文件 "${getFileName(item.file_path)}" 吗？`,
      type: 'info'
    });
    
    if (!result) return;
    
    const response = await knowledgeBaseAPI.addToKnowledgeBase(item.course_id, item.file_path);
    
    // 检查响应格式
    let success = false;
    let message = '';
    
    if (response && typeof response === 'object' && 'data' in response) {
      const data = response.data as ApiResponse;
      success = data.status === 'success';
      message = data.message || '';
    } else if (response && typeof response === 'object' && 'status' in response) {
      const apiResponse = response as ApiResponse;
      success = apiResponse.status === 'success';
      message = apiResponse.message || '';
    }
    
    if (success) {
      await fetchKnowledgeBaseStatus();
      notificationService.success('重试成功', '文件已重新加入处理队列');
    } else {
      throw new Error(message || '重试失败');
    }
  } catch (error) {
    console.error('重试处理失败:', error);
    notificationService.error('重试失败', error instanceof Error ? error.message : '未知错误');
  }
}

// 从知识库删除
async function removeFromKnowledgeBase(item: KnowledgeItem) {
  try {
    const result = await dialogService.confirm({
      title: '删除确认',
      message: `确定要从知识库中删除文件 "${getFileName(item.file_path)}" 吗？此操作不可恢复。`,
      type: 'info'
    });
    
    if (!result) return;
    
    const response = await knowledgeBaseAPI.removeFromKnowledgeBase(item.id);
    
    // 检查响应格式
    let success = false;
    let message = '';
    
    if (response && typeof response === 'object' && 'data' in response) {
      const data = response.data as ApiResponse;
      success = data.status === 'success';
      message = data.message || '';
    } else if (response && typeof response === 'object' && 'status' in response) {
      const apiResponse = response as ApiResponse;
      success = apiResponse.status === 'success';
      message = apiResponse.message || '';
    }
    
    if (success) {
      await fetchKnowledgeBaseStatus();
      notificationService.success('删除成功', '文件已从知识库中删除');
    } else {
      throw new Error(message || '删除失败');
    }
  } catch (error) {
    console.error('删除失败:', error);
    notificationService.error('删除失败', error instanceof Error ? error.message : '未知错误');
  }
}

// 在文件中搜索
function searchInFile(item: KnowledgeItem) {
  // 这里可以跳转到搜索页面或打开搜索对话框
  notificationService.info('功能开发中', `搜索功能开发中，文件: ${getFileName(item.file_path)}`);
}

// 工具函数
function getFileName(filePath: string) {
  if (!filePath) return '未知文件';
  return filePath.substring(filePath.lastIndexOf('/') + 1);
}

function getFileSize(filePath: string) {
  // 这里可以从文件信息中获取实际大小
  return '未知大小';
}

function getCourseName(courseId: number) {
  const course = courses.value.find(c => c.id === courseId);
  return course ? course.name : `课程 #${courseId}`;
}

function formatDate(dateValue: string | number) {
  if (!dateValue) return '未知时间';
  
  try {
    let timestamp: number;
    
    // 如果是字符串，尝试转换为数字
    if (typeof dateValue === 'string') {
      timestamp = parseInt(dateValue);
      if (isNaN(timestamp)) {
        // 如果不是数字字符串，尝试直接解析日期
        return new Date(dateValue).toLocaleDateString('zh-CN');
      }
    } else {
      timestamp = dateValue;
    }
    
    // 检查是否是Unix时间戳（秒）
    if (timestamp < 10000000000) {
      // 秒级时间戳，转换为毫秒
      timestamp *= 1000;
    }
    
    const date = new Date(timestamp);
    
    // 检查日期是否有效
    if (isNaN(date.getTime())) {
      return '未知时间';
    }
    
    return date.toLocaleDateString('zh-CN');
  } catch (error) {
    console.error('日期格式化错误:', error, '原始值:', dateValue);
    return '未知时间';
  }
}

function getStatusText(status: string) {
  switch (status) {
    case 'pending':
      return '等待处理';
    case 'processing':
      return '处理中';
    case 'completed':
      return '已完成';
    case 'failed':
      return '处理失败';
    default:
      return '未知状态';
  }
}

function getStatusBadgeClass(status: string) {
  switch (status) {
    case 'pending':
      return 'px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800';
    case 'processing':
      return 'px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800';
    case 'completed':
      return 'px-2 py-1 text-xs rounded-full bg-green-100 text-green-800';
    case 'failed':
      return 'px-2 py-1 text-xs rounded-full bg-red-100 text-red-800';
    default:
      return 'px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800';
  }
}

function getFileIcon(filePath: string) {
  if (!filePath) {
    return `<svg class="h-6 w-6 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
    </svg>`;
  }
  
  const extension = filePath.substring(filePath.lastIndexOf('.')).toLowerCase();
  
  switch (extension) {
    case '.pdf':
      return `<svg class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
      </svg>`;
    case '.docx':
    case '.doc':
      return `<svg class="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
      </svg>`;
    case '.txt':
    case '.md':
      return `<svg class="h-6 w-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
      </svg>`;
    default:
      return `<svg class="h-6 w-6 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
      </svg>`;
  }
}

// 批量操作函数
function toggleSelectAll() {
  if (selectAll.value) {
    selectedItemIds.value = filteredKnowledgeItems.value.map(item => item.id);
  } else {
    selectedItemIds.value = [];
  }
}

async function batchDelete() {
  if (selectedItemIds.value.length === 0) {
    notificationService.warning('操作提示', '请选择要删除的文件');
    return;
  }
  
  try {
    const result = await dialogService.confirm({
      title: '批量删除确认',
      message: `确定要删除选中的 ${selectedItemIds.value.length} 个文件吗？此操作不可恢复。`,
      type: 'info'
    });
    
    if (!result) return;
    
    batchDeleting.value = true;
    const response = await knowledgeBaseAPI.batchRemove(selectedItemIds.value);
    
    // 检查响应格式
    let success = false;
    let message = '';
    
    if (response && typeof response === 'object' && 'data' in response) {
      const data = response.data as ApiResponse;
      success = data.status === 'success';
      message = data.message || '';
    } else if (response && typeof response === 'object' && 'status' in response) {
      const apiResponse = response as ApiResponse;
      success = apiResponse.status === 'success';
      message = apiResponse.message || '';
    }
    
    if (success) {
      selectedItemIds.value = [];
      selectAll.value = false;
      await fetchKnowledgeBaseStatus();
      notificationService.success('批量删除成功', message || '所选文件已删除');
    } else {
      throw new Error(message || '批量删除失败');
    }
  } catch (error) {
    console.error('批量删除失败:', error);
    notificationService.error('批量删除失败', error instanceof Error ? error.message : '未知错误');
  } finally {
    batchDeleting.value = false;
  }
}

async function clearQueue() {
  if (!filterCourseId.value) {
    notificationService.warning('操作提示', '请先选择课程');
    return;
  }
  
  try {
    const result = await dialogService.confirm({
      title: '清空队列确认',
      message: '确定要清空当前课程的所有待处理和处理中的队列吗？此操作不可恢复。',
      type: 'info'
    });
    
    if (!result) return;
    
    clearingQueue.value = true;
    const response = await knowledgeBaseAPI.clearQueue(Number(filterCourseId.value));
    
    // 检查响应格式
    let success = false;
    let message = '';
    
    if (response && typeof response === 'object' && 'data' in response) {
      const data = response.data as ApiResponse;
      success = data.status === 'success';
      message = data.message || '';
    } else if (response && typeof response === 'object' && 'status' in response) {
      const apiResponse = response as ApiResponse;
      success = apiResponse.status === 'success';
      message = apiResponse.message || '';
    }
    
    if (success) {
      await fetchKnowledgeBaseStatus();
      notificationService.success('清空队列成功', message || '队列已清空');
    } else {
      throw new Error(message || '清空队列失败');
    }
  } catch (error) {
    console.error('清空队列失败:', error);
    notificationService.error('清空队列失败', error instanceof Error ? error.message : '未知错误');
  } finally {
    clearingQueue.value = false;
  }
}
</script> 