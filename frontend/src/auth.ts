import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/services/api'

export interface User {
  id: number
  username: string
  email: string
  role: 'admin' | 'teacher' | 'student'
  full_name: string
  created_at: string
  last_login: string | null
  is_active: boolean
}

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isTeacher = computed(() => user.value?.role === 'teacher')
  const isStudent = computed(() => user.value?.role === 'student')

  // 方法
  const login = async (credentials: { username: string; password: string }) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await authAPI.login(credentials)
      
      token.value = response.token
      user.value = response.user
      
      localStorage.setItem('token', response.token)
      localStorage.setItem('user', JSON.stringify(response.user))
      
      return response
    } catch (err: any) {
      error.value = err.error || '登录失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData: {
    username: string
    email: string
    password: string
    full_name: string
    role?: string
  }) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await authAPI.register(userData)
      return response
    } catch (err: any) {
      error.value = err.error || '注册失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  const fetchProfile = async () => {
    try {
      const response = await authAPI.getProfile()
      user.value = response.user
      localStorage.setItem('user', JSON.stringify(response.user))
      return response
    } catch (err: any) {
      error.value = err.error || '获取用户信息失败'
      throw err
    }
  }

  const updateProfile = async (data: any) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await authAPI.updateProfile(data)
      user.value = response.user
      localStorage.setItem('user', JSON.stringify(response.user))
      
      return response
    } catch (err: any) {
      error.value = err.error || '更新用户信息失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const changePassword = async (data: { old_password: string; new_password: string }) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await authAPI.changePassword(data)
      return response
    } catch (err: any) {
      error.value = err.error || '修改密码失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 初始化用户信息
  const initializeAuth = () => {
    const storedUser = localStorage.getItem('user')
    if (storedUser && token.value) {
      try {
        user.value = JSON.parse(storedUser)
      } catch (err) {
        console.error('Failed to parse stored user data:', err)
        logout()
      }
    }
  }

  // 清除错误
  const clearError = () => {
    error.value = null
  }

  return {
    // 状态
    user,
    token,
    isLoading,
    error,
    
    // 计算属性
    isAuthenticated,
    isAdmin,
    isTeacher,
    isStudent,
    
    // 方法
    login,
    register,
    logout,
    fetchProfile,
    updateProfile,
    changePassword,
    initializeAuth,
    clearError,
  }
})

