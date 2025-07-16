<template>
  <div class="submission-grader">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center items-center py-10">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>

    <div v-else class="space-y-6">
      <!-- 头部信息 -->
      <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <div class="flex justify-between items-start">
          <div>
            <h2 class="text-2xl font-bold mb-2">{{ assessment.title }}</h2>
            <p v-if="isReadOnly" class="text-blue-600 font-medium mb-2">查看提交详情</p>
            <p v-else class="text-blue-600 font-medium mb-2">评分界面</p>
            <p class="text-gray-600 mb-4">{{ assessment.description }}</p>
            <div class="flex flex-wrap gap-2 mb-2">
              <span class="px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-800">
                {{ assessment.type === 'quiz' ? '测验' : assessment.type === 'exam' ? '考试' : '作业' }}
              </span>
              <span class="px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
                总分: {{ assessment.total_score }} 分
              </span>
            </div>
          </div>
          <div class="text-right">
            <p class="text-sm text-gray-600">学生: {{ studentName }}</p>
            <p class="text-sm text-gray-600">提交时间: {{ formatDate(submission.submitted_at) }}</p>
            <p class="text-sm text-gray-600">当前得分: {{ currentScore }} / {{ assessment.total_score }}</p>
          </div>
        </div>
      </div>

      <!-- 批改进度 -->
      <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h3 class="text-lg font-semibold mb-4">批改进度</h3>
        <div class="w-full bg-gray-200 rounded-full h-2.5 mb-2">
          <div 
            class="bg-blue-600 h-2.5 rounded-full" 
            :style="{ width: `${(gradedQuestions / totalQuestions) * 100}%` }"
          ></div>
        </div>
        <div class="flex justify-between text-sm text-gray-600">
          <span>已批改: {{ gradedQuestions }}/{{ totalQuestions }}</span>
          <span>待批改: {{ totalQuestions - gradedQuestions }}</span>
        </div>
      </div>

      <!-- 题目列表 -->
      <div class="space-y-6">
        <div v-for="(question, index) in questions" :key="index" class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <!-- 题目信息 -->
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold">
              {{ index + 1 }}. {{ getQuestionTypeText(question.section_type) }}
              <span class="text-sm text-gray-500 ml-2">({{ question.score }}分)</span>
            </h3>
            <div>
              <span 
                :class="getQuestionStatusClass(question)"
                class="px-3 py-1 rounded-full text-sm"
              >
                {{ getQuestionStatusText(question) }}
              </span>
            </div>
          </div>

          <!-- 题干 -->
          <div class="mb-4">
            <p class="text-lg" v-html="formatQuestionStem(question.stem)"></p>
            
            <!-- 选项 (仅对选择题、多选题显示) -->
            <div v-if="['multiple_choice', 'multiple_select'].includes(question.section_type)" class="mt-3 space-y-2">
              <div v-for="(option, optionIndex) in question.options" :key="optionIndex"
                class="flex items-center p-2 rounded"
                :class="{
                  'bg-green-50': isOptionCorrect(question, optionIndex),
                }"
              >
                <span class="font-medium mr-2">{{ String.fromCharCode(65 + optionIndex) }}.</span>
                <span>{{ option }}</span>
                <span v-if="isOptionCorrect(question, optionIndex)" class="ml-2 text-green-600">✓</span>
              </div>
            </div>
          </div>

          <!-- 学生答案 -->
          <div class="mb-6 p-4 bg-gray-50 rounded-md">
            <p class="font-medium text-gray-700 mb-2">学生答案:</p>
            
            <!-- 选择题答案 -->
            <div v-if="question.section_type === 'multiple_choice'" class="space-y-3">
              <div class="flex items-center">
                <span class="mr-2">选择: </span>
                <span 
                  class="px-2 py-1 rounded-md" 
                  :class="isCorrectChoice(question, studentAnswers[index]) ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                >
                  {{ studentAnswers[index] }}
                </span>
              </div>
              
              <!-- 参考答案 -->
              <div class="mt-3 pt-3 border-t border-gray-200">
                <p class="font-medium text-sm text-gray-700 mb-1">参考答案:</p>
                <div class="bg-blue-50 p-2 rounded text-sm">
                  {{ getCorrectAnswerText(question) }}
                </div>
              </div>
            </div>

            <!-- 多选题答案 -->
            <div v-else-if="question.section_type === 'multiple_select'" class="space-y-3">
              <div>
                <span class="mr-2">选择: </span>
                <div class="flex flex-wrap gap-1">
                  <span 
                    v-for="option in studentAnswers[index]" 
                    :key="option"
                    class="px-2 py-1 rounded-md"
                    :class="isOptionInCorrectAnswer(question, option) ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                  >
                    {{ option }}
                  </span>
                </div>
              </div>
              
              <!-- 参考答案 -->
              <div class="mt-3 pt-3 border-t border-gray-200">
                <p class="font-medium text-sm text-gray-700 mb-1">参考答案:</p>
                <div class="bg-blue-50 p-2 rounded text-sm">
                  {{ getCorrectAnswerText(question) }}
                </div>
              </div>
            </div>

            <!-- 填空题答案 -->
            <div v-else-if="question.section_type === 'fill_blank' || question.section_type === 'fill_in_blank'" class="space-y-3">
              <div class="space-y-2">
                <div v-if="Array.isArray(studentAnswers[index])">
                  <div v-for="(blank, blankIndex) in studentAnswers[index]" :key="blankIndex" class="flex items-center">
                    <span class="mr-2">空白 {{ blankIndex + 1 }}: </span>
                    <span 
                      class="px-2 py-1 rounded-md"
                      :class="isCorrectBlank(question, blank, blankIndex) ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                    >
                      {{ blank }}
                    </span>
                  </div>
                </div>
                <div v-else class="flex items-center">
                  <span class="mr-2">答案: </span>
                  <span class="px-2 py-1 rounded-md" 
                    :class="isCorrectBlank(question, studentAnswers[index], 0) ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                    {{ studentAnswers[index] }}
                  </span>
                </div>
              </div>
              
              <!-- 参考答案 -->
              <div class="mt-3 pt-3 border-t border-gray-200">
                <p class="font-medium text-sm text-gray-700 mb-1">参考答案:</p>
                <div class="bg-blue-50 p-2 rounded text-sm">
                  <div v-if="Array.isArray(question.answer)" class="space-y-1">
                    <div v-for="(ans, idx) in question.answer" :key="idx">
                      空白 {{ idx + 1 }}: {{ ans }}
                    </div>
                  </div>
                  <div v-else>
                    {{ question.answer || question.reference_answer || '无参考答案' }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 判断题答案 -->
            <div v-else-if="question.section_type === 'true_false'" class="space-y-3">
              <div class="flex items-center">
                <span class="mr-2">回答: </span>
                <span 
                  class="px-2 py-1 rounded-md"
                  :class="isCorrectTrueFalse(question, studentAnswers[index]) ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                >
                  {{ studentAnswers[index] === 'true' ? '正确' : '错误' }}
                </span>
              </div>
              
              <!-- 参考答案 -->
              <div class="mt-3 pt-3 border-t border-gray-200">
                <p class="font-medium text-sm text-gray-700 mb-1">参考答案:</p>
                <div class="bg-blue-50 p-2 rounded text-sm">
                  {{ question.answer === 'true' ? '正确' : '错误' }}
                </div>
              </div>
            </div>

            <!-- 简答题答案 -->
            <div v-else-if="question.section_type === 'short_answer' || question.section_type === 'essay'" class="space-y-3">
              <div class="whitespace-pre-wrap">
                {{ typeof studentAnswers[index] === 'object' && studentAnswers[index].text ? studentAnswers[index].text : studentAnswers[index] }}
              </div>
              
              <!-- 附件列表 -->
              <div v-if="typeof studentAnswers[index] === 'object' && studentAnswers[index].files && studentAnswers[index].files.length > 0" class="mt-2">
                <p class="font-medium text-sm">附件:</p>
                <ul class="text-sm text-blue-600">
                  <li v-for="(file, fileIndex) in studentAnswers[index].files" :key="fileIndex" class="mt-1">
                    <a href="#" class="hover:underline">{{ file.name }}</a>
                  </li>
                </ul>
              </div>
              
              <!-- 参考答案 -->
              <div class="mt-3 pt-3 border-t border-gray-200">
                <p class="font-medium text-sm text-gray-700 mb-1">参考答案:</p>
                <div class="bg-blue-50 p-2 rounded text-sm whitespace-pre-wrap">
                  {{ question.reference_answer || question.answer || '无参考答案' }}
                </div>
              </div>
            </div>
          </div>

          <!-- 评分区域 (仅对主观题显示) -->
          <div v-if="needsManualGrading(question)" class="border-t pt-4">
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">分数 (最高 {{ question.score }} 分)</label>
              <input 
                type="number" 
                v-model="questionScores[index]" 
                class="w-24 px-3 py-2 border rounded-md"
                :min="0" 
                :max="question.score" 
                step="0.5"
                :disabled="isReadOnly"
                :class="{'bg-gray-100': isReadOnly}"
              />
            </div>
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">评语</label>
              <textarea 
                v-model="questionFeedback[index]" 
                rows="3" 
                class="w-full px-3 py-2 border rounded-md"
                placeholder="输入对此题的评语..."
                :disabled="isReadOnly"
                :class="{'bg-gray-100': isReadOnly}"
              ></textarea>
            </div>
          </div>
        </div>
      </div>

      <!-- 总体评价 -->
      <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h3 class="text-lg font-semibold mb-4">总体评价</h3>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">总分</label>
          <input 
            type="number" 
            v-model="totalScore" 
            class="w-24 px-3 py-2 border rounded-md"
            :min="0" 
            :max="assessment.total_score" 
            step="0.5"
            :disabled="isReadOnly"
            :class="{'bg-gray-100': isReadOnly}"
          />
          <span class="ml-2 text-gray-500">/ {{ assessment.total_score }}</span>
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">总体反馈</label>
          <textarea 
            v-model="overallFeedback" 
            rows="4" 
            class="w-full px-3 py-2 border rounded-md"
            placeholder="输入对整体评估的反馈..."
            :disabled="isReadOnly"
            :class="{'bg-gray-100': isReadOnly}"
          ></textarea>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="flex justify-end space-x-4">
        <button 
          @click="goBack" 
          class="px-4 py-2 border rounded-md hover:bg-gray-50"
        >
          返回
        </button>
        <button 
          v-if="!isReadOnly"
          @click="saveGrading" 
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          保存评分
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import assessmentAPI from '@/api/assessmentAPI';

const props = defineProps({
  submissionId: {
    type: [Number, String],
    required: true
  },
  readOnly: {
    type: Boolean,
    default: false
  }
});

const router = useRouter();
const route = useRoute();
// 检查URL参数中是否有readOnly=true
const isReadOnly = computed(() => props.readOnly || route.query.readOnly === 'true');

// 状态变量
const loading = ref(true);
const assessment = ref({});
const submission = ref({});
const studentName = ref('');
const questions = ref([]);
const studentAnswers = ref([]);
const questionScores = ref([]);
const questionFeedback = ref([]);
const overallFeedback = ref('');
const totalScore = ref(0);

// 计算属性
const gradedQuestions = computed(() => {
  // 计算已批改的题目数量（有分数的题目）
  return questionScores.value.filter(score => score > 0).length;
});

const totalQuestions = computed(() => {
  return questions.value.length;
});

const currentScore = computed(() => {
  return totalScore.value || 0;
});

// 方法
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString();
};

