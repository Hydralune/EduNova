import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, register, fetchUserProfile } from '@/api/auth'

export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  avatar?: string
  created_at?: string
  updated_at?: string
}

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref<string>(localStorage.getItem('token') || '')
  const user = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // 初始化 - 从本地存储加载状态
  try {
    const savedAuth = localStorage.getItem('auth')
    if (savedAuth) {
      const parsedAuth = JSON.parse(savedAuth)
      token.value = parsedAuth.token || ''
      user.value = parsedAuth.user || null
    }
  } catch (error) {
    console.error('Failed to load auth from localStorage:', error)
    localStorage.removeItem('auth')
  }
  
  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isTeacher = computed(() => user.value?.role === 'teacher')
  const isStudent = computed(() => user.value?.role === 'student')
  
  // 动作
  const setToken = (newToken: string) => {
    token.value = newToken
    saveToLocalStorage()
  }
  
  const setUser = (newUser: User | null) => {
    user.value = newUser
    saveToLocalStorage()
  }
  
  const saveToLocalStorage = () => {
    localStorage.setItem('token', token.value)
    localStorage.setItem('auth', JSON.stringify({
      token: token.value,
      user: user.value
    }))
  }
  
  const loginUser = async (username: string, password: string) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await login(username, password)
      setToken(response.token)
      setUser(response.user)
      return response
    } catch (err: any) {
      error.value = err.error || '登录失败，请检查用户名和密码'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const registerUser = async (userData: any) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await register(userData)
      return response
    } catch (err: any) {
      error.value = err.error || '注册失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const fetchProfile = async () => {
    isLoading.value = true
    
    try {
      const userProfile = await fetchUserProfile(token.value)
      setUser(userProfile)
      return userProfile
    } catch (err: any) {
      error.value = err.error || '获取用户信息失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const logout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('auth')
  }
  
  const clearError = () => {
    error.value = null
  }
  
  return {
    token,
    user,
    isLoading,
    error,
    isAuthenticated,
    isAdmin,
    isTeacher,
    isStudent,
    loginUser,
    registerUser,
    fetchProfile,
    logout,
    clearError
  }
}) 