<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <AssessmentView 
          :assessmentId="assessmentId"
          @save-progress="handleSaveProgress"
          @submit="handleSubmit"
          @cancel="goBack"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AssessmentView from '../components/assessment/AssessmentView.vue';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
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
    // 如果有courseId，返回到课程详情页面，并设置活动标签为评估测验
    router.push({ path: `/course/${courseId}`, query: { activeTab: 'assessments' } });
  } else {
    // 根据用户角色返回对应页面
    const userRole = authStore.user?.role || '';
    
    if (userRole === 'teacher') {
      router.push({ path: '/teacher', query: { activeTab: 'assessments' } });
    } else if (userRole === 'student') {
      router.push({ path: '/student', query: { activeTab: 'assessments' } });
    } else {
      router.push('/dashboard');
    }
  }
};
</script> 