const getQuestionTypeText = (type) => {
  const typeMap = {
    'multiple_choice': '选择题',
    'multiple_select': '多选题',
    'fill_in_blank': '填空题',
    'fill_blank': '填空题',
    'true_false': '判断题',
    'short_answer': '简答题',
    'essay': '论述题'
  };
  return typeMap[type] || type;
};

const getQuestionStatusClass = (question) => {
  const index = questions.value.indexOf(question);
  if (index === -1) return '';
  
  const score = questionScores.value[index];
  
  if (score === undefined || score === null) return 'bg-gray-100 text-gray-800';
  if (needsManualGrading(question)) {
    return score > 0 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800';
  } else {
    // 客观题
    return 'bg-blue-100 text-blue-800';
  }
};

const getQuestionStatusText = (question) => {
  const index = questions.value.indexOf(question);
  if (index === -1) return '';
  
  const score = questionScores.value[index];
  
  if (score === undefined || score === null) return '未评分';
  if (needsManualGrading(question)) {
    return score > 0 ? '已评分' : '未评分';
  } else {
    // 客观题
    return '自动评分';
  }
};

const needsManualGrading = (question) => {
  return ['short_answer', 'essay'].includes(question.section_type);
};

const formatQuestionStem = (stem) => {
  if (!stem) return '';
  // 将填空题的下划线替换为可见的空白
  return stem.replace(/_{3,}/g, '<span class="border-b-2 border-gray-400 inline-block min-w-20">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>');
};

