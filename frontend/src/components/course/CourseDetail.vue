<template>
  <div class="course-detail">
    <div v-if="loading" class="flex justify-center py-10">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>

    <div v-else-if="!course" class="text-center py-10">
      <p class="text-gray-500">课程不存在或已被删除</p>
      <router-link to="/courses" class="text-blue-600 hover:text-blue-800 mt-4 inline-block">返回课程列表</router-link>
    </div>

    <div v-else>
      <!-- 课程头部信息 -->
      <div class="bg-white shadow-md rounded-lg overflow-hidden border border-gray-200 mb-6">
        <div class="h-48 bg-gray-200 relative">
          <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-6">
            <div class="flex items-center justify-between">
              <h1 class="text-2xl font-bold text-white">{{ course.name }}</h1>
              <span class="px-3 py-1 text-sm rounded-full" :class="difficultyClass(course.difficulty)">
                {{ difficultyText(course.difficulty) }}
              </span>
            </div>
            <p class="text-white/80 mt-1">{{ course.category }}</p>
          </div>
        </div>
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center">
              <div class="w-10 h-10 rounded-full bg-gray-300 mr-3"></div>
              <div>
                <p class="font-semibold">{{ course.teacher_name }}</p>
                <p class="text-sm text-gray-500">教师</p>
              </div>
            </div>
            <div class="flex gap-4">
              <div class="text-center">
                <p class="font-semibold">{{ course.student_count || 0 }}</p>
                <p class="text-sm text-gray-500">学生</p>
              </div>
              <div class="text-center">
                <p class="font-semibold">{{ course.material_count || 0 }}</p>
                <p class="text-sm text-gray-500">课件</p>
              </div>
              <div class="text-center">
                <p class="font-semibold">{{ course.assessment_count || 0 }}</p>
                <p class="text-sm text-gray-500">评估</p>
              </div>
            </div>
          </div>
          <div class="border-t pt-4">
            <h3 class="text-lg font-semibold mb-2">课程描述</h3>
            <p class="text-gray-700">{{ course.description }}</p>
          </div>
        </div>
      </div>

      <!-- 课程内容导航 -->
      <div class="bg-white shadow-md rounded-lg overflow-hidden border border-gray-200 mb-6">
        <div class="flex border-b">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            @click="activeTab = tab.id"
            class="px-4 py-3 text-sm font-medium"
            :class="activeTab === tab.id ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'"
          >
            {{ tab.name }}
          </button>
        </div>
      </div>

      <!-- 课程内容 -->
      <div class="bg-white shadow-md rounded-lg overflow-hidden border border-gray-200">
        <!-- 章节内容 -->
        <div v-if="activeTab === 'chapters'" class="p-6">
          <div v-if="course.chapters && course.chapters.length > 0">
            <div v-for="(chapter, index) in course.chapters" :key="index" class="mb-6">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-lg font-semibold">{{ chapter.title }}</h3>
                <span class="text-sm text-gray-500">{{ chapter.duration || 0 }} 分钟</span>
              </div>
              <div class="ml-4 border-l-2 border-gray-200 pl-4">
                <div v-for="(section, sIndex) in chapter.sections" :key="sIndex" class="py-2">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center">
                      <span class="mr-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </span>
                      <span>{{ section.title }}</span>
                    </div>
                    <span class="text-sm text-gray-500">{{ section.duration || 0 }} 分钟</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-10">
            <p class="text-gray-500">暂无章节内容</p>
            <button 
              v-if="canEdit" 
              @click="showAddChapterModal = true"
              class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md"
            >
              添加章节
            </button>
          </div>
        </div>

        <!-- 课件资源 -->
        <div v-else-if="activeTab === 'materials'" class="p-6">
          <CourseMaterials 
            :course-id="courseId" 
            :can-upload="canEdit"
            @refresh="fetchCourseDetail"
          />
        </div>

        <!-- 评估测验 -->
        <div v-else-if="activeTab === 'assessments'" class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold">评估测验</h3>
            <button 
              v-if="canEdit" 
              @click="showAddAssessmentModal = true"
              class="px-4 py-2 bg-blue-600 text-white rounded-md"
            >
              创建评估
            </button>
          </div>

          <div v-if="assessments.length > 0" class="space-y-4">
            <div v-for="assessment in assessments" :key="assessment.id" class="p-4 border rounded-md">
              <div class="flex items-center justify-between">
                <div>
                  <h4 class="font-medium">{{ assessment.title }}</h4>
                  <p class="text-sm text-gray-500">{{ assessment.type }} · {{ assessment.question_count }}题 · {{ assessment.time_limit }}分钟</p>
                </div>
                <button class="px-4 py-2 border rounded-md">开始</button>
              </div>
              <div class="mt-2">
                <p class="text-sm text-gray-700">{{ assessment.description }}</p>
              </div>
              <div class="mt-2 flex items-center text-sm text-gray-500">
                <span>截止日期: {{ assessment.due_date || '无' }}</span>
                <span class="mx-2">|</span>
                <span>尝试次数: {{ assessment.attempts || 0 }}/{{ assessment.max_attempts || '无限制' }}</span>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-10">
            <p class="text-gray-500">暂无评估测验</p>
          </div>
        </div>

        <!-- 学生管理 -->
        <div v-else-if="activeTab === 'students'" class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold">学生管理</h3>
            <div class="flex gap-2">
              <button 
                v-if="canEdit" 
                class="px-4 py-2 border rounded-md"
              >
                导入学生
              </button>
              <button 
                v-if="canEdit" 
                @click="showAddStudentModal = true"
                class="px-4 py-2 bg-blue-600 text-white rounded-md"
              >
                添加学生
              </button>
            </div>
          </div>

          <div class="mb-4">
            <input 
              type="text" 
              v-model="studentSearch" 
              placeholder="搜索学生..." 
              class="w-full px-4 py-2 border rounded-md"
            />
          </div>

          <div v-if="students.length > 0" class="border rounded-md overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">学生</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">进度</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">最后活动</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="student in students" :key="student.id">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="flex-shrink-0 h-8 w-8 rounded-full bg-gray-200"></div>
                      <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">{{ student.name }}</div>
                        <div class="text-sm text-gray-500">{{ student.email }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                      <div class="bg-blue-600 h-2.5 rounded-full" :style="`width: ${student.progress}%`"></div>
                    </div>
                    <div class="text-xs text-gray-500 mt-1">{{ student.progress }}%</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ student.last_activity }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <button class="text-blue-600 hover:text-blue-800">查看</button>
                    <button v-if="canEdit" class="text-red-600 hover:text-red-800 ml-3">移除</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="text-center py-10">
            <p class="text-gray-500">暂无学生</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 模态框组件将在这里添加 -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '../../stores/auth';
