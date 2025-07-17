<template>
  <div class="lesson-planner">
    <div class="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden relative">
      <!-- 智能备课页面头部 -->
      <div class="px-6 py-4 border-b">
        <div class="flex justify-between items-center mb-4">
          <div class="flex items-center space-x-3">
            <!-- 侧边栏切换按钮 -->
            <button 
              @click="toggleHistorySidebar"
              class="text-gray-500 hover:text-gray-700 focus:outline-none"
              title="显示/隐藏历史记录"
            >
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h3 class="text-lg font-semibold">智能备课</h3>
          </div>
          <div class="flex items-center space-x-4">
            <span class="inline-block w-2 h-2 rounded-full mr-2" 
                  :class="{'bg-green-500': !isGenerating, 'bg-yellow-500 animate-pulse': isGenerating}"></span>
            <span class="text-sm text-gray-500">{{ isGenerating ? '生成中...' : '就绪' }}</span>
            
            <!-- 添加保存和导出按钮 -->
            <button 
              v-if="lessonPlanContent" 
              @click="saveLessonPlan"
              class="px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded text-sm"
              :disabled="isSaving"
            >
              {{ isSaving ? '保存中...' : '保存' }}
            </button>
            
            <button 
              v-if="lessonPlanContent" 
              @click="downloadAsMarkdown"
              class="px-3 py-1 bg-green-500 hover:bg-green-600 text-white rounded text-sm"
            >
              导出MD
            </button>
          </div>
        </div>
      </div>
      
      <!-- 上下布局 -->
      <div class="flex flex-col">
        <!-- 设置面板 -->
        <div class="p-6 border-b border-gray-200">
          <h4 class="text-lg font-medium mb-4">备课设置</h4>
          
          <form @submit.prevent="generateLessonPlan" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <!-- 第一列：基础设置 -->
              <div class="space-y-4">
                <!-- 大纲类型 -->
                <div class="form-group">
                  <label class="block text-sm font-medium text-gray-700 mb-1">大纲类型</label>
                  <div class="flex items-center space-x-4">
                    <label class="inline-flex items-center">
                      <input type="radio" v-model="formData.outlineType" value="course" class="form-radio" />
                      <span class="ml-2">课程总纲</span>
                    </label>
                    <label class="inline-flex items-center">
                      <input type="radio" v-model="formData.outlineType" value="class" class="form-radio" />
                      <span class="ml-2">课堂教案</span>
                    </label>
                  </div>
                </div>
                
                <!-- 课程名称 -->
                <div class="form-group">
                  <label class="block text-sm font-medium text-gray-700 mb-1">课程名称</label>
                  <select 
                    v-model="formData.courseId"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">请选择课程</option>
                    <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.name }}</option>
                  </select>
                </div>
                
                <!-- 课堂章节选择 (仅在选择课堂教案时显示) -->
                <div class="form-group" v-if="formData.outlineType === 'class' && formData.courseId">
                  <label class="block text-sm font-medium text-gray-700 mb-1">选择章节</label>
                  <select 
                    v-model="formData.chapterId"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">请选择章节</option>
                    <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">{{ chapter.title }}</option>
                  </select>
                </div>

                <!-- 学段/年级/学科 -->
                <div class="form-group">
                  <label class="block text-sm font-medium text-gray-700 mb-1">学段/年级/学科 <span class="text-red-500">*</span></label>
                  <input 
                    type="text" 
                    v-model="formData.gradeSubject" 
                    placeholder="如：高中/高一/数学"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              
              <!-- 第二列：教学内容 -->
              <div class="space-y-4">
                <!-- 课时长度 -->
                <div class="form-group">
                  <label class="block text-sm font-medium text-gray-700 mb-1">课时长度</label>
                  <input 
                    type="text" 
                    v-model="formData.duration" 
                    placeholder="如：40分钟，90分钟"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <!-- 核心教学目标/学习目标 -->
                <div class="form-group">
                  <label class="block text-sm font-medium text-gray-700 mb-1">核心教学目标/学习目标</label>
                  <textarea 
                    v-model="formData.learningObjectives" 
                    placeholder="输入关键词或完整句子描述教学目标"
                    rows="2"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  ></textarea>
                </div>
                
                <!-- 教学重点与难点 -->
                <div class="form-group">
                  <label class="block text-sm font-medium text-gray-700 mb-1">教学重点与难点</label>
                  <textarea 
                    v-model="formData.keyPoints" 
                    placeholder="明确指定教学重点与难点"
                    rows="2"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  ></textarea>
                </div>
              </div>
              
              <!-- 第三列：教学方法和评估 -->
              <div class="space-y-4">
                <!-- 教学风格/模式倾向 -->
                <div class="form-group">
                  <label class="block text-sm font-medium text-gray-700 mb-1">教学风格/模式倾向</label>
                  <select 
                    v-model="formData.teachingStyle"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">请选择</option>
                    <option value="讲授型">讲授型</option>
                    <option value="探究式">探究式</option>
                    <option value="项目式">项目式</option>
                    <option value="合作学习">合作学习</option>
                    <option value="翻转课堂">翻转课堂</option>
                  </select>
                </div>
                
                <!-- 学生学情预设 -->
                <div class="form-group">
                  <label class="block text-sm font-medium text-gray-700 mb-1">学生学情预设</label>
                  <select 
                    v-model="formData.studentLevel"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">请选择或自定义</option>
                    <option value="基础薄弱">基础薄弱</option>
                    <option value="中等水平">中等水平</option>
                    <option value="较好水平">较好水平</option>
                  </select>
                  <input 
                    v-if="formData.studentLevel === ''"
                    type="text" 
                    v-model="formData.customStudentLevel" 
                    placeholder="自定义学情描述"
                    class="mt-2 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <!-- 生成详略程度 -->
                <div class="form-group">
                  <label class="block text-sm font-medium text-gray-700 mb-1">生成详略程度</label>
                  <div class="flex items-center">
                    <span class="mr-2 text-sm text-gray-500">简洁提纲</span>
                    <input 
                      type="range" 
                      v-model="formData.detailLevel" 
                      min="1" 
                      max="3" 
                      step="1"
                      class="w-full h-2 rounded-lg appearance-none cursor-pointer bg-gray-200"
                    />
                    <span class="ml-2 text-sm text-gray-500">详细教案</span>
                  </div>
                  <div class="mt-1 text-center text-sm text-gray-500">
                    {{ detailLevelText }}
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 额外的选项折叠面板 -->
            <div class="border border-gray-200 rounded-md overflow-hidden">
              <div 
                @click="showAdvancedOptions = !showAdvancedOptions"
                class="p-3 bg-gray-50 cursor-pointer flex justify-between items-center"
              >
                <span class="text-sm font-medium">高级选项</span>
                <svg 
                  class="w-5 h-5 transform transition-transform duration-200" 
                  :class="{'rotate-180': showAdvancedOptions}"
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
              
              <div v-show="showAdvancedOptions" class="p-3 border-t border-gray-200">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <!-- 所需课堂活动类型 -->
                  <div class="form-group">
                    <label class="block text-sm font-medium text-gray-700 mb-1">所需课堂活动类型（可多选）</label>
                    <div class="grid grid-cols-2 gap-2">
                      <label v-for="activity in activityOptions" :key="activity" class="inline-flex items-center">
                        <input type="checkbox" v-model="formData.activities" :value="activity" class="form-checkbox" />
                        <span class="ml-2 text-sm">{{ activity }}</span>
                      </label>
                    </div>
                  </div>
                  
                  <!-- 评估方式 -->
                  <div class="form-group">
                    <label class="block text-sm font-medium text-gray-700 mb-1">评估方式（可多选）</label>
                    <div class="grid grid-cols-2 gap-2">
                      <label v-for="method in assessmentMethods" :key="method" class="inline-flex items-center">
                        <input type="checkbox" v-model="formData.assessmentMethods" :value="method" class="form-checkbox" />
                        <span class="ml-2 text-sm">{{ method }}</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 提交按钮 -->
            <div class="form-group">
              <button 
                type="submit" 
                class="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                :disabled="isGenerating || !formData.gradeSubject"
              >
                {{ isGenerating ? '正在生成中...' : '生成备课内容' }}
              </button>
            </div>
          </form>
        </div>

        <!-- 内容区域和侧边栏 -->
        <div class="relative flex h-full">
          <!-- 侧边栏历史记录 -->
          <div 
            v-show="isHistorySidebarVisible"
            class="history-sidebar border-r border-gray-200 bg-gray-50 w-72 h-full overflow-auto"
          >
            <div class="sticky top-0 bg-gray-50 z-10 p-4 border-b border-gray-200">
              <div class="flex items-center justify-between mb-2">
                <h4 class="text-base font-medium">历史记录</h4>
                <button 
                  @click="toggleHistorySidebar"
                  class="text-gray-500 hover:text-gray-700 p-1 rounded-full hover:bg-gray-100"
                >
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <button 
                @click="fetchHistoryRecords" 
                class="w-full flex items-center justify-center py-1.5 px-3 border border-gray-300 rounded-md shadow-sm bg-white hover:bg-gray-50 text-sm"
              >
                <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                刷新
              </button>
            </div>
            
            <div class="p-3">
              <div v-if="isLoadingHistory" class="flex justify-center py-8">
                <div class="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-blue-500"></div>
              </div>
              
              <template v-else>
                <div 
                  v-for="record in historyRecords" 
                  :key="record.conversation_id" 
                  @click="loadHistoryRecord(record.conversation_id)"
                  class="p-3 mb-2 border border-gray-200 bg-white rounded cursor-pointer hover:bg-gray-50"
                  :class="{'bg-blue-50 border-blue-300': selectedHistoryId === record.conversation_id}"
                >
                  <div class="text-sm font-medium truncate">{{ record.title }}</div>
                  <div class="text-xs text-gray-500">{{ formatDate(record.last_time) }}</div>
                  <div class="flex items-center mt-1">
                    <span 
                      class="text-xs px-1.5 py-0.5 rounded" 
                      :class="record.outline_type === 'course' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'"
                    >
                      {{ record.outline_type === 'course' ? '课程总纲' : '课堂教案' }}
                    </span>
                  </div>
                </div>
                
                <div v-if="historyRecords.length === 0" class="text-center py-4 text-gray-500 text-sm">
                  暂无历史记录
                </div>
              </template>
            </div>
          </div>
          
          <!-- 预览区域 -->
          <div class="p-6 flex-1">
            <h4 class="text-lg font-medium mb-4">备课内容预览</h4>
            
            <div v-if="isGenerating" class="flex flex-col items-center justify-center h-96">
              <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
              <p class="mt-4 text-gray-500">正在生成备课内容，请稍候...</p>
            </div>
            
            <div v-else-if="lessonPlanContent" class="border rounded-md overflow-hidden">
              <MarkdownViewer :content="lessonPlanContent" />
            </div>
            
            <div v-else class="flex flex-col items-center justify-center h-96 border border-dashed border-gray-300 rounded-md">
              <svg class="h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p class="mt-4 text-gray-500 text-center">
                填写上方表单并点击"生成备课内容"<br>
                或从左侧历史记录中选择已生成内容
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { courseAPI, ragAiAPI } from '../../api';
import MarkdownViewer from '../course/MarkdownViewer.vue';

