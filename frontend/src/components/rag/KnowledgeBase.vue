<template>
  <div class="knowledge-base">
    <div class="mb-6 flex justify-between items-center">
      <h2 class="text-2xl font-bold">知识库管理</h2>
      <button 
        @click="showImportModal = true"
        class="px-4 py-2 bg-blue-600 text-white rounded-md"
      >
        上传课件
      </button>
    </div>
    
    <!-- 知识库搜索 -->
    <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-6">
      <h3 class="text-lg font-semibold mb-4">知识库搜索</h3>
      
      <form @submit.prevent="searchKnowledge" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">搜索查询</label>
          <div class="flex">
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="输入你的问题或关键词..." 
              class="flex-1 px-4 py-2 border rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              :disabled="searching"
            />
            <button 
              type="submit" 
              class="bg-blue-600 text-white px-4 py-2 rounded-r-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              :disabled="searching || !searchQuery.trim()"
            >
              <span v-if="!searching">搜索</span>
              <span v-else class="flex items-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                搜索中
              </span>
            </button>
          </div>
        </div>
        
        <div class="flex flex-wrap gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">课程</label>
            <select 
              v-model="searchFilters.courseId" 
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">所有课程</option>
              <option v-for="course in courses" :key="course.id" :value="course.id">
                {{ course.name }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">资料类型</label>
            <select 
              v-model="searchFilters.materialType" 
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">所有类型</option>
              <option value="document">文档</option>
              <option value="video">视频</option>
              <option value="audio">音频</option>
              <option value="image">图片</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">结果数量</label>
            <select 
              v-model="searchFilters.limit" 
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="5">5</option>
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
            </select>
          </div>
        </div>
      </form>
    </div>
    
    <!-- 搜索结果 -->
    <div v-if="hasSearched" class="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-6">
      <h3 class="text-lg font-semibold mb-4">搜索结果</h3>
      
      <div v-if="searching" class="flex justify-center py-10">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
      
      <div v-else-if="searchResults.length === 0" class="text-center py-10 bg-gray-50 rounded-md">
        <p class="text-gray-500">未找到相关结果</p>
      </div>
      
      <div v-else class="space-y-6">
        <div v-for="(result, index) in searchResults" :key="index" class="border-b pb-4 last:border-b-0 last:pb-0">
          <div class="flex justify-between items-start">
            <h4 class="font-medium">{{ result.title }}</h4>
            <span class="text-sm text-gray-500">相关度: {{ result.relevance.toFixed(2) }}</span>
          </div>
          
          <p class="text-sm text-gray-600 mt-1 mb-2">{{ result.content }}</p>
          
          <div class="flex items-center text-xs text-gray-500">
            <span>{{ result.course_name }}</span>
            <span class="mx-2">•</span>
            <span>{{ result.material_type }}</span>
            <span class="mx-2">•</span>
            <span>{{ result.date }}</span>
          </div>
          
          <div class="mt-2">
            <a :href="result.url" class="text-sm text-blue-600 hover:text-blue-800">查看原文</a>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 知识库统计 -->
    <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
      <h3 class="text-lg font-semibold mb-4">知识库统计</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="border rounded-md p-4 text-center">
          <p class="text-3xl font-bold text-blue-600">{{ stats.totalDocuments }}</p>
          <p class="text-sm text-gray-500">文档总数</p>
        </div>
        
        <div class="border rounded-md p-4 text-center">
          <p class="text-3xl font-bold text-green-600">{{ stats.totalCourses }}</p>
          <p class="text-sm text-gray-500">课程覆盖</p>
        </div>
        
        <div class="border rounded-md p-4 text-center">
          <p class="text-3xl font-bold text-purple-600">{{ stats.lastUpdated }}</p>
          <p class="text-sm text-gray-500">最后更新</p>
        </div>
      </div>
      
      <div class="mt-6">
        <h4 class="font-medium mb-2">文档类型分布</h4>
        <div class="flex items-center">
          <div class="w-full bg-gray-200 rounded-full h-2.5">
            <div class="flex h-2.5">
              <div class="bg-blue-600 h-2.5 rounded-l-full" :style="`width: ${stats.typeDistribution.document}%`"></div>
              <div class="bg-green-600 h-2.5" :style="`width: ${stats.typeDistribution.video}%`"></div>
              <div class="bg-yellow-600 h-2.5" :style="`width: ${stats.typeDistribution.audio}%`"></div>
              <div class="bg-red-600 h-2.5 rounded-r-full" :style="`width: ${stats.typeDistribution.image}%`"></div>
            </div>
          </div>
        </div>
        <div class="flex justify-between mt-2 text-xs text-gray-500">
          <div class="flex items-center">
            <span class="inline-block w-3 h-3 bg-blue-600 rounded-full mr-1"></span>
            <span>文档 ({{ stats.typeDistribution.document }}%)</span>
          </div>
          <div class="flex items-center">
            <span class="inline-block w-3 h-3 bg-green-600 rounded-full mr-1"></span>
            <span>视频 ({{ stats.typeDistribution.video }}%)</span>
          </div>
          <div class="flex items-center">
            <span class="inline-block w-3 h-3 bg-yellow-600 rounded-full mr-1"></span>
            <span>音频 ({{ stats.typeDistribution.audio }}%)</span>
          </div>
          <div class="flex items-center">
            <span class="inline-block w-3 h-3 bg-red-600 rounded-full mr-1"></span>
            <span>图片 ({{ stats.typeDistribution.image }}%)</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 知识库资料列表 -->
    <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200 mt-6">
      <h3 class="text-lg font-semibold mb-4">知识库资料</h3>
      
      <div v-if="materialsLoading" class="flex justify-center py-10">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
      
      <div v-else-if="knowledgeItems.length > 0" class="space-y-4">
        <div v-for="item in knowledgeItems" :key="item.id" class="flex items-center justify-between p-4 border rounded-md">
          <div class="flex items-center">
            <span class="mr-3" v-html="getMaterialIcon(item.material_type)"></span>
            <div>
              <p class="font-medium">{{ item.title }}</p>
              <p class="text-sm text-gray-500">{{ item.course_name }} · {{ item.material_type }} · {{ item.size }}</p>
            </div>
          </div>
          <div class="flex space-x-3">
            <button @click="previewMaterial(item.id)" class="text-blue-600 hover:text-blue-800">预览</button>
            <button @click="downloadMaterial(item.id)" class="text-blue-600 hover:text-blue-800">下载</button>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-10">
        <p class="text-gray-500">暂无知识库资料</p>
      </div>
    </div>
    
    <!-- 上传课件模态框 -->
    <div v-if="showImportModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-lg">
        <h3 class="text-xl font-bold mb-4">上传课件资源</h3>
        
        <form @submit.prevent="importMaterial" class="space-y-4">
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">选择课程 <span class="text-red-500">*</span></label>
            <select 
              v-model="importForm.courseId" 
              required
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option v-for="course in courses" :key="course.id" :value="course.id">
                {{ course.name }}
              </option>
            </select>
          </div>
          
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">课件标题</label>
            <input 
              v-model="importForm.title" 
              type="text" 
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" 
              placeholder="输入课件标题（可选，默认使用文件名）" 
            />
          </div>
          
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">选择文件 <span class="text-red-500">*</span></label>
            <div class="border-2 border-dashed border-gray-300 rounded-md p-6">
              <div class="text-center">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="mt-1 text-sm text-gray-600">
                  拖放文件到这里，或者
                  <label for="file-upload" class="text-blue-600 hover:text-blue-500 cursor-pointer">浏览文件</label>
                </p>
                <p class="mt-1 text-xs text-gray-500">
                  支持 PDF, DOCX, TXT, MP4, MP3 等格式
                </p>
              </div>
              <input 
                id="file-upload" 
                type="file" 
                class="hidden" 
                @change="handleFileChange" 
                required 
              />
            </div>
            <p v-if="importForm.file" class="mt-2 text-sm text-gray-500">
              已选择: {{ importForm.file.name }} ({{ (importForm.file.size / 1024).toFixed(1) }}KB)
            </p>
          </div>
          
          <div v-if="importProgress > 0 && importProgress < 100" class="mb-4">
            <div class="w-full bg-gray-200 rounded-full h-2.5">
              <div class="bg-blue-600 h-2.5 rounded-full" :style="`width: ${importProgress}%`"></div>
            </div>
            <p class="text-sm text-gray-500 mt-1">上传中... {{ importProgress }}%</p>
          </div>
          
          <p v-if="importError" class="text-red-500 mb-4">{{ importError }}</p>
          
          <div class="flex justify-end gap-2 mt-6">
            <button 
              type="button"
              @click="showImportModal = false"
              class="px-4 py-2 border rounded-md"
            >
              取消
            </button>
            <button 
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-md"
              :disabled="importing"
            >
              <span v-if="!importing">上传</span>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, inject, watch } from 'vue';
