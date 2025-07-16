<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="border-b border-gray-200 pb-5 mb-5">
          <h1 class="text-3xl font-bold text-gray-900">系统管理</h1>
          <p class="mt-2 text-sm text-gray-500">
            管理用户、课程和系统设置
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

        <!-- 数据概览 -->
        <div v-if="activeTab === 'dashboard'" class="mb-8">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">数据概览</h2>
          <div class="grid grid-cols-1 md:grid-cols-4 gap-5">
            <div class="bg-white overflow-hidden shadow rounded-lg">
              <div class="px-4 py-5 sm:p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0 bg-blue-500 rounded-md p-3">
                    <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 truncate">
                        总用户数
                      </dt>
                      <dd class="mt-1 text-3xl font-semibold text-gray-900">
                        {{ stats.totalUsers || 0 }}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-white overflow-hidden shadow rounded-lg">
              <div class="px-4 py-5 sm:p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0 bg-green-500 rounded-md p-3">
                    <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 truncate">
                        总课程数
                      </dt>
                      <dd class="mt-1 text-3xl font-semibold text-gray-900">
                        {{ stats.totalCourses || 0 }}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-white overflow-hidden shadow rounded-lg">
              <div class="px-4 py-5 sm:p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0 bg-yellow-500 rounded-md p-3">
                    <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 truncate">
                        学习资料
                      </dt>
                      <dd class="mt-1 text-3xl font-semibold text-gray-900">
                        {{ stats.totalMaterials || 0 }}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-white overflow-hidden shadow rounded-lg">
              <div class="px-4 py-5 sm:p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0 bg-purple-500 rounded-md p-3">
                    <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 truncate">
                        总评测数
                      </dt>
                      <dd class="mt-1 text-3xl font-semibold text-gray-900">
                        {{ stats.totalAssessments || 0 }}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 管理功能 -->
        <div v-if="activeTab === 'dashboard'" class="mb-8">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">系统管理</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- 用户管理 -->
            <div class="bg-white overflow-hidden shadow rounded-lg">
              <div class="px-4 py-5 sm:p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0 bg-blue-500 rounded-md p-3">
                    <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <h3 class="text-lg font-medium text-gray-900">用户管理</h3>
                    <p class="mt-1 text-sm text-gray-500">
                      管理系统用户、角色和权限
                    </p>
                  </div>
                </div>
                <div class="mt-5">
                  <button @click="activeTab = 'admin-dashboard'" class="btn btn-primary w-full">
                    管理用户
                  </button>
                </div>
              </div>
            </div>

            <!-- 课程管理 -->
            <div class="bg-white overflow-hidden shadow rounded-lg">
              <div class="px-4 py-5 sm:p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0 bg-green-500 rounded-md p-3">
                    <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <h3 class="text-lg font-medium text-gray-900">课程管理</h3>
                    <p class="mt-1 text-sm text-gray-500">
                      管理课程、教学内容和资源
                    </p>
                  </div>
                </div>
                <div class="mt-5">
                  <button @click="activeTab = 'courses'" class="btn btn-primary w-full">
                    管理课程
                  </button>
                </div>
              </div>
            </div>

            <!-- 系统设置 -->
            <div class="bg-white overflow-hidden shadow rounded-lg">
              <div class="px-4 py-5 sm:p-6">
                <div class="flex items-center">
                  <div class="flex-shrink-0 bg-purple-500 rounded-md p-3">
                    <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <h3 class="text-lg font-medium text-gray-900">系统设置</h3>
                    <p class="mt-1 text-sm text-gray-500">
                      配置系统参数和全局设置
                    </p>
                  </div>
                </div>
                <div class="mt-5">
                  <button @click="activeTab = 'settings'" class="btn btn-primary w-full">
                    系统设置
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 系统日志 -->
        <div v-if="activeTab === 'dashboard'" class="mb-8">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">系统日志</h2>
          <div class="bg-white shadow overflow-hidden rounded-md">
            <ul class="divide-y divide-gray-200">
              <li v-if="!systemLogs || systemLogs.length === 0" class="px-6 py-4 text-center text-gray-500">
                暂无系统日志
              </li>
              <li v-else v-for="(log, index) in systemLogs" :key="index" class="px-6 py-4">
                <div class="flex items-center space-x-4">
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">
                      {{ log.message }}
                    </p>
                    <p class="text-sm text-gray-500 truncate">
                      {{ log.user }} - {{ log.action }}
                    </p>
                  </div>
                  <div class="text-sm text-gray-500">
                    {{ log.time }}
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- 管理面板 -->
        <div v-if="activeTab === 'admin-dashboard'">
          <AdminDashboard activeTab="users" />
        </div>

        <!-- 课程管理 -->
        <div v-if="activeTab === 'courses'">
          <CourseList />
        </div>

        <!-- 系统设置 -->
        <div v-if="activeTab === 'settings'">
          <AdminDashboard activeTab="settings" />
        </div>
        
        <!-- 评估管理 -->
        <div v-if="activeTab === 'assessments'">
          <h2 class="text-xl font-semibold mb-4">评估管理</h2>
          
          <div class="bg-white p-6 rounded-lg shadow-md">
            <div class="mb-6">
              <h3 class="text-lg font-medium">评估列表</h3>
              <p class="text-gray-600 text-sm">管理所有课程的评估和查看学生提交</p>
            </div>
            
            <AssessmentList 
              role="teacher"
              @create="createAssessment"
              @edit="editAssessment"
              @delete="deleteAssessment"
              @view-submissions="viewSubmissions"
              @take="takeAssessment"
            />
          </div>
        </div>
        
        <!-- 提交列表模态框 -->
        <div v-if="showSubmissionsModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white rounded-lg p-6 w-11/12 max-w-6xl max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-xl font-semibold">{{ currentAssessment ? currentAssessment.title : '' }} - 提交列表</h3>
              <button @click="closeSubmissionsModal" class="text-gray-500 hover:text-gray-700">
                <span class="text-2xl">&times;</span>
              </button>
            </div>
            
            <SubmissionList 
              :assessment-id="currentAssessment ? currentAssessment.id : null"
              :show-back-button="false"
              :show-assessment-filter="false"
              :show-assessment-info="false"
              role="teacher"
              @view="viewSubmissionDetail"
              @grade="gradeSubmission"
              @edit-grade="editGrade"
            />
          </div>
        </div>
        
        <!-- 评分模态框 -->
        <div v-if="showGradingModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white rounded-lg p-6 w-11/12 max-w-4xl max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-xl font-semibold">评分 - {{ getStudentName(currentSubmission?.student_id || 0) }}</h3>
              <button @click="closeGradingModal" class="text-gray-500 hover:text-gray-700">
                <span class="text-2xl">&times;</span>
              </button>
            </div>
            
            <div class="space-y-6">
              <!-- 学生信息 -->
              <div class="bg-gray-50 p-4 rounded-md">
                <p><span class="font-medium">学生:</span> {{ getStudentName(currentSubmission?.student_id || 0) }}</p>
                <p><span class="font-medium">评估:</span> {{ getAssessmentTitle(currentSubmission?.assessment_id || 0) }}</p>
                <p><span class="font-medium">提交时间:</span> {{ formatDate(currentSubmission?.submitted_at || '') }}</p>
              </div>
              
              <!-- 答案预览 -->
              <div>
                <h4 class="text-lg font-medium mb-2">学生答案</h4>
                <div class="bg-gray-50 p-4 rounded-md">
                  <pre class="whitespace-pre-wrap">{{ formatAnswers(currentSubmission?.answers || '') }}</pre>
                </div>
              </div>
              
              <!-- 评分表单 -->
              <div>
                <h4 class="text-lg font-medium mb-2">评分</h4>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">分数</label>
                    <input 
                      type="number" 
                      v-model="gradingForm.score"
                      min="0"
                      :max="getAssessmentTotalScore(currentSubmission?.assessment_id || 0)"
                      class="w-full px-3 py-2 border rounded-md"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">反馈</label>
                    <textarea 
                      v-model="gradingForm.feedback"
                      rows="4"
                      class="w-full px-3 py-2 border rounded-md"
                      placeholder="请输入对学生的反馈..."
                    ></textarea>
                  </div>
                  <div class="flex justify-end">
                    <button 
                      @click="submitGrade"
                      class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      提交评分
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AdminDashboard from '@/components/admin/AdminDashboard.vue';
import CourseList from '@/components/course/CourseList.vue';
import WelcomeMessage from '@/components/WelcomeMessage.vue';
import AssessmentList from '../components/assessment/AssessmentList.vue';
import SubmissionList from '../components/assessment/SubmissionList.vue';