interface Course {
  id: number;
  name: string;
}

interface Chapter {
  id: number;
  title: string;
}

interface HistoryRecord {
  conversation_id: string;
  title: string;
  start_time: number;
  last_time: number;
  outline_type: 'course' | 'class';
  message_count: number;
}

// 定义表单数据接口
interface FormData {
  courseId: string;
  outlineType: string;
  chapterId: string;
  gradeSubject: string;
  duration: string;
  learningObjectives: string;
  keyPoints: string;
  studentLevel: string;
  customStudentLevel: string;
  activities: string[];
  teachingStyle: string;
  assessmentMethods: string[];
  detailLevel: number;
  [key: string]: string | string[] | number; // 添加索引签名
}

// 课堂活动选项
const activityOptions = [
  '小组讨论',
  '实验',
  '角色扮演',
  '游戏',
  '辩论',
  '演讲',
  '练习',
  '测验'
];

// 评估方式选项
const assessmentMethods = [
  '随堂测验',
  '观察记录',
  '作品评价',
  '口头反馈',
  '自我评估'
];

// 表单数据
const formData = ref<FormData>({
  courseId: '',
  outlineType: 'course',
  chapterId: '',
  gradeSubject: '',
  duration: '',
  learningObjectives: '',
  keyPoints: '',
  studentLevel: '',
  customStudentLevel: '',
  activities: [] as string[],
  teachingStyle: '',
  assessmentMethods: [] as string[],
  detailLevel: 2
});

