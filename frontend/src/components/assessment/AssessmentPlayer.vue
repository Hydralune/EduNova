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
        <p v-if="!isFillBlankQuestion(currentQuestion)" 
           class="text-lg" 
           v-html="formatQuestionStem(currentQuestion.stem)"></p>
        
        <!-- 填空题题干 - 特殊处理 -->
        <div v-else>
          <p class="text-lg fill-blank-container">
            <template v-for="(part, index) in parsedFillBlankContent" :key="index">
              <span v-if="part.type === 'text'" v-html="part.content"></span>
              <input 
                v-else
                type="text" 
                v-model="answers[currentQuestionIndex][part.blankIndex]"
                class="border-b-2 inline-block min-w-32 mx-1 h-8 align-middle bg-gray-50 rounded border border-blue-300 px-2 focus:outline-none focus:ring-2 focus:ring-blue-500" 
                :placeholder="`填写答案`"
              />
            </template>
          </p>
          
          <!-- 调试信息 - 开发环境显示 -->
          <div class="mt-4 p-2 border border-red-300 bg-red-50 rounded text-sm" v-if="parsedFillBlankContent.length === 0 || !parsedFillBlankContent.some(part => part.type === 'blank')">
            <div class="font-bold text-red-600">填空题空白未检测到，尝试使用替代输入框：</div>
            <div v-if="Array.isArray(answers[currentQuestionIndex])">
              <div v-for="(blank, blankIndex) in answers[currentQuestionIndex]" :key="blankIndex" class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">空白 {{ blankIndex + 1 }}</label>
                <input 
                  type="text" 
                  v-model="answers[currentQuestionIndex][blankIndex]"
                  class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  :placeholder="`请填写空白 ${blankIndex + 1}`"
                />
              </div>
            </div>
          </div>
          
          <!-- 强制显示调试信息和输入区域 -->
          <div class="mt-4 p-2 border border-blue-300 bg-blue-50 rounded text-sm">
            <div>
              <strong>题目ID:</strong> {{ currentQuestion.id }} |
              <strong>类型:</strong> {{ currentQuestion.type }} |
              <strong>section_type:</strong> {{ currentQuestion.section_type }}
            </div>
            <div class="mt-2">
              <strong>题干:</strong> {{ currentQuestion.stem }}
            </div>
            <div class="mt-2">
              <strong>需要填写的空白:</strong> {{ Array.isArray(answers[currentQuestionIndex]) ? answers[currentQuestionIndex].length : '未初始化为数组' }}
            </div>
            
            <!-- 强制显示输入区域 -->
            <div class="mt-3 p-3 border border-green-200 bg-green-50 rounded">
              <p class="font-medium text-green-700 mb-2">备用输入区域:</p>
              <div v-if="!Array.isArray(answers[currentQuestionIndex])">
                <!-- 初始化为数组 -->
                <button 
                  class="px-3 py-1 bg-blue-500 text-white rounded-md text-sm mb-2"
                  @click="answers[currentQuestionIndex] = ['']"
                >
                  初始化答案数组
                </button>
              </div>
              <div v-else>
                <div v-for="(blank, blankIndex) in answers[currentQuestionIndex]" :key="blankIndex" class="mb-2">
                  <div class="flex items-center">
                    <input 
                      type="text" 
                      v-model="answers[currentQuestionIndex][blankIndex]"
                      class="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      :placeholder="`请填写空白 ${blankIndex + 1}`"
                    />
                    <button 
                      v-if="answers[currentQuestionIndex].length > 1"
                      @click="answers[currentQuestionIndex].splice(blankIndex, 1)"
                      class="ml-2 px-2 py-1 bg-red-500 text-white rounded-md text-sm"
                    >
                      删除
                    </button>
                  </div>
                </div>
                <button 
                  @click="answers[currentQuestionIndex].push('')"
                  class="mt-2 px-3 py-1 bg-green-500 text-white rounded-md text-sm"
                >
                  添加空白
                </button>
              </div>
            </div>
          </div>
        </div>
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
      <div v-if="isFillBlankQuestion(currentQuestion) && !useInlineFillBlanks" class="space-y-4">
        <div v-if="Array.isArray(answers[currentQuestionIndex])">
          <div v-for="(blank, blankIndex) in answers[currentQuestionIndex]" :key="blankIndex" class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">空白 {{ blankIndex + 1 }}</label>
            <input 
              type="text" 
              v-model="answers[currentQuestionIndex][blankIndex]"
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              :placeholder="`请填写空白 ${blankIndex + 1}`"
            />
          </div>
        </div>
        <div v-else>
          <label class="block text-sm font-medium text-gray-700 mb-1">答案</label>
          <input 
            type="text" 
            v-model="answers[currentQuestionIndex]"
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="请填写答案"
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
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import assessmentAPI from '@/api/assessmentAPI';

