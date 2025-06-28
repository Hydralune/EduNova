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
  }
  return config
})

// 响应拦截器处理错误
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    const errorMessage = error.response?.data?.error || '发生未知错误'
    return Promise.reject({ error: errorMessage })
  }
)

/**
 * 用户登录
 */
export const login = async (username: string, password: string): Promise<{ token: string; user: User }> => {
  try {
    const response = await api.post('/auth/login', { username, password }) as LoginResponse
    return {
      token: response.token,
      user: response.user
    }
  } catch (error) {
    console.error('Login error:', error)
    throw error
  }
}

/**
 * 用户注册
 */
export const register = async (userData: any) => {
  try {
    const response = await api.post('/auth/register', userData)
    return response
  } catch (error) {
    throw error
  }
}

/**
 * 获取用户资料
 */
export const fetchUserProfile = async (token: string): Promise<User> => {
  try {
    const response = await api.get('/users/profile', {
      headers: { Authorization: `Bearer ${token}` }
    })
    // The backend returns the user object directly
    return response as unknown as User
  } catch (error) {
    throw error
  }
}

/**
 * 更新用户资料
 */
export const updateUserProfile = async (token: string, userData: any) => {
  try {
    const response = await api.put('/users/profile', userData, {
      headers: { Authorization: `Bearer ${token}` }
    })
    return response
  } catch (error) {
    throw error
  }
}

/**
 * 修改密码
 */
export const changeUserPassword = async (token: string, oldPassword: string, newPassword: string) => {
  try {
    const response = await api.post('/users/change-password', 
      { old_password: oldPassword, new_password: newPassword },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    return response
  } catch (error) {
    throw error
  }
} 