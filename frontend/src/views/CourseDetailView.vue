<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
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
        <CourseDetail :id="id" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import CourseDetail from '@/components/course/CourseDetail.vue';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const id = computed(() => route.params.id);

// 返回课程列表
function goBack() {
  // 根据用户角色返回对应页面并设置活动标签为课程列表
  const userRole = authStore.user?.role || '';
  
  if (userRole === 'teacher') {
    router.push({ path: '/teacher', query: { activeTab: 'courses' } });
  } else if (userRole === 'student') {
    router.push({ path: '/student', query: { activeTab: 'courses' } });
  } else if (userRole === 'admin') {
    router.push('/admin');
  } else {
    router.push('/dashboard');
  }
}
</script> 