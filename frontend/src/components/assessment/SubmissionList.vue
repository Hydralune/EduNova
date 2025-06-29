<template>
  <div class="submission-list">
    <div class="mb-6 flex justify-between items-center">
      <h2 class="text-xl font-semibold">{{ title }}</h2>
      <div v-if="showBackButton">
        <button 
          @click="goBack" 
          class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
        >
          返回
        </button>
      </div>
    </div>
    
    <!-- 过滤器 -->
    <div v-if="showFilters" class="bg-white p-4 rounded-lg shadow-md mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-if="showStudentFilter">
          <label class="block text-sm font-medium text-gray-700 mb-1">学生</label>
          <select 
            v-model="filters.studentId"
            class="w-full px-3 py-2 border rounded-md"
          >
            <option value="">全部学生</option>
            <option v-for="student in students" :key="student.id" :value="student.id">
              {{ student.name }}
            </option>
          </select>
        </div>
        <div v-if="showAssessmentFilter">
          <label class="block text-sm font-medium text-gray-700 mb-1">评估</label>
          <select 
            v-model="filters.assessmentId"
            class="w-full px-3 py-2 border rounded-md"
          >
            <option value="">全部评估</option>
            <option v-for="assessment in assessments" :key="assessment.id" :value="assessment.id">
              {{ assessment.title }}
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
            <option value="graded">已评分</option>
            <option value="ungraded">未评分</option>
          </select>
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
    
    <!-- 提交列表 -->
    <div v-if="loading" class="text-center py-10">
      <p class="text-gray-500">加载中...</p>
    </div>
    
    <div v-else-if="submissions.length === 0" class="text-center py-10 bg-gray-50 rounded-md">
      <p class="text-gray-500">暂无提交</p>
    </div>
    
    <div v-else class="space-y-4">
      <div 
        v-for="submission in submissions" 
        :key="submission.id"
        class="bg-white p-6 rounded-lg shadow-md border border-gray-200"
      >
        <div class="flex justify-between items-start">
          <div>
            <div v-if="showStudentInfo" class="mb-2">
              <h3 class="text-lg font-semibold">{{ getStudentName(submission.student_id) }}</h3>
              <p class="text-sm text-gray-600">学生ID: {{ submission.student_id }}</p>
            </div>
            <div v-if="showAssessmentInfo" class="mb-2">
              <h3 class="text-lg font-semibold">{{ getAssessmentTitle(submission.assessment_id) }}</h3>
              <p class="text-sm text-gray-600">评估ID: {{ submission.assessment_id }}</p>
            </div>
            <div class="mt-2 flex flex-wrap gap-x-4 gap-y-2 text-sm text-gray-500">
              <span>提交时间: {{ formatDate(submission.submitted_at) }}</span>
              <span v-if="submission.graded_at">评分时间: {{ formatDate(submission.graded_at) }}</span>
              <span v-if="submission.score !== null && submission.score !== undefined">
                分数: {{ submission.score }} / {{ getAssessmentTotalScore(submission.assessment_id) }}
              </span>
            </div>
          </div>
          
          <div class="flex flex-col gap-2">
            <span 
              :class="getStatusClass(submission)"
              class="px-2 py-1 text-xs rounded-full"
            >
              {{ getStatusText(submission) }}
            </span>
            
            <div class="flex gap-2 mt-2">
              <button 
                @click="viewSubmission(submission)" 
                class="text-blue-600 hover:text-blue-800"
              >
                查看详情
              </button>
              
              <span v-if="canGrade" class="text-gray-300">|</span>
              
              <button 
                v-if="canGrade && !isGraded(submission)"
                @click="gradeSubmission(submission)" 
                class="text-blue-600 hover:text-blue-800"
              >
                评分
              </button>
              
              <button 
                v-else-if="canGrade && isGraded(submission)"
                @click="editGrade(submission)" 
                class="text-blue-600 hover:text-blue-800"
              >
                修改评分
              </button>
            </div>
          </div>
        </div>
        
        <!-- 简要答案预览 -->
        <div class="mt-4 pt-4 border-t">
          <p class="text-sm font-medium text-gray-700 mb-2">答案预览:</p>
          <div class="text-sm text-gray-600 bg-gray-50 p-3 rounded-md max-h-20 overflow-y-auto">
            {{ getAnswerPreview(submission) }}
          </div>
        </div>
        
        <!-- 反馈信息 -->
        <div v-if="submission.feedback" class="mt-4 pt-4 border-t">
          <p class="text-sm font-medium text-gray-700 mb-2">教师反馈:</p>
          <div class="text-sm text-gray-600 bg-gray-50 p-3 rounded-md">
            {{ submission.feedback }}
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
  title: {
    type: String,
    default: '提交列表'
  },
  assessmentId: {
    type: [Number, String],
    default: null
  },
  studentId: {
    type: [Number, String],
    default: null
  },
  role: {
    type: String,
    default: 'student' // 'student', 'teacher'
  },
  showBackButton: {
    type: Boolean,
    default: true
  },
  showFilters: {
    type: Boolean,
    default: true
  },
  showStudentFilter: {
    type: Boolean,
    default: true
  },
  showAssessmentFilter: {
    type: Boolean,
    default: true
  },
  showStudentInfo: {
    type: Boolean,
    default: true
  },
  showAssessmentInfo: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['view', 'grade', 'edit-grade', 'back']);

