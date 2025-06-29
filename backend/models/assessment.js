/**
 * Assessment JSON Schema
 * 
 * This file defines the JSON schema for assessment data structure
 * to be used across the application for storing and retrieving assessment data.
 */

const assessmentSchema = {
  // 基本评估信息
  assessment: {
    id: "string|number",           // 评估ID
    title: "string",               // 评估标题
    description: "string",         // 评估描述
    course_id: "string|number",    // 关联的课程ID
    type: "string",                // 评估类型: quiz, exam, homework, practice
    total_score: "number",         // 总分
    duration: "string",            // 时间限制，如 "30分钟"
    due_date: "string",            // 截止日期，ISO格式
    start_date: "string",          // 开始日期，ISO格式
    max_attempts: "number",        // 最大尝试次数，0表示无限制
    is_published: "boolean",       // 是否已发布
    is_active: "boolean",          // 是否激活
    created_at: "string",          // 创建时间，ISO格式
    updated_at: "string",          // 更新时间，ISO格式
    sections: ["section"]          // 评估部分列表
  },
  
  // 评估部分
  section: {
    type: "string",                // 部分类型: multiple_choice, multiple_select, fill_in_blank, true_false, short_answer, essay
    description: "string",         // 部分描述
    score_per_question: "number",  // 每题分值
    questions: ["question"]        // 题目列表
  },
  
  // 题目结构
  question: {
    id: "number",                  // 题目ID
    stem: "string",                // 题干
    type: "string",                // 题目类型: multiple_choice, multiple_select, fill_in_blank, true_false, short_answer, essay
    score: "number",               // 分值
    difficulty: "string",          // 难度: easy, medium, hard
    options: ["string"],           // 选项列表（选择题）
    answer: "string|[string]",     // 正确答案，可以是字符串或字符串数组
    explanation: "string",         // 解析
    reference_answer: "string",    // 参考答案（简答题、论述题）
    grading_criteria: "string",    // 评分标准（简答题、论述题）
    allow_attachment: "boolean",   // 是否允许附件（论述题）
    tags: ["string"]               // 标签列表，用于分类和筛选
  },
  
  // 学生答案结构
  studentAnswer: {
    student_id: "string|number",   // 学生ID
    assessment_id: "string|number",// 评估ID
    answers: ["answer"],           // 答案列表
    score: "number",               // 总分
    feedback: "string",            // 反馈
    submitted_at: "string",        // 提交时间，ISO格式
    graded_at: "string",           // 评分时间，ISO格式
    time_spent: "number",          // 花费时间（秒）
    attempt_number: "number"       // 尝试次数
  },
  
  // 答案结构
  answer: {
    question_id: "number",         // 题目ID
    value: "string|[string]|object", // 答案值，根据题目类型不同而不同
    score: "number",               // 得分
    feedback: "string",            // 反馈
    is_correct: "boolean",         // 是否正确
    files: ["file"]                // 附件列表（论述题）
  },
  
  // 文件结构
  file: {
    name: "string",                // 文件名
    url: "string",                 // 文件URL
    size: "number",                // 文件大小（字节）
    type: "string"                 // 文件类型
  }
};

/**
 * 评估JSON示例
 */
