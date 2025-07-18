<template>
  <div class="teacher-analytics">
    <h2 class="text-2xl font-bold mb-6">课程学情分析</h2>
    
    <!-- 课程选择器 -->
    <div class="mb-6">
      <label for="course-select" class="block text-sm font-medium text-gray-700 mb-1">选择课程</label>
      <div class="flex">
        <select 
          id="course-select"
          v-model="selectedCourseId"
          class="block w-full max-w-md rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          @change="loadCourseAnalytics"
        >
          <option value="">请选择课程</option>
          <option v-for="course in courses" :key="course.id" :value="course.id">
            {{ course.name }}
          </option>
        </select>
        <button 
          class="ml-2 px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          @click="loadCourseAnalytics"
        >
          刷新数据
        </button>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center items-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      <span class="ml-3 text-gray-600">加载中...</span>
    </div>
    
    <!-- 未选择课程提示 -->
    <div v-else-if="!selectedCourseId" class="bg-white p-8 rounded-lg shadow-md border border-gray-200 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <h3 class="text-lg font-medium text-gray-900 mb-2">请选择一个课程</h3>
      <p class="text-gray-500">选择一个课程以查看详细的学情分析数据</p>
    </div>
    
    <!-- 分析数据 -->
    <div v-else>
      <!-- 学生完成情况统计 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div class="text-sm text-gray-500 mb-1">总学生数</div>
          <div class="text-2xl font-bold text-gray-900">{{ analytics.totalStudents || 0 }}</div>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div class="text-sm text-gray-500 mb-1">已完成学生</div>
          <div class="text-2xl font-bold text-blue-600">{{ analytics.completedStudents || 0 }}</div>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div class="text-sm text-gray-500 mb-1">进行中学生</div>
          <div class="text-2xl font-bold text-yellow-600">{{ analytics.inProgressStudents || 0 }}</div>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div class="text-sm text-gray-500 mb-1">未开始学生</div>
          <div class="text-2xl font-bold text-gray-600">{{ analytics.notStartedStudents || 0 }}</div>
        </div>
      </div>
      
      <!-- 知识点掌握情况 -->
      <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-6">
        <h3 class="text-lg font-semibold mb-4">知识点掌握情况</h3>
        <div class="h-80">
          <KnowledgeRadarChart :data="analytics.knowledgePoints || []" title="班级整体知识点掌握情况" />
        </div>
      </div>
      
      <!-- 评估数据 -->
      <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-6">
        <h3 class="text-lg font-semibold mb-4">评估完成情况</h3>
        <div v-if="analytics.assessments && analytics.assessments.length > 0" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">评估标题</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">提交数量</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">平均分数</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="assessment in analytics.assessments" :key="assessment.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{{ assessment.title }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ assessment.submissionsCount }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <span class="text-sm font-medium text-gray-900 mr-2">{{ assessment.averageScore }}</span>
                    <div class="w-24 bg-gray-200 rounded-full h-2">
                      <div class="bg-blue-600 h-2 rounded-full" :style="`width: ${assessment.averageScore}%`"></div>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-6 text-gray-500">
          暂无评估数据
        </div>
      </div>
      
      <!-- 学生进度表 -->
      <div class="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
        <div class="px-6 py-4 border-b flex justify-between items-center">
          <h3 class="text-lg font-semibold">学生学习进度</h3>
          <div class="flex items-center">
            <input 
              type="text" 
              v-model="studentSearch" 
              placeholder="搜索学生" 
              class="border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
            />
          </div>
        </div>
        
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">学生姓名</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">进度</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">学习时间</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-if="!filteredStudentProgress || filteredStudentProgress.length === 0">
                <td colspan="3" class="px-6 py-4 text-center text-gray-500">暂无学生数据</td>
              </tr>
              <tr v-for="student in filteredStudentProgress" :key="student.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{{ student.name }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="w-full bg-gray-200 rounded-full h-2.5 max-w-[150px]">
                    <div 
                      class="h-2.5 rounded-full" 
                      :class="getProgressColorClass(student.progress)"
                      :style="`width: ${student.progress}%`"
                    ></div>
                  </div>
                  <div class="text-xs text-gray-500 mt-1">{{ student.progress }}%</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ student.learningTime }}小时
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
import { ref, computed, onMounted } from 'vue';
import { analyticsAPI, courseAPI, assessmentAPI } from '@/api';
import KnowledgeRadarChart from './KnowledgeRadarChart.vue';

// 数据类型定义
interface Student {
  id: number | string;
  name: string;
  progress: number;
  learningTime: number;
}

interface Assessment {
  id: number | string;
  title: string;
  submissionsCount: number;
  averageScore: number;
}

interface KnowledgePoint {
  label: string;
  value: number;
}

interface CourseAnalytics {
  totalStudents: number;
  completedStudents: number;
  inProgressStudents: number;
  notStartedStudents: number;
  studentProgress: Student[];
  assessments: Assessment[];
  knowledgePoints: KnowledgePoint[];
}

interface Course {
  id: number | string;
  name: string;
  description?: string;
}

