<template>
  <div class="container mx-auto py-6 px-4">
    <h1 class="text-2xl font-bold mb-6">测试评估界面</h1>
    
    <!-- 评估列表 -->
    <div v-if="!showPlayer && !showView" class="p-6 bg-white rounded-lg shadow-md">
      <h2 class="text-xl font-semibold mb-4">可用评估</h2>
      
      <div class="space-y-4">
        <div class="p-4 border rounded-md">
          <div class="flex items-center justify-between">
            <div>
              <h4 class="font-medium">{{ assessment.title }}</h4>
              <p class="text-sm text-gray-500">{{ assessment.type }} · {{ getTotalQuestions() }}题 · {{ assessment.duration }}</p>
            </div>
            <div class="flex gap-2">
              <button 
                @click="startAssessmentView" 
                class="px-4 py-2 border rounded-md hover:bg-gray-50"
              >
                查看模式
              </button>
            </div>
          </div>
          <div class="mt-2">
            <p class="text-sm text-gray-700">{{ assessment.description }}</p>
          </div>
          <div class="mt-2 flex items-center text-sm text-gray-500">
            <span>截止日期: {{ formatDate(assessment.due_date) }}</span>
            <span class="mx-2">|</span>
            <span>尝试次数: 0/{{ assessment.max_attempts }}</span>
          </div>
          <div class="flex justify-between items-center mt-4">
            <div>
              <span class="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">未开始</span>
            </div>
            <div>
              <button 
                @click="startAssessmentPlayer" 
                class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                开始评估
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 评估查看模式 -->
    <AssessmentView 
      v-if="showView && !showPlayer"
      :assessmentId="assessment.id" 
      :previewMode="true"
      @save-progress="handleSaveProgress"
      @submit="handleSubmit"
      @cancel="resetView"
    />
    
    <!-- 评估答题模式 -->
    <AssessmentPlayer 
      v-if="showPlayer && !showView"
      :assessmentId="assessment.id"
      @save-progress="handleSaveProgress"
      @submit="handleSubmit"
      @cancel="resetView"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import AssessmentView from '../components/assessment/AssessmentView.vue';
import AssessmentPlayer from '../components/assessment/AssessmentPlayer.vue';
import mockExam from '../assets/mock-exam.json';
import { useRouter } from 'vue-router';

const assessment = ref({});
const showView = ref(false);
const showPlayer = ref(false);
const router = useRouter();

// 从mock数据加载评估
onMounted(() => {
  assessment.value = mockExam;
  console.log('Assessment loaded:', assessment.value);
});

// 获取题目总数
const getTotalQuestions = () => {
  let count = 0;
  if (assessment.value && assessment.value.sections) {
    assessment.value.sections.forEach(section => {
      if (section.questions) {
        count += section.questions.length;
      }
    });
  }
  return count;
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

// 启动评估查看模式
const startAssessmentView = () => {
  console.log('Starting assessment view mode');
  showView.value = true;
};

// 启动评估答题模式
const startAssessmentPlayer = () => {
  console.log('Starting assessment player mode');
  router.push(`/assessments/${assessment.value.id}/take`);
};

// 重置视图
const resetView = () => {
  showView.value = false;
  showPlayer.value = false;
};

// 处理保存进度
const handleSaveProgress = (data) => {
  console.log('保存进度:', data);
  alert('进度已保存');
};

// 处理提交
const handleSubmit = (data) => {
  console.log('提交答案:', data);
  alert('答案已提交');
  resetView();
};
</script> 