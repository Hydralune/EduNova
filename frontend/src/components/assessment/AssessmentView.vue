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
        <div v-else-if="isTeacher && !editMode">
    <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-6">
      <div class="flex justify-between items-center mb-4">
        <div>
          <h2 class="text-2xl font-bold">{{ assessment.title }}</h2>
          <p class="text-gray-600">{{ assessment.description }}</p>
        </div>
        <div class="text-right">
          <p class="text-sm text-gray-600">总分: {{ assessment.total_score }} 分</p>
          <p class="text-sm text-gray-600">时间限制: {{ assessment.duration }}</p>
          <p v-if="assessment.due_date" class="text-sm text-gray-600">截止日期: {{ formatDate(assessment.due_date) }}</p>
        </div>
      </div>
        </div>
        
          <!-- 题目预览 -->
          <div class="space-y-8">
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
                          <span class="mr-2">{{ String.fromCharCode(65 + optIndex) }}.</span>
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
                  <div class="w-6 h-6 flex items-center justify-center border rounded mr-3">
                    {{ String.fromCharCode(65 + optIndex) }}
            </div>
                  <div v-html="option"></div>
          </div>
        </div>
        
        <!-- 填空题 -->
              <div v-if="currentQuestion.type === 'fill_in_blank'" class="space-y-4">
                <div 
                  v-for="(_, blankIndex) in currentAnswers[currentQuestionIndex]" 
                  :key="blankIndex"
                  class="flex items-center"
                >
                  <input 
                    type="text" 
                    :placeholder="`第 ${blankIndex + 1} 空`"
                    v-model="currentAnswers[currentQuestionIndex][blankIndex]"
                    class="border rounded-md px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
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
              <div class="flex justify-between mt-8">
                <button 
                  @click="previousQuestion"
                  :disabled="currentQuestionIndex === 0"
                  :class="[
                    'px-4 py-2 border rounded-md hover:bg-gray-50',
                    currentQuestionIndex === 0 ? 'opacity-50 cursor-not-allowed' : ''
                  ]"
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
                  v-if="currentQuestionIndex === totalQuestions - 1"
                  @click="showSubmitConfirm = true"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          提交答案
        </button>
                <button 
                  v-else
                  @click="nextQuestion"
                  class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  下一题
                </button>
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
    
    <!-- 确认提交对话框 -->
    <div v-if="showSubmitConfirm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-xl font-bold mb-4">确认提交</h3>
        <p class="mb-4">您确定要提交此评估吗？提交后将无法修改答案。</p>
        <div class="flex justify-end gap-3">
          <button 
            @click="showSubmitConfirm = false" 
              class="px-4 py-2 border rounded-md hover:bg-gray-50"
          >
            取消
          </button>
          <button 
            @click="confirmSubmit" 
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            确认提交
          </button>
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

// 其他状态变量
const loading = ref(true);
const started = ref(false);
const submitted = ref(false);
const showResults = ref(false);
const showSubmitConfirm = ref(false);
const submissionTime = ref(null);
const score = ref(0);
const timeLimit = ref(null);
const remainingTime = ref(0);
const timer = ref(null);

// 新增状态
const currentQuestionIndex = ref(0);
const markedQuestions = ref(new Set());
const currentAnswers = ref([]);

// 评估数据
const assessment = reactive({
  id: typeof props.assessmentId === 'string' ? parseInt(props.assessmentId) : props.assessmentId,
  title: '',
  description: '',
  course_id: null,
  type: 'quiz',
  total_score: 0,
  duration: '',
  due_date: null,
  start_date: null,
  max_attempts: 1,
  is_published: false,
  is_active: true,
  sections: []
});

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
  return currentAnswers.value.filter(answer => {
    if (Array.isArray(answer)) {
      return answer.some(a => a !== '');
    }
    return answer !== '' && answer !== null && answer !== undefined;
  }).length;
});

const completionPercentage = computed(() => {
  return (answeredQuestions.value / totalQuestions.value) * 100;
});