const isCorrectChoice = (question, answer) => {
  if (!question.answer) return false;
  
  // 处理不同格式的答案
  if (typeof question.answer === 'number') {
    const correctOption = String.fromCharCode(65 + question.answer);
    return answer === correctOption;
  } else {
    return answer === question.answer;
  }
};

const isOptionInCorrectAnswer = (question, option) => {
  if (!question.answer || !Array.isArray(question.answer)) return false;
  
  // 处理不同格式的答案
  const correctOptions = question.answer.map(ans => {
    if (typeof ans === 'number') {
      return String.fromCharCode(65 + ans);
    }
    return ans;
  });
  
  return correctOptions.includes(option);
};

const isCorrectBlank = (question, answer, index) => {
  if (!question.answer) return false;
  
  if (Array.isArray(question.answer)) {
    if (index >= question.answer.length) return false;
    
    // 检查答案是否匹配（不区分大小写和前后空白）
    const studentAnswer = String(answer || '').toLowerCase().trim();
    const correctAnswer = String(question.answer[index] || '').toLowerCase().trim();
    
    return studentAnswer === correctAnswer;
  } else {
    // 如果答案不是数组，但有单个答案
    const studentAnswer = String(answer || '').toLowerCase().trim();
    const correctAnswer = String(question.answer || '').toLowerCase().trim();
    
    return studentAnswer === correctAnswer;
  }
};