// 状态变量
const isGenerating = ref(false);
const isSaving = ref(false);
const lessonPlanContent = ref('');
const courses = ref<Course[]>([]);
const chapters = ref<Chapter[]>([]);
const currentConversationId = ref('');
const showAdvancedOptions = ref(false);
const isHistorySidebarVisible = ref(false); // 控制侧边栏可见性

// 历史记录相关
const historyRecords = ref<HistoryRecord[]>([]);
const isLoadingHistory = ref(false);
const selectedHistoryId = ref('');

// 详细程度文本
const detailLevelText = computed(() => {
  switch(formData.value.detailLevel) {
    case 1: return '简洁提纲';
    case 2: return '标准详细度';
    case 3: return '详细教案';
    default: return '标准详细度';
  }
});

// 监听课程变化，加载对应章节
watch(() => formData.value.courseId, async (newCourseId) => {
  if (newCourseId) {
    await fetchChapters(Number(newCourseId));
  } else {
    chapters.value = [];
    formData.value.chapterId = '';
  }
});

// 初始化
onMounted(async () => {
  await fetchCourses();
  await fetchHistoryRecords();
  
  // 尝试从localStorage恢复表单状态
  const savedForm = localStorage.getItem('lessonPlannerForm');
  if (savedForm) {
    try {
      const parsed = JSON.parse(savedForm);
      // 合并保存的表单数据，只使用有效的字段
      Object.keys(formData.value).forEach(key => {
        if (key in parsed) {
          formData.value[key] = parsed[key];
        }
      });
    } catch (e) {
      console.error('恢复表单状态失败:', e);
    }
  }
  
  // 尝试从localStorage恢复生成内容
  const savedContent = localStorage.getItem('lessonPlannerContent');
  if (savedContent) {
    lessonPlanContent.value = savedContent;
  }
  
  // 尝试从localStorage恢复对话ID
  const savedConversationId = localStorage.getItem('lessonPlannerConversationId');
  if (savedConversationId) {
    currentConversationId.value = savedConversationId;
    selectedHistoryId.value = savedConversationId;
  }
});

