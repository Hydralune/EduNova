<template>
  <div class="learning-analytics">
    <h2 class="text-2xl font-bold mb-6">学习分析</h2>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center items-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      <span class="ml-3 text-gray-600">加载中...</span>
    </div>
    
    <div v-else>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <!-- 学习进度 -->
        <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold">整体学习进度</h3>
            <span class="text-2xl font-bold text-blue-600">{{ overallProgress }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-3 mb-2">
            <div class="bg-blue-600 h-3 rounded-full" :style="`width: ${overallProgress}%`"></div>
          </div>
          <div class="flex justify-between text-sm text-gray-500">
            <span>开始</span>
            <span>完成</span>
          </div>
        </div>
        
        <!-- 学习时间 -->
        <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold">本周学习时间</h3>
            <span class="text-2xl font-bold text-green-600">{{ weeklyLearningTime }}小时</span>
          </div>
          <div class="flex items-center">
            <span class="text-sm text-gray-500 mr-2">上周：</span>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-green-600 h-2 rounded-full" :style="`width: ${(previousWeekTime / 10) * 100}%`"></div>
            </div>
            <span class="text-sm text-gray-500 ml-2">{{ previousWeekTime }}小时</span>
          </div>
        </div>
        
        <!-- 完成课程 -->
        <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold">课程完成情况</h3>
          </div>
          <CoursePieChart 
            :completed="completedCourses" 
            :in-progress="inProgressCourses" 
            :not-started="notStartedCourses" 
          />
        </div>
      </div>
      
      <!-- 学习趋势图 -->
      <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">学习趋势</h3>
          <div class="flex items-center">
            <button 
              v-for="period in trendPeriods" 
              :key="period.value"
              @click="selectedTrendPeriod = period.value"
              class="px-2 py-1 text-sm rounded-md mr-1"
              :class="selectedTrendPeriod === period.value ? 'bg-blue-100 text-blue-800' : 'text-gray-500 hover:bg-gray-100'"
            >
              {{ period.label }}
            </button>
          </div>
        </div>
        
        <LearningTrendChart :data="trendData" :title="`${selectedTrendPeriod}学习时长`" />
      </div>
      
      <!-- 知识点掌握情况 -->
      <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">知识点掌握情况</h3>
          <div class="flex items-center">
            <select 
              v-model="selectedCourseId" 
              class="border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">所有课程</option>
              <option v-for="course in courseDetails" :key="course.id" :value="course.id">
                {{ course.name }}
              </option>
            </select>
          </div>
        </div>
        
        <KnowledgeRadarChart :data="knowledgePointsData" />
      </div>
      
      <!-- AI学习建议 -->
      <div class="mb-6">
        <AIAnalysisPanel :user-id="props.userId" :course-id="selectedCourseId" />
      </div>
      
      <!-- 课程详情 -->
      <div class="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
        <div class="px-6 py-4 border-b">
          <h3 class="text-lg font-semibold">课程学习详情</h3>
        </div>
        
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">课程名称</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">进度</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">学习时间</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">最后学习</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">评分</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="course in courseDetails" :key="course.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-8 w-8 rounded bg-gray-200"></div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900">{{ course.name }}</div>
                      <div class="text-xs text-gray-500">{{ course.category }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="w-full bg-gray-200 rounded-full h-2.5 max-w-[150px]">
                    <div class="bg-blue-600 h-2.5 rounded-full" :style="`width: ${course.progress}%`"></div>
                  </div>
                  <div class="text-xs text-gray-500 mt-1">{{ course.progress }}%</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ course.learningTime }}小时
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ course.lastActivity }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <span class="text-sm font-medium text-gray-900 mr-2">{{ course.score }}</span>
                    <div class="flex">
                      <svg v-for="i in 5" :key="i" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" :class="i <= Math.round(course.score / 20) ? 'text-yellow-400' : 'text-gray-300'" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
                      </svg>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import LearningTrendChart from './LearningTrendChart.vue';
import CoursePieChart from './CoursePieChart.vue';
import KnowledgeRadarChart from './KnowledgeRadarChart.vue';
import AIAnalysisPanel from './AIAnalysisPanel.vue'; // Added import for AIAnalysisPanel
import { analyticsAPI } from '@/api';

const props = defineProps({
  userId: {
    type: [Number, String],
    required: true
  }
});

// 加载状态
const loading = ref(true);

// 数据
const overallProgress = ref(68);
const weeklyLearningTime = ref(7.5);
const previousWeekTime = ref(5.2);
const completedCourses = ref(3);
const inProgressCourses = ref(2);
const notStartedCourses = ref(1);