import CourseMaterials from '../material/CourseMaterials.vue';

const props = defineProps({
  id: {
    type: [Number, String],
    required: true
  }
});

const authStore = useAuthStore();
const courseId = computed(() => props.id);
const userRole = computed(() => authStore.user?.role || '');

const loading = ref(true);
const course = ref(null);
const activeTab = ref('chapters');
const studentSearch = ref('');
const showAddChapterModal = ref(false);
const showAddAssessmentModal = ref(false);
const showAddStudentModal = ref(false);

const tabs = [
  { id: 'chapters', name: '章节内容' },
  { id: 'materials', name: '课件资源' },
  { id: 'assessments', name: '评估测验' },
  { id: 'students', name: '学生管理' },
];

const canEdit = computed(() => {
  return userRole.value === 'admin' || 
         userRole.value === 'teacher' && course.value?.teacher_id === authStore.user?.id;
});

// 模拟数据
const assessments = ref([
  {
    id: 1,
    title: '第一章测验',
    type: '测验',
    question_count: 10,
    time_limit: 30,
    description: '测试对第一章内容的理解',
    due_date: '2025-07-15',
    attempts: 0,
    max_attempts: 3,
  },
]);

const students = ref([
  {
    id: 1,
    name: '李明',
    email: 'liming@example.com',
    progress: 75,
    last_activity: '2025-06-23 14:30',
  },
  {
    id: 2,
    name: '王红',
    email: 'wanghong@example.com',
    progress: 45,
    last_activity: '2025-06-22 09:15',
  },
]);

onMounted(async () => {
  await fetchCourseDetail();
});

async function fetchCourseDetail() {
  loading.value = true;
  try {
    // 这里应该调用API获取课程详情
    // const response = await api.getCourseDetail(courseId.value);
    
    // 模拟API响应
    setTimeout(() => {
      course.value = {
        id: Number(courseId.value),
        name: '人工智能基础',
        description: '介绍人工智能的基本概念和应用，包括机器学习、深度学习、自然语言处理等内容。本课程适合初学者，不需要特别的数学背景。',
        category: '计算机科学',
        difficulty: 'beginner',
        teacher_id: 1,
        teacher_name: '张教授',
        student_count: 42,
        material_count: 12,
        assessment_count: 5,
        chapters: [
          {
            title: '第一章：人工智能概述',
            duration: 60,
            sections: [
              { title: '1.1 什么是人工智能', duration: 15 },
              { title: '1.2 人工智能的历史', duration: 20 },
              { title: '1.3 人工智能的应用领域', duration: 25 },
            ]
          },
          {
            title: '第二章：机器学习基础',
            duration: 90,
            sections: [
              { title: '2.1 机器学习概念', duration: 20 },
              { title: '2.2 监督学习', duration: 35 },
              { title: '2.3 无监督学习', duration: 35 },
            ]
          }
        ]
      };
      loading.value = false;
    }, 500);
  } catch (error) {
    console.error('获取课程详情失败:', error);
    loading.value = false;
  }
}

function difficultyClass(difficulty) {
  switch (difficulty) {
    case 'beginner': return 'bg-green-100 text-green-800';
    case 'intermediate': return 'bg-yellow-100 text-yellow-800';
    case 'advanced': return 'bg-red-100 text-red-800';
    default: return 'bg-gray-100 text-gray-800';
  }
}

function difficultyText(difficulty) {
  switch (difficulty) {
    case 'beginner': return '初级';
    case 'intermediate': return '中级';
    case 'advanced': return '高级';
    default: return '未知';
  }
}
</script> 