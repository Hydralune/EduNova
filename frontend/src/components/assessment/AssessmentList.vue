<template>
  <div class="assessment-list">
    <div class="mb-6 flex justify-between items-center">
      <h2 class="text-xl font-semibold">评估列表</h2>
      <div v-if="isTeacher">
        <button 
          @click="createNewAssessment" 
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          创建评估
        </button>
      </div>
    </div>
    
    <!-- 过滤器 -->
    <div class="bg-white p-4 rounded-lg shadow-md mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">课程</label>
          <select 
            v-model="filters.courseId"
            class="w-full px-3 py-2 border rounded-md"
          >
            <option value="">全部课程</option>
            <option v-for="course in courses" :key="course.id" :value="course.id">
              {{ course.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">状态</label>
          <select 
            v-model="filters.status"
            class="w-full px-3 py-2 border rounded-md"
          >
            <option value="">全部状态</option>
            <option value="active">进行中</option>
            <option value="upcoming">即将开始</option>
            <option value="past">已结束</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">搜索</label>
          <input 
            type="text" 
            v-model="filters.search"
            placeholder="搜索评估标题..."
            class="w-full px-3 py-2 border rounded-md"
          />
        </div>
      </div>
      <div class="mt-4 flex justify-end">
        <button 
          @click="applyFilters"
          class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
        >
          应用过滤
        </button>
      </div>
    </div>
    
    <!-- 评估列表 -->
    <div v-if="loading" class="text-center py-10">
      <p class="text-gray-500">加载中...</p>
    </div>
    
    <div v-else-if="assessments.length === 0" class="text-center py-10 bg-gray-50 rounded-md">
      <p class="text-gray-500">暂无评估</p>
    </div>
    
    <div v-else class="space-y-4">
      <div 
        v-for="assessment in assessments" 
        :key="assessment.id"
        class="bg-white p-6 rounded-lg shadow-md border border-gray-200"
      >
        <div class="flex justify-between items-start">
          <div>
            <h3 class="text-lg font-semibold">{{ assessment.title }}</h3>
            <p class="text-sm text-gray-600">{{ assessment.description }}</p>
            <div class="mt-2 flex flex-wrap gap-x-4 gap-y-2 text-sm text-gray-500">
              <span>课程: {{ getCourseNameById(assessment.course_id) }}</span>
              <span>总分: {{ assessment.total_score }}</span>
              <span>题目数: {{ getTotalQuestions(assessment) }}</span>
              <span>时间限制: {{ assessment.duration || '无限制' }}</span>
              <span>截止日期: {{ formatDate(assessment.due_date) }}</span>
              <span>尝试次数: {{ assessment.max_attempts || '无限制' }}</span>
            </div>
          </div>
          
          <div class="flex flex-col gap-2">
            <span 
              :class="getStatusClass(assessment)"
              class="px-2 py-1 text-xs rounded-full"
            >
              {{ getStatusText(assessment) }}
            </span>
            
            <div class="flex gap-2 mt-2">
              <router-link 
                :to="`/assessments/${assessment.id}`" 
                class="text-blue-600 hover:text-blue-800"
              >
                查看
              </router-link>
              
              <span v-if="isTeacher" class="text-gray-300">|</span>
              
              <button 
                v-if="isTeacher"
                @click="editAssessment(assessment)" 
                class="text-blue-600 hover:text-blue-800"
              >
                编辑
              </button>
              
              <span v-if="isTeacher" class="text-gray-300">|</span>
              
              <button 
                v-if="isTeacher"
                @click="deleteAssessment(assessment)" 
                class="text-red-600 hover:text-red-800"
              >
                删除
              </button>
            </div>
          </div>
        </div>
        
        <!-- 学生提交状态 -->
        <div v-if="isStudent && assessment.submissions" class="mt-4 pt-4 border-t">
          <div class="flex justify-between items-center">
            <div>
              <p class="text-sm">
                <span class="font-medium">提交状态:</span>
                {{ assessment.submissions.length > 0 ? `已提交 ${assessment.submissions.length} 次` : '未提交' }}
              </p>
              <p v-if="assessment.submissions && assessment.submissions.length > 0" class="text-sm">
                <span class="font-medium">最高分:</span>
                {{ getHighestScore(assessment.submissions) }} / {{ assessment.total_score }}
              </p>
            </div>
            <div>
              <button 
                v-if="canTakeAssessment(assessment)"
                @click="takeAssessment(assessment)" 
                class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                {{ assessment.submissions && assessment.submissions.length > 0 ? '重新尝试' : '开始' }}
              </button>
              <button 
                v-else-if="assessment.submissions && assessment.submissions.length > 0"
                @click="viewSubmissions(assessment)" 
                class="px-4 py-2 border rounded-md hover:bg-gray-50"
              >
                查看提交
              </button>
            </div>
          </div>
        </div>
        
        <!-- 教师查看提交 -->
        <div v-if="isTeacher" class="mt-4 pt-4 border-t">
          <div class="flex justify-between items-center">
            <p class="text-sm">
              <span class="font-medium">提交数:</span>
              {{ assessment.submission_count || 0 }}
            </p>
            <button 
              v-if="assessment.submission_count > 0"
              @click="viewAllSubmissions(assessment)" 
              class="px-4 py-2 border rounded-md hover:bg-gray-50"
            >
              查看提交
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 分页 -->
    <div v-if="totalPages > 1" class="mt-6 flex justify-center">
      <div class="flex space-x-1">
        <button 
          @click="changePage(currentPage - 1)" 
          :disabled="currentPage === 1"
          class="px-3 py-1 border rounded-md"
          :class="currentPage === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50'"
        >
          上一页
        </button>
        
        <button 
          v-for="page in paginationRange" 
          :key="page"
          @click="changePage(page)"
          class="px-3 py-1 border rounded-md"
          :class="page === currentPage ? 'bg-blue-600 text-white' : 'hover:bg-gray-50'"
        >
          {{ page }}
        </button>
        
        <button 
          @click="changePage(currentPage + 1)" 
          :disabled="currentPage === totalPages"
          class="px-3 py-1 border rounded-md"
          :class="currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50'"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
  courseId: {
    type: [Number, String],
    default: null
  },
  role: {
    type: String,
    default: 'student' // 'student', 'teacher'
  }
});

