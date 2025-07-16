<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-semibold">{{ assessment.id ? '编辑评估' : '创建评估' }}</h2>
      <div class="flex items-center space-x-2">
        <button 
          type="button"
          @click="showAiGenerationModal = true" 
          class="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 flex items-center"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h7z"></path>
          </svg>
          AI一键生成
        </button>
        <button @click="$emit('cancel')" class="text-gray-500 hover:text-gray-700">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- 基本信息 -->
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">评估标题</label>
          <input 
            v-model="form.title"
            type="text"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="输入评估标题"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">描述</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="输入评估描述"
          ></textarea>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">所属课程</label>
            <select
              v-model="form.course_id"
              required
              :disabled="loading"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">选择课程</option>
              <option v-if="loading" value="" disabled>加载中...</option>
              <option v-else-if="courses.length === 0" value="" disabled>暂无可选课程</option>
              <option v-else v-for="course in courses" :key="course.id" :value="course.id">
                {{ course.name }}
              </option>
            </select>
            <p v-if="courses.length === 0 && !loading" class="mt-1 text-sm text-gray-500">
              请先在课程管理中创建课程
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">总分</label>
            <input
              v-model.number="form.total_score"
              type="number"
              required
              min="0"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">时间限制（分钟）</label>
            <input
              v-model.number="form.duration"
              type="number"
              min="0"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="不填则无限制"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">最大尝试次数</label>
            <input
              v-model.number="form.max_attempts"
              type="number"
              min="0"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="不填则无限制"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">开始时间</label>
            <input
              v-model="form.start_date"
              type="datetime-local"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700">截止时间</label>
            <input
              v-model="form.due_date"
              type="datetime-local"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        <div class="flex items-center">
          <input
            v-model="form.is_active"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label class="ml-2 block text-sm text-gray-900">
            立即发布
          </label>
        </div>
      </div>

      <!-- 题目列表 -->
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-medium">题目列表</h3>
          <button
            type="button"
            @click="addQuestion"
            class="px-3 py-1 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            添加题目
          </button>
        </div>

        <div v-if="form.questions.length === 0" class="text-center py-8 bg-gray-50 rounded-md">
          <p class="text-gray-500">暂无题目，点击"添加题目"按钮开始添加</p>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="(question, index) in form.questions"
            :key="index"
            class="p-4 border rounded-md"
          >
            <div class="flex justify-between items-start mb-4">
              <h4 class="font-medium">题目 {{ index + 1 }}</h4>
              <button
                type="button"
                @click="removeQuestion(index)"
                class="text-red-600 hover:text-red-800"
              >
                删除
              </button>
            </div>

            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">题目类型</label>
                <select
                  v-model="question.type"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="multiple_choice">单选题</option>
                  <option value="multiple_answer">多选题</option>
                  <option value="true_false">判断题</option>
                  <option value="fill_blank">填空题</option>
                  <option value="short_answer">简答题</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">题目内容</label>
                <textarea
                  v-model="question.content"
                  rows="3"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                ></textarea>
              </div>

              <!-- 多选题选项 -->
              <div v-if="['multiple_choice', 'multiple_answer'].includes(question.type)">
                <label class="block text-sm font-medium text-gray-700 mb-2">选项</label>
                <div class="space-y-2">
                  <div
                    v-for="(option, optionIndex) in question.options"
                    :key="optionIndex"
                    class="flex items-center space-x-2"
                  >
                    <input
                      v-if="question.type === 'multiple_choice'"
                      type="radio"
                      :name="`question_${index}`"
                      :value="optionIndex"
                      v-model="question.answer"
                      class="h-4 w-4"
                    />
                    <div v-else class="h-4 w-4">
                      <input
                        type="checkbox"
                        :id="`question_${index}_option_${optionIndex}`" 
                        :checked="isOptionSelected(question, optionIndex)"
                        @change="toggleAnswerOption(question, optionIndex)"
                        class="h-4 w-4"
                      />
                    </div>
                    <input
                      v-model="question.options[optionIndex]"
                      type="text"
                      class="flex-1 px-3 py-1 border border-gray-300 rounded-md"
                      :placeholder="'选项 ' + (optionIndex + 1)"
                    />
                    <button
                      type="button"
                      @click="removeOption(question, optionIndex)"
                      class="text-red-600 hover:text-red-800"
                    >
                      删除
                    </button>
                  </div>
                  <button
                    type="button"
                    @click="addOption(question)"
                    class="text-blue-600 hover:text-blue-800"
                  >
                    添加选项
                  </button>
                </div>
              </div>

              <!-- true/false question -->
              <div v-else-if="question.type === 'true_false'">
                <label class="block text-sm font-medium text-gray-700">正确答案</label>
                <div class="mt-1 space-x-4">
                  <label class="inline-flex items-center">
                    <input
                      type="radio"
                      v-model="question.answer"
                      :value="true"
                      class="h-4 w-4"
                    />
                    <span class="ml-2">正确</span>
                  </label>
                  <label class="inline-flex items-center">
                    <input
                      type="radio"
                      v-model="question.answer"
                      :value="false"
                      class="h-4 w-4"
                    />
                    <span class="ml-2">错误</span>
                  </label>
                </div>
              </div>

              <!-- Fill in blank question answers -->
              <div v-else-if="question.type === 'fill_blank'">
                <label class="block text-sm font-medium text-gray-700 mb-2">答案</label>
                <div v-if="!Array.isArray(question.answer)" class="mb-2">
                  <input
                    v-model="question.answer"
                    type="text"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="填入答案"
                  />
                  <button 
                    type="button"
                    @click="convertToMultipleAnswers(question)"
                    class="mt-2 text-sm text-blue-600 hover:text-blue-800"
                  >
                    使用多个空格
                  </button>
                </div>
                <div v-else class="space-y-2">
                  <div v-for="(answer, answerIndex) in question.answer" :key="answerIndex" class="flex items-center space-x-2">
                    <span class="text-sm w-24">空格 {{ answerIndex + 1 }}:</span>
                    <input
                      v-model="question.answer[answerIndex]"
                      type="text"
                      class="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                      :placeholder="`空格 ${answerIndex + 1} 的答案`"
                    />
                    <button
                      v-if="question.answer.length > 1"
                      type="button"
                      @click="removeAnswer(question, answerIndex)"
                      class="text-red-600 hover:text-red-800"
                    >
                      删除
                    </button>
                  </div>
                  <div class="flex space-x-2">
                    <button
                      type="button"
                      @click="addAnswer(question)"
                      class="text-blue-600 hover:text-blue-800"
                    >
                      添加空格
                    </button>
                    <button 
                      v-if="question.answer.length > 1"
                      type="button"
                      @click="convertToSingleAnswer(question)"
                      class="text-blue-600 hover:text-blue-800"
                    >
                      使用单个空格
                    </button>
                  </div>
                </div>
              </div>

              <!-- Short answer -->
              <div v-else-if="question.type === 'short_answer'">
                <label class="block text-sm font-medium text-gray-700">参考答案</label>
                <textarea
                  v-model="question.answer"
                  rows="3"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="输入参考答案"
                ></textarea>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">分值</label>
                <input
                  v-model.number="question.score"
                  type="number"
                  min="0"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="flex justify-end space-x-3">
        <button
          type="button"
          @click="$emit('cancel')"
          class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          取消
        </button>
        <button
          type="submit"
          class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          保存
        </button>
      </div>
    </form>

    <!-- AI生成评估模态框 -->
    <div v-if="showAiGenerationModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-xl">
        <h3 class="text-xl font-bold mb-4 flex items-center">
          <svg class="w-6 h-6 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
          </svg>
          AI生成评估
        </h3>
        
        <div v-if="isGenerating" class="py-8 text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p class="text-gray-600 font-medium">{{ statusMessage }}</p>
          <div class="mt-4 w-full bg-gray-200 rounded-full h-2.5">
            <div class="bg-purple-600 h-2.5 rounded-full progress-bar"></div>
          </div>
          <p class="mt-2 text-sm text-gray-500">生成高质量评估内容可能需要1-3分钟，请耐心等待</p>
        </div>
        
        <form v-else @submit.prevent="generateAssessmentWithAI" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">评估类型</label>
            <select 
              v-model="aiGenerationParams.assessment_type" 
              class="w-full px-3 py-2 border rounded-md"
            >
              <option value="quiz">测验</option>
              <option value="exam">考试</option>
              <option value="homework">作业</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">难度</label>
            <select 
              v-model="aiGenerationParams.difficulty" 
              class="w-full px-3 py-2 border rounded-md"
            >
              <option value="easy">简单</option>
              <option value="medium">中等</option>
              <option value="hard">困难</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">额外要求或提示（可选）</label>
            <textarea 
              v-model="aiGenerationParams.extra_info" 
              rows="3"
              class="w-full px-3 py-2 border rounded-md"
              placeholder="例如：侧重于某个章节内容、特定题型要求等"
            ></textarea>
          </div>
          
          <div class="flex justify-end space-x-3 mt-6">
            <button 
              type="button"
              @click="showAiGenerationModal = false"
              class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100"
            >
              取消
            </button>
            <button 
              type="submit"
              class="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
            >
              开始生成
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import { courseAPI, assessmentAPI } from '@/api';