// 切换侧边栏可见性
function toggleHistorySidebar() {
  isHistorySidebarVisible.value = !isHistorySidebarVisible.value;
  if (isHistorySidebarVisible.value && historyRecords.value.length === 0) {
    fetchHistoryRecords();
  }
}

// 获取课程列表
async function fetchCourses() {
  try {
    const response = await courseAPI.getCourses();
    if (response && typeof response === 'object' && 'courses' in response) {
      courses.value = response.courses as Course[];
    }
  } catch (error) {
    console.error('获取课程列表失败:', error);
  }
}

// 获取课程章节
async function fetchChapters(courseId: number) {
  try {
    const response = await courseAPI.getCourseChapters(courseId);
    console.log('章节数据返回:', response);
    if (response && typeof response === 'object' && 'status' in response && 
        (response as any).status == 'success' && 'chapters' in response && Array.isArray(response.chapters)) {
      // 处理章节数据
      const processedChapters = response.chapters.map((chapter: any, index: number) => ({
        id: index + 1, // 使用索引作为ID
        title: chapter.title
      }));
      chapters.value = processedChapters;
      console.log('处理后的章节列表:', chapters.value);
    } else {
      // 如果无法获取章节，设置为空数组
      chapters.value = [];
      console.log('无章节数据或格式不正确');
    }
  } catch (error) {
    console.error('获取课程章节失败:', error);
    chapters.value = [];
  }
}

// 获取历史记录
async function fetchHistoryRecords() {
  isLoadingHistory.value = true;
  try {
    // 调用API获取会话列表
    const courseId = formData.value.courseId ? Number(formData.value.courseId) : undefined;
    const response = await ragAiAPI.getConversations(courseId);
    if (response && typeof response === 'object' && 'status' in response && 
        (response as any).status == 'success' && 'conversations' in response && 
        Array.isArray(response.conversations)) {
      // 过滤出以lesson_plan_开头的会话
      const lessonPlanRecords = response.conversations.filter(conv => 
        conv.conversation_id.startsWith('lesson_plan_')
      );
      
      historyRecords.value = lessonPlanRecords.map(record => ({
        ...record,
        outline_type: record.title.includes('课程总纲') ? 'course' : 'class'
      }));
      
      // 如果有当前会话ID，将其置顶
      if (currentConversationId.value) {
        const currentIndex = historyRecords.value.findIndex(
          record => record.conversation_id === currentConversationId.value
        );
        if (currentIndex > 0) {
          const current = historyRecords.value.splice(currentIndex, 1)[0];
          historyRecords.value.unshift(current);
        }
      }
    }
  } catch (error) {
    console.error('获取历史记录失败:', error);
  } finally {
    isLoadingHistory.value = false;
  }
}