const trendPeriods = [
  { label: '周', value: 'week' },
  { label: '月', value: 'month' },
  { label: '年', value: 'year' }
];

const selectedTrendPeriod = ref('week');
const selectedCourseId = ref('');

// 趋势数据
const weekTrendData = ref([
  { label: '周一', value: 25 },
  { label: '周二', value: 18 },
  { label: '周三', value: 30 },
  { label: '周四', value: 22 },
  { label: '周五', value: 15 },
  { label: '周六', value: 10 },
  { label: '周日', value: 5 }
]);

const monthTrendData = ref([
  { label: '第1周', value: 20 },
  { label: '第2周', value: 25 },
  { label: '第3周', value: 18 },
  { label: '第4周', value: 30 }
]);

const yearTrendData = ref([
  { label: '1月', value: 15 },
  { label: '2月', value: 20 },
  { label: '3月', value: 25 },
  { label: '4月', value: 18 },
  { label: '5月', value: 30 },
  { label: '6月', value: 22 }
]);

// 知识点掌握情况数据
const knowledgePointsData = ref([
  { label: '编程基础', value: 85 },
  { label: '数据结构', value: 65 },
  { label: '算法设计', value: 70 },
  { label: '数据库', value: 90 },
  { label: '网络原理', value: 60 },
  { label: '软件工程', value: 75 }
]);

// 计算当前趋势数据
const trendData = computed(() => {
  switch (selectedTrendPeriod.value) {
    case 'week':
      return weekTrendData.value;
    case 'month':
      return monthTrendData.value;
    case 'year':
      return yearTrendData.value;
    default:
      return weekTrendData.value;
  }
});

// 课程详情数据
const courseDetails = ref([
  {
    id: 1,
    name: '人工智能基础',
    category: '计算机科学',
    progress: 85,
    learningTime: 12.5,
    lastActivity: '2025-06-23',
    score: 90
  },
  {
    id: 2,
    name: '高等数学',
    category: '数学',
    progress: 60,
    learningTime: 8.2,
    lastActivity: '2025-06-22',
    score: 75
  },
  {
    id: 3,
    name: '英语写作',
    category: '语言',
    progress: 100,
    learningTime: 15.0,
    lastActivity: '2025-06-20',
    score: 95
  },
  {
    id: 4,
    name: '数据结构与算法',
    category: '计算机科学',
    progress: 45,
    learningTime: 6.8,
    lastActivity: '2025-06-24',
    score: 80
  },
  {
    id: 5,
    name: '物理学基础',
    category: '自然科学',
    progress: 100,
    learningTime: 10.5,
    lastActivity: '2025-06-15',
    score: 88
  }
]);

onMounted(async () => {
  // 获取学习分析数据
  await fetchAnalyticsData();
});

async function fetchAnalyticsData() {
  try {
    loading.value = true;
    
    if (props.userId) {
      try {
        const response = await analyticsAPI.getStudentAnalytics(props.userId);
        const data = response.data || {};
        
        // 更新组件数据，添加空值检查
        overallProgress.value = data.overallProgress !== undefined ? data.overallProgress : overallProgress.value;
        weeklyLearningTime.value = data.weeklyLearningTime !== undefined ? data.weeklyLearningTime : weeklyLearningTime.value;
        previousWeekTime.value = data.previousWeekTime !== undefined ? data.previousWeekTime : previousWeekTime.value;
        completedCourses.value = data.completedCourses !== undefined ? data.completedCourses : completedCourses.value;
        inProgressCourses.value = data.inProgressCourses !== undefined ? data.inProgressCourses : inProgressCourses.value;
        notStartedCourses.value = data.notStartedCourses !== undefined ? data.notStartedCourses : notStartedCourses.value;
        
        // 更新趋势数据
        if (data.trendData) {
          weekTrendData.value = data.trendData.week || weekTrendData.value;
          monthTrendData.value = data.trendData.month || monthTrendData.value;
          yearTrendData.value = data.trendData.year || yearTrendData.value;
        }
        
        // 更新课程详情
        if (data.courseDetails) {
          courseDetails.value = data.courseDetails;
        }
        
        // 更新知识点数据
        if (data.knowledgePoints) {
          knowledgePointsData.value = data.knowledgePoints;
        }
      } catch (error) {
        console.error('API请求失败:', error);
        // 保留模拟数据
      }
    }
  } catch (error) {
    console.error('获取学习分析数据失败:', error);
  } finally {
    loading.value = false;
  }
}
</script> 