const authStore = useAuthStore();
const router = useRouter();

// 标签页
const tabs = [
  { id: 'dashboard', name: '概览' },
  { id: 'admin-dashboard', name: '用户管理' },
  { id: 'courses', name: '课程管理' },
  { id: 'assessments', name: '评估管理' },
  { id: 'settings', name: '系统设置' }
];
const activeTab = ref('dashboard');

// 示例数据
const stats = ref({
  totalUsers: 45,
  totalCourses: 12,
  totalMaterials: 68,
  totalAssessments: 124
});

const systemLogs = ref([
  {
    message: '系统备份完成',
    user: 'system',
    action: '自动备份',
    time: '10分钟前'
  },
  {
    message: '新用户注册',
    user: 'admin',
    action: '用户创建',
    time: '1小时前'
  },
  {
    message: '课程内容更新',
    user: 'teacher1',
    action: '内容更新',
    time: '2小时前'
  }
]);

// 状态变量
const showSubmissionsModal = ref(false);
const showGradingModal = ref(false);
const currentAssessment = ref<{ id: number; title: string; total_score: number } | null>(null);
const currentSubmission = ref<{ 
  id: number; 
  student_id: number; 
  assessment_id: number; 
  answers: string;
  score?: number;
  feedback?: string;
  submitted_at: string;
  graded_at?: string;
} | null>(null);
const gradingForm = ref({
  score: 0,
  feedback: ''
});