const isCorrectTrueFalse = (question, answer) => {
  if (!question.answer) return false;
  return String(answer).toLowerCase() === String(question.answer).toLowerCase();
};

const isOptionCorrect = (question, optionIndex) => {
  if (!question.answer) return false;
  
  if (question.section_type === 'multiple_choice') {
    // 单选题
    if (typeof question.answer === 'number') {
      return optionIndex === question.answer;
    } else if (typeof question.answer === 'string') {
      const letterOption = String.fromCharCode(65 + optionIndex);
      return question.answer === letterOption;
    }
  } else if (question.section_type === 'multiple_select') {
    // 多选题
    if (Array.isArray(question.answer)) {
      if (question.answer.every(ans => typeof ans === 'number')) {
        return question.answer.includes(optionIndex);
      } else {
        const letterOption = String.fromCharCode(65 + optionIndex);
        return question.answer.includes(letterOption);
      }
    }
  }
  
  return false;
};

const getCorrectAnswerText = (question) => {
  if (!question.answer && !question.reference_answer) return '无答案';
  
  // 优先使用reference_answer字段（用于主观题）
  if (question.reference_answer) {
    return String(question.reference_answer);
  }
  
  if (question.section_type === 'multiple_choice') {
    if (typeof question.answer === 'number') {
      return String.fromCharCode(65 + question.answer);
    } else if (typeof question.answer === 'string' && /^[A-Z]$/.test(question.answer)) {
      return question.answer;
    }
    return String(question.answer);
  } else if (question.section_type === 'multiple_select') {
    if (Array.isArray(question.answer)) {
      return question.answer.map(ans => {
        if (typeof ans === 'number') {
          return String.fromCharCode(65 + ans);
        } else if (typeof ans === 'string' && /^[A-Z]$/.test(ans)) {
          return ans;
        }
        return ans;
      }).join(', ');
    }
    return String(question.answer);
  } else if (question.section_type === 'true_false') {
    return question.answer === 'true' ? '正确' : '错误';
  } else {
    return String(question.answer);
  }
};

const getCorrectBlankAnswer = (question, index) => {
  if (!question.answer) return '';
  
  if (Array.isArray(question.answer)) {
    if (index >= question.answer.length) return '';
    return question.answer[index];
  } else {
    return question.answer;
  }
};

const goBack = () => {
  router.back();
};

