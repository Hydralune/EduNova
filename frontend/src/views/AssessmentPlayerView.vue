<template>
  <div class="container mx-auto py-6 px-4">
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
  router.back();
};
</script> 