const assessmentExample = {
  "id": "exam001",
  "title": "期中考试",
  "description": "本次考试覆盖第1-5章内容",
  "course_id": "course123",
  "type": "exam",
  "total_score": 100,
  "duration": "120分钟",
  "due_date": "2025-07-15T23:59:59Z",
  "start_date": "2025-07-15T09:00:00Z",
  "max_attempts": 1,
  "is_published": true,
  "is_active": true,
  "created_at": "2025-06-01T10:00:00Z",
  "updated_at": "2025-06-01T10:00:00Z",
  "sections": [
    {
      "type": "multiple_choice",
      "description": "选择题：请在每小题给出的选项中选出一个正确答案。",
      "score_per_question": 4,
      "questions": [
        {
          "id": 1,
          "stem": "以下哪个是JavaScript的基本数据类型？",
          "type": "multiple_choice",
          "score": 4,
          "difficulty": "easy",
          "options": [
            "A. Array",
            "B. Object",
            "C. String",
            "D. RegExp"
          ],
          "answer": "C",
          "explanation": "JavaScript的基本数据类型包括String、Number、Boolean、Null、Undefined和Symbol。",
          "tags": ["javascript", "基础知识"]
        }
      ]
    },
    {
      "type": "multiple_select",
      "description": "多选题：请在每小题给出的选项中选出所有正确答案。",
      "score_per_question": 5,
      "questions": [
        {
          "id": 2,
          "stem": "以下哪些是JavaScript框架或库？",
          "type": "multiple_select",
          "score": 5,
          "difficulty": "medium",
          "options": [
            "A. React",
            "B. Python",
            "C. Vue",
            "D. Angular"
          ],
          "answer": ["A", "C", "D"],
          "explanation": "React、Vue和Angular都是JavaScript框架或库，而Python是一种编程语言。",
          "tags": ["javascript", "框架"]
        }
      ]
    },
    {
      "type": "fill_in_blank",
      "description": "填空题：请在横线上填写正确的内容。",
      "score_per_question": 4,
      "questions": [
        {
          "id": 3,
          "stem": "Vue.js中，用于创建组件的API是_____。",
          "type": "fill_in_blank",
          "score": 4,
          "difficulty": "medium",
          "answer": "defineComponent",
          "explanation": "在Vue.js中，defineComponent是用于创建组件的API。",
          "tags": ["vue", "组件"]
        },
        {
          "id": 4,
          "stem": "在Vue 3中，_____函数用于创建响应式对象，而_____函数用于创建响应式基本类型。",
          "type": "fill_in_blank",
          "score": 4,
          "difficulty": "hard",
          "answer": ["reactive", "ref"],
          "explanation": "在Vue 3中，reactive函数用于创建响应式对象，而ref函数用于创建响应式基本类型。",
          "tags": ["vue", "响应式"]
        }
      ]
    },
    {
      "type": "true_false",
      "description": "判断题：请判断以下说法是否正确。",
      "score_per_question": 3,
      "questions": [
        {
          "id": 5,
          "stem": "Vue.js是一个前端框架。",
          "type": "true_false",
          "score": 3,
          "difficulty": "easy",
          "answer": "true",
          "explanation": "Vue.js是一个用于构建用户界面的渐进式JavaScript框架。",
          "tags": ["vue", "基础知识"]
        }
      ]
    },
    {
      "type": "short_answer",
      "description": "简答题：请简要回答以下问题。",
      "score_per_question": 10,
      "questions": [
        {
          "id": 6,
          "stem": "简述Vue.js的生命周期钩子函数。",
          "type": "short_answer",
          "score": 10,
          "difficulty": "medium",
          "reference_answer": "Vue组件的生命周期钩子包括：创建阶段的beforeCreate和created，挂载阶段的beforeMount和mounted，更新阶段的beforeUpdate和updated，卸载阶段的beforeUnmount和unmounted等。",
          "grading_criteria": "根据是否能准确列出主要生命周期钩子并简要说明其作用进行评分。",
          "tags": ["vue", "生命周期"]
        }
      ]
    },
    {
      "type": "essay",
      "description": "论述题：请详细回答以下问题，并上传相关资料。",
      "score_per_question": 20,
      "questions": [
        {
          "id": 7,
          "stem": "分析Vue.js和React的异同，并结合实际项目经验谈谈你的选择偏好。",
          "type": "essay",
          "score": 20,
          "difficulty": "hard",
          "reference_answer": "Vue和React都是流行的前端框架，它们有许多相似之处，如组件化架构、虚拟DOM等。不同之处在于Vue使用模板语法和选项式API，而React使用JSX和函数式组件...",
          "grading_criteria": "根据是否能准确分析两者的异同点、是否结合实际项目经验、论述是否条理清晰进行评分。",
          "allow_attachment": true,
          "tags": ["vue", "react", "比较"]
        }
      ]
    }
  ]
};

/**
 * 学生答案JSON示例
 */
const studentAnswerExample = {
  "student_id": "student123",
  "assessment_id": "exam001",
  "answers": [
    {
      "question_id": 1,
      "value": "C",
      "score": 4,
      "is_correct": true,
      "feedback": "回答正确"
    },
    {
      "question_id": 2,
      "value": ["A", "C", "D"],
      "score": 5,
      "is_correct": true,
      "feedback": "回答正确"
    },
    {
      "question_id": 3,
      "value": "defineComponent",
      "score": 4,
      "is_correct": true,
      "feedback": "回答正确"
    },
    {
      "question_id": 4,
      "value": ["reactive", "ref"],
      "score": 4,
      "is_correct": true,
      "feedback": "回答正确"
    },
    {
      "question_id": 5,
      "value": "true",
      "score": 3,
      "is_correct": true,
      "feedback": "回答正确"
    },
    {
      "question_id": 6,
      "value": "Vue组件的生命周期钩子包括：创建阶段的beforeCreate和created，挂载阶段的beforeMount和mounted，更新阶段的beforeUpdate和updated，卸载阶段的beforeUnmount和unmounted等。",
      "score": 9,
      "is_correct": true,
      "feedback": "回答基本正确，但缺少对各个钩子函数作用的详细说明。"
    },
    {
      "question_id": 7,
      "value": {
        "text": "Vue和React都是流行的前端框架，它们有许多相似之处，如组件化架构、虚拟DOM等...",
        "files": [
          {
            "name": "vue_react_comparison.pdf",
            "url": "/uploads/student123/vue_react_comparison.pdf",
            "size": 1024000,
            "type": "application/pdf"
          }
        ]
      },
      "score": 18,
      "is_correct": true,
      "feedback": "分析全面，结合了实际项目经验，论述条理清晰。"
    }
  ],
  "score": 47,
  "feedback": "整体表现良好，对Vue.js的理解较为深入。",
  "submitted_at": "2025-07-15T11:30:00Z",
  "graded_at": "2025-07-16T10:15:00Z",
  "time_spent": 5400,
  "attempt_number": 1
};

module.exports = {
  assessmentSchema,
  assessmentExample,
  studentAnswerExample
}; 