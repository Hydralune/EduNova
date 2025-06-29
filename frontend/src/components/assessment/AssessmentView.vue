<template>
  <div class="assessment-view">
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
        <!-- 评估头部信息 -->
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
          <div class="flex justify-end">
            <button 
              @click="editMode = true"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              编辑测验
            </button>
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
                      <p v-if="isTeacher" class="text-sm text-gray-600 mt-2">
                        正确答案: {{ Array.isArray(question.answer) ? question.answer.join(', ') : question.answer }}
                      </p>
                    </div>
                    
                    <!-- 判断题答案 -->
                    <div v-if="question.type === 'true_false'" class="mt-2">
                      <div class="flex items-center space-x-4">
                        <div class="flex items-center">
                          <input 
                            type="radio" 
                            :id="`q-${sectionIndex}-${qIndex}-true`" 
                            :name="`q-${sectionIndex}-${qIndex}`"
                            value="true"
                            :checked="answers[sectionIndex]?.[qIndex] === 'true'"
                            @change="answers[sectionIndex][qIndex] = 'true'"
                            class="mr-2"
                          />
                          <label :for="`q-${sectionIndex}-${qIndex}-true`">正确</label>
                        </div>
                        <div class="flex items-center">
                          <input 
                            type="radio" 
                            :id="`q-${sectionIndex}-${qIndex}-false`" 
                            :name="`q-${sectionIndex}-${qIndex}`"
                            value="false"
                            :checked="answers[sectionIndex]?.[qIndex] === 'false'"
                            @change="answers[sectionIndex][qIndex] = 'false'"
                            class="mr-2"
                          />
                          <label :for="`q-${sectionIndex}-${qIndex}-false`">错误</label>
                        </div>
                      </div>
                      <p v-if="isTeacher" class="text-sm text-gray-600 mt-2">
                        正确答案: {{ question.answer === 'true' ? '正确' : '错误' }}
                      </p>
                    </div>
                    
                    <!-- 填空题答案 -->
                    <div v-if="question.type === 'fill_in_blank'" class="mt-2">
                      <div 
                        v-for="(_, blankIndex) in answers[sectionIndex][qIndex]" 
                        :key="blankIndex"
                        class="flex items-center mb-2"
                      >
                        <input 
                          type="text" 
                          :placeholder="`第 ${blankIndex + 1} 空`"
                          v-model="answers[sectionIndex][qIndex][blankIndex]"
                          class="border rounded px-2 py-1"
                        />
                      </div>
                      <p v-if="isTeacher" class="text-sm text-gray-600 mt-2">
                        正确答案: {{ Array.isArray(question.answer) ? question.answer.join(' | ') : question.answer }}
                      </p>
                    </div>
                    
                    <!-- 简答题和论述题 -->
                    <div v-if="question.type === 'short_answer' || question.type === 'essay'" class="mt-2">
                      <textarea 
                        v-model="answers[sectionIndex][qIndex]"
                        :rows="question.type === 'essay' ? 6 : 3"
                        class="w-full border rounded px-2 py-1"
                        :placeholder="'请在此输入答案'"
                      ></textarea>
                      <p v-if="isTeacher" class="text-sm text-gray-600 mt-2">
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

      <!-- 学生模式 -->
      <div v-else>
        <!-- 评估头部信息 -->
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
          
          <div class="flex justify-between items-center">
            <div>
              <span v-if="!started && !submitted" class="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">未开始</span>
              <span v-else-if="started && !submitted" class="text-sm bg-yellow-100 text-yellow-800 px-2 py-1 rounded">进行中</span>
              <span v-else class="text-sm bg-green-100 text-green-800 px-2 py-1 rounded">已提交</span>
            </div>
            
            <div v-if="!started && !submitted">
              <button 
                @click="startAssessment" 
                class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                开始评估
              </button>
            </div>
            
            <div v-if="started && !submitted" class="text-right">
              <p class="text-sm text-red-600 mb-2" v-if="timeLimit">
                剩余时间: {{ formatTime(remainingTime) }}
              </p>
            </div>
          </div>
        </div>
        
        <!-- 评估内容 -->
        <div v-if="started && !submitted" class="space-y-8">
          <!-- 循环显示各个部分 -->
          <div v-for="(section, sectionIndex) in assessment.sections" :key="sectionIndex" class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <h3 class="text-xl font-semibold mb-4">{{ section.description }}</h3>
            <p class="text-sm text-gray-600 mb-4">每题 {{ section.score_per_question }} 分</p>
            
            <!-- 题目列表 -->
            <div class="space-y-6">
              <div v-for="(question, qIndex) in section.questions" :key="qIndex" class="border-b pb-4 last:border-b-0">
                <div class="flex">
                  <span class="font-medium mr-2">{{ qIndex + 1 }}.</span>
                  <div class="flex-1">
                    <p class="mb-3" v-html="question.stem"></p>
                    
                    <!-- 单选题 -->
                    <div v-if="question.type === 'multiple_choice'" class="space-y-2">
                      <div 
                        v-for="(option, optIndex) in question.options" 
                        :key="optIndex"
                        class="flex items-center"
                      >
                        <input 
                          type="radio" 
                          :id="`q-${sectionIndex}-${qIndex}-${optIndex}`" 
                          :name="`q-${sectionIndex}-${qIndex}`"
                          :value="String.fromCharCode(65 + optIndex)"
                          v-model="answers[sectionIndex][qIndex]"
                          class="mr-2"
                        />
                        <label :for="`q-${sectionIndex}-${qIndex}-${optIndex}`">
                          {{ String.fromCharCode(65 + optIndex) }}. {{ option }}
                        </label>
                      </div>
                    </div>
                    
                    <!-- 多选题 -->
                    <div v-if="question.type === 'multiple_select'" class="space-y-2">
                      <div 
                        v-for="(option, optIndex) in question.options" 
                        :key="optIndex"
                        class="flex items-center"
                      >
                        <input 
                          type="checkbox" 
                          :id="`q-${sectionIndex}-${qIndex}-${optIndex}`" 
                          :value="String.fromCharCode(65 + optIndex)"
                          v-model="answers[sectionIndex][qIndex]"
                          class="mr-2"
                        />
                        <label :for="`q-${sectionIndex}-${qIndex}-${optIndex}`">
                          {{ String.fromCharCode(65 + optIndex) }}. {{ option }}
                        </label>
                      </div>
                    </div>
                    
                    <!-- 判断题 -->
                    <div v-if="question.type === 'true_false'" class="space-y-2">
                      <div class="flex items-center space-x-4">
                        <div class="flex items-center">
                          <input 
                            type="radio" 
                            :id="`q-${sectionIndex}-${qIndex}-true`" 
                            :name="`q-${sectionIndex}-${qIndex}`"
                            value="true"
                            :checked="answers[sectionIndex]?.[qIndex] === 'true'"
                            @change="answers[sectionIndex][qIndex] = 'true'"
                            class="mr-2"
                          />
                          <label :for="`q-${sectionIndex}-${qIndex}-true`">正确</label>
                        </div>
                        <div class="flex items-center">
                          <input 
                            type="radio" 
                            :id="`q-${sectionIndex}-${qIndex}-false`" 
                            :name="`q-${sectionIndex}-${qIndex}`"
                            value="false"
                            :checked="answers[sectionIndex]?.[qIndex] === 'false'"
                            @change="answers[sectionIndex][qIndex] = 'false'"
                            class="mr-2"
                          />
                          <label :for="`q-${sectionIndex}-${qIndex}-false`">错误</label>
                        </div>
                      </div>
                    </div>
                    
                    <!-- 填空题 -->
                    <div v-if="question.type === 'fill_in_blank'" class="space-y-2">
                      <div 
                        v-for="(_, blankIndex) in answers[sectionIndex][qIndex]" 
                        :key="blankIndex"
                        class="flex items-center"
                      >
                        <input 
                          type="text" 
                          :placeholder="`第 ${blankIndex + 1} 空`"
                          v-model="answers[sectionIndex][qIndex][blankIndex]"
                          class="border rounded px-2 py-1"
                        />
                      </div>
                    </div>
                    
                    <!-- 简答题 -->
                    <div v-if="question.type === 'short_answer'" class="mt-2">
                      <textarea 
                        v-model="answers[sectionIndex][qIndex]"
                        rows="3"
                        class="w-full border rounded px-2 py-1"
                        :placeholder="'请在此输入答案'"
                      ></textarea>
                    </div>
                    
                    <!-- 论述题 -->
                    <div v-if="question.type === 'essay'" class="mt-2">
                      <textarea 
                        v-model="answers[sectionIndex][qIndex]"
                        rows="6"
                        class="w-full border rounded px-2 py-1"
                        :placeholder="'请在此输入答案'"
                      ></textarea>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 提交按钮 -->
          <div class="flex justify-between">
            <button 
              @click="saveProgress" 
              class="px-4 py-2 border rounded-md hover:bg-gray-50"
            >
              保存进度
            </button>
            <button 
              @click="submitAssessment" 
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              提交答案
            </button>
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
          
          <!-- 展示详细结果 -->
          <div class="space-y-6">
            <!-- 这里可以添加详细的答案和解析 -->
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
            class="px-4 py-2 border rounded-md"
          >
            取消
          </button>
          <button 
            @click="confirmSubmit" 
            class="px-4 py-2 bg-blue-600 text-white rounded-md"
          >
            确认提交
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import AssessmentEditor from './AssessmentEditor.vue';
import { assessmentAPI } from '@/api';

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

