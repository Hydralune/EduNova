<template>
  <div class="assessment-player">
    <!-- 评估头部信息 -->
    <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200 mb-6">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-2xl font-bold">{{ assessment.title }}</h2>
          <p class="text-gray-600">{{ assessment.description }}</p>
        </div>
        <div class="text-right">
          <p v-if="timeLimit" class="text-lg font-semibold text-red-600">
            {{ formatTime(remainingTime) }}
          </p>
          <p class="text-sm text-gray-600">总分: {{ assessment.total_score }} 分</p>
          <p class="text-sm text-gray-600">题目: {{ totalQuestions }} 题</p>
        </div>
      </div>
      
      <!-- 进度条 -->
      <div class="mt-4">
        <div class="w-full bg-gray-200 rounded-full h-2.5">
          <div 
            class="bg-blue-600 h-2.5 rounded-full" 
            :style="{ width: `${(currentQuestionIndex / totalQuestions) * 100}%` }"
          ></div>
        </div>
        <div class="flex justify-between mt-1 text-sm text-gray-600">
          <span>进度: {{ currentQuestionIndex }}/{{ totalQuestions }}</span>
          <span>已完成: {{ answeredCount }}/{{ totalQuestions }}</span>
        </div>
      </div>
    </div>
    
    <!-- 题目导航 -->
    <div class="bg-white p-4 rounded-lg shadow-md border border-gray-200 mb-6">
      <div class="flex flex-wrap gap-2">
        <button 
          v-for="(question, index) in flatQuestions" 
          :key="index"
          @click="navigateToQuestion(index)"
          class="w-8 h-8 flex items-center justify-center rounded-full text-sm"
          :class="getQuestionStatusClass(index)"
        >
          {{ index + 1 }}
        </button>
      </div>
    </div>
    
    <!-- 当前题目 -->
    <div v-if="currentQuestion" class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold">
          {{ currentQuestionIndex + 1 }}. {{ currentQuestion.type_text }}
          <span class="text-sm text-gray-500 ml-2">({{ currentQuestion.score }}分)</span>
        </h3>
        <div class="flex gap-2">
          <button 
            @click="markQuestion(currentQuestionIndex)"
            class="text-sm px-2 py-1 rounded-md"
            :class="markedQuestions.includes(currentQuestionIndex) ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'"
          >
            {{ markedQuestions.includes(currentQuestionIndex) ? '取消标记' : '标记题目' }}
          </button>
        </div>
      </div>
      
      <!-- 题干 -->
      <div class="mb-6">
        <p class="text-lg" v-html="formatQuestionStem(currentQuestion.stem)"></p>
      </div>
      
      <!-- 选择题 -->
      <div v-if="currentQuestion.section_type === 'multiple_choice'" class="space-y-3">
        <div 
          v-for="(option, optIndex) in currentQuestion.options" 
          :key="optIndex"
          @click="selectOption(optIndex)"
          class="p-3 border rounded-md cursor-pointer hover:bg-gray-50 flex items-center"
          :class="{'bg-blue-50 border-blue-300': answers[currentQuestionIndex] === String.fromCharCode(65 + optIndex)}"
        >
          <div class="w-6 h-6 flex items-center justify-center border rounded-full mr-3"
               :class="{'bg-blue-500 text-white border-blue-500': answers[currentQuestionIndex] === String.fromCharCode(65 + optIndex)}">
            {{ String.fromCharCode(65 + optIndex) }}
          </div>
          <div>{{ option.replace(/^[A-Z]\.\s*/, '') }}</div>
        </div>
      </div>
      
      <!-- 多选题 -->
      <div v-if="currentQuestion.section_type === 'multiple_select'" class="space-y-3">
        <div 
          v-for="(option, optIndex) in currentQuestion.options" 
          :key="optIndex"
          @click="toggleMultipleOption(optIndex)"
          class="p-3 border rounded-md cursor-pointer hover:bg-gray-50 flex items-center"
          :class="{'bg-blue-50 border-blue-300': isOptionSelected(optIndex)}"
        >
          <div class="w-6 h-6 flex items-center justify-center border mr-3"
               :class="{'bg-blue-500 text-white border-blue-500': isOptionSelected(optIndex)}">
            <svg v-if="isOptionSelected(optIndex)" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </div>
          <div>{{ option.replace(/^[A-Z]\.\s*/, '') }}</div>
        </div>
      </div>
      
      <!-- 填空题 -->
      <div v-if="currentQuestion.section_type === 'fill_in_blank'" class="space-y-4">
        <div v-for="(blank, blankIndex) in countBlanks(currentQuestion.stem)" :key="blankIndex">
          <label class="block text-sm font-medium text-gray-700 mb-1">空白 {{ blankIndex + 1 }}</label>
          <input 
            type="text" 
            v-model="answers[currentQuestionIndex][blankIndex]"
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            :placeholder="`请填写空白 ${blankIndex + 1}`"
          />
        </div>
      </div>
      
      <!-- 判断题 -->
      <div v-if="currentQuestion.section_type === 'true_false'" class="space-y-3">
        <div 
          @click="answers[currentQuestionIndex] = 'true'"
          class="p-3 border rounded-md cursor-pointer hover:bg-gray-50 flex items-center"
          :class="{'bg-blue-50 border-blue-300': answers[currentQuestionIndex] === 'true'}"
        >
          <div class="w-6 h-6 flex items-center justify-center border rounded-full mr-3"
               :class="{'bg-blue-500 text-white border-blue-500': answers[currentQuestionIndex] === 'true'}">
            <span v-if="answers[currentQuestionIndex] === 'true'">✓</span>
          </div>
          <div>正确</div>
        </div>
        <div 
          @click="answers[currentQuestionIndex] = 'false'"
          class="p-3 border rounded-md cursor-pointer hover:bg-gray-50 flex items-center"
          :class="{'bg-blue-50 border-blue-300': answers[currentQuestionIndex] === 'false'}"
        >
          <div class="w-6 h-6 flex items-center justify-center border rounded-full mr-3"
               :class="{'bg-blue-500 text-white border-blue-500': answers[currentQuestionIndex] === 'false'}">
            <span v-if="answers[currentQuestionIndex] === 'false'">✗</span>
          </div>
          <div>错误</div>
        </div>
      </div>
      
      <!-- 简答题 -->
      <div v-if="currentQuestion.section_type === 'short_answer'" class="space-y-3">
        <textarea 
          v-model="answers[currentQuestionIndex]" 
          rows="6" 
          class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="请在此输入您的答案..."
        ></textarea>
      </div>
      
      <!-- 大题/论述题 -->
      <div v-if="currentQuestion.section_type === 'essay'" class="space-y-4">
        <textarea 
          v-model="answers[currentQuestionIndex].text" 
          rows="8" 
          class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="请在此输入您的答案..."
        ></textarea>
        
        <!-- 文件上传 -->
        <div class="border-t pt-4">
          <p class="text-sm font-medium mb-2">附件上传（可选）：</p>
          <input 
            type="file" 
            @change="handleFileUpload($event)" 
            class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <div v-if="answers[currentQuestionIndex].files.length > 0" class="mt-2">
            <p class="text-sm font-medium">已上传文件：</p>
            <ul class="text-sm text-gray-600">
              <li v-for="(file, fileIndex) in answers[currentQuestionIndex].files" :key="fileIndex" class="flex items-center justify-between mt-1">
                <span>{{ file.name }}</span>
                <button 
                  @click="removeFile(fileIndex)" 
                  class="text-red-600 hover:text-red-800"
                >
                  删除
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      <!-- 导航按钮 -->
      <div class="flex justify-between mt-8">
        <button 
          @click="previousQuestion" 
          class="px-4 py-2 border rounded-md hover:bg-gray-50"
          :disabled="currentQuestionIndex === 0"
          :class="{'opacity-50 cursor-not-allowed': currentQuestionIndex === 0}"
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
        >
          提交答案
        </button>
      </div>
    </div>
    
    <!-- 确认提交对话框 -->
    <div v-if="showSubmitConfirm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-xl font-bold mb-4">确认提交</h3>
        <p class="mb-2">您确定要提交此评估吗？提交后将无法修改答案。</p>
        
        <div v-if="unansweredCount > 0" class="mb-4 p-3 bg-yellow-50 text-yellow-800 rounded-md">
          <p>您还有 {{ unansweredCount }} 道题未回答。</p>
        </div>
        
        <div class="flex justify-end gap-3">
          <button 
            @click="showSubmitConfirm = false" 
            class="px-4 py-2 border rounded-md"
          >
            返回检查
          </button>
          <button 
            @click="submitAssessment" 
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
import { useRoute } from 'vue-router';

