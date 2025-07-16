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
            
            <!-- 操作按钮 -->
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
import assessmentAPI from '@/api/assessmentAPI'; // 导入assessmentAPI
import { userAPI } from '@/api'; // 从主API模块导入userAPI

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
// 获取提交列表
const fetchSubmissions = async () => {
  try {
    loading.value = true;
    console.log('开始获取提交列表');
    
    // 准备API参数
    const params = {
      page: currentPage.value,
      per_page: itemsPerPage.value
    };
    
    // 添加过滤参数
    if (filters.value.studentId) {
      params.student_id = filters.value.studentId;
    }
    
    if (filters.value.status === 'graded') {
      params.graded = 'true';
    } else if (filters.value.status === 'ungraded') {
      params.graded = 'false';
    }
    
    let response;
    const assessmentId = props.assessmentId ? (typeof props.assessmentId === 'string' ? parseInt(props.assessmentId) : props.assessmentId) : null;
    const studentId = props.studentId ? (typeof props.studentId === 'string' ? parseInt(props.studentId) : props.studentId) : null;
    
    console.log('准备获取提交，参数:', { assessmentId, studentId, params });
    
    // 根据不同情况调用不同的API
    if (assessmentId) {
      // 如果有评估ID，获取该评估的所有提交
      console.log('通过评估ID获取提交:', assessmentId);
      try {
        response = await assessmentAPI.getSubmissionsByAssessment(assessmentId, params);
        console.log('评估提交API响应:', response);
      } catch (err) {
        console.error('获取评估提交失败:', err);
        if (err.response) {
          console.error('错误响应:', err.response.data);
          console.error('状态码:', err.response.status);
        }
        throw err;
      }
    } else if (studentId) {
      // 如果有学生ID，获取该学生的所有提交
      console.log('通过学生ID获取提交:', studentId);
      try {
        response = await assessmentAPI.getSubmissionsByStudent(studentId, params);
        console.log('学生提交API响应:', response);
      } catch (err) {
        console.error('获取学生提交失败:', err);
        if (err.response) {
          console.error('错误响应:', err.response.data);
          console.error('状态码:', err.response.status);
        }
        throw err;
      }
    } else {
      // 否则使用过滤器获取提交
      console.log('通过过滤器获取提交:', filters.value);
      if (filters.value.assessmentId) {
        try {
          response = await assessmentAPI.getSubmissionsByAssessment(parseInt(filters.value.assessmentId), params);
          console.log('过滤器评估提交API响应:', response);
        } catch (err) {
          console.error('通过过滤器获取评估提交失败:', err);
          if (err.response) {
            console.error('错误响应:', err.response.data);
            console.error('状态码:', err.response.status);
          }
          throw err;
        }
      } else if (filters.value.studentId) {
        try {
          response = await assessmentAPI.getSubmissionsByStudent(parseInt(filters.value.studentId), params);
          console.log('过滤器学生提交API响应:', response);
        } catch (err) {
          console.error('通过过滤器获取学生提交失败:', err);
          if (err.response) {
            console.error('错误响应:', err.response.data);
            console.error('状态码:', err.response.status);
          }
          throw err;
        }
      } else {
        // 默认获取所有提交（在实际系统中可能需要限制）
        console.warn('没有提供具体过滤条件，无法获取提交');
        submissions.value = [];
        loading.value = false;
        return;
      }
    }
    
    console.log('提交响应数据:', response);
    
    // 更新提交列表
    if (response && response.submissions) {
      console.log('找到提交数据:', response.submissions.length, '条记录');
      submissions.value = response.submissions;
      totalItems.value = response.total || response.submissions.length;
      totalPages.value = response.pages || Math.ceil(totalItems.value / itemsPerPage.value);
    } else {
      console.log('未找到提交数据或格式不正确');
      submissions.value = [];
      totalItems.value = 0;
      totalPages.value = 1;
    }
    
    // 如果有学生列表或评估列表，也获取它们用于筛选
    if (props.showStudentFilter) {
      fetchStudents();
    }
    
    if (props.showAssessmentFilter) {
      fetchAssessments();
    }
  } catch (error) {
    console.error('获取提交列表失败:', error);
    submissions.value = [];
  } finally {
    loading.value = false;
  }
};