// 学生和评估数据（实际应用中应该从API获取）
const students = ref([
  { id: 1, name: '张三' },
  { id: 2, name: '李四' },
  { id: 3, name: '王五' }
]);

const assessments = ref([
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
]);

// 方法
const createAssessment = () => {
  // 跳转到创建评估页面或打开模态框
  console.log('创建评估');
};

const editAssessment = (assessment: any) => {
  // 跳转到编辑评估页面或打开模态框
  console.log('编辑评估', assessment);
};

const deleteAssessment = (assessment: any) => {
  // 删除评估
  console.log('删除评估', assessment);
};

const viewSubmissions = (data: { assessment: any }) => {
  currentAssessment.value = data.assessment;
  showSubmissionsModal.value = true;
};

const closeSubmissionsModal = () => {
  showSubmissionsModal.value = false;
  currentAssessment.value = null;
};

const viewSubmissionDetail = (submission: any) => {
  // 查看提交详情
  console.log('查看提交详情', submission);
};

const gradeSubmission = (submission: any) => {
  currentSubmission.value = submission;
  gradingForm.value = {
    score: submission.score || 0,
    feedback: submission.feedback || ''
  };
  showGradingModal.value = true;
};

const editGrade = (submission: any) => {
  // 与评分相同，但使用已有的分数和反馈
  gradeSubmission(submission);
};

const closeGradingModal = () => {
  showGradingModal.value = false;
  currentSubmission.value = null;
};

const submitGrade = async () => {
  try {
    // 实际应用中，这里应该调用API
    // const response = await fetch(`/api/submissions/${currentSubmission.value.id}/grade`, {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json',
    //   },
    //   body: JSON.stringify({
    //     score: gradingForm.value.score,
    //     feedback: gradingForm.value.feedback
    //   }),
    // });
    // const data = await response.json();
    
    if (!currentSubmission.value) return;
    
    console.log('提交评分', {
      submissionId: currentSubmission.value.id,
      score: gradingForm.value.score,
      feedback: gradingForm.value.feedback
    });
    
    // 更新当前提交的评分信息
    currentSubmission.value.score = gradingForm.value.score;
    currentSubmission.value.feedback = gradingForm.value.feedback;
    currentSubmission.value.graded_at = new Date().toISOString();
    
    // 关闭模态框
    closeGradingModal();
  } catch (error) {
    console.error('评分失败:', error);
  }
};

const getStudentName = (studentId: number) => {
  const student = students.value.find(s => s.id === studentId);
  return student ? student.name : `学生 ${studentId}`;
};

const getAssessmentTitle = (assessmentId: number) => {
  const assessment = assessments.value.find(a => a.id === assessmentId);
  return assessment ? assessment.title : `评估 ${assessmentId}`;
};

const getAssessmentTotalScore = (assessmentId: number) => {
  const assessment = assessments.value.find(a => a.id === assessmentId);
  return assessment ? assessment.total_score : 100;
};

const formatDate = (dateString: string) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString();
};

const formatAnswers = (answersJson: string) => {
  try {
    const answers = JSON.parse(answersJson);
    return JSON.stringify(answers, null, 2);
  } catch (error) {
    return answersJson || '无答案';
  }
};

const takeAssessment = (assessment: any) => {
  // 导航到评估播放器
  console.log('开始评估', assessment);
  router.push(`/assessments/${assessment.id}/take`);
};
</script>

<style scoped>
.btn {
  padding: 0.5rem 1rem;
  border: 1px solid transparent;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.375rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.btn:focus {
  outline: none;
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px rgba(59, 130, 246, 0.5);
}

.btn-primary {
  color: white;
  background-color: #2563eb;
}

.btn-primary:hover {
  background-color: #1d4ed8;
}

.btn-primary:focus {
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px rgba(59, 130, 246, 0.5);
}
</style>