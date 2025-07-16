<template>
  <main class="flex-1">
    <div class="container mx-auto py-6 px-4">
      <div v-if="loading" class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>

      <div v-else>
        <!-- 教师编辑模式 -->
        <div v-if="isTeacher && editMode">
          <AssessmentEditor 
            :initial-assessment="assessment"
            @save="saveAssessment"
            @cancel="editMode = false"
          />
        </div>

        <!-- 教师查看模式 -->
        <div v-else-if="isTeacher && !editMode" class="max-w-7xl mx-auto">
          <div class="bg-white p-6 rounded-lg shadow-md mb-6">
            <div class="flex justify-between items-center">
              <div>
                <div class="flex items-center gap-3 mb-2">
                  <button 
                    @click="goBack" 
                    class="p-2 bg-white shadow-md rounded-lg hover:bg-gray-50 text-gray-700 flex items-center justify-center"
                    style="width: 40px; height: 40px;"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                  </button>
                  <h1 class="text-2xl font-bold">{{ assessment.title }}</h1>
                </div>
                <p class="text-gray-600 mt-1">{{ assessment.description }}</p>
              </div>
              <div class="text-right">
                <p class="text-sm text-gray-600">总分: {{ assessment.total_score }} 分</p>
                <p v-if="assessment.due_date" class="text-sm" :class="isDeadlinePassed ? 'text-red-600 font-bold' : 'text-green-600'">
                  截止日期: {{ formatDate(assessment.due_date) }}
                  <span v-if="isDeadlinePassed" class="ml-2">(已过期)</span>
                </p>
                <p v-if="assessment.max_attempts" class="text-sm text-gray-600">
                  最大尝试次数: {{ assessment.max_attempts }}
                </p>
              </div>
            </div>
            
            <!-- 状态提示 -->
            <div v-if="isDeadlinePassed || submitted" class="mt-4 p-3 rounded-md" :class="statusClass">
              <div class="flex items-center">
                <svg v-if="isDeadlinePassed" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <span>{{ statusMessage }}</span>
              </div>
            </div>
          </div>
          
          <!-- 题目预览 -->
          <div class="space-y-8 max-w-7xl mx-auto">
            <div v-for="(section, sectionIndex) in assessment.sections" :key="sectionIndex" class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <h3 class="text-xl font-semibold mb-4">{{ section.description }}</h3>
              <p class="text-sm text-gray-600 mb-4">每题 {{ section.score_per_question }} 分</p>
              
              <div class="space-y-6">
                <div v-for="(question, qIndex) in section.questions" :key="qIndex" class="border-b pb-4 last:border-b-0">
                  <div class="flex">
                    <span class="font-medium mr-2">{{ qIndex + 1 }}.</span>
                    <div class="flex-1">
                      <p class="mb-3" v-html="question.stem"></p>
                      
                      <!-- 选择题选项 -->
                      <div v-if="question.type === 'multiple_choice' || question.type === 'multiple_select'" class="space-y-2">
                        <div v-for="(option, optIndex) in question.options" :key="optIndex" class="flex items-center">
                          <!-- 不添加额外的选项标识，直接显示选项内容 -->
                          <span v-html="option"></span>
                        </div>
                        <p class="text-sm text-gray-600 mt-2">
                          正确答案: {{ 
                            Array.isArray(question.answer) 
                              ? question.answer.map(ans => String.fromCharCode(65 + Number(ans))).join(', ') 
                              : question.answer !== null && question.answer !== undefined 
                                ? String.fromCharCode(65 + Number(question.answer))
                                : '未设置'
                          }}
                        </p>
                      </div>

                      <!-- 判断题答案 -->
                      <div v-if="question.type === 'true_false'" class="mt-2">
                        <p class="text-sm text-gray-600">
                          正确答案: {{ question.answer === 'true' ? '正确' : '错误' }}
                        </p>
                      </div>

                      <!-- 填空题答案 -->
                      <div v-if="question.type === 'fill_in_blank'" class="mt-2">
                        <p class="text-sm text-gray-600">
                          正确答案: {{ Array.isArray(question.answer) ? question.answer.join(' | ') : question.answer }}
                        </p>
                      </div>

                      <!-- 简答题和论述题参考答案 -->
                      <div v-if="question.type === 'short_answer' || question.type === 'essay'" class="mt-2">
                        <p class="text-sm text-gray-600">
                          参考答案:
                          <span v-html="question.reference_answer || question.answer"></span>
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 学生做题模式 -->
        <div v-else class="assessment-player max-w-7xl mx-auto">
          <!-- 返回按钮 -->
          <div class="mb-4">
            <button 
              @click="handleCancel" 
              class="p-2 bg-white shadow-md rounded-lg hover:bg-gray-50 text-gray-700 flex items-center justify-center"
              style="width: 40px; height: 40px;"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
          
          <!-- 评估头部信息 -->
          <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-6">
            <div class="flex justify-between items-center">
              <div>
                <h2 class="text-2xl font-bold">{{ assessment.title }}</h2>
                <p class="text-gray-600">{{ assessment.description }}</p>
              </div>
              <div class="text-right">
                <p v-if="started && !submitted && timeLimit" class="text-lg font-semibold text-red-600">
                  {{ formatTime(remainingTime) }}
                </p>
                <p class="text-sm text-gray-600">总分: {{ assessment.total_score }} 分</p>
                <p class="text-sm text-gray-600">题目: {{ totalQuestions }} 题</p>
              </div>
            </div>

            <!-- 开始按钮 -->
            <div v-if="!started && !submitted" class="mt-4 flex justify-center">
              <button 
                @click="startAssessment"
                class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                开始答题
              </button>
            </div>
            
            <!-- 已提交提示 -->
            <div v-if="submitted && !started" class="mt-4">
              <div class="bg-green-50 border border-green-200 rounded-md p-4">
                <div class="flex">
                  <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  <div class="ml-3">
                    <h3 class="text-sm font-medium text-green-800">已完成提交</h3>
                    <div class="mt-2 text-sm text-green-700">
                      <p>您已经完成了此评估的提交。得分：{{ score }} / {{ assessment.total_score }}</p>
                      <p class="mt-1">提交时间：{{ formatDate(submissionTime) }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 进度条 -->
            <div v-if="started && !submitted" class="mt-4">
              <div class="w-full bg-gray-200 rounded-full h-2.5">
                <div 
                  class="bg-blue-600 h-2.5 rounded-full" 
                  :style="{ width: `${completionPercentage}%` }"
                ></div>
              </div>
              <div class="flex justify-between mt-1 text-sm text-gray-600">
                <span>进度: {{ currentQuestionIndex + 1 }}/{{ totalQuestions }}</span>
                <span>已完成: {{ answeredQuestions }}/{{ totalQuestions }}</span>
              </div>
            </div>
          </div>

          <!-- 以下内容只在开始答题后显示 -->
          <div v-if="started && !submitted">
            <!-- 题目导航 -->
            <div class="bg-white p-4 rounded-lg shadow-md border border-gray-200 mb-6">
              <div class="flex flex-wrap gap-2">
                <button 
                  v-for="index in totalQuestions" 
                  :key="index"
                  @click="navigateToQuestion(index - 1)"
                  :class="[
                    'w-8 h-8 flex items-center justify-center rounded-full text-sm',
                    currentQuestionIndex === index - 1 
                      ? 'bg-blue-600 text-white'
                      : isQuestionAnswered(index - 1)
                        ? 'bg-green-100 text-green-800 border'
                        : 'bg-gray-100 text-gray-800 border',
                    isQuestionMarked(index - 1) ? 'ring-2 ring-yellow-400' : ''
                  ]"
                >
                  {{ index }}
                </button>
              </div>
            </div>

            <!-- 当前题目 -->
            <div v-if="currentQuestion" class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold">
                  {{ currentQuestionIndex + 1 }}. {{ getQuestionTypeName(currentQuestion.type) }}
                  <span class="text-sm text-gray-500 ml-2">({{ currentQuestionScore }}分)</span>
                </h3>
                <div class="flex gap-2">
                  <button 
                    @click="toggleQuestionMark(currentQuestionIndex)"
                    :class="[
                      'text-sm px-2 py-1 rounded-md',
                      isQuestionMarked(currentQuestionIndex)
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                    ]"
                  >
                    标记题目
                  </button>
                </div>
              </div>

              <!-- 题干 -->
              <div class="mb-6">
                <p class="text-lg" v-html="currentQuestion.stem"></p>
              </div>

              <!-- 选择题 -->
              <div v-if="currentQuestion.type === 'multiple_choice'" class="space-y-3">
                <div 
                  v-for="(option, optIndex) in currentQuestion.options" 
                  :key="optIndex"
                  @click="selectOption(optIndex)"
                  :class="[
                    'p-3 border rounded-md cursor-pointer hover:bg-gray-50 flex items-center',
                    currentAnswers[currentQuestionIndex] === String.fromCharCode(65 + optIndex)
                      ? 'bg-blue-50 border-blue-200'
                      : ''
                  ]"
                >
                  <!-- 保留选择指示器但不重复显示选项标识 -->
                  <div class="w-6 h-6 flex items-center justify-center border rounded-full mr-3">
                    {{ String.fromCharCode(65 + optIndex) }}
                  </div>
                  <div v-html="option"></div>
                </div>
              </div>

              <!-- 多选题 -->
              <div v-if="currentQuestion.type === 'multiple_select'" class="space-y-3">
                <div 
                  v-for="(option, optIndex) in currentQuestion.options" 
                  :key="optIndex"
                  @click="toggleMultiSelect(optIndex)"
                  :class="[
                    'p-3 border rounded-md cursor-pointer hover:bg-gray-50 flex items-center',
                    isOptionSelected(optIndex) ? 'bg-blue-50 border-blue-200' : ''
                  ]"
                >
                  <!-- 保留选择指示器但不重复显示选项标识 -->
                  <div class="w-6 h-6 flex items-center justify-center border rounded mr-3">
                    {{ String.fromCharCode(65 + optIndex) }}
                  </div>
                  <div v-html="option"></div>
                </div>
              </div>
              
              <!-- 填空题 -->
              <div v-if="isFillBlankQuestion(currentQuestion)" class="space-y-4">
                <!-- 移除调试信息 -->
                
                <!-- 标准空白输入 -->
                <div v-if="Array.isArray(currentAnswers[currentQuestionIndex])">
                  <div 
                    v-for="(_, blankIndex) in currentAnswers[currentQuestionIndex]" 
                    :key="blankIndex"
                    class="flex flex-col sm:flex-row sm:items-center mb-4"
                  >
                    <label class="min-w-24 mb-1 sm:mb-0 sm:mr-3 text-sm font-medium">第 {{ blankIndex + 1 }} 空:</label>
                    <input 
                      type="text" 
                      :placeholder="`请填写第 ${blankIndex + 1} 空`"
                      v-model="currentAnswers[currentQuestionIndex][blankIndex]"
                      class="w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <!-- 添加/删除空白的按钮 -->
                  <div class="flex mt-2 space-x-2">
                    <button 
                      @click="addBlank()"
                      class="px-2 py-1 text-sm bg-blue-500 text-white rounded"
                    >
                      添加空白
                    </button>
                    <button 
                      v-if="currentAnswers[currentQuestionIndex].length > 1"
                      @click="removeBlank()"
                      class="px-2 py-1 text-sm bg-red-500 text-white rounded"
                    >
                      删除空白
                    </button>
                  </div>
                </div>
                
                <!-- 备用方案 - 如果答案不是数组 -->
                <div v-else class="border-t pt-3 mt-3">
                  <p class="text-sm text-red-600 mb-2">当前答案未正确初始化为数组，使用备用输入框:</p>
                  <input 
                    type="text" 
                    v-model="currentAnswers[currentQuestionIndex]"
                    class="border rounded-md px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="请填写答案"
                  />
                  <button 
                    @click="initializeBlankAnswers()" 
                    class="mt-2 px-3 py-1 bg-blue-500 text-white rounded-md text-sm"
                  >
                    初始化为多空白模式
                  </button>
                </div>
              </div>
              
              <!-- 判断题 -->
              <div v-if="currentQuestion.type === 'true_false'" class="space-y-3">
                <div 
                  v-for="(option, value) in { true: '正确', false: '错误' }" 
                  :key="value"
                  @click="selectTrueFalse(value)"
                  :class="[
                    'p-3 border rounded-md cursor-pointer hover:bg-gray-50 flex items-center',
                    currentAnswers[currentQuestionIndex] === value ? 'bg-blue-50 border-blue-200' : ''
                  ]"
                >
                  <div class="w-6 h-6 flex items-center justify-center border rounded-full mr-3"></div>
                  <div>{{ option }}</div>
                </div>
              </div>
              
              <!-- 简答题 -->
              <div v-if="currentQuestion.type === 'short_answer'" class="mt-4">
                <textarea 
                  v-model="currentAnswers[currentQuestionIndex]"
                  rows="4" 
                  class="w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="请输入您的答案"
                ></textarea>
              </div>
              
              <!-- 论述题 -->
              <div v-if="currentQuestion.type === 'essay'" class="mt-4">
                <textarea 
                  v-model="currentAnswers[currentQuestionIndex]"
                  rows="8"
                  class="w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="请输入您的答案"
                ></textarea>
              </div>
              
              <!-- 导航按钮 -->
              <div class="flex justify-between items-center mt-8">
                <button 
                  @click="previousQuestion"
                  :disabled="currentQuestionIndex === 0"
                  class="px-4 py-2 border rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  上一题
                </button>
                
                <button 
                  @click="saveProgress" 
                  class="px-4 py-2 border rounded-md hover:bg-gray-50"
                >
                  保存进度
                </button>

                <button 
                  v-if="currentQuestionIndex < totalQuestions - 1"
                  @click="nextQuestion"
                  class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  下一题
                </button>
                
                <button 
                  v-else
                  @click="showSubmitConfirm = true"
                  class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  :disabled="!canSubmitAssessment"
                  :class="{ 'opacity-50 cursor-not-allowed': !canSubmitAssessment }"
                >
                  {{ submitButtonStatus }}
                </button>
              </div>

              <!-- 提交确认对话框 -->
              <div v-if="showSubmitConfirm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div class="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
                  <h3 class="text-xl font-bold mb-4">确认提交</h3>
                  <p class="mb-6">您确定要提交此评估吗？提交后将无法更改您的答案。</p>
                  
                  <div v-if="isDeadlinePassed" class="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
                    警告：评估截止日期已过，提交可能会失败。
                  </div>
                  
                  <div class="flex justify-end space-x-4">
                    <button 
                      @click="showSubmitConfirm = false" 
                      class="px-4 py-2 border rounded-md hover:bg-gray-50"
                    >
                      取消
                    </button>
                    <button 
                      @click="submitAssessment" 
                      class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      确认提交
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 结果展示 -->
          <div v-if="submitted && showResults" class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <h3 class="text-xl font-semibold mb-4">评估结果</h3>
            <div class="flex justify-between items-center mb-6">
              <div>
                <p class="text-lg">得分: <span class="font-bold">{{ score }}</span> / {{ assessment.total_score }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">提交时间: {{ formatDate(submissionTime) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter, useRoute } from 'vue-router';
import AssessmentEditor from './AssessmentEditor.vue';
import { assessmentAPI } from '@/api';

const router = useRouter();
const route = useRoute();

const props = defineProps({
  assessmentId: {
    type: [Number, String],
    required: true,
    validator: (value) => {
      const id = typeof value === 'string' ? parseInt(value) : value;
      return !isNaN(id) && id > 0;
    }
  },
  previewMode: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['submit', 'save-progress', 'cancel']);

// 获取用户角色
const authStore = useAuthStore();
const isTeacher = computed(() => authStore.user?.role === 'teacher');

// 编辑模式状态
const editMode = ref(false);

// 状态变量
const loading = ref(true);
const started = ref(false);
const currentQuestionIndex = ref(0);
const currentAnswers = ref({});
const markedQuestions = ref(new Set());
const showResults = ref(false);
const submitted = ref(false);
const submissionTime = ref(null);
const score = ref(0);
const showSubmitConfirm = ref(false);

// 评估数据
const assessment = reactive({
  id: typeof props.assessmentId === 'string' ? parseInt(props.assessmentId) : props.assessmentId,
  title: '',
  description: '',
  course_id: null,
  type: 'quiz',
  total_score: 0,
  duration: null,
  due_date: null,
  start_date: null,
  max_attempts: 1,
  is_published: false,
  is_active: true,
  sections: []
});

// 时间相关变量
const timeLimit = ref(null); // 初始为null，在fetchAssessment后设置
const remainingTime = ref(null);
const timer = ref(null);

// 计算属性
const totalQuestions = computed(() => {
  return assessment.sections.reduce((total, section) => total + section.questions.length, 0);
});

const currentQuestion = computed(() => {
  let questionCount = 0;
  for (const section of assessment.sections) {
    if (questionCount + section.questions.length > currentQuestionIndex.value) {
      return section.questions[currentQuestionIndex.value - questionCount];
    }
    questionCount += section.questions.length;
  }
  return null;
});

const currentQuestionScore = computed(() => {
  let questionCount = 0;
  for (const section of assessment.sections) {
    if (questionCount + section.questions.length > currentQuestionIndex.value) {
      return section.score_per_question;
    }
    questionCount += section.questions.length;
  }
  return 0;
});

const answeredQuestions = computed(() => {
  // 如果currentAnswers是数组
  if (Array.isArray(currentAnswers.value)) {
    return currentAnswers.value.filter(answer => {
      if (Array.isArray(answer)) {
        return answer.some(a => a !== '');
      }
      return answer !== '' && answer !== null && answer !== undefined;
    }).length;
  } 
  // 如果currentAnswers是对象
  else if (typeof currentAnswers.value === 'object') {
    return Object.values(currentAnswers.value).filter(answer => {
      if (Array.isArray(answer)) {
        return answer.some(a => a !== '');
      }
      return answer !== '' && answer !== null && answer !== undefined;
    }).length;
  }
  
  return 0;
});

const completionPercentage = computed(() => {
  return (answeredQuestions.value / totalQuestions.value) * 100;
});

// 初始化答案
const initAnswers = () => {
  // 检查sections是否存在且不为空
  if (!assessment.sections || assessment.sections.length === 0) {
    currentAnswers.value = [];
    return;
  }
  
  currentAnswers.value = assessment.sections.flatMap(section => {
    // 检查section.questions是否存在且不为空
    if (!section.questions || section.questions.length === 0) {
      return [];
    }
    
    return section.questions.map(question => {
      if (question.type === 'multiple_choice' || question.type === 'true_false') {
        return '';
      } else if (question.type === 'multiple_select') {
        return [];
      } else if (isFillBlankQuestion(question)) {
        // 检查答案是否已经是数组
        if (question.answer && Array.isArray(question.answer)) {
          console.log(`填空题：答案已经是数组，长度 ${question.answer.length}`);
          return Array(question.answer.length).fill('');
        }
        
        // 使用增强的空白计数方法
        const blankCount = countBlanks(question.stem);
        console.log(`填空题：${question.stem} - 检测到 ${blankCount} 个空白`);
        return Array(blankCount).fill('');
      } else if (question.type === 'short_answer' || question.type === 'essay') {
        return '';
      }
      return null;
    });
  });
};

// 从后端获取评估数据
const fetchAssessment = async () => {
  try {
    loading.value = true;
    const id = typeof props.assessmentId === 'string' ? parseInt(props.assessmentId) : props.assessmentId;
    console.log('Fetching assessment with ID:', id);
    
    const response = await assessmentAPI.getAssessment(id);
    console.log('Received assessment data:', response);
    
    // 将后端的 questions 转换为前端需要的格式
    const questions = Array.isArray(response.questions) ? response.questions : [];
    console.log('Questions from backend:', questions);
    
    // 创建一个包含所有题目的 section
    const sections = [{
      type: 'all',
      description: '请回答以下问题',
      score_per_question: questions.length > 0 ? Math.floor(response.total_score / questions.length) : 0,
      questions: questions.map(q => {
        // 标准化填空题类型 - 确保fill_blank和fill_in_blank都被识别
        let questionType = q.type || 'multiple_choice';
        if (questionType.includes('fill') && questionType.includes('blank')) {
          // 统一填空题类型为fill_in_blank
          questionType = 'fill_in_blank';
        }
        
        return {
          ...q,
          stem: q.content || q.stem || '',  // 兼容不同的题目格式
          options: q.options || [],
          type: questionType,
          answer: q.answer,  // 不设置默认值，保持原始值
          // 确保判断题的答案是字符串类型
          ...(q.type === 'true_false' ? { answer: String(q.answer) } : {})
        };
      })
    }];
    
    console.log('Generated sections:', sections);
    
    // 更新评估数据
    Object.assign(assessment, {
      ...response,
      sections
    });
    
    // 初始化答案
    initAnswers();
    
    // 设置时间限制
    if (response.duration) {
      timeLimit.value = response.duration * 60; // 转换为秒
      remainingTime.value = timeLimit.value;
    }
    
    // 检查学生是否已经提交过此评估
    if (!isTeacher.value && !props.previewMode) {
      try {
        // 获取当前用户ID
        const userId = authStore.user?.id || parseInt(localStorage.getItem('userId') || '0');
        console.log('Current user ID for submission check:', userId);
        
        // 从本地存储中检查是否有提交ID
        const submissionId = localStorage.getItem(`assessment_${id}_submission_id`);
        console.log('Submission ID from localStorage:', submissionId);
        
        // 获取学生的提交记录
        console.log(`Fetching submissions for student ${userId} and assessment ${id}`);
        const submissionsResponse = await assessmentAPI.getSubmissionsByStudent(userId, {
          assessment_id: id
        });
        
        console.log('Student submissions response:', submissionsResponse);
        
        // 如果有提交记录，显示最新的提交结果
        if (submissionsResponse.submissions && submissionsResponse.submissions.length > 0) {
          const latestSubmission = submissionsResponse.submissions[0]; // 假设按时间降序排列
          console.log('Found latest submission:', latestSubmission);
          
          submitted.value = true;
          submissionTime.value = new Date(latestSubmission.submitted_at);
          score.value = latestSubmission.score;
          showResults.value = true;
          
          // 重要：保存提交ID，以便将来可能需要查看详情
          localStorage.setItem(`assessment_${id}_submission_id`, latestSubmission.id);
          
          // 加载已提交的答案，以便学生可以查看自己的回答
          if (latestSubmission.answers) {
            try {
              // 有可能answers已经是对象，也可能是JSON字符串
              const parsedAnswers = typeof latestSubmission.answers === 'string' 
                ? JSON.parse(latestSubmission.answers) 
                : latestSubmission.answers;
              
              console.log('Loaded previous answers:', parsedAnswers);
              
              // 将已提交的答案加载到当前答案中，但设为只读
              currentAnswers.value = parsedAnswers;
              
              // 设置已提交状态，防止重新提交
              started.value = false;
              submitted.value = true;
            } catch (parseError) {
              console.error('解析提交答案失败:', parseError);
            }
          }
          
          console.log('Student has already submitted this assessment, loading submission data');
        } else {
          console.log('No previous submissions found for this assessment');
        }
      } catch (submissionError) {
        console.error('获取提交记录失败:', submissionError);
        if (submissionError.response) {
          console.error('Error response:', submissionError.response);
        }
      }
    }
    
    console.log('Updated assessment data:', assessment);
  } catch (error) {
    console.error('获取评估数据失败:', error);
    if (error.response) {
      console.error('Error response:', error.response.data);
      console.error('Error status:', error.response.status);
    }
  } finally {
    loading.value = false;
  }
};

// 开始评估
const startAssessment = () => {
  // 如果已经提交过，不允许再次开始
  if (submitted.value) {
    alert('您已经提交过此评估，不能再次提交');
    return;
  }
  
  started.value = true;
  initAnswers();
  if (assessment.duration) {
      startTimer();
  }
};

// 计时器
const startTimer = () => {
  timer.value = setInterval(() => {
    if (remainingTime.value > 0) {
      remainingTime.value--;
    } else {
      // 时间到，自动提交
      clearInterval(timer.value);
      submitAssessment();
    }
  }, 1000);
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 格式化时间（秒转为分:秒）
const formatTime = (seconds) => {
  if (seconds === null || seconds === undefined) return '--:--';
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
};

// 计算填空题的空格数
const countBlanks = (stem) => {
  if (!stem) return 1;
  
  console.log("分析填空题题干:", stem);
  
  // 尝试匹配所有可能的空白标记格式
  const underscoreMatches = (stem.match(/_____/g) || []).length;
  const regex3PlusMatches = (stem.replace(/_____/g, '').match(/_{3,}/g) || []).length;
  const blankMatches = (stem.match(/\[BLANK\]/gi) || []).length;
  const chineseMatches = (stem.match(/【空白】/g) || []).length;
  const bracketMatches1 = (stem.match(/（）/g) || []).length;
  const bracketMatches2 = (stem.match(/\(\)/g) || []).length;
  
  const blankCount = underscoreMatches + regex3PlusMatches + 
                     blankMatches + chineseMatches + 
                     bracketMatches1 + bracketMatches2;
  
  console.log("检测到的空白标记:", {
    underscoreMatches,
    regex3PlusMatches,
    blankMatches,
    chineseMatches,
    bracketMatches1,
    bracketMatches2,
    total: blankCount
  });
                     
  // 如果检测到空白，返回空白数量；否则检查答案数组长度；如果都没有，默认为1
  if (blankCount > 0) {
    return blankCount;
  }
  
  // 如果没有检测到空白标记，可能是题目没有明显标记但答案是数组
  // 在这种情况下直接返回默认值2
  return 2;
};

// 格式化填空题题干
const formatBlankQuestion = (stem) => {
  return stem.replace(/_{3,}/g, '<u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u>');
};

// 处理文件上传
const handleFileUpload = (event, sectionIndex, qIndex) => {
  const file = event.target.files[0];
  if (file) {
    currentAnswers.value[qIndex].files.push(file);
  }
  // 重置文件输入以允许重复选择同一文件
  event.target.value = '';
};

// 移除文件
const removeFile = (sectionIndex, qIndex, fileIndex) => {
  currentAnswers.value[qIndex].files.splice(fileIndex, 1);
};

// 保存进度
const saveProgress = () => {
  try {
    // 获取当前用户ID
    const userId = authStore.user?.id || parseInt(localStorage.getItem('userId') || '0');
    
    // 保存到本地存储
    localStorage.setItem(`assessment_${assessment.id}_progress`, JSON.stringify(currentAnswers.value));
    localStorage.setItem(`assessment_${assessment.id}_progress_time`, new Date().toISOString());
    
    // 显示保存成功提示
    alert('进度已保存');
    
    console.log('保存进度:', currentAnswers.value);
    emit('save-progress', {
      assessmentId: assessment.id,
      answers: JSON.parse(JSON.stringify(currentAnswers.value))
    });
  } catch (error) {
    console.error('保存进度失败:', error);
    alert('保存进度失败，请重试');
  }
};

// 保存提交状态到本地存储
const saveSubmissionState = (submissionData) => {
  const id = assessment.id;
  
  // 保存提交ID
  if (submissionData.submission_id) {
    localStorage.setItem(`assessment_${id}_submission_id`, submissionData.submission_id);
  }
  
  // 保存提交状态
  localStorage.setItem(`assessment_${id}_submitted`, 'true');
  localStorage.setItem(`assessment_${id}_score`, submissionData.score || score.value);
  localStorage.setItem(`assessment_${id}_submitted_at`, submissionData.submitted_at || new Date().toISOString());
  
  console.log('提交状态已保存到本地存储');
};

// 提交评估
const submitAssessment = async () => {
  if (timer.value) {
    clearInterval(timer.value);
  }
  
  // 检查截止日期
  if (isDeadlinePassed.value) {
    alert('评估提交截止日期已过，无法提交');
    return;
  }
  
  try {
    // 获取当前用户ID
    const userId = authStore.user?.id || parseInt(localStorage.getItem('userId') || '0');
    
    // 在提交前检查并修复所有填空题的答案格式
    assessment.sections.forEach((section, sectionIndex) => {
      section.questions.forEach((question, questionIndex) => {
        const globalQuestionIndex = assessment.sections.slice(0, sectionIndex)
          .reduce((total, s) => total + s.questions.length, 0) + questionIndex;
        
        if (isFillBlankQuestion(question)) {
          // 确保填空题答案是数组格式
          const answer = Array.isArray(currentAnswers.value) 
            ? currentAnswers.value[globalQuestionIndex] 
            : currentAnswers.value[globalQuestionIndex.toString()];
          
          if (!Array.isArray(answer)) {
            console.log(`提交前修复填空题答案格式: 问题 #${globalQuestionIndex}`);
            const blankCount = countBlanks(question.stem);
            
            if (Array.isArray(currentAnswers.value)) {
              currentAnswers.value[globalQuestionIndex] = Array(blankCount).fill('');
              // 如果有单个答案，将其放入数组的第一个位置
              if (answer && typeof answer === 'string') {
                currentAnswers.value[globalQuestionIndex][0] = answer;
              }
            } else {
              currentAnswers.value[globalQuestionIndex.toString()] = Array(blankCount).fill('');
              // 如果有单个答案，将其放入数组的第一个位置
              if (answer && typeof answer === 'string') {
                currentAnswers.value[globalQuestionIndex.toString()][0] = answer;
              }
            }
          }
        }
      });
    });
    
    // 准备提交数据 - 确保answers是数组格式
    const submissionData = {
      student_id: userId,
      answers: Array.isArray(currentAnswers.value) ? currentAnswers.value : Object.values(currentAnswers.value),
      submitted_at: new Date().toISOString(),
      time_spent: timeLimit.value ? timeLimit.value - remainingTime.value : null
    };
    
    // 添加调试日志，查看提交的数据结构
    console.log('提交评估数据:', JSON.stringify(submissionData));
    
    // 调用API提交评估
    let result;
    try {
      result = await assessmentAPI.submitAssessment(assessment.id, submissionData);
      console.log('提交结果:', result);
      
      // 更新状态
      submitted.value = true;
      submissionTime.value = new Date();
      
      // 使用后端返回的分数
      if (result && result.score !== undefined) {
        score.value = result.score;
      } else {
        // 如果后端没有返回分数，使用前端计算的分数
        calculateScore();
      }
      
      // 保存提交状态
      saveSubmissionState({
        submission_id: result?.submission_id,
        score: score.value,
        submitted_at: submissionTime.value.toISOString()
      });
      
      // 显示结果
      showResults.value = true;
      
      // 显示提交成功消息
      alert(`评估已成功提交！您的得分是：${score.value}/${assessment.total_score}`);
    } catch (apiError) {
      console.error('API调用失败:', apiError);
      
      // 提取具体错误信息
      let errorMessage = '提交失败，请重试';
      
      if (apiError.response) {
        // 处理特定错误情况
        if (apiError.response.status === 400) {
          if (apiError.response.data && apiError.response.data.error) {
            errorMessage = apiError.response.data.error;
            
            // 针对特定错误提供更友好的中文提示
            if (errorMessage === 'Assessment submission deadline has passed') {
              errorMessage = '评估提交截止日期已过，无法提交';
            } else if (errorMessage === 'Maximum number of attempts reached') {
              errorMessage = '已达到最大尝试次数，无法再次提交';
            }
          }
        } else if (apiError.response.status === 404) {
          errorMessage = '评估不存在或已被删除';
        }
      }
      
      // 使用增强的错误信息
      if (apiError.backendError) {
        console.log('后端返回的错误:', apiError.backendError);
        
        // 翻译常见错误消息
        const errorTranslations = {
          'Assessment submission deadline has passed': '评估提交截止日期已过，无法提交',
          'Maximum number of attempts reached': '已达到最大尝试次数，无法再次提交',
          'Assessment not found': '评估不存在或已被删除'
        };
        
        errorMessage = errorTranslations[apiError.backendError] || apiError.backendError;
      }
      
      // 显示错误消息
      alert(errorMessage);
      throw apiError;
    }
  } catch (error) {
    console.error('提交评估失败:', error);
    alert('提交失败，请重试');
    
    // 恢复状态，允许重试
    submitted.value = false;
    showResults.value = false;
  }
  
  // 通知父组件
  emit('submit', {
    assessmentId: assessment.id,
    answers: JSON.parse(JSON.stringify(currentAnswers.value)),
    submissionTime: submissionTime.value,
    timeSpent: timeLimit.value ? timeLimit.value - remainingTime.value : null,
    score: score.value
  });
};

  // 计算得分（简单模拟）
const calculateScore = () => {
  let totalScore = 0;
  let questionIndex = 0;
  
  assessment.sections.forEach((section) => {
    section.questions.forEach((question) => {
      const userAnswer = currentAnswers.value[questionIndex];
      let isCorrect = false;

      switch (question.type) {
        case 'multiple_choice':
          // 将用户答案转换为数字进行比较
          const userChoice = String.fromCharCode(65 + Number(question.answer)) === userAnswer;
          isCorrect = userChoice;
          break;

        case 'multiple_select':
          // 多选题：将用户答案和正确答案都转换为字母数组进行比较
          if (Array.isArray(userAnswer) && Array.isArray(question.answer)) {
            const userLetters = userAnswer.map(ans => String.fromCharCode(65 + Number(ans))).sort();
            const correctLetters = question.answer.map(ans => String.fromCharCode(65 + Number(ans))).sort();
            isCorrect = JSON.stringify(userLetters) === JSON.stringify(correctLetters);
          }
          break;

        case 'fill_in_blank':
        case 'fill_blank':
          // 填空题处理 - 支持部分得分
          let partialScore = 0;
          
          // 如果答案是数组且用户答案也是数组
          if (Array.isArray(question.answer) && Array.isArray(userAnswer)) {
            console.log(`填空题评分: 用户答案(${userAnswer.length}个) vs 正确答案(${question.answer.length}个)`);
            
            // 计算部分得分
            const scorePerBlank = section.score_per_question / question.answer.length;
            
            // 计算正确数量
            let correctCount = 0;
            const minLength = Math.min(userAnswer.length, question.answer.length);
            
            for (let i = 0; i < minLength; i++) {
              const userAns = String(userAnswer[i] || '').trim().toLowerCase();
              const correctAns = String(question.answer[i] || '').trim().toLowerCase();
              
              if (userAns === correctAns) {
                correctCount++;
              }
            }
            
            // 计算部分分数
            partialScore = scorePerBlank * correctCount;
            console.log(`填空题得分: ${correctCount}/${question.answer.length} 空白正确，得分 ${partialScore}`);
            
            // 添加部分分数
            totalScore += partialScore;
          } 
          // 如果答案是字符串但用户答案是数组
          else if (!Array.isArray(question.answer) && Array.isArray(userAnswer)) {
            // 检查第一个答案是否匹配
            if (userAnswer.length > 0) {
              const userAns = String(userAnswer[0] || '').trim().toLowerCase();
              const correctAns = String(question.answer || '').trim().toLowerCase();
              
              if (userAns === correctAns) {
                isCorrect = true;
              }
            }
          } 
          // 如果答案是数组但用户答案是字符串
          else if (Array.isArray(question.answer) && !Array.isArray(userAnswer)) {
            // 检查是否匹配第一个答案
            if (question.answer.length > 0) {
              const userAns = String(userAnswer || '').trim().toLowerCase();
              const correctAns = String(question.answer[0] || '').trim().toLowerCase();
              
              if (userAns === correctAns) {
                isCorrect = true;
              }
            }
          } 
          // 如果两者都是字符串
          else {
            isCorrect = String(userAnswer || '').trim().toLowerCase() === String(question.answer || '').trim().toLowerCase();
          }
          
          // 跳过isCorrect分数加成，因为已经处理了部分分数
          if (Array.isArray(question.answer) && Array.isArray(userAnswer)) {
            isCorrect = false;
          }
          break;

        case 'true_false':
          isCorrect = userAnswer === question.answer;
          break;

        // 简答题和论述题需要人工评分
        case 'short_answer':
        case 'essay':
          break;
      }

      if (isCorrect) {
        totalScore += section.score_per_question;
      }
      questionIndex++;
    });
  });
  
  score.value = totalScore;
};

// 保存评估（教师）
const saveAssessment = async (updatedAssessment) => {
  try {
    // TODO: 调用API保存更新后的评估
    Object.assign(assessment, updatedAssessment);
    editMode.value = false;
  } catch (error) {
    console.error('保存评估失败:', error);
  }
};

// 新增方法
const navigateToQuestion = (index) => {
  currentQuestionIndex.value = index;
};

const toggleQuestionMark = (index) => {
  if (markedQuestions.value.has(index)) {
    markedQuestions.value.delete(index);
  } else {
    markedQuestions.value.add(index);
  }
};

const isQuestionMarked = (index) => {
  return markedQuestions.value.has(index);
};

const isQuestionAnswered = (index) => {
  // 确保currentAnswers.value是有效的
  if (!currentAnswers.value) {
    return false;
  }
  
  // 获取答案（兼容数组和对象格式）
  const answer = Array.isArray(currentAnswers.value) 
    ? currentAnswers.value[index] 
    : currentAnswers.value[index.toString()];
  
  if (Array.isArray(answer)) {
    return answer.some(a => a !== '');
  }
  return answer !== '' && answer !== null && answer !== undefined;
};

// 获取题目类型名称
const getQuestionTypeName = (type) => {
  const typeNames = {
    'multiple_choice': '选择题',
    'multiple_select': '多选题',
    'true_false': '判断题',
    'fill_in_blank': '填空题',
    'fill_blank': '填空题',
    'short_answer': '简答题',
    'essay': '论述题'
  };
  return typeNames[type] || type;
};

// 判断题目是否为填空题类型
const isFillBlankQuestion = (question) => {
  if (!question) return false;
  
  const type = String(question.type || '').toLowerCase();
  
  // 检查类型是否是填空题类型
  return (
    type === 'fill_blank' || 
    type === 'fill_in_blank' ||
    (type.includes('fill') && type.includes('blank'))
  );
};

const selectOption = (optIndex) => {
  const value = String.fromCharCode(65 + optIndex);
  if (Array.isArray(currentAnswers.value)) {
    currentAnswers.value[currentQuestionIndex.value] = value;
  } else {
    currentAnswers.value[currentQuestionIndex.value.toString()] = value;
  }
};

const toggleMultiSelect = (optIndex) => {
  const index = currentQuestionIndex.value.toString();
  const answer = String.fromCharCode(65 + optIndex);
  
  // 确保当前答案是数组
  if (Array.isArray(currentAnswers.value)) {
    if (!Array.isArray(currentAnswers.value[currentQuestionIndex.value])) {
      currentAnswers.value[currentQuestionIndex.value] = [];
    }
    
    const answerArray = currentAnswers.value[currentQuestionIndex.value];
    const answerIndex = answerArray.indexOf(answer);
    
    if (answerIndex === -1) {
      answerArray.push(answer);
    } else {
      answerArray.splice(answerIndex, 1);
    }
  } else {
    if (!Array.isArray(currentAnswers.value[index])) {
      currentAnswers.value[index] = [];
    }
    
    const answerArray = currentAnswers.value[index];
    const answerIndex = answerArray.indexOf(answer);
    
    if (answerIndex === -1) {
      answerArray.push(answer);
    } else {
      answerArray.splice(answerIndex, 1);
    }
  }
};

const isOptionSelected = (optIndex) => {
  const answer = Array.isArray(currentAnswers.value) 
    ? currentAnswers.value[currentQuestionIndex.value] 
    : currentAnswers.value[currentQuestionIndex.value.toString()];
  
  return Array.isArray(answer) && answer.includes(String.fromCharCode(65 + optIndex));
};

const selectTrueFalse = (value) => {
  if (Array.isArray(currentAnswers.value)) {
    currentAnswers.value[currentQuestionIndex.value] = value;
  } else {
    currentAnswers.value[currentQuestionIndex.value.toString()] = value;
  }
};

const previousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--;
  }
};

const nextQuestion = () => {
  if (currentQuestionIndex.value < totalQuestions.value - 1) {
    currentQuestionIndex.value++;
  }
};

// 检查是否可以提交评估
const canSubmitAssessment = computed(() => {
  // 已提交则不能再次提交
  if (submitted.value) {
    return false;
  }
  
  // 截止日期已过则不能提交
  if (isDeadlinePassed.value) {
    return false;
  }
  
  return true;
});

// 获取提交按钮的状态信息
const submitButtonStatus = computed(() => {
  if (submitted.value) {
    return '已提交';
  }
  
  if (isDeadlinePassed.value) {
    return '截止日期已过';
  }
  
  return '提交评估';
});

// 确认提交评估
const confirmSubmit = () => {
  showSubmitConfirm.value = false;
  submitAssessment();
};

// 从本地存储中恢复提交状态
const restoreSubmissionState = () => {
  const id = typeof props.assessmentId === 'string' ? parseInt(props.assessmentId) : props.assessmentId;
  
  // 检查是否有提交记录
  const isSubmitted = localStorage.getItem(`assessment_${id}_submitted`) === 'true';
  if (!isSubmitted) {
    return false;
  }
  
  console.log('从本地存储中恢复提交状态');
  
  // 恢复提交状态
  submitted.value = true;
  
  // 恢复分数
  const savedScore = localStorage.getItem(`assessment_${id}_score`);
  if (savedScore) {
    score.value = parseFloat(savedScore);
  }
  
  // 恢复提交时间
  const savedSubmittedAt = localStorage.getItem(`assessment_${id}_submitted_at`);
  if (savedSubmittedAt) {
    submissionTime.value = new Date(savedSubmittedAt);
  } else {
    submissionTime.value = new Date();
  }
  
  // 设置显示结果
  showResults.value = true;
  started.value = false;
  
  console.log('已从本地存储中恢复提交状态');
  return true;
};

// 检查用户是否已提交评估
const checkSubmissionStatus = async () => {
  if (isTeacher.value || props.previewMode) {
    return; // 教师或预览模式不需要检查
  }
  
  // 首先尝试从本地存储中恢复状态
  if (restoreSubmissionState()) {
    console.log('已从本地存储中恢复提交状态，跳过API查询');
    return;
  }
  
  try {
    const userId = authStore.user?.id || parseInt(localStorage.getItem('userId') || '0');
    if (!userId) {
      console.warn('无法获取用户ID，跳过提交状态检查');
      return;
    }
    
    const id = typeof props.assessmentId === 'string' ? parseInt(props.assessmentId) : props.assessmentId;
    console.log(`检查用户 ${userId} 对评估 ${id} 的提交状态`);
    
    // 从本地存储中检查是否有提交记录
    const submissionId = localStorage.getItem(`assessment_${id}_submission_id`);
    if (submissionId) {
      console.log(`从本地存储中找到提交ID: ${submissionId}`);
      
      // 可以选择直接加载提交详情
      try {
        const submission = await assessmentAPI.getSubmission(submissionId);
        console.log('加载提交详情:', submission);
        
        if (submission) {
          // 更新状态
          submitted.value = true;
          submissionTime.value = new Date(submission.submitted_at);
          score.value = submission.score || 0;
          showResults.value = true;
          started.value = false;
          
          // 加载答案
          if (submission.answers) {
            const parsedAnswers = typeof submission.answers === 'string' 
              ? JSON.parse(submission.answers) 
              : submission.answers;
            
            currentAnswers.value = parsedAnswers;
          }
          
          console.log('已加载之前的提交记录');
          return;
        }
      } catch (err) {
        console.error('加载提交详情失败:', err);
        // 如果直接加载失败，继续尝试列表查询
      }
    }
    
    // 查询提交记录列表
    const submissionsResponse = await assessmentAPI.getSubmissionsByStudent(userId, {
      assessment_id: id
    });
    
    console.log('提交记录查询结果:', submissionsResponse);
    
    if (submissionsResponse.submissions && submissionsResponse.submissions.length > 0) {
      const latestSubmission = submissionsResponse.submissions[0];
      console.log('找到最新提交:', latestSubmission);
      
      // 更新状态
      submitted.value = true;
      submissionTime.value = new Date(latestSubmission.submitted_at);
      score.value = latestSubmission.score || 0;
      showResults.value = true;
      started.value = false;
      
      // 保存提交ID
      localStorage.setItem(`assessment_${id}_submission_id`, latestSubmission.id);
      
      // 加载答案
      if (latestSubmission.answers) {
        const parsedAnswers = typeof latestSubmission.answers === 'string' 
          ? JSON.parse(latestSubmission.answers) 
          : latestSubmission.answers;
        
        currentAnswers.value = parsedAnswers;
      }
      
      console.log('已加载之前的提交记录');
    } else {
      console.log('未找到提交记录');
      submitted.value = false;
      showResults.value = false;
    }
  } catch (error) {
    console.error('检查提交状态失败:', error);
  }
};

// 在组件挂载时获取数据
onMounted(() => {
  fetchAssessment().then(() => {
    console.log('评估数据加载完成，开始初始化填空题');
    
    // 检查并修复所有填空题
    assessment.sections.forEach((section, sectionIndex) => {
      section.questions.forEach((question, questionIndex) => {
        // 计算全局题目索引
        const globalQuestionIndex = assessment.sections.slice(0, sectionIndex)
          .reduce((total, s) => total + s.questions.length, 0) + questionIndex;
        
        // 检查是否为填空题
        if (isFillBlankQuestion(question)) {
          console.log(`检查填空题: 问题 #${globalQuestionIndex} - ${question.type}`);
          console.log('填空题题干:', question.stem);
          console.log('填空题答案:', question.answer);
          
          // 确保填空题答案是数组格式
          const answer = Array.isArray(currentAnswers.value) 
            ? currentAnswers.value[globalQuestionIndex] 
            : currentAnswers.value[globalQuestionIndex.toString()];
          
          if (!Array.isArray(answer)) {
            console.log(`初始化填空题答案为数组: 问题 #${globalQuestionIndex}`);
            
            // 确定空白数量
            let blankCount = 2; // 默认值
            
            // 优先使用答案数组长度
            if (question.answer && Array.isArray(question.answer)) {
              blankCount = question.answer.length;
              console.log(`  答案数组长度: ${blankCount}`);
            } else {
              // 尝试从题干中计算空白数量
              blankCount = countBlanks(question.stem);
              console.log(`  从题干计算空白数量: ${blankCount}`);
            }
            
            // 创建填空题答案数组
            if (Array.isArray(currentAnswers.value)) {
              currentAnswers.value[globalQuestionIndex] = Array(blankCount).fill('');
            } else {
              currentAnswers.value[globalQuestionIndex.toString()] = Array(blankCount).fill('');
            }
            
            console.log(`  已初始化为 ${blankCount} 个空白`);
          } else {
            console.log(`填空题答案已是数组，长度为 ${answer.length}`);
          }
        }
      });
    });
  });
  
  checkSubmissionStatus();
});

// 组件卸载前清除定时器
onBeforeUnmount(() => {
  if (timer.value) {
    clearInterval(timer.value);
  }
});

// 路由变化监听
watch(() => started.value && !submitted.value, (isActive) => {
  if (isActive) {
    window.addEventListener('beforeunload', confirmLeave);
  } else {
    window.removeEventListener('beforeunload', confirmLeave);
  }
});

const confirmLeave = (e) => {
  e.preventDefault();
  e.returnValue = '您有未保存的答案，确定要离开吗？';
  return e.returnValue;
};

// 处理返回按钮点击
const handleCancel = () => {
  // 检查路由参数和查询参数中是否有courseId
  const courseIdFromQuery = route.query.courseId;
  const courseIdFromAssessment = assessment.course_id;
  
  // 优先使用查询参数中的courseId，其次使用评估中的course_id
  const courseId = courseIdFromQuery || courseIdFromAssessment;
  
  if (courseId) {
    // 如果有courseId，返回到课程详情页面
    router.push({ 
      path: `/course/${courseId}`, 
      query: { activeTab: 'assessments' } 
    });
  } else {
    // 根据用户角色返回对应页面
    const userRole = authStore.user?.role || '';
    
    if (userRole === 'teacher') {
      router.push({ path: '/teacher', query: { activeTab: 'assessments' } });
    } else if (userRole === 'student') {
      router.push({ path: '/student', query: { activeTab: 'assessments' } });
    } else {
      router.push('/dashboard');
    }
  }
};

// 检查截止日期是否已过
const isDeadlinePassed = computed(() => {
  if (!assessment.due_date) {
    return false;
  }
  const dueDate = new Date(assessment.due_date);
  const now = new Date();
  return now > dueDate;
});

// 获取评估状态的类和消息
const statusClass = computed(() => {
  if (isDeadlinePassed.value) {
    return 'bg-red-100 text-red-800';
  } else if (submitted.value) {
    return 'bg-green-100 text-green-800';
  }
  return 'bg-yellow-100 text-yellow-800';
});

const statusMessage = computed(() => {
  if (isDeadlinePassed.value) {
    return '评估截止日期已过，您无法提交答案。';
  } else if (submitted.value) {
    return '您已成功提交此评估。';
  }
  return '您可以开始答题。';
});

// 添加这个新方法
const initializeBlankAnswers = () => {
  if (!currentQuestion.value) return;
  
  // 首先检查答案是否是数组
  if (currentQuestion.value.answer && Array.isArray(currentQuestion.value.answer)) {
    const answerLength = currentQuestion.value.answer.length;
    console.log(`题目有 ${answerLength} 个预定义答案，使用此数量`);
    
    // 使用答案数组的长度
    if (Array.isArray(currentAnswers.value)) {
      currentAnswers.value[currentQuestionIndex.value] = Array(answerLength).fill('');
    } else {
      currentAnswers.value[currentQuestionIndex.value.toString()] = Array(answerLength).fill('');
    }
  } else {
    // 计算应该有多少个空白
    const blankCount = countBlanks(currentQuestion.value.stem);
    console.log(`需要初始化 ${blankCount} 个空白输入框`);
    
    // 创建填空题答案数组
    if (Array.isArray(currentAnswers.value)) {
      currentAnswers.value[currentQuestionIndex.value] = Array(blankCount).fill('');
    } else {
      currentAnswers.value[currentQuestionIndex.value.toString()] = Array(blankCount).fill('');
    }
  }
  
  console.log('已初始化填空题答案数组:', currentAnswers.value[currentQuestionIndex.value]);
};

// 添加/删除空白
const addBlank = () => {
  if (Array.isArray(currentAnswers.value[currentQuestionIndex.value])) {
    currentAnswers.value[currentQuestionIndex.value].push('');
  }
};

const removeBlank = () => {
  if (Array.isArray(currentAnswers.value[currentQuestionIndex.value]) && 
      currentAnswers.value[currentQuestionIndex.value].length > 1) {
    currentAnswers.value[currentQuestionIndex.value].pop();
  }
};

// 在组件挂载后和currentQuestionIndex变化时检查并修复填空题
watch(currentQuestionIndex, (newIndex) => {
  const question = assessment.sections.flatMap(s => s.questions)[newIndex];
  if (question && isFillBlankQuestion(question)) {
    // 检查答案是否已经初始化为数组
    const answer = Array.isArray(currentAnswers.value) 
      ? currentAnswers.value[newIndex] 
      : currentAnswers.value[newIndex.toString()];
    
    if (!Array.isArray(answer)) {
      console.log(`填空题答案未初始化为数组，当前索引: ${newIndex}`);
      initializeBlankAnswers();
    } else {
      // 检查答案数组长度是否符合预期
      const expectedBlanks = countBlanks(question.stem);
      if (answer.length !== expectedBlanks) {
        console.log(`填空题答案数组长度不匹配: 当前${answer.length}, 预期${expectedBlanks}`);
        initializeBlankAnswers();
      }
    }
  }
});

// 返回按钮处理函数
const goBack = () => {
  // 获取当前用户角色
  const userRole = 'teacher'; // 这里应该从authStore获取，但为简化直接使用teacher
  
  // 返回到教师工作台的评估测试页面
  router.push({ 
    path: `/${userRole}`, 
    query: { activeTab: 'assessments' } 
  });
};
</script> 