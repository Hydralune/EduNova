<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="border-b border-gray-200 pb-5 mb-5">
          <h1 class="text-3xl font-bold text-gray-900">教师工作台</h1>
          <p class="mt-2 text-sm text-gray-500">
            管理课程、创建教学内容和查看学生进度
          </p>
        </div>

        <!-- 导航标签 -->
        <div class="border-b border-gray-200 mb-6">
          <nav class="flex -mb-px">
            <button 
              v-for="tab in tabs" 
              :key="tab.id"
              @click="activeTab = tab.id"
              class="px-4 py-3 text-sm font-medium"
              :class="activeTab === tab.id ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'"
            >
              {{ tab.name }}
            </button>
          </nav>
        </div>

        <!-- 欢迎页 -->
        <div v-if="activeTab === 'dashboard'">
          <WelcomeMessage v-model:activeTab="activeTab" />
        </div>

        <!-- 功能区 -->
        <div v-if="activeTab === 'dashboard'" class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- 课程管理 -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <div class="flex items-center">
                <div class="flex-shrink-0 bg-blue-500 rounded-md p-3">
                  <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dt class="text-lg font-medium text-gray-900">课程管理</dt>
                  <dd class="mt-2 text-sm text-gray-500">
                    创建和管理您的课程内容
                  </dd>
                </div>
              </div>
              <div class="mt-5">
                <button @click="activeTab = 'courses'" class="btn btn-primary w-full">
                  查看我的课程
                </button>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-4 sm:px-6">
              <div class="text-sm">
                <span class="font-medium text-blue-600 hover:text-blue-500">
                  {{ coursesCount || 0 }} 个课程
                </span>
              </div>
            </div>
          </div>

          <!-- 智能备课 -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <div class="flex items-center">
                <div class="flex-shrink-0 bg-green-500 rounded-md p-3">
                  <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dt class="text-lg font-medium text-gray-900">智能备课</dt>
                  <dd class="mt-2 text-sm text-gray-500">
                    使用AI辅助创建教学内容
                  </dd>
                </div>
              </div>
              <div class="mt-5">
                <button @click="activeTab = 'lesson-planner'" class="btn btn-primary w-full">
                  开始备课
                </button>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-4 sm:px-6">
              <div class="text-sm">
                <span class="font-medium text-green-600 hover:text-green-500">
                  AI辅助备课
                </span>
              </div>
            </div>
          </div>

          <!-- 学情分析 -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <div class="flex items-center">
                <div class="flex-shrink-0 bg-purple-500 rounded-md p-3">
                  <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dt class="text-lg font-medium text-gray-900">学情分析</dt>
                  <dd class="mt-2 text-sm text-gray-500">
                    查看学生学习数据和进度
                  </dd>
                </div>
              </div>
              <div class="mt-5">
                <button @click="activeTab = 'analytics'" class="btn btn-primary w-full">
                  查看分析报告
                </button>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-4 sm:px-6">
              <div class="text-sm">
                <span class="font-medium text-purple-600 hover:text-purple-500">
                  {{ studentsCount || 0 }} 名学生
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 课程列表 -->
        <div v-if="activeTab === 'courses'">
          <CourseList />
        </div>

        <!-- 评估测试 -->
        <div v-if="activeTab === 'assessments'">
          <div v-if="showSubmissionsList">
            <div class="flex justify-between mb-4">
              <h2 class="text-xl font-semibold">{{ currentAssessment.title }} - 学生提交</h2>
              <button 
                @click="closeSubmissionsList" 
                class="px-4 py-2 border rounded-md hover:bg-gray-50"
              >
                返回评估列表
              </button>
            </div>
            <SubmissionList 
              :assessmentId="currentAssessment.id" 
              :role="'teacher'"
              @back="closeSubmissionsList"
            />
          </div>
          <div v-else>
            <AssessmentList 
              :role="'teacher'" 
              @view-submissions="viewSubmissions"
            />
          </div>
        </div>

        <!-- AI助手 -->
        <div v-if="activeTab === 'ai-assistant'">
          <AIAssistant :user-id="userId || ''" />
        </div>

        <!-- 智能备课 -->
        <div v-if="activeTab === 'lesson-planner'">
          <LessonPlanner />
        </div>

        <!-- 学习分析 -->
        <div v-if="activeTab === 'analytics'">
          <TeacherAnalytics />
        </div>

        <!-- 知识库 -->
        <div v-if="activeTab === 'knowledge-base'">
          <KnowledgeBase />
        </div>

        <!-- 最近活动 -->
        <div v-if="activeTab === 'dashboard'" class="mt-8">
          <h2 class="text-lg font-medium text-gray-900">最近活动</h2>
          <div class="mt-4 bg-white shadow overflow-hidden rounded-md">
            <ul class="divide-y divide-gray-200">
              <li v-if="!recentActivities || recentActivities.length === 0" class="px-6 py-4">
                暂无活动记录
              </li>
              <li v-else v-for="(activity, index) in recentActivities" :key="index" class="px-6 py-4">
                <div class="flex items-center space-x-4">
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">
                      {{ activity.title }}
                    </p>
                    <p class="text-sm text-gray-500 truncate">
                      {{ activity.description }}
                    </p>
                  </div>
                  <div class="text-sm text-gray-500">
                    {{ activity.time }}
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRoute } from 'vue-router';
import CourseList from '@/components/course/CourseList.vue';
import AIAssistant from '@/components/ai/AIAssistant.vue';
import LessonPlanner from '@/components/ai/LessonPlanner.vue';
import LearningAnalytics from '@/components/analytics/LearningAnalytics.vue';
import KnowledgeBase from '@/components/rag/KnowledgeBase.vue';
import WelcomeMessage from '@/components/WelcomeMessage.vue';
import AssessmentList from '@/components/assessment/AssessmentList.vue';
import SubmissionList from '@/components/assessment/SubmissionList.vue';
import TeacherAnalytics from '@/components/analytics/TeacherAnalytics.vue';