import { ragAiAPI, materialAPI, courseAPI } from '../../api';

// 全局状态注入
const globalCourses = inject('courses', ref([]));
const globalMaterials = inject('materials', ref([]));
const isDataLoaded = inject('isDataLoaded', ref(false));

// 搜索相关
const searchQuery = ref('');
const searching = ref(false);
const hasSearched = ref(false);
const searchResults = ref([]);
const searchFilters = reactive({
  courseId: '',
  materialType: '',
  limit: '10'
});

// 导入相关
const showImportModal = ref(false);
const importing = ref(false);
const importProgress = ref(0);
const importError = ref('');
const importForm = reactive({
  courseId: '',
  title: '',
  file: null as File | null
});

// 课程列表
const courses = ref([]);
const coursesLoading = ref(false);
const materialsLoading = ref(false);

const stats = reactive({
  totalDocuments: 0,
  totalCourses: 0,
  lastUpdated: '',
  typeDistribution: {
    document: 0,
    video: 0,
    audio: 0,
    image: 0
  }
});

// 知识库资料列表
const knowledgeItems = ref([]);

onMounted(async () => {
  // 如果全局数据已加载，直接使用
  if (isDataLoaded.value && globalCourses.value.length > 0) {
    courses.value = globalCourses.value;
    processGlobalMaterials();
    updateStats();
  } else {
    // 否则加载数据
    await Promise.all([
      fetchCourses(),
      fetchKnowledgeItems()
    ]);
  }
});

