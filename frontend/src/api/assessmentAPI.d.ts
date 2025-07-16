declare interface AssessmentParams {
  course_id?: number | string;
  is_published?: boolean;
  search?: string;
  page?: number;
  limit?: number;
}

declare interface SubmissionParams {
  page?: number;
  limit?: number;
  status?: string;
}

declare interface AssessmentData {
  id?: number;
  title: string;
  description: string;
  type: string;
  time_limit: number;
  max_attempts: number;
  start_date: string;
  due_date: string;
  is_published: boolean;
  questions: any[];
  course_id?: number | string;
  sections?: any[];
}

declare interface AIGenerationParams {
  course_name: string;
  course_description: string;
  assessment_type: string;
  difficulty: string;
  extra_info: string;
  course_id?: number | string;
}

declare interface GradeData {
  score: number;
  feedback: string;
  graded_by: string;
}

declare interface QuestionGradeData {
  question_index: number;
  question_data: any;
}

declare interface AxiosResponse {
  data: any;
  status: number;
  statusText: string;
  headers: any;
  config: any;
}

declare const assessmentAPI: {
  getAssessments: (params?: AssessmentParams) => Promise<any>;
  getAssessment: (assessmentId: number) => Promise<any>;
  createAssessment: (data: AssessmentData) => Promise<any>;
  updateAssessment: (assessmentId: number, data: AssessmentData) => Promise<any>;
  deleteAssessment: (assessmentId: number) => Promise<any>;
  submitAssessment: (assessmentId: number, data: any) => Promise<any>;
  getSubmissionsByAssessment: (assessmentId: number, params?: SubmissionParams) => Promise<any>;
  getSubmissionsByStudent: (studentId: number | string, params?: SubmissionParams) => Promise<any>;
  getSubmission: (submissionId: number) => Promise<any>;
  gradeSubmission: (submissionId: number, data: GradeData) => Promise<any>;
  getAssessmentStats: (assessmentId: number) => Promise<any>;
  getSubmissionCount: (assessmentId: number) => Promise<any>;
  getCourseAssessments: (courseId: number | string, params?: AssessmentParams) => Promise<any>;
  aiGradeQuestion: (submissionId: number, questionIndex: number, questionData: any) => Promise<any>;
  aiGradeAllSubjective: (submissionId: number, questionsData: QuestionGradeData[]) => Promise<any>;
  generateAssessmentWithAI: (params: AIGenerationParams) => Promise<any>;
};

export default assessmentAPI; 