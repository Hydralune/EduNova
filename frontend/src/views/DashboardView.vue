<template>
  <div class="dashboard-container">
    <h2>Dashboard</h2>
    <div v-if="auth.isAuthenticated && auth.currentUser">
      <p>Welcome, <strong>{{ auth.currentUser.username }}</strong>!</p>
      <p>Your role is: <strong>{{ auth.currentUser.role }}</strong>.</p>
    </div>
    <div v-else>
      <p>Loading user data...</p>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
</script>

<style scoped>
.dashboard-container {
  max-width: 600px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
  text-align: center;
}
</style> 