// 监听全局数据变化
watch(() => globalMaterials.value, () => {
  if (globalMaterials.value.length > 0) {
    processGlobalMaterials();
    updateStats();
  }
}, { deep: true });

function processGlobalMaterials() {
  if (globalMaterials.value.length > 0) {
    // 处理全局材料数据，添加课程名称
    const materialsWithCourseNames = globalMaterials.value.map(material => {
      const course = globalCourses.value.find(c => c.id === material.course_id);
      return {
        ...material,
        course_name: course ? course.name : '未知课程'
      };
    });
    
    // 按上传时间降序排序，最新的在最上面
    knowledgeItems.value = materialsWithCourseNames.sort((a, b) => {
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    });
  }
}

function updateStats() {
  // 更新统计数据
  if (knowledgeItems.value.length > 0) {
    stats.totalDocuments = knowledgeItems.value.length;
    
    // 获取涉及的课程数量
    const uniqueCourseIds = new Set(knowledgeItems.value.map(item => item.course_id));
    stats.totalCourses = uniqueCourseIds.size;
    
    // 获取最后更新时间
    const latestMaterial = knowledgeItems.value[0]; // 已按时间排序，第一个是最新的
    stats.lastUpdated = latestMaterial.created_at ? new Date(latestMaterial.created_at).toLocaleDateString() : '';
    
    // 计算类型分布
    const typeCount = {
      document: 0,
      video: 0,
      audio: 0,
      image: 0
    };
    
    knowledgeItems.value.forEach(item => {
      const type = item.material_type.toLowerCase();
      if (type.includes('文档') || type.includes('pdf') || type.includes('doc')) {
        typeCount.document++;
      } else if (type.includes('视频') || type.includes('video')) {
        typeCount.video++;
      } else if (type.includes('音频') || type.includes('audio')) {
        typeCount.audio++;
      } else if (type.includes('图片') || type.includes('image')) {
        typeCount.image++;
      } else {
        typeCount.document++; // 默认归为文档
      }
    });
    
    const total = knowledgeItems.value.length;
    stats.typeDistribution = {
      document: Math.round((typeCount.document / total) * 100) || 0,
      video: Math.round((typeCount.video / total) * 100) || 0,
      audio: Math.round((typeCount.audio / total) * 100) || 0,
      image: Math.round((typeCount.image / total) * 100) || 0
    };
  }
}

