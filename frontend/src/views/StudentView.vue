<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="border-b border-gray-200 pb-5 mb-5">
          <h1 class="text-3xl font-bold text-gray-900">学习中心</h1>
          <p class="mt-2 text-sm text-gray-500">
            探索课程、完成作业和跟踪您的学习进度
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

        <!-- 课程列表 -->
        <div v-if="activeTab === 'courses'">
          <CourseList />
        </div>

        <!-- 学习分析 -->
        <div v-if="activeTab === 'analytics'">
          <LearningAnalytics :user-id="userId || ''" />
        </div>

        <!-- AI助手 -->
        <div v-if="activeTab === 'ai-assistant'">
          <AIAssistant :user-id="userId || ''" />
        </div>

        <!-- 知识库 -->
        <div v-if="activeTab === 'knowledge-base'">
          <KnowledgeBase />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import CourseList from '@/components/course/CourseList.vue';
import AIAssistant from '@/components/ai/AIAssistant.vue';
import LearningAnalytics from '@/components/analytics/LearningAnalytics.vue';
import KnowledgeBase from '@/components/rag/KnowledgeBase.vue';
import WelcomeMessage from '@/components/WelcomeMessage.vue';

const authStore = useAuthStore();
const userId = computed(() => authStore.user?.id);

// 标签页
const tabs = [
  { id: 'dashboard', name: '首页' },
  { id: 'courses', name: '课程目录' },
  { id: 'analytics', name: '学习分析' },
  { id: 'ai-assistant', name: '智能助手' },
  { id: 'knowledge-base', name: '知识库' }
];
const activeTab = ref('dashboard');

// 示例数据
const enrolledCourses = ref([
  {
    id: 1,
    title: 'Python编程基础',
    description: '学习Python编程的基本概念和语法',
    progress: 45
  },
  {
    id: 2,
    title: '数据结构与算法',
    description: '掌握常见数据结构和算法',
    progress: 20
  }
]);

const learningStats = ref({
  completedLessons: 12,
  completedAssignments: 8,
  averageScore: 85
});

// 这里可以添加获取课程和学习数据的API调用
</script>

<style scoped>
.btn {
  @apply px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2;
}

.btn-primary {
  @apply text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500;
}
</style> 