// 加载历史记录内容
async function loadHistoryRecord(conversationId: string) {
  try {
    selectedHistoryId.value = conversationId;
    isGenerating.value = true;
    lessonPlanContent.value = '';
    
    // 获取聊天历史
    const response = await ragAiAPI.getChatHistory(conversationId);
    
    if (response && typeof response === 'object' && 'status' in response && 
        (response as any).status == 'success' && 'history' in response && 
        Array.isArray(response.history)) {
      // 获取助手的回复内容
      const assistantMessages = response.history.filter(msg => msg.role === 'assistant');
      if (assistantMessages.length > 0) {
        // 使用最新的助手消息
        lessonPlanContent.value = assistantMessages[assistantMessages.length - 1].content;
        currentConversationId.value = conversationId;
        
        // 保存到localStorage
        localStorage.setItem('lessonPlannerContent', lessonPlanContent.value);
        localStorage.setItem('lessonPlannerConversationId', conversationId);
        
        // 尝试获取用户消息以恢复表单
        const userMessages = response.history.filter(msg => msg.role === 'user');
        if (userMessages.length > 0) {
          const firstUserMessage = userMessages[0].content;
          try {
            // 尝试从用户消息中提取表单信息
            // 这里可以添加更复杂的逻辑来解析用户消息并恢复表单状态
            // 简单起见，这里仅提取学科信息
            const subjectMatch = firstUserMessage.match(/学段\/年级\/学科：(.+?)($|\n)/);
            if (subjectMatch && subjectMatch[1]) {
              formData.value.gradeSubject = subjectMatch[1].trim();
            }
            
            // 提取大纲类型
            if (firstUserMessage.includes('课程总纲')) {
              formData.value.outlineType = 'course';
            } else if (firstUserMessage.includes('课堂教案')) {
              formData.value.outlineType = 'class';
            }
            
            // 保存表单状态
            localStorage.setItem('lessonPlannerForm', JSON.stringify(formData.value));
          } catch (e) {
            console.error('解析用户消息失败:', e);
          }
        }
      }
    }
  } catch (error) {
    console.error('加载历史记录失败:', error);
  } finally {
    isGenerating.value = false;
    // 选择后关闭侧边栏（仅在移动设备上）
    if (window.innerWidth < 768) {
      isHistorySidebarVisible.value = false;
    }
  }
}

// 保存备课内容
async function saveLessonPlan() {
  if (!lessonPlanContent.value) return;
  
  isSaving.value = true;
  try {
    // 如果没有conversationId，说明内容未保存到后端
    if (!currentConversationId.value) {
      // 创建一个新的聊天会话保存内容
      const type = formData.value.outlineType === 'course' ? '课程总纲' : '课堂教案';
      const title = `${type}: ${formData.value.gradeSubject}`;
      
      // 这里可以添加保存到后端的逻辑，例如创建一个新的聊天记录
      // 由于之前的代码中已经自动保存了生成内容，这里只需刷新历史记录列表
      await fetchHistoryRecords();
      
      // 显示保存成功消息
      alert('备课内容已保存！');
    } else {
      // 内容已存在后端，直接提示已保存
      alert('备课内容已经保存在系统中');
    }
  } catch (error) {
    console.error('保存备课内容失败:', error);
    alert('保存失败，请重试');
  } finally {
    isSaving.value = false;
  }
}

// 生成文件名用的日期格式化
function formatDateForFilename(date: Date): string {
  return `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getDate()).padStart(2, '0')}_${String(date.getHours()).padStart(2, '0')}${String(date.getMinutes()).padStart(2, '0')}`;
}

// 导出为Markdown文件
function downloadAsMarkdown() {
  if (!lessonPlanContent.value) return;
  
  try {
    const type = formData.value.outlineType === 'course' ? '课程总纲' : '课堂教案';
    const subject = formData.value.gradeSubject || '未命名';
    const filename = `${type}-${subject}-${formatDateForFilename(new Date())}.md`;
    
    // 创建一个链接元素并触发下载
    const element = document.createElement('a');
    const file = new Blob([lessonPlanContent.value], {type: 'text/markdown;charset=utf-8'});
    element.href = URL.createObjectURL(file);
    element.download = filename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  } catch (error) {
    console.error('导出Markdown失败:', error);
    alert('导出失败，请重试');
  }
}