const props = defineProps({
  assessmentId: {
    type: [Number, String],
    required: true
  }
});

const emit = defineEmits(['submit', 'save-progress', 'cancel']);

// 状态变量
const currentQuestionIndex = ref(0);
const showSubmitConfirm = ref(false);
const markedQuestions = ref([]);
const timeLimit = ref(null);
const remainingTime = ref(0);
const timer = ref(null);

// 评估数据
const assessment = reactive({});

// 组件挂载时
onMounted(async () => {
  try {
    // 获取assessmentId
    const id = props.assessmentId;
    
    console.log('Assessment ID from props:', id);
    
    if (!id) {
      console.error('No assessmentId provided');
      return;
    }
    
    // 实际应用中应该从API获取数据
    // const response = await fetch(`/api/assessments/${id}`);
    // const data = await response.json();
    
    // 从本地导入的mock数据
    const mockExam = await import('../../assets/mock-exam.json');
    const data = mockExam.default;
    
    // 填充评估数据
    Object.assign(assessment, data);
    
    console.log('Assessment loaded in player:', assessment);
    
    // 初始化答案
    initializeAnswers();
    
    // 设置时间限制
    if (assessment.duration) {
      startTimer();
    }
  } catch (error) {
    console.error('Failed to load assessment:', error);
  }
});