const router = useRouter();

// 状态变量
const submissions = ref([]);
const students = ref([]);
const assessments = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const totalPages = ref(1);
const totalItems = ref(0);
const itemsPerPage = ref(10);

// 过滤器
const filters = ref({
  studentId: props.studentId || '',
  assessmentId: props.assessmentId || '',
  status: ''
});

// 计算属性
const canGrade = computed(() => props.role === 'teacher');

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
const fetchSubmissions = async () => {
  loading.value = true;
  
  try {
    // 构建查询参数
    const params = new URLSearchParams();
    params.append('page', currentPage.value);
    params.append('per_page', itemsPerPage.value);
    
    if (filters.value.studentId) {
      params.append('student_id', filters.value.studentId);
    }
    
    if (filters.value.assessmentId) {
      params.append('assessment_id', filters.value.assessmentId);
    }
    
    if (filters.value.status === 'graded') {
      params.append('graded', 'true');
    } else if (filters.value.status === 'ungraded') {
      params.append('graded', 'false');
    }
    
    // 发送请求
    // 实际应用中，这里应该调用API
    // let url = '/api/submissions';
    // if (props.assessmentId) {
    //   url = `/api/assessments/${props.assessmentId}/submissions`;
    // } else if (props.studentId) {
    //   url = `/api/students/${props.studentId}/submissions`;
    // }
    // const response = await fetch(`${url}?${params.toString()}`);
    // const data = await response.json();
    
    // 模拟数据
    await new Promise(resolve => setTimeout(resolve, 500));
    const data = {
      submissions: [
        {
          id: 1,
          student_id: 1,
          assessment_id: 1,
          answers: JSON.stringify({
            "1": "C",
            "2": "B",
            "3": ["A", "C", "D"],
            "4": "defineComponent",
            "5": ["reactive", "ref"],
            "6": "true",
            "7": "false",
            "8": "Vue的生命周期钩子包括created, mounted, updated, unmounted等...",
            "9": "Vue和React都是现代前端框架，但有不同的设计理念..."
          }),
          score: 85,
          feedback: "整体表现不错，但在React和Vue的比较中缺少具体案例。",
          submitted_at: '2025-06-10T15:30:00Z',
          graded_at: '2025-06-11T10:15:00Z',
          graded_by: 2
        },
        {
          id: 2,
          student_id: 2,
          assessment_id: 1,
          answers: JSON.stringify({
            "1": "C",
            "2": "A", // 错误答案
            "3": ["A", "C"],
            "4": "createComponent", // 错误答案
            "5": ["reactive", "ref"],
            "6": "true",
            "7": "false",
            "8": "Vue生命周期包括beforeCreate, created...",
            "9": "Vue使用模板语法，React使用JSX..."
          }),
          score: 70,
          feedback: "对Vue和React的理解基本正确，但有些细节概念不清晰。",
          submitted_at: '2025-06-09T14:20:00Z',
          graded_at: '2025-06-11T10:30:00Z',
          graded_by: 2
        },
        {
          id: 3,
          student_id: 3,
          assessment_id: 1,
          answers: JSON.stringify({
            "1": "C",
            "2": "B",
            "3": ["A", "C", "D"],
            "4": "defineComponent",
            "5": ["reactive", "ref"],
            "6": "true",
            "7": "false",
            "8": "Vue的生命周期包括...",
            "9": "Vue和React的比较..."
          }),
          submitted_at: '2025-06-11T09:45:00Z'
        }
      ],
      total: 3,
      pages: 1,
      current_page: 1
    };
    
    submissions.value = data.submissions;
    totalItems.value = data.total;
    totalPages.value = data.pages;
    currentPage.value = data.current_page;
  } catch (error) {
    console.error('获取提交列表失败:', error);
  } finally {
    loading.value = false;
  }
};