async function fetchCourses() {
  try {
    coursesLoading.value = true;
    // 调用API获取课程列表
    const response = await courseAPI.getCourses();
    courses.value = response.courses || [];
    
    if (courses.value.length === 0) {
      // 如果API返回为空或出错，使用模拟数据
      courses.value = [
        { id: 1, name: '人工智能基础' },
        { id: 2, name: '高等数学' },
        { id: 3, name: '英语写作' }
      ];
      console.warn('使用模拟课程数据，实际项目中应从API获取');
    }
  } catch (error) {
    console.error('获取课程列表失败:', error);
    // 出错时使用模拟数据
    courses.value = [
      { id: 1, name: '人工智能基础' },
      { id: 2, name: '高等数学' },
      { id: 3, name: '英语写作' }
    ];
  } finally {
    coursesLoading.value = false;
  }
}

async function fetchKnowledgeItems() {
  try {
    materialsLoading.value = true;
    // 获取所有课程的材料
    const allMaterials = [];
    
    // 遍历所有课程，获取每个课程的材料
    for (const course of courses.value) {
      try {
        const response = await materialAPI.getMaterials(course.id);
        if (response && response.materials && response.materials.length > 0) {
          // 为每个材料添加课程名称
          const materialsWithCourseName = response.materials.map(material => ({
            ...material,
            course_name: course.name
          }));
          allMaterials.push(...materialsWithCourseName);
        }
      } catch (error) {
        console.error(`获取课程 ${course.id} 的材料失败:`, error);
      }
    }
    
    // 如果API返回的材料为空，使用模拟数据
    if (allMaterials.length === 0) {
      console.warn('未找到材料数据，使用模拟数据');
      knowledgeItems.value = [
        {
          id: 1,
          title: '机器学习基础概念',
          material_type: '文档',
          course_name: '人工智能基础',
          size: '2.5MB',
          created_at: '2025-05-15'
        },
        {
          id: 2,
          title: '深度学习简介',
          material_type: '视频',
          course_name: '人工智能基础',
          size: '45MB',
          created_at: '2025-06-01'
        },
        {
          id: 3,
          title: '微积分基础',
          material_type: '文档',
          course_name: '高等数学',
          size: '1.8MB',
          created_at: '2025-04-20'
        }
      ];
    } else {
      // 按上传时间降序排序，最新的在最上面
      knowledgeItems.value = allMaterials.sort((a, b) => {
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      });
    }
    
    // 更新统计数据
    updateStats();
  } catch (error) {
    console.error('获取知识库资料列表失败:', error);
    // 出错时使用模拟数据
    knowledgeItems.value = [
      {
        id: 1,
        title: '机器学习基础概念',
        material_type: '文档',
        course_name: '人工智能基础',
        size: '2.5MB',
        created_at: '2025-05-15'
      },
      {
        id: 2,
        title: '深度学习简介',
        material_type: '视频',
        course_name: '人工智能基础',
        size: '45MB',
        created_at: '2025-06-01'
      },
      {
        id: 3,
        title: '微积分基础',
        material_type: '文档',
        course_name: '高等数学',
        size: '1.8MB',
        created_at: '2025-04-20'
      }
    ];
  } finally {
    materialsLoading.value = false;
  }
}

async function fetchKnowledgeStats() {
  try {
    // 实际项目中应该调用API获取数据
    // const response = await ragAiAPI.getKnowledgeBaseStatus();
    // stats.totalDocuments = response.totalDocuments;
    // ...
    
    // 更新统计数据
    updateStats();
  } catch (error) {
    console.error('获取知识库统计数据失败:', error);
  }
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    importForm.file = target.files[0];
    if (!importForm.title) {
      importForm.title = importForm.file.name;
    }
  }
}

