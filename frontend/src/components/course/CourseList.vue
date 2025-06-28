<template>
  <div class="course-list">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">课程列表</h2>
      <button 
        v-if="userRole === 'teacher' || userRole === 'admin'"
        @click="showCreateModal = true" 
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
      >
        创建课程
      </button>
    </div>
    
    <div class="mb-4 flex justify-between">
      <div class="flex gap-2">
        <select v-model="filters.category" class="border rounded-md px-3 py-2">
          <option value="">所有分类</option>
          <option value="计算机科学">计算机科学</option>
          <option value="数学">数学</option>
          <option value="语言">语言</option>
          <option value="自然科学">自然科学</option>
        </select>
        <select v-model="filters.difficulty" class="border rounded-md px-3 py-2">
          <option value="">所有难度</option>
          <option value="beginner">初级</option>
          <option value="intermediate">中级</option>
          <option value="advanced">高级</option>
        </select>
      </div>
      <div class="relative">
        <input 
          type="text" 
          v-model="filters.search" 
          placeholder="搜索课程..." 
          class="border rounded-md pl-10 pr-3 py-2 w-64"
        />
        <span class="absolute left-3 top-2.5 text-gray-400">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </span>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-10">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>

    <div v-else-if="courses.length === 0" class="text-center py-10 bg-gray-50 rounded-md">
      <p class="text-gray-500">暂无课程</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="course in courses" :key="course.id" class="bg-white rounded-lg shadow-md overflow-hidden border border-gray-200">
        <div class="h-40 bg-gray-200"></div>
        <div class="p-4">
          <div class="flex justify-between items-start">
            <h3 class="text-lg font-semibold">{{ course.name }}</h3>
            <span class="px-2 py-1 text-xs rounded-full" :class="difficultyClass(course.difficulty)">
              {{ difficultyText(course.difficulty) }}
            </span>
          </div>
          <p class="text-gray-600 text-sm mt-2 line-clamp-2">{{ course.description }}</p>
          <div class="mt-4 flex justify-between items-center">
            <span class="text-sm text-gray-500">{{ course.teacher_name }}</span>
            <router-link :to="`/course/${course.id}`" class="text-blue-600 hover:text-blue-800">查看详情</router-link>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-6 flex justify-center">
      <nav class="flex items-center">
        <button 
          @click="changePage(currentPage - 1)" 
          :disabled="currentPage === 1" 
          class="px-3 py-1 rounded-md border"
          :class="currentPage === 1 ? 'text-gray-400 cursor-not-allowed' : 'hover:bg-gray-100'"
        >
          上一页
        </button>
        <span class="mx-4">{{ currentPage }} / {{ totalPages }}</span>
        <button 
          @click="changePage(currentPage + 1)" 
          :disabled="currentPage === totalPages" 
          class="px-3 py-1 rounded-md border"
          :class="currentPage === totalPages ? 'text-gray-400 cursor-not-allowed' : 'hover:bg-gray-100'"
        >
          下一页
        </button>
      </nav>
    </div>

    <!-- 创建课程模态框 -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-lg">
        <h3 class="text-xl font-bold mb-4">创建新课程</h3>
        <form @submit.prevent="createCourse">
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">课程名称</label>
            <input v-model="newCourse.name" type="text" required class="w-full px-3 py-2 border rounded-md" />
          </div>
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">课程描述</label>
            <textarea v-model="newCourse.description" required class="w-full px-3 py-2 border rounded-md" rows="3"></textarea>
          </div>
          <div class="mb-4 grid grid-cols-2 gap-4">
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">分类</label>
              <select v-model="newCourse.category" required class="w-full px-3 py-2 border rounded-md">
                <option value="计算机科学">计算机科学</option>
                <option value="数学">数学</option>
                <option value="语言">语言</option>
                <option value="自然科学">自然科学</option>
              </select>
            </div>
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">难度</label>
              <select v-model="newCourse.difficulty" required class="w-full px-3 py-2 border rounded-md">
                <option value="beginner">初级</option>
                <option value="intermediate">中级</option>
                <option value="advanced">高级</option>
              </select>
            </div>
          </div>
          <div class="flex justify-end gap-2 mt-6">
            <button type="button" @click="showCreateModal = false" class="px-4 py-2 border rounded-md">取消</button>
            <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md">创建</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { useAuthStore } from '../../stores/auth';

const authStore = useAuthStore();
const userRole = computed(() => authStore.user?.role || '');

const courses = ref([]);
const loading = ref(true);
const currentPage = ref(1);
const totalPages = ref(1);
const showCreateModal = ref(false);

const filters = reactive({
  search: '',
  category: '',
  difficulty: ''
});

const newCourse = reactive({
  name: '',
  description: '',
  category: '计算机科学',
  difficulty: 'beginner',
  is_public: true
});

onMounted(async () => {
  await fetchCourses();
});

async function fetchCourses() {
  loading.value = true;
  try {
    // 这里应该调用API获取课程列表
    // const response = await api.getCourses({
    //   page: currentPage.value,
    //   per_page: 9,
    //   search: filters.search,
    //   category: filters.category,
    //   difficulty: filters.difficulty
    // });
    
    // 模拟API响应
    setTimeout(() => {
      courses.value = [
        {
          id: 1,
          name: '人工智能基础',
          description: '介绍人工智能的基本概念和应用',
          category: '计算机科学',
          difficulty: 'beginner',
          teacher_name: '张教授'
        },
        {
          id: 2,
          name: '高等数学',
          description: '微积分和线性代数基础',
          category: '数学',
          difficulty: 'intermediate',
          teacher_name: '李教授'
        },
        {
          id: 3,
          name: '英语写作',
          description: '学术英语写作技巧和方法',
          category: '语言',
          difficulty: 'advanced',
          teacher_name: '王教授'
        }
      ];
      totalPages.value = 3;
      loading.value = false;
    }, 500);
  } catch (error) {
    console.error('获取课程失败:', error);
    loading.value = false;
  }
}

function changePage(page) {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  fetchCourses();
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

async function createCourse() {
  try {
    // 这里应该调用API创建课程
    // await api.createCourse(newCourse);
    
    // 模拟API调用
    console.log('创建课程:', newCourse);
    
    // 重置表单和关闭模态框
    Object.assign(newCourse, {
      name: '',
      description: '',
      category: '计算机科学',
      difficulty: 'beginner',
      is_public: true
    });
    showCreateModal.value = false;
    
    // 刷新课程列表
    await fetchCourses();
  } catch (error) {
    console.error('创建课程失败:', error);
  }
}
</script> 