// 获取提交数据
const fetchSubmission = async () => {
  try {
    loading.value = true;
    
    console.log('Fetching submission with ID:', props.submissionId);
    const response = await assessmentAPI.getSubmission(props.submissionId);
    
    console.log('Submission data:', response);
    
    // 设置提交数据
    if (response) {
      submission.value = response;
      
      // 设置学生名称
      studentName.value = response.student_name || `学生 ${response.student_id}`;
      
      // 设置评估数据
      if (response.assessment) {
        assessment.value = response.assessment;
      } else {
        // 如果提交中没有包含评估数据，则需要单独获取
        try {
          const assessmentResponse = await assessmentAPI.getAssessment(response.assessment_id);
          assessment.value = assessmentResponse;
        } catch (assessmentError) {
          console.error('获取评估数据失败:', assessmentError);
        }
      }
      
      // 解析题目和答案
      parseQuestionsAndAnswers(response);
      
      // 设置总分
      totalScore.value = response.score !== null ? response.score : 0;
      
      // 设置整体评价
      overallFeedback.value = response.feedback || '';
    }
  } catch (error) {
    console.error('获取提交数据失败:', error);
  } finally {
    loading.value = false;
  }
};

// 解析题目和答案
const parseQuestionsAndAnswers = (submissionData) => {
  // 解析题目
  if (assessment.value && assessment.value.questions) {
    let assessmentQuestions;
    try {
      assessmentQuestions = Array.isArray(assessment.value.questions) 
        ? assessment.value.questions 
        : JSON.parse(assessment.value.questions);
    } catch (error) {
      console.error('解析问题JSON失败:', error);
      assessmentQuestions = [];
    }
    
    console.log('评估问题原始数据:', assessmentQuestions);
    
    // 处理题目数据
    const parsedQuestions = [];
    
    // 将问题转换为统一格式
    if (assessmentQuestions) {
      if (Array.isArray(assessmentQuestions)) {
        // 如果直接是问题数组
        assessmentQuestions.forEach(q => {
          console.log('问题对象:', q);
          console.log('问题答案:', q.answer);
          
          // 确保answer字段存在，对于主观题，为每个题目设置默认参考答案
          let answer = q.answer;
          let reference_answer = q.reference_answer;
          
          // 处理题型
          let questionType = q.type || q.section_type || 'multiple_choice';
          
          // 标准化题型命名
          if (questionType === 'fill_in_blank') questionType = 'fill_blank';
          if (questionType === 'essay') questionType = 'short_answer'; // 论述题当作简答题处理
          
          // 如果有reference_answer但没有answer，使用reference_answer作为answer
          if ((!answer || answer === '') && reference_answer) {
            answer = reference_answer;
          }
          
          // 如果既没有answer也没有reference_answer，设置默认值
          if (answer === undefined || answer === null || (answer === '' && questionType !== 'short_answer')) {
            if (['short_answer', 'essay'].includes(questionType)) {
              // 对于主观题，设置默认的参考答案提示 - 不再设置为false
              reference_answer = reference_answer || '教师未提供参考答案';
              answer = answer || reference_answer;
            } else if (questionType === 'multiple_choice' && q.options && q.options.length > 0) {
              // 对于选择题，使用第一个选项作为默认答案
              answer = 'A';
            } else if (questionType === 'multiple_select' && q.options && q.options.length > 0) {
              // 对于多选题，使用前两个选项作为默认答案
              answer = ['A', 'B'];
            } else if (questionType === 'true_false') {
              // 对于判断题，默认为"正确"
              answer = 'true';
            } else if (questionType === 'fill_blank' || questionType === 'fill_in_blank') {
              // 对于填空题，根据stem中的空白数量设置默认答案
              const stem = q.stem || q.question || '';
              const blankCount = (stem.match(/_{3,}/g) || []).length || 1;
              answer = Array(blankCount).fill('未提供参考答案');
            }
          }
          
          parsedQuestions.push({
            ...q,
            answer: answer, // 确保answer字段存在
            reference_answer: reference_answer || answer, // 确保reference_answer字段存在
            section_type: questionType,
            score: q.score || (assessment.value.total_score / assessmentQuestions.length)
          });
        });
      } else if (assessmentQuestions.sections) {
        // 如果是带sections的新格式
        assessmentQuestions.sections.forEach(section => {
          section.questions.forEach(q => {
            console.log('段落问题对象:', q);
            console.log('段落问题答案:', q.answer);
            
            // 确保answer字段存在，对于主观题，为每个题目设置默认参考答案
            let answer = q.answer;
            let reference_answer = q.reference_answer;
            
            // 处理题型
            let questionType = q.type || section.type || 'multiple_choice';
            
            // 标准化题型命名
            if (questionType === 'fill_in_blank') questionType = 'fill_blank';
            if (questionType === 'essay') questionType = 'short_answer'; // 论述题当作简答题处理
            
            // 如果有reference_answer但没有answer，使用reference_answer作为answer
            if ((!answer || answer === '') && reference_answer) {
              answer = reference_answer;
            }
            
            // 如果既没有answer也没有reference_answer，设置默认值
            if (answer === undefined || answer === null || (answer === '' && questionType !== 'short_answer')) {
              if (['short_answer', 'essay'].includes(questionType)) {
                // 对于主观题，设置默认的参考答案提示 - 不再设置为false
                reference_answer = reference_answer || '教师未提供参考答案';
                answer = answer || reference_answer;
              } else if (questionType === 'multiple_choice' && q.options && q.options.length > 0) {
                // 对于选择题，使用第一个选项作为默认答案
                answer = 'A';
              } else if (questionType === 'multiple_select' && q.options && q.options.length > 0) {
                // 对于多选题，使用前两个选项作为默认答案
                answer = ['A', 'B'];
              } else if (questionType === 'true_false') {
                // 对于判断题，默认为"正确"
                answer = 'true';
              } else if (questionType === 'fill_blank' || questionType === 'fill_in_blank') {
                // 对于填空题，根据stem中的空白数量设置默认答案
                const stem = q.stem || q.question || '';
                const blankCount = (stem.match(/_{3,}/g) || []).length || 1;
                answer = Array(blankCount).fill('未提供参考答案');
              }
            }
            
            parsedQuestions.push({
              ...q,
              answer: answer, // 确保answer字段存在
              reference_answer: reference_answer || answer, // 确保reference_answer字段存在
              section_type: questionType,
              score: q.score || section.score_per_question || (assessment.value.total_score / section.questions.length)
            });
          });
        });
      }
    }
    
    questions.value = parsedQuestions;
    console.log('解析后的问题:', questions.value);
  }
  
  // 解析答案
  if (submissionData.answers) {
    try {
      // 答案可能是字符串或已解析的对象
      const parsedAnswers = typeof submissionData.answers === 'string' 
        ? JSON.parse(submissionData.answers) 
        : submissionData.answers;
      
      studentAnswers.value = parsedAnswers;
    } catch (error) {
      console.error('解析答案失败:', error);
      studentAnswers.value = [];
    }
  }
  
  // 初始化题目分数和反馈
  if (submissionData.question_scores) {
    try {
      const scores = typeof submissionData.question_scores === 'string'
        ? JSON.parse(submissionData.question_scores)
        : submissionData.question_scores;
      
      questionScores.value = scores;
    } catch (error) {
      console.error('解析题目分数失败:', error);
      // 初始化为零分数组
      questionScores.value = questions.value.map(() => 0);
    }
  } else {
    // 初始化为零分数组
    questionScores.value = questions.value.map(() => 0);
  }
  
  if (submissionData.question_feedback) {
    try {
      const feedback = typeof submissionData.question_feedback === 'string'
        ? JSON.parse(submissionData.question_feedback)
        : submissionData.question_feedback;
      
      questionFeedback.value = feedback;
    } catch (error) {
      console.error('解析题目反馈失败:', error);
      // 初始化为空反馈数组
      questionFeedback.value = questions.value.map(() => '');
    }
  } else {
    // 初始化为空反馈数组
    questionFeedback.value = questions.value.map(() => '');
  }
};

// 保存评分
const saveGrading = async () => {
  try {
    // 准备提交数据
    const gradingData = {
      score: totalScore.value,
      feedback: overallFeedback.value,
      question_scores: questionScores.value,
      question_feedback: questionFeedback.value,
      grader_id: 1 // 应该从用户状态获取
    };
    
    console.log('Saving grading:', gradingData);
    
    // 调用API提交评分
    const response = await assessmentAPI.gradeSubmission(props.submissionId, gradingData);
    
    console.log('Grading response:', response);
    
    // 显示成功消息
    alert('评分已保存');
    
    // 返回提交列表
    goBack();
  } catch (error) {
    console.error('保存评分失败:', error);
    alert('保存评分失败，请重试');
  }
};

// 监听题目评分变化，自动更新总分
watch(questionScores, (newScores) => {
  // 计算总分
  totalScore.value = newScores.reduce((sum, score) => sum + (score || 0), 0);
}, { deep: true });

// 组件挂载时获取数据
onMounted(() => {
  fetchSubmission();
});
</script> 