// 计算属性
const totalQuestions = computed(() => {
  let count = 0;
  if (assessment.sections) {
    assessment.sections.forEach(section => {
      if (section.questions) {
        count += section.questions.length;
      }
    });
  }
  return count;
});

const flatQuestions = computed(() => {
  const questions = [];
  if (assessment.sections) {
    assessment.sections.forEach(section => {
      if (section.questions) {
        section.questions.forEach(question => {
          // 添加section类型信息到question
          questions.push({
            ...question,
            section_type: section.type,
            type_text: getQuestionTypeText(section.type)
          });
        });
      }
    });
  }
  return questions;
});

const getQuestionTypeText = (type) => {
  switch (type) {
    case 'multiple_choice': return '选择题';
    case 'multiple_select': return '多选题';
    case 'fill_in_blank': return '填空题';
    case 'true_false': return '判断题';
    case 'short_answer': return '简答题';
    case 'essay': return '论述题';
    default: return type;
  }
};

const currentQuestion = computed(() => {
  return flatQuestions.value[currentQuestionIndex.value] || null;
});

// 初始化答案数据结构
const answers = reactive([]);

const initializeAnswers = () => {
  flatQuestions.value.forEach((question, index) => {
    const type = question.section_type || question.type;
    
    if (type === 'multiple_choice' || type === 'true_false') {
      answers[index] = '';
    } else if (type === 'multiple_select') {
      answers[index] = [];
    } else if (type === 'fill_in_blank') {
      const blankCount = countBlanks(question.stem);
      answers[index] = Array(blankCount).fill('');
    } else if (type === 'short_answer') {
      answers[index] = '';
    } else if (type === 'essay') {
      answers[index] = {
        text: '',
        files: []
      };
    }
  });
  
  console.log('Answers initialized:', answers);
};

// 计算已回答的题目数量
const answeredCount = computed(() => {
  let count = 0;
  answers.forEach((answer, index) => {
    if (isQuestionAnswered(index)) {
      count++;
    }
  });
  return count;
});

// 计算未回答的题目数量
const unansweredCount = computed(() => {
  return totalQuestions.value - answeredCount.value;
});

// 检查题目是否已回答
const isQuestionAnswered = (index) => {
  const answer = answers[index];
  const question = flatQuestions.value[index];
  
  if (!answer || !question) return false;
  
  const type = question.section_type || question.type;
  
  if (type === 'multiple_choice' || type === 'true_false') {
    return answer !== '';
  } else if (type === 'multiple_select') {
    return answer.length > 0;
  } else if (type === 'fill_in_blank') {
    return answer.some(blank => blank !== '');
  } else if (type === 'short_answer') {
    return answer !== '';
  } else if (type === 'essay') {
    return answer.text !== '' || answer.files.length > 0;
  }
  
  return false;
};

