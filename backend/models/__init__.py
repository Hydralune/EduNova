# Models package initialization 
# This file intentionally left empty to avoid circular imports 

from backend.extensions import db

# 导入所有模型以确保它们在创建表时被识别
from backend.models.user import User
from backend.models.course import Course
from backend.models.material import Material
from backend.models.learning import LearningRecord, ChatHistory
from backend.models.assessment import Assessment, StudentAnswer, AssessmentSubmission
from backend.models.config import Config
# 确保在Course之后导入依赖Course的模型
from backend.models.student_quiz import StudentAIQuiz 