// 数据
const loading = ref(false);
const selectedCourseId = ref('');
const courses = ref<Course[]>([]);
const analytics = ref<CourseAnalytics>({
  totalStudents: 0,
  completedStudents: 0,
  inProgressStudents: 0,
  notStartedStudents: 0,
  studentProgress: [],
  assessments: [],
  knowledgePoints: []
});
const studentSearch = ref('');

// 计算属性：过滤后的学生进度
const filteredStudentProgress = computed(() => {
  if (!analytics.value.studentProgress) return [];
  
  if (!studentSearch.value) {
    return analytics.value.studentProgress;
  }
  
  const search = studentSearch.value.toLowerCase();
  return analytics.value.studentProgress.filter(student => 
    student.name.toLowerCase().includes(search)
  );
});

// 根据进度获取颜色类
function getProgressColorClass(progress: number) {
  if (progress >= 80) return 'bg-green-600';
  if (progress >= 50) return 'bg-blue-600';
  if (progress >= 20) return 'bg-yellow-600';
  return 'bg-red-600';
}

// 加载课程列表
async function loadCourses() {
  try {
    console.log('开始加载课程列表');
    const response = await courseAPI.getCourses();
    console.log('课程API响应:', response);
    
    // 检查响应格式，使用类型断言
    const responseData = response as any;
    if (responseData && responseData.courses) {
      courses.value = responseData.courses;
      console.log('成功加载课程列表:', courses.value);
    } else if (Array.isArray(responseData)) {
      courses.value = responseData;
      console.log('成功加载课程列表(数组格式):', courses.value);
    } else if (responseData && typeof responseData === 'object' && 'data' in responseData && responseData.data && responseData.data.courses) {
      courses.value = responseData.data.courses;
      console.log('成功加载课程列表(嵌套格式):', courses.value);
    } else {
      console.error('API响应格式异常:', responseData);
      courses.value = [];
    }
    
    // 如果有课程且没有选择课程，自动选择第一个课程
    if (courses.value.length > 0 && !selectedCourseId.value) {
      console.log('自动选择第一个课程:', courses.value[0].id);
      selectedCourseId.value = courses.value[0].id;
      loadCourseAnalytics(); // 加载选中课程的分析数据
    }
  } catch (error) {
    console.error('获取课程列表失败:', error);
    courses.value = [];
  }
}

// 加载课程学情分析数据
async function loadCourseAnalytics() {
  if (!selectedCourseId.value) return;
  
  try {
    loading.value = true;
    
    // 获取课程学情分析数据
    console.log('开始获取课程学情分析数据:', selectedCourseId.value);
    const analyticsResponse = await analyticsAPI.getCourseAnalytics(Number(selectedCourseId.value));
    console.log('课程学情分析数据原始响应:', analyticsResponse);
    
    // 检查响应格式
    let responseData;
    if (analyticsResponse && typeof analyticsResponse === 'object') {
      // 如果响应有data属性，使用它
      if ('data' in analyticsResponse) {
        responseData = analyticsResponse.data;
        console.log('从analyticsResponse.data获取数据');
      } else {
        // 否则直接使用响应
        responseData = analyticsResponse;
        console.log('直接使用analyticsResponse作为数据');
      }
      
      console.log('处理后的响应数据:', responseData);
      
      // 确保assessments字段存在并且是数组
      if (!responseData.assessments) {
        console.warn('响应中缺少assessments字段，设置为空数组');
        responseData.assessments = [];
      } else if (!Array.isArray(responseData.assessments)) {
        console.warn('assessments不是数组，设置为空数组');
        responseData.assessments = [];
      }
      
      // 调试评估数据
      console.log('评估数据:', responseData.assessments);
      
      // 确保每个评估都有必要的字段
      responseData.assessments = responseData.assessments.map((assessment: any) => ({
        id: assessment.id || 0,
        title: assessment.title || '未命名评估',
        submissionsCount: assessment.submissionsCount || 0,
        averageScore: assessment.averageScore || 0
      }));
      
      // 更新分析数据
      analytics.value = {
        totalStudents: responseData.totalStudents || 0,
        completedStudents: responseData.completedStudents || 0,
        inProgressStudents: responseData.inProgressStudents || 0,
        notStartedStudents: responseData.notStartedStudents || 0,
        studentProgress: responseData.studentProgress || [],
        assessments: responseData.assessments,
        knowledgePoints: responseData.knowledgePoints || []
      };
      
      console.log('成功加载课程学情分析数据:', analytics.value);
      console.log('评估数据处理后:', analytics.value.assessments);
    } else {
      console.error('API响应格式异常:', analyticsResponse);
      analytics.value = {
        totalStudents: 0,
        completedStudents: 0,
        inProgressStudents: 0,
        notStartedStudents: 0,
        studentProgress: [],
        assessments: [],
        knowledgePoints: []
      };
    }
  } catch (error) {
    console.error('获取课程学情分析数据失败:', error);
    analytics.value = {
      totalStudents: 0,
      completedStudents: 0,
      inProgressStudents: 0,
      notStartedStudents: 0,
      studentProgress: [],
      assessments: [],
      knowledgePoints: []
    };
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await loadCourses();
});
</script> 