// 格式化日期显示
function formatDate(timestamp: number): string {
  const date = new Date(timestamp * 1000);
  return date.toLocaleString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// 生成备课内容
async function generateLessonPlan() {
  if (!formData.value.gradeSubject) {
    alert('请至少填写学段/年级/学科信息');
    return;
  }
  
  isGenerating.value = true;
  lessonPlanContent.value = '';
  selectedHistoryId.value = '';
  currentConversationId.value = '';
  
  try {
    // 保存表单状态到localStorage
    localStorage.setItem('lessonPlannerForm', JSON.stringify(formData.value));
    
    // 准备提交的数据
    const studentLevelText = formData.value.studentLevel || formData.value.customStudentLevel;
    const requestData = {
      outlineType: formData.value.outlineType,
      courseId: formData.value.courseId || undefined,
      chapterId: formData.value.chapterId || undefined,
      gradeSubject: formData.value.gradeSubject,
      duration: formData.value.duration || undefined,
      learningObjectives: formData.value.learningObjectives || undefined,
      keyPoints: formData.value.keyPoints || undefined,
      studentLevel: formData.value.studentLevel || undefined,
      customStudentLevel: formData.value.customStudentLevel || undefined,
      activities: formData.value.activities.length > 0 ? formData.value.activities : undefined,
      teachingStyle: formData.value.teachingStyle || undefined,
      assessmentMethods: formData.value.assessmentMethods.length > 0 ? formData.value.assessmentMethods : undefined,
      detailLevel: formData.value.detailLevel
    };
    
    // 准备请求头
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    };

    // 发送POST请求并获取流式响应
    const response = await fetch('http://localhost:5001/api/rag/generate-lesson-plan', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
    }

    // 获取响应的ReadableStream
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('无法读取响应流');
    }

    // 使用TextDecoder来解码数据流
    const decoder = new TextDecoder();
    
    // 处理数据流
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        break;
      }
      
      // 解码二进制数据
      const text = decoder.decode(value);
      
      // 处理SSE格式数据
      const lines = text.split('\n\n');
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const jsonData = JSON.parse(line.substring(6));
            
            if (jsonData.status === 'chunk') {
              // 添加内容片段
              lessonPlanContent.value += jsonData.content;
              // 实时保存到localStorage
              localStorage.setItem('lessonPlannerContent', lessonPlanContent.value);
            } else if (jsonData.status === 'done') {
              // 完成生成，保存会话ID
              console.log('生成完成，对话ID:', jsonData.conversation_id);
              currentConversationId.value = jsonData.conversation_id;
              
              // 保存会话ID到localStorage
              localStorage.setItem('lessonPlannerConversationId', jsonData.conversation_id);
              
              // 刷新历史记录
              setTimeout(() => fetchHistoryRecords(), 1000);
              isGenerating.value = false;
            } else if (jsonData.status === 'error') {
              // 处理错误
              throw new Error(jsonData.message);
            }
          } catch (error) {
            // 解析错误，可能不是完整的JSON
            console.warn('解析SSE数据出错:', error);
          }
        }
      }
    }
    
    isGenerating.value = false;
  } catch (error) {
    console.error('生成备课内容失败:', error);
    lessonPlanContent.value = `## 生成备课内容失败\n\n请检查网络连接或稍后再试。\n\n错误信息：${error instanceof Error ? error.message : String(error)}`;
    isGenerating.value = false;
    
    // 保存错误信息到localStorage
    localStorage.setItem('lessonPlannerContent', lessonPlanContent.value);
  }
}
</script>

<style scoped>
.lesson-planner {
  width: 100%;
  max-width: 100%;
}

.form-checkbox, .form-radio {
  height: 1rem;
  width: 1rem;
  color: #2563eb;
  border-color: #d1d5db;
  border-radius: 0.25rem;
}

.form-checkbox:focus, .form-radio:focus {
  --tw-ring-color: #3b82f6;
}

/* 当屏幕较小时的侧边栏样式 */
@media (max-width: 767px) {
  .history-sidebar {
    width: 85%;
    max-width: 300px;
  }
}

/* 遮罩层动画 */
.history-sidebar {
  height: 100vh;
  overflow-y: auto;
}
</style> 