// 获取学生列表
const fetchStudents = async () => {
  try {
    // 调用API获取学生列表，这里可能需要根据实际API调整
    const response = await userAPI.getUsers({ role: 'student' });
    
    if (response && response.users) {
      students.value = response.users;
    } else {
      students.value = [];
    }
  } catch (error) {
    console.error('获取学生列表失败:', error);
    students.value = [];
  }
};

// 获取评估列表
const fetchAssessments = async () => {
  try {
    // 调用API获取评估列表
    const response = await assessmentAPI.getAssessments();
    
    if (response && response.assessments) {
      assessments.value = response.assessments;
    } else {
      assessments.value = [];
    }
  } catch (error) {
    console.error('获取评估列表失败:', error);
    assessments.value = [];
  }
};

// 查看提交详情
const viewSubmission = (submission) => {
  console.log('View submission:', submission);
  // 跳转到查看提交详情页面，使用评分页面但添加readOnly参数
  router.push(`/submissions/${submission.id}/grade?readOnly=true`);
};

// 评分提交
const gradeSubmission = (submission) => {
  console.log('Grade submission:', submission);
  // 跳转到评分页面
  router.push(`/submissions/${submission.id}/grade`);
};

// 修改评分
const editGrade = (submission) => {
  console.log('Edit grade:', submission);
  // 跳转到评分页面
  router.push(`/submissions/${submission.id}/grade`);
};

// 返回按钮
const goBack = () => {
  emit('back');
  router.back();
};

// 切换页面
const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  fetchSubmissions();
};

// 应用过滤器
const applyFilters = () => {
  currentPage.value = 1;
  fetchSubmissions();
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString();
};

// 获取学生姓名
const getStudentName = (studentId) => {
  const student = students.value.find(s => s.id === studentId);
  return student ? student.full_name || student.username : `学生 ${studentId}`;
};

// 获取评估标题
const getAssessmentTitle = (assessmentId) => {
  const assessment = assessments.value.find(a => a.id === assessmentId);
  return assessment ? assessment.title : `评估 ${assessmentId}`;
};

// 获取评估总分
const getAssessmentTotalScore = (assessmentId) => {
  const assessment = assessments.value.find(a => a.id === assessmentId);
  return assessment ? assessment.total_score : 100;
};

// 获取答案预览
const getAnswerPreview = (submission) => {
  if (!submission.answers) return '无答案数据';
  
  try {
    // 答案可能是字符串或已解析的对象
    const answers = typeof submission.answers === 'string' 
      ? JSON.parse(submission.answers) 
      : submission.answers;
    
    if (Array.isArray(answers)) {
      // 简单展示前几个答案
      return answers.slice(0, 3).map(ans => {
        if (typeof ans === 'object') {
          return JSON.stringify(ans).slice(0, 30) + '...';
        }
        return String(ans).slice(0, 30);
      }).join(', ') + (answers.length > 3 ? '...' : '');
    } else if (typeof answers === 'object') {
      return JSON.stringify(answers).slice(0, 50) + '...';
    }
    
    return String(answers).slice(0, 50) + '...';
  } catch (error) {
    console.error('解析答案预览失败:', error);
    return '答案格式错误';
  }
};

// 检查提交状态
const getStatusClass = (submission) => {
  if (submission.graded_at) {
    return 'bg-green-100 text-green-800';
  } else {
    return 'bg-yellow-100 text-yellow-800';
  }
};

// 获取提交状态文本
const getStatusText = (submission) => {
  if (submission.graded_at) {
    return '已评分';
  } else {
    return '待评分';
  }
};

// 检查是否已评分
const isGraded = (submission) => {
  return submission.graded_at != null;
};

// 监听属性变化
watch(
  () => [props.assessmentId, props.studentId],
  () => {
    // 重置过滤器和页码
    if (props.assessmentId) {
      filters.value.assessmentId = props.assessmentId;
    }
    
    if (props.studentId) {
      filters.value.studentId = props.studentId;
    }
    
    currentPage.value = 1;
    fetchSubmissions();
  },
  { immediate: true }
);

// 初始化
onMounted(() => {
  fetchStudents();
  fetchAssessments();
  fetchSubmissions();
});
</script> 