const authStore = useAuthStore();
const route = useRoute();
const userId = computed(() => authStore.user?.id);

// 标签页
const tabs = [
  { id: 'dashboard', name: '工作台' },
  { id: 'courses', name: '课程管理' },
  { id: 'assessments', name: '评估测试' },
  { id: 'lesson-planner', name: '智能备课' },
  { id: 'ai-assistant', name: '智能助手' },
  { id: 'analytics', name: '学情分析' },
  { id: 'knowledge-base', name: '知识库' }
];
const activeTab = ref('dashboard');

// 评估测试相关状态
const showSubmissionsList = ref(false);
const currentAssessment = ref<{ id: string | number; title: string }>({ id: '', title: '' });

const viewSubmissions = (data: { assessment: { id: string | number; title: string } }) => {
  console.log('查看提交:', data);
  currentAssessment.value = {
    id: data.assessment.id,
    title: data.assessment.title
  };
  showSubmissionsList.value = true;
};

const closeSubmissionsList = () => {
  showSubmissionsList.value = false;
  currentAssessment.value = { id: '', title: '' };
};


// 监听路由查询参数变化，更新活动标签
watch(() => route.query.activeTab, (newTab) => {
  if (newTab && typeof newTab === 'string' && tabs.some(tab => tab.id === newTab)) {
    activeTab.value = newTab;
  }
}, { immediate: true });

// 示例数据
const coursesCount = ref(3);
const studentsCount = ref(42);
const recentActivities = ref([
  {
    title: '课程更新',
    description: '您更新了"Python编程基础"课程内容',
    time: '2小时前'
  },
  {
    title: '学生提问',
    description: '学生张三在"数据结构"课程中提出了一个问题',
    time: '昨天'
  }
]);

// 这里可以添加获取课程和学生数据的API调用
</script>

<style scoped>
.btn {
  @apply px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2;
}

.btn-primary {
  @apply text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500;
}
</style> 