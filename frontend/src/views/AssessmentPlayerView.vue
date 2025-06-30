<template>
  <div class="container mx-auto py-6 px-4">
    <div class="mb-4">
      <button 
        @click="goBack" 
        class="p-2 bg-white shadow-md rounded-lg hover:bg-gray-50 text-gray-700 flex items-center justify-center"
        style="width: 40px; height: 40px;"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
    <AssessmentPlayer 
      :assessmentId="assessmentId"
      @save-progress="handleSaveProgress"
      @submit="handleSubmit"
      @cancel="goBack"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import AssessmentPlayer from '../components/assessment/AssessmentPlayer.vue';

const route = useRoute();
const router = useRouter();
const assessmentId = computed(() => route.params.id);

// 处理保存进度
const handleSaveProgress = (data) => {
  console.log('保存进度:', data);
  alert('进度已保存');
};

// 处理提交
const handleSubmit = (data) => {
  console.log('提交答案:', data);
  alert('答案已提交');
  goBack();
};

// 返回上一页
const goBack = () => {
  // 检查是否有courseId查询参数
  const courseId = route.query.courseId;
  if (courseId) {
    // 如果有courseId，返回到课程详情页面
    router.push(`/course/${courseId}`);
  } else {
    // 否则返回上一页
    router.back();
  }
};
</script> 