const fetchStudents = async () => {
  try {
    // 实际应用中，这里应该调用API
    // const response = await fetch('/api/students');
    // const data = await response.json();
    
    // 模拟数据
    const data = {
      students: [
        { id: 1, name: '张三' },
        { id: 2, name: '李四' },
        { id: 3, name: '王五' }
      ]
    };
    
    students.value = data.students;
  } catch (error) {
    console.error('获取学生列表失败:', error);
  }
};

const fetchAssessments = async () => {
  try {
    // 实际应用中，这里应该调用API
    // const response = await fetch('/api/assessments');
    // const data = await response.json();
    
    // 模拟数据
    const data = {
      assessments: [
        {
          id: 1,
          title: '第一章测验',
          total_score: 100
        },
        {
          id: 2,
          title: '期中考试',
          total_score: 100
        }
      ]
    };
    
    assessments.value = data.assessments;
  } catch (error) {
    console.error('获取评估列表失败:', error);
  }
};

const applyFilters = () => {
  currentPage.value = 1;
  fetchSubmissions();
};

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  fetchSubmissions();
};

const getStudentName = (studentId) => {
  const student = students.value.find(s => s.id === studentId);
  return student ? student.name : `学生 ${studentId}`;
};

const getAssessmentTitle = (assessmentId) => {
  const assessment = assessments.value.find(a => a.id === assessmentId);
  return assessment ? assessment.title : `评估 ${assessmentId}`;
};

const getAssessmentTotalScore = (assessmentId) => {
  const assessment = assessments.value.find(a => a.id === assessmentId);
  return assessment ? assessment.total_score : 100;
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString();
};

const getStatusText = (submission) => {
  if (submission.graded_at) {
    return '已评分';
  } else {
    return '待评分';
  }
};

const getStatusClass = (submission) => {
  if (submission.graded_at) {
    return 'bg-green-100 text-green-800';
  } else {
    return 'bg-yellow-100 text-yellow-800';
  }
};

const isGraded = (submission) => {
  return !!submission.graded_at;
};

const getAnswerPreview = (submission) => {
  try {
    const answers = JSON.parse(submission.answers);
    // 生成简短的预览
    const keys = Object.keys(answers);
    if (keys.length === 0) return '无答案';
    
    // 选择前两个问题的答案作为预览
    const previewKeys = keys.slice(0, 2);
    const preview = previewKeys.map(key => {
      const answer = answers[key];
      if (Array.isArray(answer)) {
        return `问题${key}: ${answer.join(', ')}`;
      } else if (typeof answer === 'string' && answer.length > 30) {
        return `问题${key}: ${answer.substring(0, 30)}...`;
      } else {
        return `问题${key}: ${answer}`;
      }
    }).join(' | ');
    
    return keys.length > 2 ? `${preview} | ...` : preview;
  } catch (error) {
    return '答案格式错误';
  }
};

const viewSubmission = (submission) => {
  emit('view', submission);
};

const gradeSubmission = (submission) => {
  emit('grade', submission);
};

const editGrade = (submission) => {
  emit('edit-grade', submission);
};

const goBack = () => {
  emit('back');
};

// 监听过滤器变化
watch(() => props.assessmentId, (newVal) => {
  if (newVal !== filters.value.assessmentId) {
    filters.value.assessmentId = newVal || '';
    currentPage.value = 1;
    fetchSubmissions();
  }
});

watch(() => props.studentId, (newVal) => {
  if (newVal !== filters.value.studentId) {
    filters.value.studentId = newVal || '';
    currentPage.value = 1;
    fetchSubmissions();
  }
});

// 初始化
onMounted(() => {
  fetchStudents();
  fetchAssessments();
  fetchSubmissions();
});
</script> 