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
                    <p class="mb-3">{{ question.stem }}</p>
                    
                    <!-- 选择题选项 -->
                    <div v-if="section.type === 'multiple_choice' || section.type === 'multiple_select'" class="space-y-2">
                      <div v-for="(option, optIndex) in question.options" :key="optIndex" class="flex items-center">
                        <span class="mr-2">{{ String.fromCharCode(65 + optIndex) }}.</span>
                        <span>{{ option }}</span>
                      </div>
                      <p class="text-sm text-gray-600 mt-2">
                        正确答案: {{ Array.isArray(question.answer) ? question.answer.join(', ') : question.answer }}
                      </p>
                    </div>
                    
                    <!-- 判断题答案 -->
                    <div v-if="section.type === 'true_false'" class="mt-2">
                      <p class="text-sm text-gray-600">正确答案: {{ question.answer === 'true' ? '正确' : '错误' }}</p>
                    </div>
                    
                    <!-- 填空题答案 -->
                    <div v-if="section.type === 'fill_in_blank'" class="mt-2">
                      <p class="text-sm text-gray-600">
                        正确答案: {{ Array.isArray(question.answer) ? question.answer.join(' | ') : question.answer }}
                      </p>
                    </div>
                    
                    <!-- 简答题和论述题参考答案 -->
                    <div v-if="section.type === 'short_answer' || section.type === 'essay'" class="mt-2">
                      <p class="text-sm text-gray-600">参考答案:</p>
                      <p class="text-sm mt-1 pl-4">{{ question.reference_answer }}</p>
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
            
            <!-- 选择题 -->
            <div v-if="section.type === 'multiple_choice'" class="space-y-6">
              <div v-for="(question, qIndex) in section.questions" :key="qIndex" class="border-b pb-4 last:border-b-0">
                <div class="flex">
                  <span class="font-medium mr-2">{{ qIndex + 1 }}.</span>
                  <div class="flex-1">
                    <p class="mb-3">{{ question.stem }}</p>
                    <div class="space-y-2">
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
                        <label :for="`q-${sectionIndex}-${qIndex}-${optIndex}`">{{ option }}</label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 多选题 -->
            <div v-if="section.type === 'multiple_select'" class="space-y-6">
              <div v-for="(question, qIndex) in section.questions" :key="qIndex" class="border-b pb-4 last:border-b-0">
                <div class="flex">
                  <span class="font-medium mr-2">{{ qIndex + 1 }}.</span>
                  <div class="flex-1">
                    <p class="mb-3">{{ question.stem }}</p>
                    <div class="space-y-2">
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
                        <label :for="`q-${sectionIndex}-${qIndex}-${optIndex}`">{{ option }}</label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 填空题 -->
            <div v-if="section.type === 'fill_in_blank'" class="space-y-6">
              <div v-for="(question, qIndex) in section.questions" :key="qIndex" class="border-b pb-4 last:border-b-0">
                <div class="flex">
                  <span class="font-medium mr-2">{{ qIndex + 1 }}.</span>
                  <div class="flex-1">
                    <p class="mb-3" v-html="formatBlankQuestion(question.stem)"></p>
                    <div v-for="(blank, blankIndex) in countBlanks(question.stem)" :key="blankIndex" class="mb-2">
                      <input 
                        type="text" 
                        :placeholder="`空白 ${blankIndex + 1}`"
                        v-model="answers[sectionIndex][qIndex][blankIndex]"
                        class="px-3 py-2 border rounded-md w-full"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 判断题 -->
            <div v-if="section.type === 'true_false'" class="space-y-6">
              <div v-for="(question, qIndex) in section.questions" :key="qIndex" class="border-b pb-4 last:border-b-0">
                <div class="flex">
                  <span class="font-medium mr-2">{{ qIndex + 1 }}.</span>
                  <div class="flex-1">
                    <p class="mb-3">{{ question.stem }}</p>
                    <div class="space-y-2">
                      <div class="flex items-center">
                        <input 
                          type="radio" 
                          :id="`q-${sectionIndex}-${qIndex}-true`" 
                          :name="`q-${sectionIndex}-${qIndex}`"
                          value="true"
                          v-model="answers[sectionIndex][qIndex]"
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
                          v-model="answers[sectionIndex][qIndex]"
                          class="mr-2"
                        />
                        <label :for="`q-${sectionIndex}-${qIndex}-false`">错误</label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 简答题 -->
            <div v-if="section.type === 'short_answer'" class="space-y-6">
              <div v-for="(question, qIndex) in section.questions" :key="qIndex" class="border-b pb-4 last:border-b-0">
                <div class="flex">
                  <span class="font-medium mr-2">{{ qIndex + 1 }}.</span>
                  <div class="flex-1">
                    <p class="mb-3">{{ question.stem }}</p>
                    <textarea 
                      v-model="answers[sectionIndex][qIndex]" 
                      rows="4" 
                      class="w-full px-3 py-2 border rounded-md"
                      placeholder="请在此输入您的答案..."
                    ></textarea>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 大题/论述题 -->
            <div v-if="section.type === 'essay'" class="space-y-6">
              <div v-for="(question, qIndex) in section.questions" :key="qIndex" class="border-b pb-4 last:border-b-0">
                <div class="flex">
                  <span class="font-medium mr-2">{{ qIndex + 1 }}.</span>
                  <div class="flex-1">
                    <p class="mb-3">{{ question.stem }}</p>
                    <textarea 
                      v-model="answers[sectionIndex][qIndex].text" 
                      rows="6" 
                      class="w-full px-3 py-2 border rounded-md mb-3"
                      placeholder="请在此输入您的答案..."
                    ></textarea>
                    
                    <!-- 文件上传 -->
                    <div class="border-t pt-3">
                      <p class="text-sm text-gray-600 mb-2">附件上传（可选）：</p>
                      <input 
                        type="file" 
                        @change="handleFileUpload($event, sectionIndex, qIndex)" 
                        class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                      />
                      <div v-if="answers[sectionIndex][qIndex].files.length > 0" class="mt-2">
                        <p class="text-sm font-medium">已上传文件：</p>
                        <ul class="text-sm text-gray-600">
                          <li v-for="(file, fileIndex) in answers[sectionIndex][qIndex].files" :key="fileIndex" class="flex items-center justify-between mt-1">
                            <span>{{ file.name }}</span>
                            <button 
                              @click="removeFile(sectionIndex, qIndex, fileIndex)" 
                              class="text-red-600 hover:text-red-800"
                            >
                              删除
                            </button>
                          </li>
                        </ul>
                      </div>
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