const emit = defineEmits(['submit', 'save-progress']);

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

// 答案数据
const answers = ref([]);

// 初始化答案
const initAnswers = () => {
  answers.value = assessment.sections.map(section => {
    return section.questions.map(question => {
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
    });
  });
  console.log('Initialized answers:', answers.value);
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
        answer: q.answer || '',
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
    answers[sectionIndex][qIndex].files.push(file);
  }
  // 重置文件输入以允许重复选择同一文件
  event.target.value = '';
};

// 移除文件
const removeFile = (sectionIndex, qIndex, fileIndex) => {
  answers[sectionIndex][qIndex].files.splice(fileIndex, 1);
};

// 保存进度
const saveProgress = () => {
  // 实际应用中应该调用API保存进度
  console.log('保存进度:', answers);
  emit('save-progress', {
    assessmentId: assessment.id,
    answers: JSON.parse(JSON.stringify(answers))
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
    answers: JSON.parse(JSON.stringify(answers)),
    submissionTime: submissionTime.value,
    timeSpent: timeLimit.value ? timeLimit.value - remainingTime.value : null
  });
  
  // 显示结果
  showResults.value = true;
};

// 计算得分（简单模拟）
const calculateScore = () => {
  let totalScore = 0;
  
  assessment.sections.forEach((section, sectionIndex) => {
    section.questions.forEach((question, qIndex) => {
      if (question.type === 'multiple_choice') {
        if (answers[sectionIndex][qIndex] === question.answer) {
          totalScore += section.score_per_question;
        }
      } else if (question.type === 'multiple_select') {
        // 多选题要完全匹配才得分
        const userAnswer = answers[sectionIndex][qIndex].sort();
        const correctAnswer = question.answer.sort();
        if (JSON.stringify(userAnswer) === JSON.stringify(correctAnswer)) {
          totalScore += section.score_per_question;
        }
      } else if (question.type === 'fill_in_blank') {
        // 简单处理单个空和多个空的情况
        if (Array.isArray(question.answer)) {
          let correct = true;
          question.answer.forEach((ans, i) => {
            if (answers[sectionIndex][qIndex][i]?.toLowerCase() !== ans.toLowerCase()) {
              correct = false;
            }
          });
          if (correct) totalScore += section.score_per_question;
        } else if (answers[sectionIndex][qIndex][0]?.toLowerCase() === question.answer.toLowerCase()) {
          totalScore += section.score_per_question;
        }
      } else if (question.type === 'true_false') {
        if (answers[sectionIndex][qIndex] === question.answer) {
          totalScore += section.score_per_question;
        }
      }
      // 简答题和论述题需要人工评分
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
</script> 