const emit = defineEmits(['create', 'edit', 'delete', 'take', 'view-submissions']);

const router = useRouter();

// 状态变量
const assessments = ref([]);
const courses = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const totalPages = ref(1);
const totalItems = ref(0);
const itemsPerPage = ref(10);

// 过滤器
const filters = ref({
  courseId: props.courseId || '',
  status: '',
  search: ''
});

// 计算属性
const isTeacher = computed(() => props.role === 'teacher');
const isStudent = computed(() => props.role === 'student');

const paginationRange = computed(() => {
  const range = [];
  const maxVisiblePages = 5;
  
  if (totalPages.value <= maxVisiblePages) {
    // 如果总页数小于等于最大可见页数，显示所有页码
    for (let i = 1; i <= totalPages.value; i++) {
      range.push(i);
    }
  } else {
    // 否则，显示当前页附近的页码
    let start = Math.max(1, currentPage.value - Math.floor(maxVisiblePages / 2));
    let end = Math.min(totalPages.value, start + maxVisiblePages - 1);
    
    // 调整起始页，确保显示正确数量的页码
    if (end - start + 1 < maxVisiblePages) {
      start = Math.max(1, end - maxVisiblePages + 1);
    }
    
    for (let i = start; i <= end; i++) {
      range.push(i);
    }
  }
  
  return range;
});

// 方法
const fetchAssessments = async () => {
  loading.value = true;
  
  try {
    // 构建查询参数
    const params = new URLSearchParams();
    params.append('page', currentPage.value);
    params.append('per_page', itemsPerPage.value);
    
    if (filters.value.courseId) {
      params.append('course_id', filters.value.courseId);
    }
    
    if (filters.value.status === 'active') {
      params.append('is_active', 'true');
    } else if (filters.value.status === 'inactive') {
      params.append('is_active', 'false');
    }
    
    if (filters.value.search) {
      params.append('search', filters.value.search);
    }
    
    // 发送请求
    // 实际应用中，这里应该调用API
    // const response = await fetch(`/api/assessments?${params.toString()}`);
    // const data = await response.json();
    
    // 模拟数据
    await new Promise(resolve => setTimeout(resolve, 500));
    const data = {
      assessments: [
        {
          id: 1,
          title: '第一章测验',
          description: '测试对第一章内容的理解',
          course_id: 1,
          total_score: 100,
          duration: '30分钟',
          due_date: '2025-07-15T23:59:59Z',
          start_date: '2025-06-01T09:00:00Z',
          max_attempts: 3,
          is_active: true,
          created_at: '2025-06-01T10:00:00Z',
          updated_at: '2025-06-01T10:00:00Z',
          submission_count: 5
        },
        {
          id: 2,
          title: '期中考试',
          description: '涵盖第1-5章内容',
          course_id: 1,
          total_score: 100,
          duration: '120分钟',
          due_date: '2025-08-15T23:59:59Z',
          start_date: '2025-08-15T09:00:00Z',
          max_attempts: 1,
          is_active: false,
          created_at: '2025-06-01T10:00:00Z',
          updated_at: '2025-06-01T10:00:00Z',
          submission_count: 0
        }
      ],
      total: 2,
      pages: 1,
      current_page: 1
    };
    
    assessments.value = data.assessments;
    totalItems.value = data.total;
    totalPages.value = data.pages;
    currentPage.value = data.current_page;
    
    // 如果是学生，获取提交状态
    if (isStudent.value) {
      await fetchStudentSubmissions();
    }
  } catch (error) {
    console.error('获取评估列表失败:', error);
  } finally {
    loading.value = false;
  }
};

