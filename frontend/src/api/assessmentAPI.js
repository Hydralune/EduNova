import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5001/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response?.status === 401) {
      // 清除token并跳转到登录页
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    
    // 增强错误对象，添加更多有用的信息
    if (error.response && error.response.data) {
      // 将后端返回的错误信息附加到错误对象上
      error.backendError = error.response.data.error || error.response.data.message || '未知错误';
      console.error('API错误详情:', {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        url: error.config.url,
        method: error.config.method
      });
    }
    
    return Promise.reject(error);
  }
);

// 评估API
const assessmentAPI = {
  // 获取评估列表
  getAssessments: (params) => {
    return api.get('/assessments', { params });
  },

  // 获取单个评估
  getAssessment: (assessmentId) => {
    return api.get(`/assessments/${assessmentId}`);
  },

  // 创建评估
  createAssessment: (data) => {
    return api.post('/assessments', data);
  },

  // 更新评估
  updateAssessment: (assessmentId, data) => {
    return api.put(`/assessments/${assessmentId}`, data);
  },

  // 删除评估
  deleteAssessment: (assessmentId) => {
    return api.delete(`/assessments/${assessmentId}`);
  },

  // 提交评估答案
  submitAssessment: (assessmentId, data) => {
    return api.post(`/assessments/${assessmentId}/submit`, data);
  },

  // 获取评估的提交记录
  getSubmissionsByAssessment: (assessmentId, params) => {
    return api.get(`/assessments/${assessmentId}/submissions`, { params });
  },

  // 获取学生的提交记录
  getSubmissionsByStudent: (studentId, params) => {
    return api.get(`/students/${studentId}/submissions`, { params });
  },

  // 获取单个提交记录
  getSubmission: (submissionId) => {
    return api.get(`/submissions/${submissionId}`);
  },

  // 评分提交
  gradeSubmission: (submissionId, data) => {
    return api.post(`/submissions/${submissionId}/grade`, data);
  },

  // 获取评估统计数据
  getAssessmentStats: (assessmentId) => {
    return api.get(`/assessments/${assessmentId}/stats`);
  },

  // 获取评估的提交数量
  getSubmissionCount: (assessmentId) => {
    return api.get(`/assessments/${assessmentId}/submission-count`);
  },

  // 获取课程的所有评估
  getCourseAssessments: (courseId, params) => {
    return api.get(`/courses/${courseId}/assessments`, { params });
  },
};

export default assessmentAPI; 