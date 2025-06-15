<template>
  <div class="auth-container">
    <h2>Register</h2>
    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <label for="username">Username</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <div class="form-group">
        <label for="role">Role</label>
        <select id="role" v-model="role">
          <option value="student">Student</option>
          <option value="teacher">Teacher</option>
          <option value="admin">Admin</option>
        </select>
      </div>
      <button type="submit">Register</button>
      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="success" class="success-message">{{ success }}</p>
    </form>
    <p>
      Already have an account? <router-link to="/login">Login here</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const username = ref('');
const password = ref('');
const role = ref('student');
const error = ref(null);
const success = ref(null);
const authStore = useAuthStore();
const router = useRouter();

const handleRegister = async () => {
  error.value = null;
  success.value = null;
  try {
    await authStore.register({
      username: username.value,
      password: password.value,
      role: role.value,
    });
    success.value = 'Registration successful! You can now log in.';
    setTimeout(() => {
      router.push('/login');
    }, 2000);
  } catch (err) {
    if (err.response) {
      // The server responded with an error
      error.value = `Registration failed: ${err.response.data.msg || 'Server error'}`;
    } else if (err.request) {
      // The request was made but no response was received
      error.value = 'Registration failed: Cannot connect to the server. Is the backend running?';
    } else {
      // Something else happened
      error.value = 'An unknown error occurred.';
    }
    console.error(err);
  }
};
</script>

<style scoped>
/* Using the same styles as LoginView.vue */
.auth-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
.form-group {
  margin-bottom: 15px;
}
label {
  display: block;
  margin-bottom: 5px;
}
input, select {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}
button {
  width: 100%;
  padding: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.error-message {
  color: red;
  margin-top: 10px;
}
.success-message {
  color: green;
  margin-top: 10px;
}
</style> 