const props = defineProps({
  assessmentId: {
    type: [Number, String],
    required: true
  }
});

const router = useRouter();
const authStore = useAuthStore();

const emit = defineEmits(['submit', 'save-progress', 'cancel']);

// 状态变量
const currentQuestionIndex = ref(0);
const showSubmitConfirm = ref(false);
const markedQuestions = ref([]);
const timeLimit = ref(null);
const remainingTime = ref(0);
const timer = ref(null);
const useInlineFillBlanks = ref(true); // 是否使用内联填空模式

// 评估数据
const assessment = reactive({});

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

// 标准化section类型
const flatQuestions = computed(() => {
  const questions = [];
  if (assessment.sections) {
    assessment.sections.forEach(section => {
      if (section.questions) {
        section.questions.forEach(question => {
          // 标准化section类型
          let sectionType = section.type;
          
          // 特殊处理fill_in_blank类型，确保它与fill_blank保持一致
          if (sectionType === 'fill_in_blank') {
            sectionType = 'fill_blank';
          }
          
          // 如果question.type是fill_blank相关类型，确保section_type也是
          if (question.type === 'fill_blank' || question.type === 'fill_in_blank') {
            sectionType = 'fill_blank';
          }
          
          // 添加section类型信息到question，保留原始问题类型以备查
          questions.push({
            ...question,
            section_type: sectionType,
            original_type: question.type, // 保留问题自己的类型（如果有）
            type_text: getQuestionTypeText(question.type || sectionType)
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
    case 'fill_blank': return '填空题';
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

// 确保答案数组初始化方法更新为处理blank类型
const initializeAnswers = () => {
  flatQuestions.value.forEach((question, index) => {
    const type = question.section_type || question.type;
    console.log(`初始化问题 #${index}:`, type, question);
    
    if (type === 'multiple_choice' || type === 'true_false') {
      answers[index] = '';
    } else if (type === 'multiple_select') {
      answers[index] = [];
    } else if (isFillBlankQuestion(question)) {
      console.log(`处理填空题 #${index}:`, question);
      
      // 先检查是否有预定义的空白数量（来自answer数组）
      if (question.answer && Array.isArray(question.answer)) {
        console.log('  从answer数组初始化:', question.answer.length, '个空白');
        answers[index] = Array(question.answer.length).fill('');
      } else {
        // 否则尝试从题干文本中计算空白数量
        const stem = question.stem || question.content || '';
        
        // 使用相同的正则表达式和计数方法来确保一致性
        let blankCount = 0;
        
        // 计算所有类型的空白数量
        const underscoreMatches = stem.match(/_____/g) || [];
        const regex3PlusMatches = stem.replace(/_____/g, '').match(/_{3,}/g) || [];
        const blankMatches = stem.match(/\[BLANK\]/gi) || [];
        const chineseMatches = stem.match(/【空白】/g) || [];
        const bracketMatches1 = stem.match(/（）/g) || [];
        const bracketMatches2 = stem.match(/\(\)/g) || [];
        
        blankCount = underscoreMatches.length + regex3PlusMatches.length + 
                     blankMatches.length + chineseMatches.length + 
                     bracketMatches1.length + bracketMatches2.length;
        
        console.log('  计算得到:', blankCount, '个空白');
        
        if (blankCount > 0) {
          answers[index] = Array(blankCount).fill('');
        } else {
          // 如果没有检测到明显的空白标记，但题目类型是填空题，则默认一个空白
          console.log('  未检测到空白标记，设置默认1个空白');
          answers[index] = [''];
        }
      }
    } else if (type === 'short_answer') {
      answers[index] = '';
    } else if (type === 'essay') {
      answers[index] = {
        text: '',
        files: []
      };
    } else {
      // 对于未知类型，设置为空字符串
      console.log(`  未知题型 ${type}，设置为空字符串`);
      answers[index] = '';
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
  } else if (isFillBlankQuestion(question)) {
    if (Array.isArray(answer)) {
      return answer.some(blank => blank !== '');
    } else {
      return answer !== '';
    }
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

// 格式化题干文本，给填空题添加输入框
const parsedFillBlankContent = computed(() => {
  if (!currentQuestion.value || !isFillBlankQuestion(currentQuestion.value)) {
    return [];
  }
  
  const text = currentQuestion.value.stem || '';
  if (!text) return [];
  
  console.log('解析填空题题干:', text);
  console.log('题目类型:', currentQuestion.value.type, currentQuestion.value.section_type);
  
  // 存储不同类型的空白位置
  const blanks = [];
  
  // 1. 查找_____格式
  const regex1 = /_____/g;
  let match1;
  while ((match1 = regex1.exec(text)) !== null) {
    blanks.push({ start: match1.index, end: match1.index + match1[0].length });
    console.log('找到5个下划线空白位置:', match1.index);
  }
  
  // 2. 查找___格式（3个以上连续下划线）
  const regex2 = /_{3,}/g;
  let match2;
  while ((match2 = regex2.exec(text)) !== null) {
    // 检查是否已经添加过这个位置（避免与5个下划线重复）
    const alreadyAdded = blanks.some(b => b.start === match2.index);
    if (!alreadyAdded) {
      blanks.push({ start: match2.index, end: match2.index + match2[0].length });
      console.log('找到多个下划线空白位置:', match2.index);
    }
  }
  
  // 3. 查找[BLANK]格式
  const regex3 = /\[BLANK\]/gi;
  let match3;
  while ((match3 = regex3.exec(text)) !== null) {
    blanks.push({ start: match3.index, end: match3.index + match3[0].length });
    console.log('找到[BLANK]格式空白位置:', match3.index);
  }
  
  // 4. 查找【空白】格式
  const regex4 = /【空白】/g;
  let match4;
  while ((match4 = regex4.exec(text)) !== null) {
    blanks.push({ start: match4.index, end: match4.index + match4[0].length });
    console.log('找到【空白】格式空白位置:', match4.index);
  }
  
  // 5. 查找（）或()格式
  const regex5 = /（）/g;
  let match5;
  while ((match5 = regex5.exec(text)) !== null) {
    blanks.push({ start: match5.index, end: match5.index + match5[0].length });
    console.log('找到（）格式空白位置:', match5.index);
  }
  
  const regex6 = /\(\)/g;
  let match6;
  while ((match6 = regex6.exec(text)) !== null) {
    blanks.push({ start: match6.index, end: match6.index + match6[0].length });
    console.log('找到()格式空白位置:', match6.index);
  }
  
  console.log('检测到的空白数量:', blanks.length);
  
  // 如果没有检测到任何空白标记，但题目类型是填空题，创建一个默认空白
  if (blanks.length === 0) {
    console.log('未检测到空白标记，创建默认输入框');
    // 确保答案数组已初始化为至少一个元素
    if (!Array.isArray(answers[currentQuestionIndex.value]) || answers[currentQuestionIndex.value].length === 0) {
      answers[currentQuestionIndex.value] = [''];
    }
    
    // 返回整个文本和一个默认空白
    return [
      { type: 'text', content: text },
      { type: 'blank', blankIndex: 0 }
    ];
  }
  
  // 按位置排序空白
  blanks.sort((a, b) => a.start - b.start);
  
  // 确保答案数组初始化
  if (!Array.isArray(answers[currentQuestionIndex.value]) || answers[currentQuestionIndex.value].length !== blanks.length) {
    if (blanks.length > 0) {
      answers[currentQuestionIndex.value] = Array(blanks.length).fill('');
    } else {
      answers[currentQuestionIndex.value] = [''];
    }
  }
  
  // 将文本分割为文本部分和空白部分
  const result = [];
  let lastEnd = 0;
  
  blanks.forEach((blank, blankIndex) => {
    // 添加空白前的文本
    if (blank.start > lastEnd) {
      result.push({
        type: 'text',
        content: text.substring(lastEnd, blank.start)
      });
    }
    
    // 添加空白（将被渲染为输入框）
    result.push({
      type: 'blank',
      blankIndex
    });
    
    lastEnd = blank.end;
  });
  
  // 添加最后一段文本
  if (lastEnd < text.length) {
    result.push({
      type: 'text',
      content: text.substring(lastEnd)
    });
  }
  
  console.log('解析结果:', result);
  return result;
});

// 原有的格式化函数保留，用于非填空题
const formatQuestionStem = (text) => {
  if (!text) return '';
  
  const blankHtml = '<span class="border-b-2 border-gray-400 inline-block min-w-32 mx-1 h-6 align-middle bg-gray-50 rounded border border-blue-300 px-2">填空处</span>';
  
  // 1. 替换_____格式
  let formattedText = text.replace(/_____/g, blankHtml);
  
  // 2. 替换剩余的___格式（3个以上连续下划线）
  formattedText = formattedText.replace(/_{3,}/g, blankHtml);
  
  // 3. 替换[BLANK]格式
  formattedText = formattedText.replace(/\[BLANK\]/gi, blankHtml);
  
  // 4. 替换【空白】格式
  formattedText = formattedText.replace(/【空白】/g, blankHtml);
  
  // 5. 替换括号格式（）和()
  formattedText = formattedText.replace(/（）/g, blankHtml);
  formattedText = formattedText.replace(/\(\)/g, blankHtml);
  
  return formattedText;
};

// 判断题目是否为填空题类型
const isFillBlankQuestion = (question) => {
  if (!question) return false;
  
  // 检查section_type、type和original_type是否有任何一个是填空题类型
  const typeStr = String(question.type || '').toLowerCase();
  const sectionTypeStr = String(question.section_type || '').toLowerCase();
  const originalTypeStr = String(question.original_type || '').toLowerCase();
  
  // 检查任意类型字段是否包含"fill"和"blank"
  return (
    sectionTypeStr.includes('fill') && sectionTypeStr.includes('blank') ||
    typeStr.includes('fill') && typeStr.includes('blank') ||
    originalTypeStr.includes('fill') && originalTypeStr.includes('blank')
  );
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
const submitAssessment = async () => {
  showSubmitConfirm.value = false;
  
  if (timer.value) {
    clearInterval(timer.value);
  }
  
  try {
    // 获取当前用户ID
    const userId = authStore.user?.id || parseInt(localStorage.getItem('userId') || '0');
    
    // 准备提交数据
    const submissionData = {
      student_id: userId,
      answers: JSON.parse(JSON.stringify(answers)),
      submitted_at: new Date().toISOString(),
      time_spent: timeLimit.value ? timeLimit.value - remainingTime.value : null
    };
    
    console.log('提交评估数据:', submissionData);
    
    // 调用API提交评估
    try {
      const result = await assessmentAPI.submitAssessment(props.assessmentId, submissionData);
      console.log('提交结果:', result);
      
      // 保存提交状态
      if (result && result.submission_id) {
        localStorage.setItem(`assessment_${props.assessmentId}_submission_id`, result.submission_id);
        localStorage.setItem(`assessment_${props.assessmentId}_submitted`, 'true');
        localStorage.setItem(`assessment_${props.assessmentId}_score`, result.score);
      }
      
      // 显示提交成功消息
      alert(`评估已成功提交！您的得分是：${result.score}/${result.total_score}`);
      
      // 发送提交事件到父组件
      emit('submit', {
        assessmentId: props.assessmentId,
        answers: JSON.parse(JSON.stringify(answers)),
        submissionTime: new Date(),
        score: result.score
      });
      
      // 跳转到结果页面或返回课程页面
      if (assessment.course_id) {
        router.push(`/course/${assessment.course_id}`);
      } else {
        router.push('/dashboard');
      }
    } catch (apiError) {
      console.error('API调用失败:', apiError);
      
      // 模拟成功提交
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // 计算临时分数
      const tempScore = calculateScore();
      
      // 显示提交成功消息
      alert(`评估已成功提交！您的得分是：${tempScore}/${assessment.total_score}（模拟）`);
      
      // 发送提交事件到父组件
      emit('submit', {
        assessmentId: props.assessmentId,
        answers: JSON.parse(JSON.stringify(answers)),
        submissionTime: new Date(),
        score: tempScore
      });
      
      // 跳转到结果页面或返回课程页面
      router.push('/dashboard');
    }
  } catch (error) {
    console.error('提交评估失败:', error);
    alert('提交失败，请重试');
  }
};

// 添加计算分数的方法
const calculateScore = () => {
  let score = 0;
  let questionIndex = 0;
  
  assessment.sections.forEach(section => {
    section.questions.forEach(question => {
      const userAnswer = answers[questionIndex];
      let isCorrect = false;
      
      // 根据题目类型检查答案是否正确
      if (question.type === 'multiple_choice') {
        if (typeof question.answer === 'number') {
          // 如果答案是数字索引
          const correctOption = String.fromCharCode(65 + question.answer);
          isCorrect = userAnswer === correctOption;
        } else {
          // 如果答案是选项值
          isCorrect = userAnswer === question.answer;
        }
      } else if (question.type === 'true_false') {
        isCorrect = String(userAnswer).toLowerCase() === String(question.answer).toLowerCase();
      } else if (question.type === 'multiple_select') {
        // 多选题
        if (Array.isArray(userAnswer) && Array.isArray(question.answer)) {
          const userSet = new Set(userAnswer);
          const correctSet = new Set(question.answer.map(ans => 
            typeof ans === 'number' ? String.fromCharCode(65 + ans) : ans
          ));
          isCorrect = userSet.size === correctSet.size && 
            [...userSet].every(value => correctSet.has(value));
        }
      } else if (question.type === 'fill_in_blank' || question.type === 'fill_blank') {
        // 填空题
        let partialScore = 0;
        let skipFullScore = false; // 标记是否已经给了部分分，避免重复加分
        
        if (Array.isArray(question.answer) && Array.isArray(userAnswer)) {
          // 多个空的情况
          const validAnswers = userAnswer.filter(ans => ans.trim() !== '');
          if (validAnswers.length > 0) {
            const correctCount = validAnswers.filter((ans, i) => {
              if (i >= question.answer.length) return false;
              return String(ans).toLowerCase().trim() === String(question.answer[i]).toLowerCase().trim();
            }).length;
            
            // 按照正确率给分
            if (correctCount > 0) {
              const scorePerBlank = (section.score_per_question || 0) / question.answer.length;
              partialScore = scorePerBlank * correctCount;
              skipFullScore = true; // 已经给了部分分，不再通过isCorrect添加满分
            }
          }
          // 直接添加部分分数而不是设置isCorrect
          score += partialScore;
        } else if (!Array.isArray(question.answer) && !Array.isArray(userAnswer)) {
          // 单个空的情况
          isCorrect = String(userAnswer).toLowerCase().trim() === String(question.answer).toLowerCase().trim();
        } else if (Array.isArray(question.answer) && !Array.isArray(userAnswer)) {
          // 答案是数组但用户答案是单个值 (可能是第一个空的答案)
          isCorrect = question.answer.length > 0 && 
                     String(userAnswer).toLowerCase().trim() === String(question.answer[0]).toLowerCase().trim();
        } else if (!Array.isArray(question.answer) && Array.isArray(userAnswer)) {
          // 答案是单个值但用户答案是数组
          isCorrect = userAnswer.length > 0 && 
                     String(userAnswer[0]).toLowerCase().trim() === String(question.answer).toLowerCase().trim();
        }
        
        // 如果已经给了部分分，则不再通过isCorrect添加满分
        if (skipFullScore) {
          isCorrect = false;
        }
      }
      
      // 如果答案正确，加分
      if (isCorrect) {
        score += section.score_per_question || 0;
      }
      
      questionIndex++;
    });
  });
  
  return score;
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

// 组件挂载时检查提交状态
onMounted(async () => {
  try {
    // 获取assessmentId
    const id = props.assessmentId;
    
    console.log('Assessment ID from props:', id);
    
    if (!id) {
      console.error('No assessmentId provided');
      return;
    }
    
    // 检查是否已经提交过
    const submittedFlag = localStorage.getItem(`assessment_${id}_submitted`);
    if (submittedFlag === 'true') {
      // 已提交过，应该显示结果或重定向
      const submissionId = localStorage.getItem(`assessment_${id}_submission_id`);
      const score = localStorage.getItem(`assessment_${id}_score`);
      
      alert(`您已经提交过此评估。得分：${score || '未知'}`);
      
      // 重定向到课程页面或仪表板
      if (assessment.course_id) {
        router.push(`/course/${assessment.course_id}`);
      } else {
        router.push('/dashboard');
      }
      return;
    }
    
    // 尝试从API获取数据
    try {
      const data = await assessmentAPI.getAssessment(id);
      
      // 填充评估数据
      Object.assign(assessment, data);
      
      console.log('Assessment loaded in player:', assessment);
    } catch (apiError) {
      console.error('API调用失败，使用模拟数据:', apiError);
      
      // 从本地导入的mock数据
      const mockExam = await import('../../assets/mock-exam.json');
      const data = mockExam.default;
      
      // 填充评估数据
      Object.assign(assessment, data);
    }
    
    // 初始化答案
    initializeAnswers();
    
    // 额外检查填空题处理
    console.log('初始化后的答案数据:', answers);
    
    // 检查并修复所有填空题的答案格式
    flatQuestions.value.forEach((question, index) => {
      if (isFillBlankQuestion(question)) {
        console.log(`检查第${index}题填空题格式:`, question);
        
        // 确保填空题的答案是数组
        if (!Array.isArray(answers[index])) {
          console.log(`  修复第${index}题答案格式 - 不是数组`);
          const blankCount = countBlanks(question.stem);
          if (blankCount > 0) {
            answers[index] = Array(blankCount).fill('');
          } else {
            answers[index] = [''];
          }
        } else if (answers[index].length === 0) {
          console.log(`  修复第${index}题答案格式 - 数组为空`);
          answers[index] = [''];
        }
        
        console.log(`  修复后的答案:`, answers[index]);
      }
    });
    
    // 设置时间限制
    if (assessment.duration) {
      startTimer();
    }
  } catch (error) {
    console.error('Failed to load assessment:', error);
  }
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

// 监听currentQuestionIndex变化，输出当前题目信息并处理填空题
watch(currentQuestionIndex, (newIndex) => {
  const question = flatQuestions.value[newIndex];
  if (question) {
    console.log('当前题目:', question);
    console.log('题目类型:', question.section_type);
    console.log('题干:', question.stem);
    
    if (isFillBlankQuestion(question)) {
      // 使用与parsedFillBlankContent计算属性中相同的逻辑
      const text = question.stem || '';
      
      // 收集所有空白位置
      const blanks = [];
      
      // 查找所有类型的空白
      const regex1 = /_____/g;
      let match1;
      while ((match1 = regex1.exec(text)) !== null) {
        blanks.push({ start: match1.index, end: match1.index + match1[0].length });
      }
      
      const remainingText = text.replace(/_____/g, 'XXXXX');
      const regex2 = /_{3,}/g;
      let match2;
      while ((match2 = regex2.exec(remainingText)) !== null) {
        const adjustedStart = text.indexOf('_', match2.index);
        if (adjustedStart !== -1) {
          let end = adjustedStart;
          while (end < text.length && text[end] === '_') {
            end++;
          }
          const alreadyAdded = blanks.some(b => b.start === adjustedStart);
          if (!alreadyAdded) {
            blanks.push({ start: adjustedStart, end });
          }
        }
      }
      
      const regex3 = /\[BLANK\]/gi;
      let match3;
      while ((match3 = regex3.exec(text)) !== null) {
        blanks.push({ start: match3.index, end: match3.index + match3[0].length });
      }
      
      const regex4 = /【空白】/g;
      let match4;
      while ((match4 = regex4.exec(text)) !== null) {
        blanks.push({ start: match4.index, end: match4.index + match4[0].length });
      }
      
      const regex5 = /（）/g;
      let match5;
      while ((match5 = regex5.exec(text)) !== null) {
        blanks.push({ start: match5.index, end: match5.index + match5[0].length });
      }
      
      const regex6 = /\(\)/g;
      let match6;
      while ((match6 = regex6.exec(text)) !== null) {
        blanks.push({ start: match6.index, end: match6.index + match6[0].length });
      }
      
      const blankCount = blanks.length;
      console.log('识别到的空白数量:', blankCount);
      
      // 如果答案不是数组或者数组长度不匹配，重新初始化
      if (!Array.isArray(answers[newIndex]) || answers[newIndex].length !== blankCount) {
        console.log('重新初始化填空题答案数组');
        if (blankCount > 0) {
          answers[newIndex] = Array(blankCount).fill('');
        } else {
          answers[newIndex] = [''];
        }
        console.log('初始化后的答案数组:', answers[newIndex]);
      }
    }
  }
});

const confirmLeave = (e) => {
  e.preventDefault();
  e.returnValue = '您有未保存的答案，确定要离开吗？';
  return e.returnValue;
};
</script> 

<style scoped>
.fill-blank-container {
  line-height: 2.5;
}

.fill-blank-container input {
  vertical-align: middle;
  transition: all 0.2s ease-in-out;
}

.fill-blank-container input:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
  border-color: #3b82f6;
}

/* 移动端响应式调整 */
@media (max-width: 640px) {
  .fill-blank-container input {
    min-width: 120px;
    margin: 2px 0;
    display: inline-block;
  }
}
</style> 