const props = defineProps({
  assessmentId: {
    type: [Number, String],
    required: true
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
  id: props.assessmentId,
  title: "第一章测验",
  description: "测试对第一章内容的理解",
  total_score: 100,
  duration: "30分钟",
  due_date: "2025-07-15",
  max_attempts: 3,
  sections: [
    {
      type: "multiple_choice",
      description: "选择题：请在每小题给出的选项中选出一个正确答案。",
      score_per_question: 4,
      questions: [
        {
          id: 1,
          stem: "以下哪个是JavaScript的基本数据类型？",
          options: [
            "A. Array",
            "B. Object",
            "C. String",
            "D. RegExp"
          ],
          answer: "C"
        },
        {
          id: 2,
          stem: "Vue.js中用于响应式数据的API是？",
          options: [
            "A. useState",
            "B. reactive",
            "C. useEffect",
            "D. setState"
          ],
          answer: "B"
        }
      ]
    },
    {
      type: "multiple_select",
      description: "多选题：请在每小题给出的选项中选出所有正确答案。",
      score_per_question: 5,
      questions: [
        {
          id: 1,
          stem: "以下哪些是JavaScript框架或库？",
          options: [
            "A. React",
            "B. Python",
            "C. Vue",
            "D. Angular"
          ],
          answer: ["A", "C", "D"]
        }
      ]
    },
    {
      type: "fill_in_blank",
      description: "填空题：请在横线上填写正确的内容。",
      score_per_question: 4,
      questions: [
        {
          id: 1,
          stem: "Vue.js中，用于创建组件的API是_____。",
          answer: "defineComponent"
        },
        {
          id: 2,
          stem: "在Vue 3中，_____函数用于创建响应式对象，而_____函数用于创建响应式基本类型。",
          answer: ["reactive", "ref"]
        }
      ]
    },
    {
      type: "true_false",
      description: "判断题：请判断以下说法是否正确。",
      score_per_question: 3,
      questions: [
        {
          id: 1,
          stem: "Vue.js是一个前端框架。",
          answer: "true"
        },
        {
          id: 2,
          stem: "React使用模板语法而不是JSX。",
          answer: "false"
        }
      ]
    },
    {
      type: "short_answer",
      description: "简答题：请简要回答以下问题。",
      score_per_question: 10,
      questions: [
        {
          id: 1,
          stem: "简述Vue.js的生命周期钩子函数。",
          reference_answer: "Vue组件的生命周期钩子包括：创建阶段的beforeCreate和created，挂载阶段的beforeMount和mounted，更新阶段的beforeUpdate和updated，卸载阶段的beforeUnmount和unmounted等。"
        }
      ]
    },
    {
      type: "essay",
      description: "论述题：请详细回答以下问题，并上传相关资料。",
      score_per_question: 20,
      questions: [
        {
          id: 1,
          stem: "分析Vue.js和React的异同，并结合实际项目经验谈谈你的选择偏好。",
          reference_answer: "Vue和React都是流行的前端框架，它们有许多相似之处，如组件化架构、虚拟DOM等。不同之处在于Vue使用模板语法和选项式API，而React使用JSX和函数式组件..."
        }
      ]
    }
  ]
});

// 答案数据
const answers = reactive([]);

// 初始化答案数据结构
const initializeAnswers = () => {
  assessment.sections.forEach((section, sectionIndex) => {
    answers[sectionIndex] = [];
    
    section.questions.forEach((question, qIndex) => {
      if (section.type === 'multiple_choice' || section.type === 'true_false') {
        answers[sectionIndex][qIndex] = '';
      } else if (section.type === 'multiple_select') {
        answers[sectionIndex][qIndex] = [];
      } else if (section.type === 'fill_in_blank') {
        const blankCount = countBlanks(question.stem);
        answers[sectionIndex][qIndex] = Array(blankCount).fill('');
      } else if (section.type === 'short_answer') {
        answers[sectionIndex][qIndex] = '';
      } else if (section.type === 'essay') {
        answers[sectionIndex][qIndex] = {
          text: '',
          files: []
        };
      }
    });
  });
};

// 开始评估
const startAssessment = () => {
  started.value = true;
  
  // 设置时间限制
  if (assessment.duration) {
    // 简单解析时间限制，如"30分钟"转换为1800秒
    const match = assessment.duration.match(/(\d+)/);
    if (match) {
      timeLimit.value = parseInt(match[1]) * 60; // 转换为秒
      remainingTime.value = timeLimit.value;
      startTimer();
    }
  }
  
  initializeAnswers();
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

// 处理填空题
const countBlanks = (text) => {
  return (text.match(/_____/g) || []).length;
};

const formatBlankQuestion = (text) => {
  return text.replace(/_____/g, '<span class="border-b-2 border-gray-400 inline-block min-w-20">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>');
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
      if (section.type === 'multiple_choice') {
        if (answers[sectionIndex][qIndex] === question.answer) {
          totalScore += section.score_per_question;
        }
      } else if (section.type === 'multiple_select') {
        // 多选题要完全匹配才得分
        const userAnswer = answers[sectionIndex][qIndex].sort();
        const correctAnswer = question.answer.sort();
        if (JSON.stringify(userAnswer) === JSON.stringify(correctAnswer)) {
          totalScore += section.score_per_question;
        }
      } else if (section.type === 'fill_in_blank') {
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
      } else if (section.type === 'true_false') {
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

// 组件挂载时
onMounted(async () => {
  try {
    // TODO: 从API获取评估数据
    loading.value = false;
  } catch (error) {
    console.error('加载评估失败:', error);
  }
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