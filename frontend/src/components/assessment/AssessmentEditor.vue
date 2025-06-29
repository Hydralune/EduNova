<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-semibold">{{ assessment.id ? '编辑评估' : '创建评估' }}</h2>
      <button @click="$emit('cancel')" class="text-gray-500 hover:text-gray-700">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
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
                      :name="'question_' + index"
                      :value="optionIndex"
                      v-model="question.answer"
                      class="h-4 w-4"
                    />
                    <input
                      v-else
                      type="checkbox"
                      v-model="question.answers"
                      :value="optionIndex"
                      class="h-4 w-4"
                    />
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { courseAPI } from '@/api';

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
};

// 删除选项
const removeOption = (question, index) => {
  question.options.splice(index, 1);
  if (question.type === 'multiple_choice') {
    if (question.answer >= index) {
      question.answer = Math.max(0, question.answer - 1);
    }
  } else if (question.type === 'multiple_answer') {
    question.answers = question.answers.filter(a => a !== index)
      .map(a => a > index ? a - 1 : a);
  }
};

// 提交表单
const handleSubmit = () => {
  // 计算总分
  const totalScore = form.value.questions.reduce((sum, q) => sum + (q.score || 0), 0);
  form.value.total_score = totalScore;

  const assessment = {
    ...props.assessment,
    ...form.value,
    is_published: form.value.is_active // 设置发布状态
  };
  emit('save', assessment);
};

// 在组件挂载时获取课程列表
onMounted(() => {
  fetchCourses();
});
</script> 