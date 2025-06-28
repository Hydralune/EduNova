<template>
  <div class="assessment-creator">
    <h2 class="text-2xl font-bold mb-6">创建评估</h2>
    
    <form @submit.prevent="saveAssessment" class="space-y-6">
      <!-- 基本信息 -->
      <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h3 class="text-lg font-semibold mb-4">基本信息</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">评估标题</label>
            <input 
              type="text" 
              v-model="assessment.title" 
              required
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="例如：第一章测验"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">评估类型</label>
            <select 
              v-model="assessment.type" 
              required
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="quiz">测验</option>
              <option value="exam">考试</option>
              <option value="homework">作业</option>
              <option value="practice">练习</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">时间限制（分钟）</label>
            <input 
              type="number" 
              v-model.number="assessment.time_limit" 
              min="0"
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="0表示无时间限制"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">最大尝试次数</label>
            <input 
              type="number" 
              v-model.number="assessment.max_attempts" 
              min="0"
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="0表示无限制"
            />
          </div>
          
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">评估描述</label>
            <textarea 
              v-model="assessment.description" 
              rows="3"
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="描述评估的目的和内容"
            ></textarea>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">开始日期</label>
            <input 
              type="date" 
              v-model="assessment.start_date" 
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">截止日期</label>
            <input 
              type="date" 
              v-model="assessment.due_date" 
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div class="md:col-span-2">
            <div class="flex items-center">
              <input 
                type="checkbox" 
                id="is_published" 
                v-model="assessment.is_published"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500"
              />
              <label for="is_published" class="ml-2 text-sm text-gray-700">立即发布</label>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 题目列表 -->
      <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">题目列表</h3>
          <div class="flex gap-2">
            <button 
              type="button"
              @click="showQuestionBank = true"
              class="px-3 py-1.5 border rounded-md text-sm"
            >
              从题库添加
            </button>
            <button 
              type="button"
              @click="addNewQuestion"
              class="px-3 py-1.5 bg-blue-600 text-white rounded-md text-sm"
            >
              添加新题目
            </button>
          </div>
        </div>
        
        <div v-if="assessment.questions.length === 0" class="text-center py-10 bg-gray-50 rounded-md">
          <p class="text-gray-500">暂无题目，请添加题目</p>
        </div>
        
        <div v-else class="space-y-4">
          <div 
            v-for="(question, index) in assessment.questions" 
            :key="index"
            class="border rounded-md p-4"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <div class="flex items-center">
                  <span class="font-medium mr-2">问题 {{ index + 1 }}</span>
                  <span class="text-sm px-2 py-0.5 bg-gray-100 rounded-full">{{ questionTypeText(question.type) }}</span>
                  <span class="ml-2 text-sm text-gray-500">{{ question.points }} 分</span>
                </div>
                <p class="mt-2">{{ question.question }}</p>
                
                <!-- 选择题选项 -->
                <div v-if="question.type === 'multiple_choice'" class="mt-3 space-y-2">
                  <div 
                    v-for="(option, optIndex) in question.options" 
                    :key="optIndex"
                    class="flex items-center"
                  >
                    <span class="w-6 h-6 flex items-center justify-center border rounded-full mr-2" :class="question.correct_answer === optIndex ? 'bg-green-100 border-green-500' : ''">
                      {{ String.fromCharCode(65 + optIndex) }}
                    </span>
                    <span>{{ option }}</span>
                  </div>
                </div>
                
                <!-- 填空题答案 -->
                <div v-else-if="question.type === 'fill_blank'" class="mt-3">
                  <p class="text-sm text-gray-600">答案: {{ question.correct_answer }}</p>
                </div>
                
                <!-- 简答题参考答案 -->
                <div v-else-if="question.type === 'short_answer'" class="mt-3">
                  <p class="text-sm text-gray-600">参考答案:</p>
                  <p class="mt-1 text-sm">{{ question.reference_answer }}</p>
                </div>
              </div>
              
              <div class="flex gap-2">
                <button 
                  type="button"
                  @click="editQuestion(index)"
                  class="text-blue-600 hover:text-blue-800"
                >
                  编辑
                </button>
                <button 
                  type="button"
                  @click="removeQuestion(index)"
                  class="text-red-600 hover:text-red-800"
                >
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="mt-4 flex justify-between items-center">
          <p class="text-sm text-gray-500">
            总题数: {{ assessment.questions.length }} | 
            总分: {{ totalPoints }}
          </p>
          <button 
            type="button"
            @click="randomizeQuestionOrder"
            class="text-sm text-blue-600 hover:text-blue-800"
            :disabled="assessment.questions.length < 2"
          >
            随机排序
          </button>
        </div>
      </div>
      
      <!-- 提交按钮 -->
      <div class="flex justify-end gap-3">
        <button 
          type="button"
          @click="cancel"
          class="px-4 py-2 border rounded-md"
        >
          取消
        </button>
        <button 
          type="submit"
          class="px-4 py-2 bg-blue-600 text-white rounded-md"
        >
          保存评估
        </button>
      </div>
    </form>
    
    <!-- 添加/编辑题目模态框 -->
    <div v-if="showQuestionModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-bold mb-4">{{ isEditingQuestion ? '编辑题目' : '添加题目' }}</h3>
        
        <form @submit.prevent="saveQuestion" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">题目类型</label>
            <select 
              v-model="currentQuestion.type" 
              required
              class="w-full px-3 py-2 border rounded-md"
            >
              <option value="multiple_choice">选择题</option>
              <option value="fill_blank">填空题</option>
              <option value="short_answer">简答题</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">题目内容</label>
            <textarea 
              v-model="currentQuestion.question" 
              required
              rows="3"
              class="w-full px-3 py-2 border rounded-md"
              placeholder="输入题目内容"
            ></textarea>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">分值</label>
            <input 
              type="number" 
              v-model.number="currentQuestion.points" 
              required
              min="1"
              class="w-full px-3 py-2 border rounded-md"
            />
          </div>
          
          <!-- 选择题选项 -->
          <div v-if="currentQuestion.type === 'multiple_choice'">
            <label class="block text-sm font-medium text-gray-700 mb-1">选项</label>
            <div v-for="(option, index) in currentQuestion.options" :key="index" class="flex items-center mb-2">
              <span class="w-6 h-6 flex items-center justify-center border rounded-full mr-2">
                {{ String.fromCharCode(65 + index) }}
              </span>
              <input 
                type="text" 
                v-model="currentQuestion.options[index]" 
                class="flex-1 px-3 py-2 border rounded-md"
                :placeholder="`选项 ${String.fromCharCode(65 + index)}`"
              />
              <button 
                type="button"
                @click="removeOption(index)"
                class="ml-2 text-red-600 hover:text-red-800"
                :disabled="currentQuestion.options.length <= 2"
              >
                删除
              </button>
            </div>
            <button 
              type="button"
              @click="addOption"
              class="mt-2 text-sm text-blue-600 hover:text-blue-800"
              :disabled="currentQuestion.options.length >= 6"
            >
              添加选项
            </button>
            
            <div class="mt-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">正确答案</label>
              <select 
                v-model="currentQuestion.correct_answer" 
                required
                class="w-full px-3 py-2 border rounded-md"
              >
                <option 
                  v-for="(option, index) in currentQuestion.options" 
                  :key="index"
                  :value="index"
                >
                  {{ String.fromCharCode(65 + index) }}: {{ option }}
                </option>
              </select>
            </div>
          </div>
          
          <!-- 填空题答案 -->
          <div v-else-if="currentQuestion.type === 'fill_blank'">
            <label class="block text-sm font-medium text-gray-700 mb-1">正确答案</label>
            <input 
              type="text" 
              v-model="currentQuestion.correct_answer" 
              required
              class="w-full px-3 py-2 border rounded-md"
              placeholder="输入正确答案"
            />
          </div>
          
          <!-- 简答题参考答案 -->
          <div v-else-if="currentQuestion.type === 'short_answer'">
            <label class="block text-sm font-medium text-gray-700 mb-1">参考答案</label>
            <textarea 
              v-model="currentQuestion.reference_answer" 
              rows="3"
              class="w-full px-3 py-2 border rounded-md"
              placeholder="输入参考答案"
            ></textarea>
          </div>
          
          <div class="flex justify-end gap-2 mt-6">
            <button 
              type="button"
              @click="showQuestionModal = false"
              class="px-4 py-2 border rounded-md"
            >
              取消
            </button>
            <button 
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-md"
            >
              保存题目
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 题库模态框 -->
    <div v-if="showQuestionBank" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-bold mb-4">题库</h3>
        
        <div class="mb-4 flex justify-between">
          <div class="flex gap-2">
            <select v-model="questionBankFilters.type" class="border rounded-md px-3 py-2">
              <option value="">所有类型</option>
              <option value="multiple_choice">选择题</option>
              <option value="fill_blank">填空题</option>
              <option value="short_answer">简答题</option>
            </select>
            <select v-model="questionBankFilters.difficulty" class="border rounded-md px-3 py-2">
              <option value="">所有难度</option>
              <option value="easy">简单</option>
              <option value="medium">中等</option>
              <option value="hard">困难</option>
            </select>
          </div>
          <div class="relative">
            <input 
              type="text" 
              v-model="questionBankFilters.search" 
              placeholder="搜索题目..." 
              class="border rounded-md pl-10 pr-3 py-2 w-64"
            />
            <span class="absolute left-3 top-2.5 text-gray-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </span>
          </div>
        </div>
        
        <div class="border rounded-md overflow-hidden">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="w-12 px-3 py-3">
                  <input 
                    type="checkbox" 
                    v-model="selectAllQuestions"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500"
                  />
                </th>
                <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">题目</th>
                <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">类型</th>
                <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">难度</th>
                <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">分值</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="question in filteredBankQuestions" :key="question.id">
                <td class="px-3 py-4">
                  <input 
                    type="checkbox" 
                    v-model="question.selected"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500"
                  />
                </td>
                <td class="px-3 py-4">
                  <p class="line-clamp-2">{{ question.question }}</p>
                </td>
                <td class="px-3 py-4 whitespace-nowrap">
                  {{ questionTypeText(question.type) }}
                </td>
                <td class="px-3 py-4 whitespace-nowrap">
                  <span class="px-2 py-1 text-xs rounded-full" :class="difficultyClass(question.difficulty)">
                    {{ difficultyText(question.difficulty) }}
                  </span>
                </td>
                <td class="px-3 py-4 whitespace-nowrap">
                  {{ question.points }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div class="flex justify-end gap-2 mt-6">
          <button 
            type="button"
            @click="showQuestionBank = false"
            class="px-4 py-2 border rounded-md"
          >
            取消
          </button>
          <button 
            type="button"
            @click="addSelectedQuestions"
            class="px-4 py-2 bg-blue-600 text-white rounded-md"
          >
            添加所选题目
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';

const props = defineProps({
  courseId: {
    type: [Number, String],
    required: true
  }
});

const emit = defineEmits(['save', 'cancel']);

const assessment = reactive({
  title: '',
  description: '',
  type: 'quiz',
  time_limit: 30,
  max_attempts: 1,
  start_date: '',
  due_date: '',
  is_published: false,
  questions: []
});

const showQuestionModal = ref(false);
const showQuestionBank = ref(false);
const isEditingQuestion = ref(false);
const editingQuestionIndex = ref(-1);

const currentQuestion = reactive({
  type: 'multiple_choice',
  question: '',
  points: 10,
  options: ['', ''],
  correct_answer: 0,
  reference_answer: ''
});

const questionBankFilters = reactive({
  search: '',
  type: '',
  difficulty: ''
});

// 模拟题库数据
const bankQuestions = ref([
  {
    id: 1,
    question: '什么是人工智能？',
    type: 'multiple_choice',
    options: ['计算机科学的一个分支', '一种编程语言', '一种硬件设备', '一种软件应用'],
    correct_answer: 0,
    points: 10,
    difficulty: 'easy',
    selected: false
  },
  {
    id: 2,
    question: '机器学习的主要目标是什么？',
    type: 'multiple_choice',
    options: ['让计算机能够学习', '提高计算机性能', '降低能耗', '增加存储容量'],
    correct_answer: 0,
    points: 10,
    difficulty: 'medium',
    selected: false
  },
  {
    id: 3,
    question: '深度学习使用的主要数据结构是什么？',
    type: 'fill_blank',
    correct_answer: '神经网络',
    points: 15,
    difficulty: 'hard',
    selected: false
  }
]);

const totalPoints = computed(() => {
  return assessment.questions.reduce((total, q) => total + q.points, 0);
});

const filteredBankQuestions = computed(() => {
  return bankQuestions.value.filter(q => {
    const matchType = !questionBankFilters.type || q.type === questionBankFilters.type;
    const matchDifficulty = !questionBankFilters.difficulty || q.difficulty === questionBankFilters.difficulty;
    const matchSearch = !questionBankFilters.search || q.question.toLowerCase().includes(questionBankFilters.search.toLowerCase());
    return matchType && matchDifficulty && matchSearch;
  });
});

const selectAllQuestions = computed({
  get() {
    return filteredBankQuestions.value.length > 0 && filteredBankQuestions.value.every(q => q.selected);
  },
  set(value) {
    filteredBankQuestions.value.forEach(q => q.selected = value);
  }
});

function addNewQuestion() {
  isEditingQuestion.value = false;
  editingQuestionIndex.value = -1;
  
  // 重置当前题目
  Object.assign(currentQuestion, {
    type: 'multiple_choice',
    question: '',
    points: 10,
    options: ['', ''],
    correct_answer: 0,
    reference_answer: ''
  });
  
  showQuestionModal.value = true;
}

function editQuestion(index) {
  isEditingQuestion.value = true;
  editingQuestionIndex.value = index;
  
  const question = assessment.questions[index];
  
  // 复制题目数据到当前题目
  Object.assign(currentQuestion, {
    type: question.type,
    question: question.question,
    points: question.points,
    options: question.options ? [...question.options] : ['', ''],
    correct_answer: question.correct_answer,
    reference_answer: question.reference_answer || ''
  });
  
  showQuestionModal.value = true;
}

function removeQuestion(index) {
  if (confirm('确定要删除这个题目吗？')) {
    assessment.questions.splice(index, 1);
  }
}

function saveQuestion() {
  const questionData = {
    type: currentQuestion.type,
    question: currentQuestion.question,
    points: currentQuestion.points
  };
  
  if (currentQuestion.type === 'multiple_choice') {
    questionData.options = [...currentQuestion.options];
    questionData.correct_answer = currentQuestion.correct_answer;
  } else if (currentQuestion.type === 'fill_blank') {
    questionData.correct_answer = currentQuestion.correct_answer;
  } else if (currentQuestion.type === 'short_answer') {
    questionData.reference_answer = currentQuestion.reference_answer;
  }
  
  if (isEditingQuestion.value) {
    // 更新现有题目
    assessment.questions[editingQuestionIndex.value] = questionData;
  } else {
    // 添加新题目
    assessment.questions.push(questionData);
  }
  
  showQuestionModal.value = false;
}

function addOption() {
  if (currentQuestion.options.length < 6) {
    currentQuestion.options.push('');
  }
}

function removeOption(index) {
  if (currentQuestion.options.length > 2) {
    currentQuestion.options.splice(index, 1);
    // 如果删除的是正确答案，重置正确答案
    if (currentQuestion.correct_answer === index) {
      currentQuestion.correct_answer = 0;
    } else if (currentQuestion.correct_answer > index) {
      currentQuestion.correct_answer--;
    }
  }
}

function addSelectedQuestions() {
  const selectedQuestions = bankQuestions.value.filter(q => q.selected);
  
  selectedQuestions.forEach(q => {
    const questionData = {
      type: q.type,
      question: q.question,
      points: q.points
    };
    
    if (q.type === 'multiple_choice') {
      questionData.options = [...q.options];
      questionData.correct_answer = q.correct_answer;
    } else if (q.type === 'fill_blank') {
      questionData.correct_answer = q.correct_answer;
    } else if (q.type === 'short_answer') {
      questionData.reference_answer = q.reference_answer || '';
    }
    
    assessment.questions.push(questionData);
  });
  
  // 重置选择状态
  bankQuestions.value.forEach(q => q.selected = false);
  
  showQuestionBank.value = false;
}

function randomizeQuestionOrder() {
  assessment.questions = [...assessment.questions].sort(() => Math.random() - 0.5);
}

function saveAssessment() {
  // 这里应该调用API保存评估
  // 添加课程ID
  const assessmentData = {
    ...assessment,
    course_id: props.courseId
  };
  
  emit('save', assessmentData);
}

function cancel() {
  emit('cancel');
}

function questionTypeText(type) {
  switch (type) {
    case 'multiple_choice': return '选择题';
    case 'fill_blank': return '填空题';
    case 'short_answer': return '简答题';
    default: return '未知类型';
  }
}

function difficultyClass(difficulty) {
  switch (difficulty) {
    case 'easy': return 'bg-green-100 text-green-800';
    case 'medium': return 'bg-yellow-100 text-yellow-800';
    case 'hard': return 'bg-red-100 text-red-800';
    default: return 'bg-gray-100 text-gray-800';
  }
}

function difficultyText(difficulty) {
  switch (difficulty) {
    case 'easy': return '简单';
    case 'medium': return '中等';
    case 'hard': return '困难';
    default: return '未知';
  }
}
</script> 