const fetchCourses = async () => {
  try {
    // 实际应用中，这里应该调用API
    // const response = await fetch('/api/courses');
    // const data = await response.json();
    
    // 模拟数据
    const data = {
      courses: [
        { id: 1, name: 'Web开发基础' },
        { id: 2, name: '前端框架进阶' }
      ]
    };
    
    courses.value = data.courses;
  } catch (error) {
    console.error('获取课程列表失败:', error);
  }
};

const fetchStudentSubmissions = async () => {
  try {
    // 实际应用中，这里应该调用API
    // const response = await fetch(`/api/students/1/submissions`);
    // const data = await response.json();
    
    // 模拟数据
    const data = {
      submissions: [
        {
          id: 1,
          student_id: 1,
          assessment_id: 1,
          score: 85,
          submitted_at: '2025-06-10T15:30:00Z',
          graded_at: '2025-06-11T10:15:00Z'
        }
      ]
    };
    
    // 将提交数据添加到对应的评估中
    assessments.value.forEach(assessment => {
      assessment.submissions = data.submissions.filter(
        submission => submission.assessment_id === assessment.id
      );
    });
  } catch (error) {
    console.error('获取提交状态失败:', error);
  }
};

const applyFilters = () => {
  currentPage.value = 1;
  fetchAssessments();
};

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  fetchAssessments();
};

const getCourseNameById = (courseId) => {
  const course = courses.value.find(c => c.id === courseId);
  return course ? course.name : '未知课程';
};

const getTotalQuestions = (assessment) => {
  // 实际应用中，应该从评估的questions字段中计算题目数量
  return 10; // 示例值
};

const formatDate = (dateString) => {
  if (!dateString) return '无截止日期';
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

const getStatusText = (assessment) => {
  const now = new Date();
  const startDate = assessment.start_date ? new Date(assessment.start_date) : null;
  const dueDate = assessment.due_date ? new Date(assessment.due_date) : null;
  
  if (!assessment.is_active) {
    return '未发布';
  } else if (startDate && now < startDate) {
    return '即将开始';
  } else if (dueDate && now > dueDate) {
    return '已结束';
  } else {
    return '进行中';
  }
};

const getStatusClass = (assessment) => {
  const status = getStatusText(assessment);
  
  switch (status) {
    case '未发布':
      return 'bg-gray-100 text-gray-800';
    case '即将开始':
      return 'bg-yellow-100 text-yellow-800';
    case '进行中':
      return 'bg-green-100 text-green-800';
    case '已结束':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getHighestScore = (submissions) => {
  if (!submissions || submissions.length === 0) return 0;
  return Math.max(...submissions.map(s => s.score || 0));
};

const canTakeAssessment = (assessment) => {
  const now = new Date();
  const startDate = assessment.start_date ? new Date(assessment.start_date) : null;
  const dueDate = assessment.due_date ? new Date(assessment.due_date) : null;
  
  // 检查评估是否激活
  if (!assessment.is_active) return false;
  
  // 检查是否在有效时间范围内
  if (startDate && now < startDate) return false;
  if (dueDate && now > dueDate) return false;
  
  // 检查尝试次数
  if (assessment.max_attempts && assessment.submissions) {
    if (assessment.submissions.length >= assessment.max_attempts) return false;
  }
  
  return true;
};

const createNewAssessment = () => {
  emit('create');
};

const editAssessment = (assessment) => {
  emit('edit', assessment);
};

const deleteAssessment = (assessment) => {
  if (confirm(`确定要删除评估 "${assessment.title}" 吗？`)) {
    emit('delete', assessment);
  }
};

const takeAssessment = (assessment) => {
  emit('take', assessment);
  // 或者直接导航到评估页面
  // router.push(`/assessments/${assessment.id}/take`);
};

const viewSubmissions = (assessment) => {
  emit('view-submissions', { assessment, student: true });
  // 或者直接导航到提交页面
  // router.push(`/assessments/${assessment.id}/submissions`);
};

const viewAllSubmissions = (assessment) => {
  emit('view-submissions', { assessment, student: false });
  // 或者直接导航到提交页面
  // router.push(`/assessments/${assessment.id}/all-submissions`);
};

// 监听过滤器变化
watch(() => props.courseId, (newVal) => {
  if (newVal !== filters.value.courseId) {
    filters.value.courseId = newVal || '';
    currentPage.value = 1;
    fetchAssessments();
  }
});

// 初始化
onMounted(() => {
  fetchCourses();
  fetchAssessments();
});
</script> 