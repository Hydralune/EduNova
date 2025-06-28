import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api'

export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  avatar_url?: string
  created_at?: string
  updated_at?: string
}

interface LoginResponse {
  token: string
  user: User
  message?: string
}

interface ProfileResponse {
  user: User
  message?: string
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
    console.log('设置用户信息:', newUser);
    if (newUser) {
      // 确保用户信息完整
      if (!newUser.id || !newUser.username || !newUser.role) {
        console.error('用户信息不完整，拒绝更新:', newUser);
        return;
      }
    }
    user.value = newUser;
    saveToLocalStorage();
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
      const response = await authAPI.login({ username, password })
      const data = response as unknown as LoginResponse
      setToken(data.token)
      setUser(data.user)
      return data
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
      const response = await authAPI.register(userData)
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
    error.value = null
    
    try {
      console.log('开始获取用户资料...')
      const response = await authAPI.getProfile() as any
      console.log('获取用户资料响应:', response)
      
      // 确保响应中包含用户数据
      if (response && response.user) {
        console.log('获取用户资料成功:', response.user)
        setUser(response.user)
        return response.user
      } else {
        console.error('响应中没有用户数据:', response)
        throw new Error('响应中没有用户数据')
      }
    } catch (err: any) {
      console.error('获取用户信息失败:', err)
      error.value = err.error || '获取用户信息失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const updateProfile = async (userData: any) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authAPI.updateProfile(userData)
      const data = response as unknown as ProfileResponse
      if (data && data.user) {
        setUser(data.user)
      }
      return data
    } catch (err: any) {
      error.value = err.error || '更新用户信息失败'
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
    updateProfile,
    logout,
    clearError,
    setUser,
    setToken
  }
}) 