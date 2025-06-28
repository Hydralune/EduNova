import axios from 'axios'
import { User } from '@/stores/auth'

const API_URL = 'http://localhost:5001/api'

// Define response types
interface LoginResponse {
  message: string;
  token: string;
  refresh_token: string;
  user: User;
}

interface AvatarResponse {
  message: string;
  avatar_url: string;
}

// 创建axios实例
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true  // 添加这个以确保跨域请求正确发送cookies
})

// 请求拦截器添加认证token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    console.log('添加认证头:', `Bearer ${token.substring(0, 10)}...`)
  }
  return config
})

// 响应拦截器处理错误
api.interceptors.response.use(
  response => {
    console.log(`API响应成功: ${response.config.url}`)
    return response.data
  },
  error => {
    console.error('API错误:', error.response?.status, error.response?.data)
    
    // 处理401未授权错误
    if (error.response && error.response.status === 401) {
      console.error('认证失败，可能需要重新登录')
      // 清除本地存储的令牌
      localStorage.removeItem('token')
      localStorage.removeItem('auth')
    }
    
    const errorMessage = error.response?.data?.error || '发生未知错误'
    return Promise.reject({ error: errorMessage, status: error.response?.status })
  }
)

/**
 * 用户登录
 */
export const login = async (userData: { username: string, password: string }): Promise<{ token: string; user: User }> => {
  try {
    console.log('尝试登录:', userData.username)
    const response = await api.post('/auth/login', userData) as LoginResponse
    console.log('登录成功:', response.user.username)
    return {
      token: response.token,
      user: response.user
    }
  } catch (error) {
    console.error('登录失败:', error)
    throw error
  }
}

/**
 * 用户注册
 */
export const register = async (userData: any) => {
  try {
    console.log('尝试注册新用户')
    const response = await api.post('/auth/register', userData)
    console.log('注册成功')
    return response
  } catch (error) {
    console.error('注册失败:', error)
    throw error
  }
}

/**
 * 获取用户资料
 */
export const fetchUserProfile = async (): Promise<User> => {
  try {
    console.log('获取用户资料')
    const response = await api.get('/auth/profile')
    console.log('获取用户资料成功')
    return response.user
  } catch (error) {
    console.error('获取用户资料失败:', error)
    throw error
  }
}

/**
 * 更新用户资料
 */
export const updateUserProfile = async (userData: any) => {
  try {
    console.log('更新用户资料')
    const response = await api.put('/auth/profile', userData)
    console.log('更新用户资料成功')
    return response
  } catch (error) {
    console.error('更新用户资料失败:', error)
    throw error
  }
}

/**
 * 修改密码
 */
export const changeUserPassword = async (data: { old_password: string; new_password: string }) => {
  try {
    console.log('修改密码')
    const response = await api.post('/auth/change-password', data)
    console.log('修改密码成功')
    return response
  } catch (error) {
    console.error('修改密码失败:', error)
    throw error
  }
}

/**
 * 上传头像
 */
export const uploadAvatar = async (file: File): Promise<AvatarResponse> => {
  try {
    console.log('上传头像')
    const formData = new FormData()
    formData.append('avatar', file)
    
    // 创建一个特殊的实例来处理文件上传，不设置Content-Type让浏览器自动设置
    const response = await axios.post(`${API_URL}/auth/avatar`, formData, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    console.log('头像上传成功')
    return response.data as AvatarResponse
  } catch (error) {
    console.error('头像上传失败:', error)
    throw error
  }
} 