async function importMaterial() {
  if (!importForm.file || !importForm.courseId) return;
  
  importing.value = true;
  importError.value = '';
  importProgress.value = 10;
  
  try {
    // 创建FormData对象
    const formData = new FormData();
    formData.append('file', importForm.file);
    formData.append('title', importForm.title || importForm.file.name);
    
    importProgress.value = 30;
    
    // 调用API上传课件
    const response = await materialAPI.uploadMaterial(Number(importForm.courseId), formData);
    
    importProgress.value = 80;
    
    // 关闭模态框
    showImportModal.value = false;
    
    // 获取新上传的资料信息
    const newMaterial = response.material || {
      id: Date.now(), // 临时ID
      title: importForm.title || importForm.file.name,
      material_type: getMaterialTypeFromFileName(importForm.file.name),
      size: formatFileSize(importForm.file.size),
      course_id: Number(importForm.courseId),
      created_at: new Date().toISOString()
    };
    
    // 添加课程名称
    const course = courses.value.find(c => c.id === Number(importForm.courseId));
    newMaterial.course_name = course ? course.name : '未知课程';
    
    // 将新资料添加到列表最前面
    knowledgeItems.value.unshift(newMaterial);
    
    // 更新统计数据
    updateStats();
    
    // 重置表单
    importForm.title = '';
    importForm.file = null;
    importProgress.value = 0;
    
    // 显示成功提示
    alert('课件上传成功！');
  } catch (error) {
    console.error('上传课件失败:', error);
    importError.value = '上传失败，请重试';
    importProgress.value = 0;
  } finally {
    importing.value = false;
  }
}

function getMaterialTypeFromFileName(fileName: string) {
  const extension = fileName.split('.').pop()?.toLowerCase();
  if (!extension) return '文档';
  
  if (['pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'xls', 'xlsx'].includes(extension)) {
    return '文档';
  } else if (['mp4', 'avi', 'mov', 'wmv', 'flv'].includes(extension)) {
    return '视频';
  } else if (['mp3', 'wav', 'ogg', 'flac'].includes(extension)) {
    return '音频';
  } else if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg'].includes(extension)) {
    return '图片';
  }
  
  return '文档';
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) return bytes + 'B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB';
  return (bytes / (1024 * 1024)).toFixed(1) + 'MB';
}

function getMaterialIcon(materialType: string) {
  const type = materialType.toLowerCase();
  switch (type) {
    case 'pdf':
    case '文档':
      return `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      `;
    case 'video':
    case '视频':
      return `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      `;
    case 'audio':
    case '音频':
      return `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
        </svg>
      `;
    case 'image':
    case '图片':
      return `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      `;
    default:
      return `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      `;
  }
}

async function searchKnowledge() {
  if (!searchQuery.value.trim()) return;
  
  searching.value = true;
  hasSearched.value = true;
  
  try {
    // 这里应该调用API搜索知识库
    // const response = await ragAiAPI.searchKnowledgeBase({
    //   query: searchQuery.value,
    //   course_id: searchFilters.courseId,
    //   material_type: searchFilters.materialType,
    //   limit: parseInt(searchFilters.limit)
    // });
    
    // 模拟API响应
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // 模拟搜索结果
    if (searchQuery.value.toLowerCase().includes('机器学习')) {
      searchResults.value = [
        {
          title: '机器学习基础概念',
          content: '机器学习是人工智能的一个分支，它使计算机能够在没有明确编程的情况下学习和改进。机器学习算法通过使用数学模型从样本数据中学习，这些模型可以用来做预测或决策...',
          course_name: '人工智能基础',
          material_type: '文档',
          date: '2025-05-15',
          relevance: 0.95,
          url: '#'
        },
        {
          title: '监督学习与无监督学习',
          content: '监督学习是指从标记的训练数据中学习的机器学习任务。无监督学习是指从未标记的数据中找出模式的机器学习任务...',
          course_name: '人工智能基础',
          material_type: '文档',
          date: '2025-05-20',
          relevance: 0.85,
          url: '#'
        },
        {
          title: '深度学习简介',
          content: '深度学习是机器学习的一个子领域，它使用多层神经网络来模拟人脑的工作方式。深度学习在图像识别、自然语言处理等领域取得了突破性进展...',
          course_name: '人工智能基础',
          material_type: '视频',
          date: '2025-06-01',
          relevance: 0.75,
          url: '#'
        }
      ];
    } else {
      searchResults.value = [];
    }
  } catch (error) {
    console.error('搜索知识库失败:', error);
    searchResults.value = [];
  } finally {
    searching.value = false;
  }
}

function previewMaterial(materialId: number) {
  // 实际项目中应该跳转到预览页面或打开预览模态框
  console.log('预览资料:', materialId);
}

function downloadMaterial(materialId: number) {
  materialAPI.downloadMaterial(materialId);
}
</script> 