import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5001/api', // 直接连接后端API
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response?.status === 401) {
      // 清除token并跳转到登录页
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error.response?.data || error.message)
  }
)

// 认证相关API
export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/auth/login', credentials),
  
  register: (userData: {
    username: string
    email: string
    password: string
    full_name: string
    role?: string
  }) => api.post('/auth/register', userData),
  
  getProfile: () => api.get('/auth/profile'),
  
  updateProfile: (data: any) => api.put('/auth/profile', data),
  
  changePassword: (data: { old_password: string; new_password: string }) =>
    api.post('/auth/change-password', data),
}

// 用户管理API
export const userAPI = {
  getUsers: (params?: any) => api.get('/admin/users', { params }),
  getUser: (userId: number) => api.get(`/admin/users/${userId}`),
  createUser: (data: any) => api.post('/admin/users', data),
  updateUser: (userId: number, data: any) => api.put(`/admin/users/${userId}`, data),
  deleteUser: (userId: number) => api.delete(`/admin/users/${userId}`),
}

// 课程管理API
export const courseAPI = {
  getCourses: (params?: any) => api.get('/learning/courses', { params }),
  getCourse: (courseId: number) => api.get(`/learning/courses/${courseId}`),
  createCourse: (data: any) => api.post('/learning/courses', data),
  updateCourse: (courseId: number, data: any) => api.put(`/learning/courses/${courseId}`, data),
  deleteCourse: (courseId: number) => api.delete(`/learning/courses/${courseId}`),
  getMyCourses: () => api.get('/learning/my-courses'),
  enrollCourse: (courseId: number) => api.post(`/learning/enroll/${courseId}`),
  unenrollCourse: (courseId: number) => api.post(`/learning/unenroll/${courseId}`),
  getCourseStudents: (courseId: number) => api.get(`/learning/courses/${courseId}/students`),
  addStudentsToCourse: (courseId: number, studentIds: number[]) => 
    api.post(`/learning/courses/${courseId}/students`, { student_ids: studentIds }),
  removeStudentFromCourse: (courseId: number, studentId: number) => 
    api.delete(`/learning/courses/${courseId}/students/${studentId}`),
}

// 课件资源API
export const materialAPI = {
  getMaterials: (courseId: number) => api.get(`/courses/${courseId}/materials`),
  getMaterial: (materialId: number) => api.get(`/materials/${materialId}`),
  uploadMaterial: (courseId: number, formData: FormData) =>
    api.post(`/courses/${courseId}/materials`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  updateMaterial: (materialId: number, data: any) =>
    api.put(`/materials/${materialId}`, data),
  deleteMaterial: (materialId: number) => api.delete(`/materials/${materialId}`),
  downloadMaterial: (materialId: number) => {
    const token = localStorage.getItem('token')
    const url = `http://localhost:5001/api/materials/${materialId}/download`
    const link = document.createElement('a')
    link.href = token ? `${url}?token=${token}` : url
    link.target = '_blank'
    link.click()
  },
}

// 评估管理API
export const assessmentAPI = {
  getAssessments: (courseId: number) => api.get(`/courses/${courseId}/assessments`),
  getAssessment: (assessmentId: number) => api.get(`/assessments/${assessmentId}`),
  createAssessment: (courseId: number, data: any) =>
    api.post(`/courses/${courseId}/assessments`, data),
  submitAnswer: (assessmentId: number, data: any) =>
    api.post(`/assessments/${assessmentId}/submit`, data),
  getAssessmentAnswers: (assessmentId: number) =>
    api.get(`/assessments/${assessmentId}/answers`),
  gradeAnswer: (answerId: number, data: any) =>
    api.post(`/answers/${answerId}/grade`, data),
  getMyAnswers: () => api.get('/my-answers'),
}

// 学习助手API
export const learningAPI = {
  chatWithAssistant: (data: { question: string; course_id?: number }) =>
    api.post('/chat', data),
  getChatHistory: (params?: any) => api.get('/chat/history', { params }),
  generatePractice: (data: any) => api.post('/practice/generate', data),
  submitPractice: (data: any) => api.post('/practice/submit', data),
  getLearningRecords: (params?: any) => api.get('/learning-records', { params }),
}

// 管理员API
export const adminAPI = {
  getDashboardOverview: () => api.get('/admin/dashboard/overview'),
  getActivityStats: (params?: any) => api.get('/admin/dashboard/activity', { params }),
  getPerformanceStats: () => api.get('/admin/dashboard/performance'),
  getTopErrors: (params?: any) => api.get('/admin/dashboard/top-errors', { params }),
  getSystemStats: () => api.get('/admin/stats'),
  updateConfig: (data: any) => api.put('/admin/config', data),
}

// RAG和AI功能API
export const ragAiAPI = {
  getKnowledgeBaseStatus: () => api.get('/rag/knowledge-base/status'),
  uploadToKnowledgeBase: (data: any) => api.post('/rag/knowledge-base/upload', data),
  searchKnowledgeBase: (data: { query: string; top_k?: number }) =>
    api.post('/rag/search', data),
  generateCourseContent: (data: any) => api.post('/ai/generate-course-content', data),
  generateAssessment: (data: any) => api.post('/ai/generate-assessment', data),
  autoGradeAnswer: (data: any) => api.post('/ai/auto-grade', data),
  analyzeLearningPattern: (data?: any) => api.post('/ai/analyze-learning-pattern', data),
  recommendResources: (data: any) => api.post('/ai/recommend-resources', data),
}

// 健康检查API
export const healthAPI = {
  check: () => api.get('/health'),
}

export default api

