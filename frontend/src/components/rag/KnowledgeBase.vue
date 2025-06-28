<template>
  <div class="knowledge-base">
    <div class="mb-6 flex justify-between items-center">
      <h2 class="text-2xl font-bold">知识库管理</h2>
      <button 
        @click="showImportModal = true"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
      >
        导入资料
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
    
    <!-- 导入资料模态框 -->
    <div v-if="showImportModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-lg">
        <h3 class="text-xl font-bold mb-4">导入资料到知识库</h3>
        
        <form @submit.prevent="importMaterial" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">选择课程</label>
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
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">资料类型</label>
            <select 
              v-model="importForm.materialType" 
              required
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="document">文档</option>
              <option value="video">视频</option>
              <option value="audio">音频</option>
              <option value="image">图片</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">上传文件</label>
            <div class="border-2 border-dashed border-gray-300 rounded-md p-6">
              <div class="text-center">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="mt-1 text-sm text-gray-600">
                  拖放文件到这里，或者
                  <span class="text-blue-600 hover:text-blue-500 cursor-pointer">浏览文件</span>
                </p>
                <p class="mt-1 text-xs text-gray-500">
                  支持 PDF, DOCX, TXT, MP4, MP3 等格式
                </p>
              </div>
              <input type="file" class="hidden" />
            </div>
          </div>
          
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
              <span v-if="!importing">导入</span>
              <span v-else class="flex items-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                导入中
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';

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
const importForm = reactive({
  courseId: '',
  materialType: 'document'
});

// 模拟数据
const courses = ref([
  { id: 1, name: '人工智能基础' },
  { id: 2, name: '高等数学' },
  { id: 3, name: '英语写作' }
]);

const stats = reactive({
  totalDocuments: 156,
  totalCourses: 8,
  lastUpdated: '2025-06-24',
  typeDistribution: {
    document: 60,
    video: 20,
    audio: 15,
    image: 5
  }
});

onMounted(async () => {
  // 这里可以调用API获取知识库统计数据
  await fetchKnowledgeStats();
});

async function fetchKnowledgeStats() {
  try {
    // 实际项目中应该调用API获取数据
    // const response = await api.getKnowledgeBaseStats();
    // stats.totalDocuments = response.totalDocuments;
    // ...
    
    // 模拟API调用延迟
    await new Promise(resolve => setTimeout(resolve, 500));
  } catch (error) {
    console.error('获取知识库统计数据失败:', error);
  }
}

async function searchKnowledge() {
  if (!searchQuery.value.trim()) return;
  
  searching.value = true;
  hasSearched.value = true;
  
  try {
    // 这里应该调用API搜索知识库
    // const response = await api.searchKnowledgeBase({
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

async function importMaterial() {
  importing.value = true;
  
  try {
    // 这里应该调用API导入资料
    // const formData = new FormData();
    // formData.append('file', file);
    // formData.append('course_id', importForm.courseId);
    // formData.append('material_type', importForm.materialType);
    // await api.importKnowledgeBase(formData);
    
    // 模拟API调用延迟
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 关闭模态框
    showImportModal.value = false;
    
    // 更新知识库统计
    await fetchKnowledgeStats();
  } catch (error) {
    console.error('导入资料失败:', error);
  } finally {
    importing.value = false;
  }
}
</script> 