// 获取题目状态样式
const getQuestionStatusClass = (index) => {
  if (index === currentQuestionIndex.value) {
    return 'bg-blue-600 text-white';
  } else if (markedQuestions.value.includes(index)) {
    return 'bg-yellow-100 text-yellow-800 border border-yellow-400';
  } else if (isQuestionAnswered(index)) {
    return 'bg-green-100 text-green-800 border border-green-400';
  } else {
    return 'bg-gray-100 text-gray-800 border';
  }
};

// 导航到指定题目
const navigateToQuestion = (index) => {
  if (index >= 0 && index < totalQuestions.value) {
    currentQuestionIndex.value = index;
  }
};

// 下一题
const nextQuestion = () => {
  if (currentQuestionIndex.value < totalQuestions.value - 1) {
    currentQuestionIndex.value++;
  }
};

// 上一题
const previousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--;
  }
};

// 标记题目
const markQuestion = (index) => {
  const markedIndex = markedQuestions.value.indexOf(index);
  if (markedIndex === -1) {
    markedQuestions.value.push(index);
  } else {
    markedQuestions.value.splice(markedIndex, 1);
  }
};

// 选择选项（单选题）
const selectOption = (optIndex) => {
  answers[currentQuestionIndex.value] = String.fromCharCode(65 + optIndex);
};

// 选择选项（多选题）
const toggleMultipleOption = (optIndex) => {
  const option = String.fromCharCode(65 + optIndex);
  const index = answers[currentQuestionIndex.value].indexOf(option);
  
  if (index === -1) {
    answers[currentQuestionIndex.value].push(option);
  } else {
    answers[currentQuestionIndex.value].splice(index, 1);
  }
};

// 检查选项是否被选中（多选题）
const isOptionSelected = (optIndex) => {
  const option = String.fromCharCode(65 + optIndex);
  return answers[currentQuestionIndex.value].includes(option);
};

// 处理填空题
const countBlanks = (text) => {
  return (text.match(/_____/g) || []).length;
};

const formatQuestionStem = (text) => {
  return text.replace(/_____/g, '<span class="border-b-2 border-gray-400 inline-block min-w-20">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>');
};

// 处理文件上传
const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    answers[currentQuestionIndex.value].files.push(file);
  }
  // 重置文件输入以允许重复选择同一文件
  event.target.value = '';
};

// 移除文件
const removeFile = (fileIndex) => {
  answers[currentQuestionIndex.value].files.splice(fileIndex, 1);
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
  showSubmitConfirm.value = false;
  
  if (timer.value) {
    clearInterval(timer.value);
  }
  
  // 发送数据到后端
  emit('submit', {
    assessmentId: assessment.id,
    answers: JSON.parse(JSON.stringify(answers)),
    submissionTime: new Date(),
    timeSpent: timeLimit.value ? timeLimit.value - remainingTime.value : null
  });
};

// 格式化时间显示
const formatTime = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
};

// 开始计时器
const startTimer = () => {
  // 确保assessment.duration存在
  if (!assessment.duration) {
    console.warn('No duration specified for assessment');
    return;
  }
  
  // 解析时间限制，如"30分钟"转换为1800秒
  const match = assessment.duration.match(/(\d+)/);
  if (match) {
    timeLimit.value = parseInt(match[1]) * 60; // 转换为秒
    remainingTime.value = timeLimit.value;
    
    timer.value = setInterval(() => {
      if (remainingTime.value > 0) {
        remainingTime.value--;
      } else {
        // 时间到，自动提交
        clearInterval(timer.value);
        submitAssessment();
      }
    }, 1000);
  }
};

// 组件挂载时
onMounted(() => {
  initializeAnswers();
  startTimer();
  
  // 实际应用中，这里应该从API获取评估数据
  // 并检查是否有保存的进度
});

// 组件卸载前清除定时器
onBeforeUnmount(() => {
  if (timer.value) {
    clearInterval(timer.value);
  }
});

// 监听路由变化，提醒用户保存进度
watch(() => true, (isActive) => {
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