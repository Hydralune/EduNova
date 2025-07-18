<template>
  <div class="learning-analytics">
    <h2 class="text-2xl font-bold mb-6">学习分析</h2>
    
    <!-- 加载状态 -->
    <div v-if="loading || coursesLoading" class="flex justify-center items-center py-20">
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
              <option v-for="course in realCourses" :key="course.id" :value="course.id">
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
        
        <div v-if="courseDetails.length === 0" class="p-6 text-center text-gray-500">
          暂无课程数据
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/4">课程名称</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/4">进度</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/4">学习时间</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/4">最后学习</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="course in courseDetails" :key="course.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <!-- 删除不能正常加载的图标 -->
                    <div class="ml-0">
                      <div class="text-sm font-medium text-gray-900">{{ course.name }}</div>
                      <div class="text-xs text-gray-500">{{ course.category }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="w-full bg-gray-200 rounded-full h-2.5 max-w-[120px]">
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
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import LearningTrendChart from './LearningTrendChart.vue';
import CoursePieChart from './CoursePieChart.vue';
import KnowledgeRadarChart from './KnowledgeRadarChart.vue';
import AIAnalysisPanel from './AIAnalysisPanel.vue'; // Added import for AIAnalysisPanel
import { analyticsAPI, courseAPI } from '@/api';

// 定义课程接口
interface Course {
  id: number;
  name: string;
  description?: string;
  category?: string;
  difficulty?: string;
  teacher_name?: string;
  student_count?: number;
  is_public?: boolean;
  cover_image?: string;
  created_at?: string;
  updated_at?: string;
}

// 定义课程详情接口
interface CourseDetail {
  id: number;
  name: string;
  category: string;
  progress: number;
  learningTime: number;
  lastActivity: string;
  score: number;
}

const props = defineProps({
  userId: {
    type: [Number, String],
    required: true
  }
});

// 加载状态
const loading = ref(true);
const coursesLoading = ref(true);

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

// 真实课程列表
const realCourses = ref<Course[]>([]);

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

// 根据课程ID生成随机知识点数据
const generateRandomKnowledgePoints = (courseId: string | number) => {
  // 不同课程的知识点映射
  const courseKnowledgePoints: Record<string, { label: string; value: number }[]> = {
    // 默认/所有课程的知识点
    'default': [
      { label: '编程基础', value: Math.floor(Math.random() * 30) + 60 },
      { label: '数据结构', value: Math.floor(Math.random() * 30) + 60 },
      { label: '算法设计', value: Math.floor(Math.random() * 30) + 60 },
      { label: '数据库', value: Math.floor(Math.random() * 30) + 60 },
      { label: '网络原理', value: Math.floor(Math.random() * 30) + 60 },
      { label: '软件工程', value: Math.floor(Math.random() * 30) + 60 }
    ]
  };
  
  // 为真实课程生成随机知识点
  realCourses.value.forEach(course => {
    // 为每个课程生成5-7个随机知识点
    const knowledgePointCount = Math.floor(Math.random() * 3) + 5; // 5-7个知识点
    const knowledgePoints: { label: string; value: number }[] = [];
    
    // 根据课程类别生成不同的知识点名称
    const category = course.category?.toLowerCase() || '';
    let baseKnowledgePoints: string[] = [];
    
    if (category.includes('计算机') || category.includes('编程')) {
      baseKnowledgePoints = ['编程基础', '数据结构', '算法设计', '数据库', '网络原理', '软件工程', '操作系统', '编译原理', '人工智能', '机器学习'];
    } else if (category.includes('数学')) {
      baseKnowledgePoints = ['微积分', '线性代数', '概率论', '离散数学', '数学分析', '复变函数', '微分方程', '数值计算', '统计学', '优化理论'];
    } else if (category.includes('物理')) {
      baseKnowledgePoints = ['力学', '热学', '光学', '电磁学', '原子物理', '量子力学', '相对论', '固体物理', '流体力学', '热力学'];
    } else if (category.includes('语言')) {
      baseKnowledgePoints = ['语法结构', '词汇运用', '阅读理解', '写作技巧', '口语表达', '听力理解', '文学赏析', '修辞手法', '翻译技巧', '学术写作'];
    } else {
      // 通用知识点
      baseKnowledgePoints = ['基础理论', '实践应用', '分析能力', '解决问题', '创新思维', '团队协作', '专业素养', '研究方法', '技术应用', '学科前沿'];
    }
    
    // 随机选择知识点
    const selectedPoints = new Set<string>();
    while (selectedPoints.size < knowledgePointCount && baseKnowledgePoints.length > 0) {
      const randomIndex = Math.floor(Math.random() * baseKnowledgePoints.length);
      selectedPoints.add(baseKnowledgePoints[randomIndex]);
      baseKnowledgePoints.splice(randomIndex, 1); // 避免重复
    }
    
    // 为每个知识点生成随机掌握度
    Array.from(selectedPoints).forEach(point => {
      knowledgePoints.push({
        label: point,
        value: Math.floor(Math.random() * 30) + 60 // 60-90之间的随机值
      });
    });
    
    // 添加到映射中
    courseKnowledgePoints[course.id.toString()] = knowledgePoints;
  });
  
  // 根据课程ID返回对应知识点，如果没有对应ID则返回默认知识点
  return courseKnowledgePoints[courseId.toString()] || courseKnowledgePoints['default'];
};

// 监听selectedCourseId变化，更新知识点数据
watch(selectedCourseId, (newCourseId) => {
  knowledgePointsData.value = generateRandomKnowledgePoints(newCourseId);
});

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
const courseDetails = ref<CourseDetail[]>([]);

// 根据真实课程生成虚拟的课程详情数据
const generateCourseDetails = (courses: Course[]): CourseDetail[] => {
  return courses.map(course => ({
    id: course.id,
    name: course.name,
    category: course.category || '未分类',
    progress: Math.floor(Math.random() * 100),
    learningTime: parseFloat((Math.random() * 20).toFixed(1)),
    lastActivity: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    score: Math.floor(Math.random() * 40) + 60
  }));
};

// 获取真实课程列表
async function fetchCourses() {
  coursesLoading.value = true;
  try {
    console.log('开始获取课程列表...');
    const response = await courseAPI.getCourses();
    console.log('课程API响应:', response);
    
    // 处理API响应数据
    if (response && typeof response === 'object' && 'courses' in response) {
      realCourses.value = (response as any).courses || [];
    } else if (Array.isArray(response)) {
      realCourses.value = response;
    } else if (response && typeof response === 'object' && 'data' in response && response.data && response.data.courses) {
      realCourses.value = response.data.courses;
    } else {
      console.warn('API返回格式不符合预期:', response);
      realCourses.value = [];
    }
    
    console.log('获取到课程列表:', realCourses.value);
    
    // 根据真实课程生成课程详情数据
    if (realCourses.value.length > 0) {
      courseDetails.value = generateCourseDetails(realCourses.value);
    } else {
      courseDetails.value = [];
    }
    
  } catch (error) {
    console.error('获取课程列表失败:', error);
    realCourses.value = [];
    courseDetails.value = [];
  } finally {
    coursesLoading.value = false;
  }
}

onMounted(async () => {
  try {
    loading.value = true;
    
    // 获取课程列表
    await fetchCourses();
    
    // 获取学习分析数据
    await fetchAnalyticsData();
    
    // 初始化知识点数据 - 在课程数据加载后执行
    if (realCourses.value.length > 0) {
      // 如果有课程，默认选择第一个课程
      if (!selectedCourseId.value && realCourses.value.length > 0) {
        selectedCourseId.value = realCourses.value[0].id.toString();
      }
      knowledgePointsData.value = generateRandomKnowledgePoints(selectedCourseId.value);
    }
  } catch (error) {
    console.error('初始化学习分析数据失败:', error);
  } finally {
    loading.value = false;
  }
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