import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authAPI from '@/api/auth'

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

interface ProfileUpdateResponse {
  message: string
  user: User
}

interface AvatarResponse {
  message: string
  avatar_url: string
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
      console.log('从本地存储加载认证状态:', user.value?.username || '无用户')
    }
  } catch (error) {
    console.error('从本地存储加载认证状态失败:', error)
    localStorage.removeItem('auth')
    localStorage.removeItem('token')
  }
  
  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isTeacher = computed(() => user.value?.role === 'teacher')
  const isStudent = computed(() => user.value?.role === 'student')
  
  // 动作
  const setToken = (newToken: string) => {
    console.log('设置新令牌')
    token.value = newToken
    localStorage.setItem('token', newToken)
    saveToLocalStorage()
  }
  
  const setUser = (newUser: User | null) => {
    console.log('设置用户信息:', newUser?.username || '无用户');
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
    try {
      localStorage.setItem('token', token.value)
      localStorage.setItem('auth', JSON.stringify({
        token: token.value,
        user: user.value
      }))
      console.log('认证状态已保存到本地存储')
    } catch (e) {
      console.error('保存认证状态到本地存储失败:', e)
    }
  }
  
  const loginUser = async (username: string, password: string) => {
    isLoading.value = true
    error.value = null
    
    try {
      console.log('开始登录流程:', username)
      const data = await authAPI.login({ username, password })
      console.log('登录API调用成功:', data.user.username)
      
      setToken(data.token)
      setUser(data.user)
      return data
    } catch (err: any) {
      console.error('登录失败:', err)
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
      console.log('开始注册流程')
      const response = await authAPI.register(userData)
      console.log('注册成功')
      return response
    } catch (err: any) {
      console.error('注册失败:', err)
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
      const userData = await authAPI.fetchUserProfile()
      console.log('获取用户资料成功:', userData)
      
      // 更新用户信息
      setUser(userData)
      return userData
    } catch (err: any) {
      console.error('获取用户信息失败:', err)
      
      // 如果是401错误，清除认证状态
      if (err.status === 401) {
        console.error('认证失败，清除认证状态')
        logout()
      }
      
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
      console.log('开始更新用户资料')
      const response = await authAPI.updateUserProfile(userData) as ProfileUpdateResponse
      console.log('更新用户资料成功')
      
      // 更新用户信息
      if (response && response.user) {
        setUser(response.user)
      }
      return response
    } catch (err: any) {
      console.error('更新用户信息失败:', err)
      error.value = err.error || '更新用户信息失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const uploadUserAvatar = async (file: File) => {
    isLoading.value = true
    error.value = null
    
    try {
      // 确保用户已登录且有用户ID
      if (!user.value || !user.value.id) {
        throw new Error('用户未登录或用户ID不可用')
      }
      
      console.log('开始上传头像，用户ID:', user.value.id)
      const response = await authAPI.uploadAvatar(file, user.value.id)
      console.log('上传头像成功:', response)
      
      // 更新用户头像URL
      if (response && response.avatar_url && user.value) {
        user.value.avatar_url = response.avatar_url
        saveToLocalStorage()
      }
      
      return response
    } catch (err: any) {
      console.error('上传头像失败:', err)
      error.value = err.error || '上传头像失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const simpleUploadUserAvatar = async (file: File) => {
    isLoading.value = true
    error.value = null
    
    try {
      // 确保用户已登录且有用户ID
      if (!user.value || !user.value.id) {
        throw new Error('用户未登录或用户ID不可用')
      }
      
      console.log('开始简单上传头像，用户ID:', user.value.id)
      const response = await authAPI.simpleAvatarUpload(file, user.value.id)
      console.log('上传头像成功:', response)
      
      // 更新用户头像URL
      if (response && response.avatar_url && user.value) {
        user.value.avatar_url = response.avatar_url
        saveToLocalStorage()
      }
      
      return response
    } catch (err: any) {
      console.error('上传头像失败:', err)
      error.value = err.error || '上传头像失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const logout = () => {
    console.log('用户登出')
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
    uploadUserAvatar,
    simpleUploadUserAvatar,
    logout,
    clearError,
    setUser,
    setToken
  }
}) 