const props = defineProps({
  assessment: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['save', 'cancel']);

// 表单数据
const form = ref({
  title: props.assessment.title || '',
  description: props.assessment.description || '',
  course_id: props.assessment.course_id || '',
  total_score: props.assessment.total_score || 100,
  duration: props.assessment.duration || null,
  start_date: props.assessment.start_date || null,
  due_date: props.assessment.due_date || null,
  max_attempts: props.assessment.max_attempts || null,
  is_active: props.assessment.is_active || false,
  questions: props.assessment.questions || []
});

// 课程列表
const courses = ref([]);
const loading = ref(false);

// 获取课程列表
const fetchCourses = async () => {
  loading.value = true;
  try {
    const response = await courseAPI.getMyCourses();
    courses.value = response.courses || [];
  } catch (error) {
    console.error('获取课程列表失败:', error);
  } finally {
    loading.value = false;
  }
};

// 添加题目
const addQuestion = () => {
  form.value.questions.push({
    type: 'multiple_choice',
    content: '',
    options: ['', ''],
    answer: 0,
    answers: [false, false], // 为多选题初始化answers数组
    score: 10
  });
};

// 删除题目
const removeQuestion = (index) => {
  form.value.questions.splice(index, 1);
};

// 添加选项
const addOption = (question) => {
  question.options.push('');
  
  // 如果是多选题，确保answers数组已初始化
  if (question.type === 'multiple_answer') {
    if (!question.answers) {
      question.answers = Array(question.options.length).fill(false);
    }
    // 为新选项添加一个默认为false的状态
    question.answers.push(false);
  }
};

// 填空题相关函数
const convertToMultipleAnswers = (question) => {
  // 将单一答案转换为数组形式
  const currentAnswer = question.answer;
  question.answer = [currentAnswer || ''];
};

const convertToSingleAnswer = (question) => {
  // 将多答案数组转换为单一答案
  if (Array.isArray(question.answer) && question.answer.length > 0) {
    question.answer = question.answer[0] || '';
  }
};

const addAnswer = (question) => {
  // 添加一个新的填空答案
  if (Array.isArray(question.answer)) {
    question.answer.push('');
  } else {
    question.answer = [question.answer || '', ''];
  }
};

const removeAnswer = (question, index) => {
  // 删除指定索引的填空答案
  if (Array.isArray(question.answer) && question.answer.length > 1) {
    question.answer.splice(index, 1);
  }
};

// 多选题相关函数
const isOptionSelected = (question, optionIndex) => {
  // 确保answers数组已初始化
  if (!question.answers) {
    question.answers = Array(question.options.length).fill(false);
  }
  
  // 如果answers数组长度不足，扩展它
  while (question.answers.length < question.options.length) {
    question.answers.push(false);
  }
  
  return question.answers[optionIndex];
};

const toggleAnswerOption = (question, optionIndex) => {
  // 确保answers数组已初始化
  if (!question.answers) {
    question.answers = Array(question.options.length).fill(false);
  }
  
  // 如果answers数组长度不足，扩展它
  while (question.answers.length < question.options.length) {
    question.answers.push(false);
  }
  
  // 切换选项状态
  question.answers[optionIndex] = !question.answers[optionIndex];
};

// 删除选项
const removeOption = (question, index) => {
  question.options.splice(index, 1);
  if (question.type === 'multiple_choice') {
    if (question.answer >= index) {
      question.answer = Math.max(0, question.answer - 1);
    }
  } else if (question.type === 'multiple_answer') {
    // 确保answers数组存在
    if (!question.answers) {
      question.answers = Array(question.options.length).fill(false);
    } else {
      // 移除对应的答案项
      question.answers.splice(index, 1);
    }
  }
};

// 处理题目保存
const handleSubmit = async () => {
  try {
    // 转换题目数据为sections格式
    const sections = [];
    
    // 按题目类型分组
    const groupedQuestions = {};
    
    form.value.questions.forEach(question => {
      if (!groupedQuestions[question.type]) {
        groupedQuestions[question.type] = [];
      }
      
      // 为填空题做特殊处理，确保类型正确
      let questionType = question.type;
      
      // 准备题目数据
      const questionData = {
        id: question.id || sections.length + groupedQuestions[question.type].length + 1,
        stem: question.content,
        score: question.score,
        type: questionType, // 保持原始类型
      };
      
      // 根据题目类型设置特定属性
      if (question.type === 'multiple_choice' || question.type === 'multiple_answer') {
        questionData.options = question.options;
        
        if (question.type === 'multiple_choice') {
          questionData.answer = question.answer;
        } else {
          // 多选题答案
          questionData.answer = question.answers
            .map((isSelected, index) => isSelected ? index : null)
            .filter(index => index !== null);
        }
      } else if (question.type === 'fill_blank' || question.type === 'fill_in_blank') {
        // 确保填空题答案格式正确
        if (Array.isArray(question.answer) && question.answer.length > 0) {
          questionData.answer = question.answer.map(item => item || '');
        } else if (typeof question.answer === 'string') {
          // 如果是单个空白，确保不是空字符串
          questionData.answer = question.answer || '';
        } else {
          // 默认值
          questionData.answer = '';
        }
        
        // 如果是填空题，也设置section_type属性确保兼容性
        questionData.section_type = 'fill_blank';
      } else if (question.type === 'true_false') {
        questionData.answer = question.answer;
      } else if (question.type === 'short_answer') {
        questionData.reference_answer = question.reference_answer || '';
      }
      
      groupedQuestions[question.type].push(questionData);
    });
    
    // 构建sections
    Object.entries(groupedQuestions).forEach(([type, questions]) => {
      if (questions.length > 0) {
        // 为填空题类型做特殊处理，确保兼容性
        let sectionType = type;
        if (type === 'fill_blank') {
          sectionType = 'fill_in_blank'; // 使用后端期望的类型
        }
        
        sections.push({
          type: sectionType,
          description: getSectionDescription(type),
          score_per_question: getAverageScore(questions),
          questions: questions
        });
      }
    });
    
    // 准备提交数据
    const assessmentData = {
      ...form.value,
      sections: sections
    };
    
    // 如果正在编辑现有评估
    if (props.assessment.id) {
      assessmentData.id = props.assessment.id;
    }
    
    // 发送保存事件
    emit('save', assessmentData);
    
  } catch (error) {
    console.error('准备评估数据失败:', error);
    alert('保存失败，请检查表单数据');
  }
};

// 获取分区描述
const getSectionDescription = (type) => {
  switch (type) {
    case 'multiple_choice': return '选择题：请在每小题给出的选项中选出一个正确答案。';
    case 'multiple_answer': return '多选题：请在每小题给出的选项中选出所有正确答案。';
    case 'fill_blank':
    case 'fill_in_blank': return '填空题：请在横线上填写正确的内容。';
    case 'true_false': return '判断题：请判断以下说法是否正确。';
    case 'short_answer': return '简答题：请简要回答以下问题。';
    default: return `${type}题`;
  }
};

// 计算平均分值
const getAverageScore = (questions) => {
  if (!questions || questions.length === 0) return 10;
  const totalScore = questions.reduce((sum, q) => sum + (q.score || 0), 0);
  return Math.round(totalScore / questions.length);
};

// 在组件挂载时获取课程列表
onMounted(() => {
  fetchCourses();
});

// AI生成评估相关逻辑
const showAiGenerationModal = ref(false);
const isGenerating = ref(false);
const aiGenerationParams = reactive({
  assessment_type: 'quiz',
  difficulty: 'medium',
  extra_info: ''
});
const statusMessage = ref('初始化中...');

// 辅助函数：处理和标准化评估数据
const processAssessmentData = (data) => {
  // 检查和提取评估数据，处理不同的数据结构
  let assessmentData = null;
  
  // 情况1: data本身就是评估数据
  if (data && data.title && (data.questions || data.sections)) {
    assessmentData = data;
  } 
  // 情况2: data.assessment包含评估数据
  else if (data && data.assessment) {
    assessmentData = data.assessment;
  }
  // 情况3: data可能是一个嵌套对象
  else if (data && typeof data === 'object') {
    // 尝试查找含有评估数据的对象
    for (const key in data) {
      if (data[key] && 
          (data[key].title || data[key].questions || data[key].sections) &&
          typeof data[key] === 'object') {
        assessmentData = data[key];
        break;
      }
    }
  }
  
  if (assessmentData) {
    console.log('成功提取评估数据:', assessmentData);
  } else {
    console.error('无法从响应中提取评估数据:', data);
  }
  
  return assessmentData;
};

const generateAssessmentWithAI = async () => {
  // 验证是否选择了课程
  if (!form.value.course_id) {
    showAiGenerationModal.value = false;
    alert('请先选择课程，AI需要课程信息来生成相关评估内容');
    return;
  }
  
  isGenerating.value = true;
  statusMessage.value = '正在初始化生成请求...';
  
  try {
    console.log('开始发送生成请求...');
    // 获取选中课程的信息
    const selectedCourse = courses.value.find(course => course.id == form.value.course_id) || {};
    
    // 准备请求数据
    const requestData = {
      course_name: selectedCourse.name || form.value.title || '',
      course_description: selectedCourse.description || form.value.description || '',
      assessment_type: aiGenerationParams.assessment_type,
      difficulty: aiGenerationParams.difficulty,
      extra_info: aiGenerationParams.extra_info,
      course_id: form.value.course_id
    };
    
    console.log('发送AI生成请求:', requestData);
    statusMessage.value = '评估生成中...这可能需要1-2分钟，请耐心等待';
    
    // 发送生成请求，获取请求ID
    const response = await assessmentAPI.generateAssessmentWithAI(requestData);
    console.log('收到AI生成响应:', response);
    
    // 检查响应中是否包含请求ID
    if (!response) {
      console.error('无响应对象');
      throw new Error('服务器未返回响应');
    }
    
    // 调试: 打印完整响应对象
    console.log('响应对象完整内容:', response);
    console.log('响应数据类型:', typeof response.data);
    
    // 检查 request_id 是否存在
    if (response.data && response.data.request_id) {
      const requestId = response.data.request_id;
      console.log('成功获取请求ID:', requestId);
      statusMessage.value = '正在获取生成结果...';
      
      // 设置轮询参数
      const maxAttempts = 30; // 增加尝试次数，以适应长时间的生成过程
      const pollingInterval = 6000; // 6秒查询一次
      let assessmentData = null;
      
      // 轮询等待结果
      for (let i = 0; i < maxAttempts; i++) {
        statusMessage.value = `正在生成评估内容 (${i+1}/${maxAttempts})...`;
        
        try {
          // 等待一段时间后查询
          await new Promise(resolve => setTimeout(resolve, pollingInterval));
          
          const statusResponse = await assessmentAPI.getAIGenerationStatus(requestId);
          console.log(`查询状态 ${i+1}:`, statusResponse);
          
          // 安全检查: 确保statusResponse存在
          if (!statusResponse) {
            console.error(`查询状态响应为空:`, statusResponse);
            continue; // 继续尝试
          }
          
          // 处理不同的响应数据结构 (拦截器可能已经提取了.data属性)
          // 情况1: statusResponse就是原始响应对象 {status, assessment, ...}
          // 情况2: statusResponse包含data属性 {data: {status, assessment, ...}}
          const responseData = statusResponse.data || statusResponse;
          
          console.log(`处理后的响应数据:`, responseData);
          
          // 检查状态
          if (responseData.status === 'success' && responseData.assessment) {
            // 成功获取评估数据
            assessmentData = processAssessmentData(responseData);
            if (assessmentData) break;
          } else if (responseData.status === 'error') {
            // 生成出错
            console.error('生成过程报错:', responseData.error || responseData.message);
            throw new Error(responseData.error || responseData.message || '生成失败');
          } else if (responseData.status === 'processing') {
            // 继续等待，更新进度信息
            console.log('生成仍在处理中:', responseData.progress || '无进度信息');
            if (responseData.progress) {
              statusMessage.value = responseData.progress;
            }
            
            // 检测特定条件，判断是否可能后端已完成但返回有问题
            // 后端日志显示"评估已生成完成"但前端仍在等待的情况
            if (i > 10 && !assessmentData) { // 如果轮询超过10次还没有数据，尝试直接获取
              try {
                console.log("尝试直接获取评估文件内容...");
                // 使用一个API来请求直接获取文件内容
                const directResponse = await fetch(`/api/assessments/ai-file/${requestId}`, {
                  method: 'GET',
                  headers: { 'Content-Type': 'application/json' }
                });
                
                if (directResponse.ok) {
                  const fileData = await directResponse.json();
                  if (fileData && fileData.assessment) {
                    console.log('通过直接访问文件获取评估数据:', fileData);
                    assessmentData = processAssessmentData(fileData);
                    if (assessmentData) break;
                  }
                }
              } catch (fileError) {
                console.warn('直接获取文件失败，继续轮询:', fileError);
                // 继续轮询，不中断流程
              }
            }
            
            continue;
          } else {
            // 未识别的状态
            console.warn(`未识别的状态响应:`, responseData);
            continue;
          }
        } catch (err) {
          console.error('查询状态失败:', err);
          
          // 如果不是最后一次尝试，继续轮询
          if (i < maxAttempts - 1) {
            console.log(`将在${pollingInterval/1000}秒后重试...`);
            continue;
          }
          
          // 如果是最后一次尝试，则抛出错误
          throw new Error('多次尝试后仍无法获取生成结果，请稍后再试');
        }
      }
      
      // 如果成功获取到评估数据
      if (assessmentData) {
        // 应用到表单
        form.value.title = assessmentData.title || form.value.title;
        form.value.description = assessmentData.description || form.value.description;
        
        // 处理题目数据
        let questions = [];
        
        try {
          console.log('处理评估题目数据:', assessmentData);
          
          // 处理sections格式
          if (assessmentData.sections && assessmentData.sections.length > 0) {
            console.log('使用sections格式处理题目');
            assessmentData.sections.forEach(section => {
              if (section.questions && section.questions.length > 0) {
                section.questions.forEach(q => {
                  // 处理选项 - 如果选项是字符串数组
                  const options = q.options || [];
                  
                  // 将AI生成的题型映射到前端支持的题型
                  let mappedType = q.type || section.type || 'multiple_choice';
                  let mappedAnswer = q.answer || '';
                  
                  // 题型映射
                  if (mappedType === 'multiple_select') {
                    mappedType = 'multiple_answer'; // 多选题映射
                  } else if (mappedType === 'essay') {
                    mappedType = 'short_answer'; // 论述题映射为简答题
                  } else if (mappedType === 'fill_in_blank') {
                    mappedType = 'fill_blank'; // 填空题映射
                  }
                  
                  // 答案处理
                  if (mappedType === 'multiple_choice') {
                    // 单选题答案处理
                    if (typeof mappedAnswer === 'string' && /^[A-Z]$/.test(mappedAnswer)) {
                      // 如果答案是字母A-Z，转换为索引
                      mappedAnswer = mappedAnswer.charCodeAt(0) - 65; // A=0, B=1, ...
                    }
                  } else if (mappedType === 'multiple_answer') {
                    // 多选题答案处理
                    let answers = [];
                    if (Array.isArray(mappedAnswer)) {
                      answers = mappedAnswer.map(ans => {
                        if (typeof ans === 'string' && /^[A-Z]$/.test(ans)) {
                          return ans.charCodeAt(0) - 65; // A=0, B=1, ...
                        }
                        return ans;
                      });
                    }
                    mappedAnswer = answers;
                  }
                  
                  // 标准化问题对象
                  questions.push({
                    id: questions.length + 1,
                    type: mappedType,
                    content: q.stem || q.question || '',
                    score: parseFloat(q.score || section.score_per_question || 5),
                    options: options,
                    answer: mappedType === 'multiple_answer' ? 0 : mappedAnswer, // 单选题用answer
                    answers: mappedType === 'multiple_answer' ? mappedAnswer : undefined, // 多选题用answers
                    explanation: q.explanation || '',
                    reference_answer: q.reference_answer || q.answer || '' // 保存参考答案
                  });
                });
              }
            });
          } 
          // 处理直接的questions格式
          else if (assessmentData.questions) {
            console.log('使用questions格式处理题目');
            assessmentData.questions.forEach((q, index) => {
              // 将AI生成的题型映射到前端支持的题型
              let mappedType = q.type || 'multiple_choice';
              let mappedAnswer = q.answer || '';
              
              // 题型映射
              if (mappedType === 'multiple_select') {
                mappedType = 'multiple_answer'; // 多选题映射
              } else if (mappedType === 'essay') {
                mappedType = 'short_answer'; // 论述题映射为简答题
              } else if (mappedType === 'fill_in_blank') {
                mappedType = 'fill_blank'; // 填空题映射
              }
              
              // 答案处理
              if (mappedType === 'multiple_choice') {
                // 单选题答案处理
                if (typeof mappedAnswer === 'string' && /^[A-Z]$/.test(mappedAnswer)) {
                  // 如果答案是字母A-Z，转换为索引
                  mappedAnswer = mappedAnswer.charCodeAt(0) - 65; // A=0, B=1, ...
                }
              } else if (mappedType === 'multiple_answer') {
                // 多选题答案处理
                let answers = [];
                if (Array.isArray(mappedAnswer)) {
                  answers = mappedAnswer.map(ans => {
                    if (typeof ans === 'string' && /^[A-Z]$/.test(ans)) {
                      return ans.charCodeAt(0) - 65; // A=0, B=1, ...
                    }
                    return ans;
                  });
                }
                mappedAnswer = answers;
              }
              
              questions.push({
                id: index + 1,
                type: mappedType,
                content: q.stem || q.question || '',
                score: parseFloat(q.score || 5),
                options: q.options || [],
                answer: mappedType === 'multiple_answer' ? 0 : mappedAnswer, // 单选题用answer
                answers: mappedType === 'multiple_answer' ? mappedAnswer : undefined, // 多选题用answers
                explanation: q.explanation || '',
                reference_answer: q.reference_answer || q.answer || '' // 保存参考答案
              });
            });
          }
          // 尝试处理其他可能的格式
          else if (Array.isArray(assessmentData)) {
            console.log('处理数组格式的题目');
            assessmentData.forEach((q, index) => {
              // 将AI生成的题型映射到前端支持的题型
              let mappedType = q.type || 'multiple_choice';
              let mappedAnswer = q.answer || '';
              
              // 题型映射
              if (mappedType === 'multiple_select') {
                mappedType = 'multiple_answer'; // 多选题映射
              } else if (mappedType === 'essay') {
                mappedType = 'short_answer'; // 论述题映射为简答题
              } else if (mappedType === 'fill_in_blank') {
                mappedType = 'fill_blank'; // 填空题映射
              }
              
              // 答案处理
              if (mappedType === 'multiple_choice') {
                // 单选题答案处理
                if (typeof mappedAnswer === 'string' && /^[A-Z]$/.test(mappedAnswer)) {
                  // 如果答案是字母A-Z，转换为索引
                  mappedAnswer = mappedAnswer.charCodeAt(0) - 65; // A=0, B=1, ...
                }
              } else if (mappedType === 'multiple_answer') {
                // 多选题答案处理
                let answers = [];
                if (Array.isArray(mappedAnswer)) {
                  answers = mappedAnswer.map(ans => {
                    if (typeof ans === 'string' && /^[A-Z]$/.test(ans)) {
                      return ans.charCodeAt(0) - 65; // A=0, B=1, ...
                    }
                    return ans;
                  });
                }
                mappedAnswer = answers;
              }
              
              questions.push({
                id: index + 1,
                type: mappedType,
                content: q.stem || q.question || '',
                score: parseFloat(q.score || 5),
                options: q.options || [],
                answer: mappedType === 'multiple_answer' ? 0 : mappedAnswer, // 单选题用answer
                answers: mappedType === 'multiple_answer' ? mappedAnswer : undefined, // 多选题用answers
                explanation: q.explanation || '',
                reference_answer: q.reference_answer || q.answer || '' // 保存参考答案
              });
            });
          }
          
          // 设置题目
          if (questions.length > 0) {
            console.log(`成功处理 ${questions.length} 道题目`);
            form.value.questions = questions;
          } else {
            console.warn('没有找到有效的题目数据');
            if (assessmentData.content) {
              // 尝试解析content字段作为原始数据
              try {
                const contentData = typeof assessmentData.content === 'string' 
                  ? JSON.parse(assessmentData.content)
                  : assessmentData.content;
                
                if (contentData && (contentData.questions || contentData.sections)) {
                  console.log('从content字段中提取评估数据，重新处理');
                  const reprocessedData = processAssessmentData(contentData);
                  if (reprocessedData) {
                    // 递归调用自身处理新提取的数据
                    return generateAssessmentWithAI();
                  }
                }
              } catch (parseError) {
                console.error('解析content字段失败:', parseError);
              }
            }
          }
        } catch (processError) {
          console.error('处理评估数据时出错:', processError);
        }
        
        // 关闭模态框并显示成功消息
        showAiGenerationModal.value = false;
        isGenerating.value = false;
        alert('评估内容生成成功！');
        return;
      } else {
        throw new Error('超时或未能获取有效的评估数据');
      }
    } else {
      console.error('响应格式错误，缺少request_id:', response.data);
      throw new Error('服务器响应格式错误，缺少必要的请求ID');
    }
  } catch (error) {
    console.error('生成评估失败:', error);
    alert('生成评估失败: ' + (error.message || '未知错误'));
  } finally {
    isGenerating.value = false;
    showAiGenerationModal.value = false;
  }
};
</script>

<style>
.progress-bar {
  animation: progress-animation 3s infinite;
  width: 30%;
}

@keyframes progress-animation {
  0% { width: 5%; }
  50% { width: 70%; }
  100% { width: 5%; }
}
</style> 