// 初始化答案
const initAnswers = () => {
  currentAnswers.value = assessment.sections.flatMap(section => 
    section.questions.map(question => {
      if (question.type === 'multiple_choice' || question.type === 'true_false') {
        return '';
      } else if (question.type === 'multiple_select') {
        return [];
      } else if (question.type === 'fill_in_blank') {
        const blankCount = (question.stem.match(/_{3,}/g) || []).length || 1;
        return Array(blankCount).fill('');
      } else if (question.type === 'short_answer' || question.type === 'essay') {
        return '';
      }
      return null;
    })
  );
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
      questions: questions.map(q => ({
        ...q,
        stem: q.content || q.stem || '',  // 兼容不同的题目格式
        options: q.options || [],
        type: q.type || 'multiple_choice',
        answer: q.answer,  // 不设置默认值，保持原始值
        // 确保判断题的答案是字符串类型
        ...(q.type === 'true_false' ? { answer: String(q.answer) } : {})
      }))
    }];
    
    console.log('Generated sections:', sections);
    
    // 更新评估数据
    Object.assign(assessment, {
      ...response,
      sections
    });
    
    // 初始化答案
    initAnswers();
    
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

// 格式化时间显示
const formatTime = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
};

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

// 计算填空题的空格数
const countBlanks = (stem) => {
  const matches = stem.match(/_{3,}/g);
  return matches ? matches.length : 1;
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
  // 实际应用中应该调用API保存进度
  console.log('保存进度:', currentAnswers.value);
  emit('save-progress', {
    assessmentId: assessment.id,
    answers: JSON.parse(JSON.stringify(currentAnswers.value))
  });
};

// 提交评估
const submitAssessment = () => {
  showSubmitConfirm.value = true;
};

// 确认提交
const confirmSubmit = () => {
  showSubmitConfirm.value = false;
  submitted.value = true;
  submissionTime.value = new Date();
  
  if (timer.value) {
    clearInterval(timer.value);
  }
  
  // 计算得分（实际应用中应该由后端计算）
  calculateScore();
  
  // 发送数据到后端
  emit('submit', {
    assessmentId: assessment.id,
    answers: JSON.parse(JSON.stringify(currentAnswers.value)),
    submissionTime: submissionTime.value,
    timeSpent: timeLimit.value ? timeLimit.value - remainingTime.value : null
  });
  
  // 显示结果
  showResults.value = true;
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
          if (Array.isArray(question.answer)) {
            isCorrect = question.answer.every((ans, i) => 
              userAnswer[i]?.toLowerCase().trim() === ans.toLowerCase().trim()
            );
          } else {
            isCorrect = userAnswer[0]?.toLowerCase().trim() === question.answer.toLowerCase().trim();
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
  const answer = currentAnswers.value[index];
  if (Array.isArray(answer)) {
    return answer.some(a => a !== '');
  }
  return answer !== '' && answer !== null && answer !== undefined;
};

const getQuestionTypeName = (type) => {
  const typeNames = {
    'multiple_choice': '选择题',
    'multiple_select': '多选题',
    'true_false': '判断题',
    'fill_in_blank': '填空题',
    'short_answer': '简答题',
    'essay': '论述题'
  };
  return typeNames[type] || type;
};

const selectOption = (optIndex) => {
  currentAnswers.value[currentQuestionIndex.value] = String.fromCharCode(65 + optIndex);
};

const toggleMultiSelect = (optIndex) => {
  if (!Array.isArray(currentAnswers.value[currentQuestionIndex.value])) {
    currentAnswers.value[currentQuestionIndex.value] = [];
  }
  const answer = String.fromCharCode(65 + optIndex);
  const index = currentAnswers.value[currentQuestionIndex.value].indexOf(answer);
  if (index === -1) {
    currentAnswers.value[currentQuestionIndex.value].push(answer);
  } else {
    currentAnswers.value[currentQuestionIndex.value].splice(index, 1);
  }
};

const isOptionSelected = (optIndex) => {
  const answers = currentAnswers.value[currentQuestionIndex.value];
  return Array.isArray(answers) && answers.includes(String.fromCharCode(65 + optIndex));
};

const selectTrueFalse = (value) => {
  currentAnswers.value[currentQuestionIndex.value] = value;
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

// 在组件挂载时获取数据
onMounted(() => {
  fetchAssessment();
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
</script> 