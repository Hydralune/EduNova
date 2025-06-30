<template>
  <div class="course-list">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">课程列表</h2>
      <button 
        v-if="userRole === 'teacher' || userRole === 'admin' || true"
        @click="openCreateModal()" 
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
        <div class="h-40 bg-gray-200 relative">
          <img v-if="course.cover_image" :src="`http://localhost:5001${course.cover_image}`" alt="课程封面" class="w-full h-full object-cover" />
          <div v-else class="w-full h-full flex items-center justify-center bg-gradient-to-r from-blue-500 to-indigo-600">
            <h3 class="text-xl font-bold text-white">{{ course.name }}</h3>
          </div>
        </div>
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
            <div class="flex space-x-2">
              <router-link :to="`/course/${course.id}`" class="text-blue-600 hover:text-blue-800">查看详情</router-link>
              <div v-if="userRole === 'teacher' || userRole === 'admin'" class="flex space-x-2">
                <button @click="openEditModal(course)" class="text-green-600 hover:text-green-800">编辑</button>
                <button @click="confirmDeleteCourse(course)" class="text-red-600 hover:text-red-800">删除</button>
              </div>
            </div>
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

    <!-- 创建/编辑课程模态框 -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-lg">
        <h3 class="text-xl font-bold mb-4">{{ isEditing ? '编辑课程' : '创建新课程' }}</h3>
        <form @submit.prevent="saveCourse">
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">课程名称 <span class="text-red-500">*</span></label>
            <input v-model="newCourse.name" type="text" required class="w-full px-3 py-2 border rounded-md" />
          </div>
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">课程描述 <span class="text-red-500">*</span></label>
            <textarea v-model="newCourse.description" required class="w-full px-3 py-2 border rounded-md" rows="3"></textarea>
          </div>
          <div class="mb-4 grid grid-cols-2 gap-4">
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">分类 <span class="text-red-500">*</span></label>
              <select v-model="newCourse.category" required class="w-full px-3 py-2 border rounded-md">
                <option value="计算机科学">计算机科学</option>
                <option value="数学">数学</option>
                <option value="语言">语言</option>
                <option value="自然科学">自然科学</option>
                <option value="测试分类">测试分类</option>
              </select>
            </div>
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">难度 <span class="text-red-500">*</span></label>
              <select v-model="newCourse.difficulty" required class="w-full px-3 py-2 border rounded-md">
                <option value="beginner">初级</option>
                <option value="intermediate">中级</option>
                <option value="advanced">高级</option>
              </select>
            </div>
          </div>
          <div class="mb-4">
            <div class="flex items-center">
              <input type="checkbox" id="is-public" v-model="newCourse.is_public" class="mr-2" />
              <label for="is-public" class="text-gray-700 text-sm font-bold">公开课程</label>
            </div>
          </div>
          <div class="flex justify-end gap-2 mt-6">
            <button type="button" @click="showCreateModal = false" class="px-4 py-2 border rounded-md">取消</button>
            <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md">
              {{ isEditing ? '保存' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue';
import { useAuthStore } from '../../stores/auth';
import { courseAPI } from '../../api';

// 定义Course接口
interface Course {
  id: number;
  name: string;
  description: string;
  category?: string;
  difficulty?: string;
  teacher_name?: string;
  student_count?: number;
  is_public?: boolean;
  cover_image?: string;
  created_at?: string;
  updated_at?: string;
}

const authStore = useAuthStore();
const userRole = computed(() => authStore.user?.role || '');

const courses = ref<Course[]>([]);
const loading = ref(true);
const currentPage = ref(1);
const totalPages = ref(1);
const showCreateModal = ref(false);
const isEditing = ref(false);
const currentCourseId = ref<number | null>(null);

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

// 监听筛选条件变化，自动重新获取课程数据
watch(filters, () => {
  currentPage.value = 1; // 重置到第一页
  fetchCourses();
}, { deep: true });

// 监听搜索框变化，添加防抖
let searchTimeout: number | null = null;
watch(() => filters.search, (newSearch) => {
  if (searchTimeout) {
    clearTimeout(searchTimeout);
  }
  searchTimeout = window.setTimeout(() => {
    currentPage.value = 1; // 重置到第一页
    fetchCourses();
  }, 500); // 500ms防抖
});

async function fetchCourses() {
  loading.value = true;
  try {
    console.log('开始获取课程列表，筛选参数:', {
      page: currentPage.value,
      per_page: 9,
      search: filters.search,
      category: filters.category,
      difficulty: filters.difficulty
    });
    
    // 调用API获取课程列表
    const response = await courseAPI.getCourses({
      page: currentPage.value,
      per_page: 9,
      search: filters.search,
      category: filters.category,
      difficulty: filters.difficulty
    });
    
    console.log('课程API响应:', response);
    
    // 处理API响应数据
    const responseData = response as any; // 类型断言为any以避免TypeScript错误
    if (responseData && responseData.courses) {
      courses.value = responseData.courses;
      totalPages.value = responseData.pages || 1;
      currentPage.value = responseData.page || 1;
      console.log('课程数据设置完成:', {
        课程数量: courses.value.length,
        总页数: totalPages.value,
        当前页: currentPage.value
      });
    } else {
      console.warn('API返回格式不符合预期:', response);
      courses.value = [];
      totalPages.value = 1;
    }
    loading.value = false;
  } catch (error) {
    console.error('获取课程失败:', error);
    loading.value = false;
  }
}

function changePage(page: number) {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  fetchCourses();
}

function difficultyClass(difficulty: string | undefined) {
  switch (difficulty) {
    case 'beginner': return 'bg-green-100 text-green-800';
    case 'intermediate': return 'bg-yellow-100 text-yellow-800';
    case 'advanced': return 'bg-red-100 text-red-800';
    default: return 'bg-gray-100 text-gray-800';
  }
}

function difficultyText(difficulty: string | undefined) {
  switch (difficulty) {
    case 'beginner': return '初级';
    case 'intermediate': return '中级';
    case 'advanced': return '高级';
    default: return '未知';
  }
}

function openCreateModal() {
  // 重置表单
  Object.assign(newCourse, {
    name: '',
    description: '',
    category: '计算机科学',
    difficulty: 'beginner',
    is_public: true
  });
  isEditing.value = false;
  currentCourseId.value = null;
  showCreateModal.value = true;
}

function openEditModal(course: Course) {
  // 填充表单数据
  Object.assign(newCourse, {
    name: course.name,
    description: course.description,
    category: course.category || '计算机科学',
    difficulty: course.difficulty || 'beginner',
    is_public: course.is_public !== false
  });
  isEditing.value = true;
  currentCourseId.value = course.id;
  showCreateModal.value = true;
}

async function saveCourse() {
  try {
    // 验证表单
    if (!newCourse.name || !newCourse.description || !newCourse.category || !newCourse.difficulty) {
      alert('请填写所有必填字段');
      return;
    }
    
    // 准备提交的数据
    const courseData = {
      name: newCourse.name,
      description: newCourse.description,
      category: newCourse.category,
      difficulty: newCourse.difficulty,
      is_public: newCourse.is_public
    };
    
    console.log('准备提交的课程数据:', courseData);
    
    let response;
    
    if (isEditing.value && currentCourseId.value) {
      // 更新现有课程
      console.log('更新课程:', currentCourseId.value);
      response = await courseAPI.updateCourse(currentCourseId.value, courseData);
      console.log('课程更新成功:', response);
      alert('课程更新成功');
    } else {
      // 创建新课程
      console.log('创建新课程');
      response = await courseAPI.createCourse(courseData);
      console.log('课程创建成功:', response);
      alert('课程创建成功');
    }
    
    // 关闭模态框
    showCreateModal.value = false;
    
    // 重新加载课程列表
    await fetchCourses();
  } catch (error) {
    console.error(isEditing.value ? '更新课程失败:' : '创建课程失败:', error);
    alert(isEditing.value ? '更新课程失败，请重试' : '创建课程失败，请重试');
  }
}

async function confirmDeleteCourse(course: Course) {
  if (confirm(`确定要删除课程"${course.name}"吗？此操作不可恢复。`)) {
    try {
      await courseAPI.deleteCourse(course.id);
      alert('课程删除成功');
      // 重新加载课程列表
      await fetchCourses();
    } catch (error) {
      console.error('删除课程失败:', error);
      alert('删除课程失败，请重试');
    }
  }
}
</script> 