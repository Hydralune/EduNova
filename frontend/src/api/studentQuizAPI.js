import api from '@/api';

/**
 * Student AI Quiz API Module
 * Handles all API calls related to student self-assessment quizzes
 */
const studentQuizAPI = {
  // Generate a new quiz
  generateQuiz: (data) => {
    return api.post('/student/quizzes/ai-generate', data);
  },
  
  // Generate a quiz incrementally (one question at a time)
  generateQuizIncremental: async (data) => {
    console.log('开始生成逐题测验，请求数据:', data);
    
    // 添加重试机制
    const maxRetries = 2;
    let retries = 0;
    let lastError = null;
    
    while (retries <= maxRetries) {
      try {
        if (retries > 0) {
          console.log(`尝试重新生成测验 (第${retries}次重试)...`);
        }
        
        const response = await api.post('/student/quizzes/ai-generate-incremental', data, {
          timeout: 180000 // 增加单独请求的超时时间到3分钟
        });
        
        console.log('逐题测验生成响应:', response);
        return response;
      } catch (error) {
        lastError = error;
        console.error(`生成测验失败 (尝试 ${retries + 1}/${maxRetries + 1}):`, error);
        
        // 如果不是超时错误，或者已经重试了最大次数，则抛出错误
        if (error.code !== 'ECONNABORTED' || retries >= maxRetries) {
          break;
        }
        
        // 增加重试次数
        retries++;
        
        // 等待一段时间后重试
        const waitTime = 1000 * retries; // 1秒, 2秒, ...
        console.log(`等待 ${waitTime}ms 后重试...`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
      }
    }
    
    // 如果所有重试都失败，抛出最后一个错误
    throw lastError || new Error('生成测验失败，请刷新页面重试');
  },
  
  // Get quiz status and available questions
  getQuizStatus: async (quizId) => {
    try {
      const response = await api.get(`/student/quizzes/${quizId}/status`);
      console.log(`获取测验状态 (ID: ${quizId}):`, response);
      
      // 确保questions字段是数组
      if (response && !response.questions) {
        response.questions = [];
      }
      
      return response;
    } catch (error) {
      console.error(`获取测验状态失败 (ID: ${quizId}):`, error);
      throw error;
    }
  },
  
  // Submit answers for grading
  submitQuizAnswers: (quizId, answers) => {
    return api.post(`/student/quizzes/${quizId}/submit`, { answers });
  },
  
  // Get quiz results
  getQuizResults: (quizId) => {
    return api.get(`/student/quizzes/${quizId}/results`);
  },
  
  // Delete a quiz
  deleteQuiz: (quizId) => {
    return api.delete(`/student/quizzes/${quizId}`);
  },
  
  // Get student's quizzes
  getStudentQuizzes: (studentId) => {
    return api.get(`/student/quizzes?student_id=${studentId}`);
  }
};

export default studentQuizAPI; 