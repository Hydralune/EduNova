import { defineStore } from 'pinia';
import apiClient from '@/services/api';
import { ref, computed } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null);
  const user = ref(JSON.parse(localStorage.getItem('user')) || null);

  const isAuthenticated = computed(() => !!token.value);
  const currentUser = computed(() => user.value);

  function setToken(newToken) {
    token.value = newToken;
    localStorage.setItem('token', newToken);
  }

  function setUser(newUser) {
    user.value = newUser;
    localStorage.setItem('user', JSON.stringify(newUser));
  }

  function clearAuth() {
    token.value = null;
    user.value = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  async function login(credentials) {
    try {
      const response = await apiClient.post('/auth/login', credentials);
      const accessToken = response.data.access_token;
      setToken(accessToken);
      
      // After login, get user profile
      await fetchProfile();
      // Navigation is now handled by the component
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  async function register(userInfo) {
    try {
      await apiClient.post('/auth/register', userInfo);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }

  async function fetchProfile() {
    if (!token.value) return;
    try {
      const response = await apiClient.get('/auth/profile');
      setUser(response.data.logged_in_as);
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      clearAuth(); // Token might be invalid, clear auth state
    }
  }

  function logout() {
    clearAuth();
    // Navigation is now handled by the component
  }

  // Check user profile on initial load if token exists
  if (token.value) {
    fetchProfile();
  }

  return {
    token,
    user,
    isAuthenticated,
    currentUser,
    login,
    register,
    logout,
    fetchProfile,
  };
}); 