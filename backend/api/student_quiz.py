from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
import os
from datetime import datetime
import threading
import time
import uuid
from backend.models.user import User
from backend.models.course import Course
from backend.models.student_quiz import StudentAIQuiz
from backend.extensions import db
from backend.api.learning import api_error_handler, generate_assessment_with_ai
from backend.api.rag_ai import get_api_config
import re
import openai
import difflib  # 用于计算文本相似度

# 计算文本相似度的函数
def calculate_similarity(text1, text2):
    """计算两个文本的相似度，返回0-1之间的值，1表示完全相同"""
    return difflib.SequenceMatcher(None, text1, text2).ratio()

student_quiz_bp = Blueprint('student_quiz', __name__)

@student_quiz_bp.route('/student/quizzes/ai-generate', methods=['POST'])
@api_error_handler
def generate_student_quiz():
    """Generate a quiz for a student using AI"""
    data = request.json
    if not data:
        return jsonify({'error': '无效的请求数据'}), 400
    
    # 获取学生ID (如果有JWT则从JWT获取，否则从请求中获取)
    try:
        student_id = get_jwt_identity()
    except:
        student_id = data.get('student_id')
        
    if not student_id:
        return jsonify({'error': '缺少学生ID'}), 400
    
    course_id = data.get('course_id')
    if not course_id:
        return jsonify({'error': '缺少课程ID'}), 400
    
    # 查找课程
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': '找不到指定的课程'}), 404
    
    # 创建测验记录
    quiz = StudentAIQuiz(
        student_id=student_id,
        course_id=course_id,
        title=f"AI自测 - {course.name}",
        description=f"基于{course.name}课程内容的自测测验",
        status="generating",
        config=json.dumps(data)
    )
    db.session.add(quiz)
    db.session.commit()
    
    # 启动后台线程生成测验
    app = current_app  # Use the current_app directly
    thread = threading.Thread(
        target=generate_quiz_in_background,
        args=(app, quiz.id, data, course)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'status': 'generating',
        'message': '测验生成中，请稍后查询结果',
        'quiz_id': quiz.id
    })

def generate_quiz_in_background(app, quiz_id, data, course):
    """在后台生成测验题目"""
    with app.app_context():
        try:
            # 获取测验记录
            quiz = StudentAIQuiz.query.get(quiz_id)
            if not quiz:
                app.logger.error(f"找不到测验记录: {quiz_id}")
                return
            
            # 获取配置
            difficulty = data.get('difficulty', 'medium')
            question_types = data.get('question_types', [])
            
            # 构建额外信息
            extra_info = f"请生成以下类型的题目: "
            for qt in question_types:
                extra_info += f"{qt['count']}道{get_question_type_text(qt['type'])}，"
            
            # 调用AI生成评估内容
            assessment_data = generate_assessment_with_ai(
                course_name=course.name,
                course_description=course.description or "",
                extra_info=extra_info,
                assessment_type="quiz",
                difficulty=difficulty
            )
            
            # 更新测验记录
            quiz.status = "in_progress"
            quiz.questions = json.dumps(assessment_data.get('sections', []))
            db.session.commit()
            
            app.logger.info(f"测验 {quiz_id} 生成完成")
            
        except Exception as e:
            app.logger.error(f"生成测验时出错: {str(e)}")
            import traceback
            app.logger.error(traceback.format_exc())
            
            # 更新测验状态为错误
            try:
                quiz = StudentAIQuiz.query.get(quiz_id)
                if quiz:
                    quiz.status = "error"
                    quiz.description = f"生成测验时出错: {str(e)}"
                    db.session.commit()
            except:
                pass

def generate_quiz_questions_incrementally(app, quiz_id, data, course):
    """逐题生成测验题目"""
    with app.app_context():
        try:
            # 获取测验记录
            quiz = StudentAIQuiz.query.get(quiz_id)
            if not quiz:
                app.logger.error(f"找不到测验记录: {quiz_id}")
                return
            
            # 获取配置
            difficulty = data.get('difficulty', 'medium')
            question_types = data.get('question_types', [])
            
            # 初始化问题列表
            questions = []
            
            # 设置测验状态为进行中
            quiz.status = "generating"
            db.session.commit()
            
            # 逐个生成每种类型的题目
            for qt in question_types:
                question_type = qt['type']
                count = qt['count']
                type_text = get_question_type_text(question_type)
                
                app.logger.info(f"开始生成 {count} 道{type_text}...")
                
                # 每次生成一道题
                for i in range(count):
                    try:
                        # 构建提示词，只生成一道题
                        prompt = f"""
                        请根据以下课程信息生成一道{type_text}：
                        
                        课程名称: {course.name}
                        课程描述: {course.description or ""}
                        难度级别: {difficulty}
                        
                        请按照以下JSON格式返回题目内容，确保格式正确：
                        {{
                          "type": "{question_type}",
                          "stem": "题干内容",
                          "score": 10,
                          "difficulty": "{difficulty}",
                        """
                        
                        # 根据题型添加特定字段
                        if question_type == "multiple_choice":
                            prompt += """
                          "options": ["A. 选项内容", "B. 选项内容", "C. 选项内容", "D. 选项内容"],
                          "answer": "C",
                          "explanation": "答案解析"
                            """
                        elif question_type == "fill_in_blank":
                            prompt += """
                          "answer": "正确答案",
                          "explanation": "答案解析"
                            """
                        elif question_type == "short_answer":
                            prompt += """
                          "reference_answer": "参考答案",
                          "explanation": "答案解析"
                            """
                        
                        prompt += """
                        }}
                        
                        请只返回JSON格式的题目内容，不要添加任何额外的解释或说明。
                        """
                        
                        # 调用AI API生成一道题
                        api_key, api_base, model_name = get_api_config()
                        
                        if not api_key:
                            app.logger.error("API密钥未配置")
                            continue
                        
                        # 设置API客户端
                        if api_base:
                            client = openai.OpenAI(api_key=api_key, base_url=api_base)
                        else:
                            client = openai.OpenAI(api_key=api_key)
                        
                        # 调用AI API
                        response = client.chat.completions.create(
                            model=model_name or "gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "你是一个专业的教育内容创建者，擅长根据课程信息生成高质量的测验题目。"},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7,
                            max_tokens=1000
                        )
                        
                        # 提取生成的内容
                        ai_response = response.choices[0].message.content
                        if ai_response:
                            ai_response = ai_response.strip()
                        else:
                            app.logger.error("AI响应为空")
                            continue
                        
                        # 解析JSON
                        try:
                            # 使用正则表达式找到JSON部分
                            json_match = re.search(r'({[\s\S]*})', ai_response)
                            if json_match:
                                json_str = json_match.group(1)
                                question_data = json.loads(json_str)
                            else:
                                question_data = json.loads(ai_response)
                            
                            # 添加题目ID
                            question_data["id"] = len(questions) + 1
                            
                            # 添加到题目列表
                            questions.append(question_data)
                            
                            # 更新测验记录
                            quiz.questions = json.dumps(questions)
                            db.session.commit()
                            
                            app.logger.info(f"已生成第 {len(questions)} 道题")
                            
                        except json.JSONDecodeError as e:
                            app.logger.error(f"JSON解析错误: {str(e)}")
                            continue
                        
                    except Exception as e:
                        app.logger.error(f"生成题目时出错: {str(e)}")
                        continue
            
            # 更新测验状态为进行中
            quiz.status = "in_progress"
            db.session.commit()
            
            app.logger.info(f"测验 {quiz_id} 生成完成，共 {len(questions)} 道题")
            
        except Exception as e:
            app.logger.error(f"生成测验时出错: {str(e)}")
            import traceback
            app.logger.error(traceback.format_exc())
            
            # 更新测验状态为错误
            try:
                quiz = StudentAIQuiz.query.get(quiz_id)
                if quiz:
                    quiz.status = "error"
                    quiz.description = f"生成测验时出错: {str(e)}"
                    db.session.commit()
            except:
                pass

@student_quiz_bp.route('/student/quizzes/ai-generate-incremental', methods=['POST'])
@api_error_handler
def generate_student_quiz_incremental():
    """逐题生成测验"""
    data = request.json
    if not data:
        return jsonify({'error': '无效的请求数据'}), 400
    
    # 获取学生ID (如果有JWT则从JWT获取，否则从请求中获取)
    try:
        student_id = get_jwt_identity()
    except:
        student_id = data.get('student_id')
        
    if not student_id:
        return jsonify({'error': '缺少学生ID'}), 400
    
    course_id = data.get('course_id')
    if not course_id:
        return jsonify({'error': '缺少课程ID'}), 400
    
    # 获取题目侧重点（如果有）
    focus_point = data.get('focus_point', '')
    
    # 查找课程
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': '找不到指定的课程'}), 404
    
    # 保存课程信息，而不是课程对象
    course_name = course.name
    course_description = course.description or ""
    
    # 创建测验记录
    quiz = StudentAIQuiz(
        student_id=student_id,
        course_id=course_id,
        title=f"AI自测 - {course_name} (逐题生成)",
        description=f"基于{course_name}课程内容的自测测验，逐题生成",
        status="generating",
        config=json.dumps(data)
    )
    db.session.add(quiz)
    db.session.commit()
    
    # 在当前请求上下文中直接生成第一道题目
    try:
        # 获取配置
        difficulty = data.get('difficulty', 'medium')
        question_types = data.get('question_types', [])
        
        # 如果有题型配置，尝试生成第一道题
        if question_types:
            first_type = question_types[0]
            question_type = first_type['type']
            type_text = get_question_type_text(question_type)
            
            # 构建提示词，只生成一道题
            prompt = f"""
            请根据以下课程信息生成一道{type_text}：
            
            课程名称: {course_name}
            课程描述: {course_description}
            难度级别: {difficulty}
            """
            
            # 如果有题目侧重点，添加到提示中
            focus_point = data.get('focus_point', '')
            if focus_point:
                prompt += f"""
            题目侧重点: {focus_point}
            """
            
            prompt += """
            请按照以下JSON格式返回题目内容，确保格式正确：
            {
              "type": "%s",
              "stem": "题干内容",
              "score": 10,
              "difficulty": "%s",
            """ % (question_type, difficulty)
            
            # 根据题型添加特定字段
            if question_type == "multiple_choice":
                # 随机选择一个答案选项（A, B, C, D）
                import random
                correct_option = random.choice(["A", "B", "C", "D"])
                
                prompt += f"""
              "options": ["A. 选项内容", "B. 选项内容", "C. 选项内容", "D. 选项内容"],
              "answer": "{correct_option}",
              "explanation": "答案解析"
                """
            elif question_type == "fill_in_blank":
                prompt += """
              "answer": "正确答案",
              "explanation": "答案解析"
                """
            elif question_type == "short_answer":
                prompt += """
              "reference_answer": "参考答案",
              "explanation": "答案解析"
                """
            
            prompt += """
            }}
            
            请只返回JSON格式的题目内容，不要添加任何额外的解释或说明。
            """
            
            # 调用AI API生成一道题
            api_key, api_base, model_name = get_api_config()
            
            if api_key:
                # 设置API客户端
                if api_base:
                    client = openai.OpenAI(api_key=api_key, base_url=api_base)
                else:
                    client = openai.OpenAI(api_key=api_key)
                
                # 调用AI API
                response = client.chat.completions.create(
                    model=model_name or "gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "你是一个专业的教育内容创建者，擅长根据课程信息生成高质量的测验题目。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                # 提取生成的内容
                ai_response = response.choices[0].message.content
                if ai_response:
                    ai_response = ai_response.strip()
                    
                    # 解析JSON
                    try:
                        # 使用正则表达式找到JSON部分
                        json_match = re.search(r'({[\s\S]*})', ai_response)
                        if json_match:
                            json_str = json_match.group(1)
                            question_data = json.loads(json_str)
                        else:
                            question_data = json.loads(ai_response)
                        
                        # 统一题目类型
                        original_type = question_data.get('type', '')
                        # 处理各种选择题类型
                        if original_type in ['single_choice', 'choice', 'mcq', 'multiple_choice_question', 'selection']:
                            question_data['type'] = 'multiple_choice'
                            current_app.logger.info(f"将{original_type}类型转换为multiple_choice")
                        # 处理各种填空题类型
                        elif original_type in ['fill_in_the_blank', 'fill_blank', 'blank_filling', 'completion']:
                            question_data['type'] = 'fill_in_blank'
                            current_app.logger.info(f"将{original_type}类型转换为fill_in_blank")
                        # 处理各种简答题类型
                        elif original_type in ['short_answer_question', 'brief_answer', 'open_question', 'essay']:
                            question_data['type'] = 'short_answer'
                            current_app.logger.info(f"将{original_type}类型转换为short_answer")
                        
                        # 添加题目ID
                        question_data["id"] = 1
                        
                        # 保存第一道题
                        quiz.questions = json.dumps([question_data])
                        db.session.commit()
                        
                        current_app.logger.info("已生成第1道题")
                    except json.JSONDecodeError as e:
                        current_app.logger.error(f"JSON解析错误: {str(e)}")
    except Exception as e:
        current_app.logger.error(f"生成第一道题时出错: {str(e)}")
    
    # 启动后台线程继续生成剩余题目
    # 使用 app.app_context() 创建一个新的应用上下文
    from backend.main import app as flask_app
    
    def continue_generation():
        with flask_app.app_context():
            try:
                # 获取测验记录和课程信息
                quiz_obj = StudentAIQuiz.query.get(quiz.id)
                if not quiz_obj:
                    current_app.logger.error(f"找不到测验记录: {quiz.id}")
                    return
                
                # 重新获取课程信息
                course_obj = Course.query.get(course_id)
                if not course_obj:
                    current_app.logger.error(f"找不到课程: {course_id}")
                    return
                
                course_name = course_obj.name
                course_description = course_obj.description or ""
                
                # 获取已生成的题目
                existing_questions = []
                if quiz_obj.questions:
                    try:
                        existing_questions = json.loads(quiz_obj.questions)
                    except:
                        existing_questions = []
                
                # 获取配置
                config = json.loads(quiz_obj.config) if quiz_obj.config else {}
                difficulty = config.get('difficulty', 'medium')
                question_types = config.get('question_types', [])
                
                # 跟踪已生成的题目数量
                question_count = len(existing_questions)
                
                # 逐个生成每种类型的题目
                for qt in question_types:
                    question_type = qt['type']
                    count = qt['count']
                    type_text = get_question_type_text(question_type)
                    
                    # 计算已生成的此类型题目数量
                    existing_type_count = sum(1 for q in existing_questions if q.get('type') == question_type)
                    
                    # 计算还需生成多少道此类型题目
                    remaining_count = max(0, count - existing_type_count)
                    
                    current_app.logger.info(f"开始生成 {remaining_count} 道{type_text}...")
                    
                    # 每次生成一道题
                    for i in range(remaining_count):
                        try:
                            # 构建提示词，只生成一道题
                            prompt = f"""
                            请根据以下课程信息生成一道{type_text}：
                            
                            课程名称: {course_name}
                            课程描述: {course_description}
                            难度级别: {difficulty}
                            """
                            
                            # 如果有题目侧重点，添加到提示中
                            focus_point = config.get('focus_point', '')
                            if focus_point:
                                prompt += f"""
                            题目侧重点: {focus_point}
                            """
                            
                            prompt += """
                            请按照以下JSON格式返回题目内容，确保格式正确：
                            {{
                              "type": "{question_type}",
                              "stem": "题干内容",
                              "score": 10,
                              "difficulty": "{difficulty}",
                            """
                            
                            # 根据题型添加特定字段
                            if question_type == "multiple_choice":
                                # 随机选择一个答案选项（A, B, C, D）
                                import random
                                correct_option = random.choice(["A", "B", "C", "D"])
                                
                                prompt += f"""
                              "options": ["A. 选项内容", "B. 选项内容", "C. 选项内容", "D. 选项内容"],
                              "answer": "{correct_option}",
                              "explanation": "答案解析"
                                """
                            elif question_type == "fill_in_blank":
                                prompt += """
                              "answer": "正确答案",
                              "explanation": "答案解析"
                                """
                            elif question_type == "short_answer":
                                prompt += """
                              "reference_answer": "参考答案",
                              "explanation": "答案解析"
                                """
                            
                            prompt += """
                            }}
                            
                            请只返回JSON格式的题目内容，不要添加任何额外的解释或说明。
                            """
                            
                            # 调用AI API生成一道题
                            api_key, api_base, model_name = get_api_config()
                            
                            if not api_key:
                                current_app.logger.error("API密钥未配置")
                                continue
                            
                            # 设置API客户端
                            if api_base:
                                client = openai.OpenAI(api_key=api_key, base_url=api_base)
                            else:
                                client = openai.OpenAI(api_key=api_key)
                            
                            # 调用AI API
                            response = client.chat.completions.create(
                                model=model_name or "gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": "你是一个专业的教育内容创建者，擅长根据课程信息生成高质量的测验题目。"},
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=0.7,
                                max_tokens=1000
                            )
                            
                            # 提取生成的内容
                            ai_response = response.choices[0].message.content
                            if ai_response:
                                ai_response = ai_response.strip()
                                
                                # 解析JSON
                                try:
                                    # 使用正则表达式找到JSON部分
                                    json_match = re.search(r'({[\s\S]*})', ai_response)
                                    if json_match:
                                        json_str = json_match.group(1)
                                        question_data = json.loads(json_str)
                                    else:
                                        question_data = json.loads(ai_response)
                                    
                                    # 统一题目类型
                                    original_type = question_data.get('type', '')
                                    # 处理各种选择题类型
                                    if original_type in ['single_choice', 'choice', 'mcq', 'multiple_choice_question', 'selection']:
                                        question_data['type'] = 'multiple_choice'
                                        current_app.logger.info(f"将{original_type}类型转换为multiple_choice")
                                    # 处理各种填空题类型
                                    elif original_type in ['fill_in_the_blank', 'fill_blank', 'blank_filling', 'completion']:
                                        question_data['type'] = 'fill_in_blank'
                                        current_app.logger.info(f"将{original_type}类型转换为fill_in_blank")
                                    # 处理各种简答题类型
                                    elif original_type in ['short_answer_question', 'brief_answer', 'open_question', 'essay']:
                                        question_data['type'] = 'short_answer'
                                        current_app.logger.info(f"将{original_type}类型转换为short_answer")
                                    
                                    # 更新题目ID
                                    question_count += 1
                                    question_data["id"] = question_count
                                    
                                    # 重新获取最新的题目列表
                                    quiz_obj = StudentAIQuiz.query.get(quiz.id)
                                    if quiz_obj and quiz_obj.questions:
                                        try:
                                            current_questions = json.loads(quiz_obj.questions)
                                        except:
                                            current_questions = []
                                    else:
                                        current_questions = []
                                    
                                    # 检查题目是否重复
                                    is_duplicate = False
                                    for existing_q in current_questions:
                                        # 比较题干相似度
                                        if question_data.get('stem') and existing_q.get('stem'):
                                            # 简单的相似度检查：如果两个题干有80%以上的相似度，认为是重复题目
                                            similarity = calculate_similarity(
                                                question_data.get('stem', ''), 
                                                existing_q.get('stem', '')
                                            )
                                            if similarity > 0.8:
                                                is_duplicate = True
                                                current_app.logger.info(f"检测到重复题目，相似度: {similarity}")
                                                break
                                    
                                    # 如果不是重复题目，添加到题目列表
                                    if not is_duplicate:
                                        # 添加新题目
                                        current_questions.append(question_data)
                                        
                                        # 更新测验记录
                                        quiz_obj.questions = json.dumps(current_questions)
                                        db.session.commit()
                                        
                                        current_app.logger.info(f"已生成第 {question_count} 道题")
                                    else:
                                        # 如果是重复题目，重试生成，但最多重试3次
                                        # 使用字典存储重试次数
                                        retry_counts = {}
                                        if hasattr(quiz_obj, 'retry_counts') and quiz_obj.retry_counts:
                                            try:
                                                retry_counts = json.loads(quiz_obj.retry_counts)
                                            except:
                                                retry_counts = {}
                                            
                                        retry_key = f"{question_type}_{i}"
                                        retry_count = retry_counts.get(retry_key, 0) + 1
                                        retry_counts[retry_key] = retry_count
                                        
                                        # 将字典转换为JSON字符串存储
                                        quiz_obj.retry_counts = json.dumps(retry_counts)
                                        db.session.commit()
                                        
                                        # 如果重试次数超过3次，就接受这个题目，避免无限循环
                                        if retry_count > 3:
                                            current_app.logger.info(f"重复题目重试已达3次，接受此题目")
                                            # 修改题干，添加标记以区分
                                            question_data["stem"] = f"[变题{retry_count}] {question_data['stem']}"
                                            current_questions.append(question_data)
                                            
                                            # 更新测验记录
                                            quiz_obj.questions = json.dumps(current_questions)
                                            db.session.commit()
                                            
                                            current_app.logger.info(f"已生成第 {question_count} 道题 (重复题目变形)")
                                        else:
                                            # 重试生成
                                            current_app.logger.info(f"检测到重复题目，重试生成 (第{retry_count}次)")
                                            i -= 1  # 重试当前索引
                                            continue
                                    
                                except json.JSONDecodeError as e:
                                    current_app.logger.error(f"JSON解析错误: {str(e)}")
                                    continue
                        except Exception as e:
                            current_app.logger.error(f"生成题目时出错: {str(e)}")
                            continue
                
                # 更新测验状态为进行中
                quiz_obj = StudentAIQuiz.query.get(quiz.id)
                if quiz_obj:
                    quiz_obj.status = "in_progress"
                    db.session.commit()
                
                current_app.logger.info(f"测验 {quiz.id} 生成完成，共 {question_count} 道题")
                
            except Exception as e:
                current_app.logger.error(f"生成测验时出错: {str(e)}")
                import traceback
                current_app.logger.error(traceback.format_exc())
                
                # 更新测验状态为错误
                try:
                    quiz_obj = StudentAIQuiz.query.get(quiz.id)
                    if quiz_obj:
                        quiz_obj.status = "error"
                        quiz_obj.description = f"生成测验时出错: {str(e)}"
                        db.session.commit()
                except:
                    pass
    
    # 启动后台线程
    thread = threading.Thread(target=continue_generation)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'status': 'generating',
        'message': '测验生成中，请稍后查询结果',
        'quiz_id': quiz.id
    })

@student_quiz_bp.route('/student/quizzes/<int:quiz_id>/status', methods=['GET'])
@api_error_handler
def get_quiz_status(quiz_id):
    """获取测验状态和可用的题目"""
    quiz = StudentAIQuiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'error': '找不到测验记录'}), 404
    
    # 转换为字典
    result = quiz.to_dict()
    
    # 即使状态是生成中，也返回已生成的题目内容
    if quiz.status == 'generating' and quiz.questions:
        try:
            result['questions'] = json.loads(quiz.questions)
            current_app.logger.info(f"返回已生成的 {len(result['questions'])} 道题目")
        except:
            result['questions'] = []
    
    return jsonify(result)

@student_quiz_bp.route('/student/quizzes/<int:quiz_id>/submit', methods=['POST'])
@api_error_handler
def submit_quiz_answers(quiz_id):
    """提交测验答案并评分"""
    data = request.json
    if not data:
        return jsonify({'error': '无效的请求数据'}), 400
    
    answers = data.get('answers')
    if not answers:
        return jsonify({'error': '缺少答案数据'}), 400
    
    # 获取测验记录
    quiz = StudentAIQuiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'error': '找不到测验记录'}), 404
    
    # 保存答案
    quiz.answers = json.dumps(answers)
    db.session.commit()
    
    # 从后端导入 Flask 应用实例
    from backend.main import app as flask_app
    
    # 启动后台线程评分
    def grade_quiz_in_background():
        with flask_app.app_context():
            try:
                # 获取测验记录
                quiz_obj = StudentAIQuiz.query.get(quiz_id)
                if not quiz_obj:
                    current_app.logger.error(f"找不到测验记录: {quiz_id}")
                    return
                
                # 解析题目和答案
                questions = json.loads(quiz_obj.questions) if quiz_obj.questions else []
                answers = json.loads(quiz_obj.answers) if quiz_obj.answers else []
                
                # 初始化分数和反馈
                question_scores = []
                question_feedback = []
                total_score = 0
                total_possible_score = 0
                
                # 评分逻辑
                for i, question in enumerate(questions):
                    student_answer = answers[i] if i < len(answers) else ""
                    correct_answer = question.get('answer', '')
                    max_score = question.get('score', 10)
                    total_possible_score += max_score
                    
                    # 根据题目类型评分
                    score = 0
                    feedback = ""
                    
                    if question.get('type') == 'multiple_choice':
                        # 选择题评分
                        if student_answer == correct_answer:
                            score = max_score
                            feedback = "回答正确"
                        else:
                            score = 0
                            feedback = f"回答错误，正确答案是: {correct_answer}"
                    
                    elif question.get('type') == 'fill_in_blank' or question.get('type') in ['fill_in_the_blank', 'fill_blank', 'blank_filling', 'completion']:
                        # 使用AI评分填空题，更加灵活
                        try:
                            # 获取AI配置
                            api_key, api_base, model_name = get_api_config()
                            
                            if not api_key:
                                current_app.logger.error("API密钥未配置，使用传统方式评分填空题")
                                # 传统评分方式
                                if isinstance(correct_answer, list):
                                    # 多个空的情况
                                    correct_count = 0
                                    for j, correct in enumerate(correct_answer):
                                        if j < len(student_answer) and student_answer[j].strip().lower() == correct.strip().lower():
                                            correct_count += 1
                                    
                                    score = (correct_count / len(correct_answer)) * max_score
                                    if correct_count == len(correct_answer):
                                        feedback = "所有空都填写正确"
                                    else:
                                        feedback = f"部分正确，正确答案是: {', '.join(correct_answer)}"
                                else:
                                    # 单个空的情况
                                    if student_answer.strip().lower() == correct_answer.strip().lower():
                                        score = max_score
                                        feedback = "回答正确"
                                    else:
                                        score = 0
                                        feedback = f"回答错误，正确答案是: {correct_answer}"
                            else:
                                # 设置API客户端
                                if api_base:
                                    client = openai.OpenAI(api_key=api_key, base_url=api_base)
                                else:
                                    client = openai.OpenAI(api_key=api_key)
                                
                                # 构建评分提示
                                prompt = f"""
                                请评分以下学生的填空题答案，满分为{max_score}分。请采用宽松的评分标准。
                                
                                问题: {question.get('stem', '')}
                                
                                正确答案: {correct_answer if isinstance(correct_answer, str) else ', '.join(correct_answer)}
                                
                                学生答案: {student_answer}
                                
                                评分指导:
                                1. 如果学生答案与正确答案完全一致，给予满分
                                2. 如果学生答案包含关键词或核心概念，即使表述不完全一致，也应给予至少70%的分数
                                3. 如果学生答案有拼写错误但明显是正确概念，给予80-90%的分数
                                4. 如果学生答案部分正确，给予相应比例的分数
                                5. 只有完全错误的答案才给予0分
                                
                                请使用以下JSON格式回复:
                                {{
                                  "score": 分数(0-{max_score}分，可精确到0.5分),
                                  "feedback": "简短评语(不超过20字)",
                                  "is_correct": true或false(是否基本正确)
                                }}
                                """
                                
                                # 调用AI API
                                response = client.chat.completions.create(
                                    model=model_name or "gpt-3.5-turbo",
                                    messages=[
                                        {"role": "system", "content": "你是一个专业的教育评分助手，擅长灵活评价填空题答案。"},
                                        {"role": "user", "content": prompt}
                                    ],
                                    temperature=0.3,
                                    max_tokens=300
                                )
                                
                                # 解析AI响应
                                ai_response = response.choices[0].message.content
                                if ai_response:
                                    ai_response = ai_response.strip()
                                else:
                                    ai_response = ""
                                
                                try:
                                    # 使用正则表达式找到JSON部分
                                    json_match = re.search(r'({[\s\S]*})', ai_response)
                                    if json_match:
                                        json_str = json_match.group(1)
                                        result = json.loads(json_str)
                                    else:
                                        result = json.loads(ai_response)
                                    
                                    # 提取分数和反馈
                                    score = float(result.get('score', max_score * 0.6))
                                    feedback = result.get('feedback', '')
                                    is_correct = result.get('is_correct', score >= max_score * 0.8)
                                    
                                    # 如果AI判断基本正确，确保分数至少达到80%
                                    if is_correct and score < max_score * 0.8:
                                        score = max_score * 0.8
                                        
                                except Exception as e:
                                    current_app.logger.error(f"解析AI填空题评分结果失败: {str(e)}")
                                    # 回退到传统评分
                                    if student_answer.strip().lower() == str(correct_answer).strip().lower():
                                        score = max_score
                                        feedback = "回答正确"
                                    else:
                                        # 给予部分分数，而不是直接0分
                                        score = max_score * 0.3
                                        feedback = f"回答部分正确，正确答案是: {correct_answer}"
                        except Exception as e:
                            current_app.logger.error(f"AI评分填空题出错: {str(e)}")
                            # 回退到简单评分
                            if student_answer.strip().lower() == str(correct_answer).strip().lower():
                                score = max_score
                                feedback = "回答正确"
                            else:
                                score = 0
                                feedback = f"回答错误，正确答案是: {correct_answer}"
                    
                    else:
                        # 简答题等主观题，调用AI评分
                        try:
                            # 获取AI配置
                            api_key, api_base, model_name = get_api_config()
                            
                            if not api_key:
                                current_app.logger.error("API密钥未配置，无法进行AI评分")
                                score = max_score * 0.6  # 默认给60%的分数
                                feedback = "无法进行AI评分，给予默认分数"
                            else:
                                # 设置API客户端
                                if api_base:
                                    client = openai.OpenAI(api_key=api_key, base_url=api_base)
                                else:
                                    client = openai.OpenAI(api_key=api_key)
                                
                                # 构建评分提示
                                reference_answer = question.get('reference_answer', '') or question.get('explanation', '')
                                
                                prompt = f"""
                                请评分以下学生对问题的回答，满分为{max_score}分。请采用相对宽松的评分标准，鼓励学生学习。

                                问题: {question.get('stem', '')}
                                
                                参考答案: {reference_answer}
                                
                                学生回答: {student_answer}
                                
                                评分指导:
                                1. 只要学生回答包含关键概念或要点，即使表述不完全一致，也应给予较高分数
                                2. 对于部分正确的答案，应至少给予60%的分数
                                3. 如果学生回答表现出对概念的理解，即使不完整，也应给予积极评价
                                4. 只有完全错误或无关的回答才应得到低分
                                5. 对于空白答案，给予0分
                                
                                请提供:
                                1. 分数 (0-{max_score}分，可精确到0.5分，请倾向于给予较高分数)
                                2. 简短评语 (不超过30字，以鼓励为主)
                                3. 改进建议 (不超过30字，具体指出可以如何提高)
                                
                                请使用以下JSON格式回复:
                                {{
                                  "score": 分数,
                                  "feedback": "评语",
                                  "suggestion": "改进建议"
                                }}
                                """
                                
                                # 调用AI API
                                response = client.chat.completions.create(
                                    model=model_name or "gpt-3.5-turbo",
                                    messages=[
                                        {"role": "system", "content": "你是一个专业的教育评分助手，擅长公平客观地评价学生回答。"},
                                        {"role": "user", "content": prompt}
                                    ],
                                    temperature=0.3,
                                    max_tokens=500
                                )
                                
                                # 解析AI响应
                                ai_response = response.choices[0].message.content
                                if ai_response:
                                    ai_response = ai_response.strip()
                                else:
                                    ai_response = ""
                                try:
                                    # 使用正则表达式找到JSON部分
                                    json_match = re.search(r'({[\s\S]*})', ai_response)
                                    if json_match:
                                        json_str = json_match.group(1)
                                        result = json.loads(json_str)
                                    else:
                                        result = json.loads(ai_response)
                                    
                                    # 提取分数和反馈
                                    score = float(result.get('score', max_score * 0.6))
                                    feedback = result.get('feedback', '')
                                    suggestion = result.get('suggestion', '')
                                    
                                    # 如果有学习建议，添加到反馈中
                                    if suggestion:
                                        feedback = f"{feedback}\n\n学习建议: {suggestion}"
                                    
                                except Exception as e:
                                    current_app.logger.error(f"解析AI评分结果失败: {str(e)}")
                                    score = max_score * 0.6  # 默认给60%的分数
                                    feedback = f"AI评分解析失败，给予默认分数。原始响应: {ai_response[:100]}..."
                        except Exception as e:
                            current_app.logger.error(f"AI评分出错: {str(e)}")
                            score = max_score * 0.6  # 默认给60%的分数
                            feedback = "AI评分过程中出错，给予默认分数"
                    
                    # 四舍五入到最接近的0.5
                    score = round(score * 2) / 2
                    total_score += score
                    
                    # 添加到结果
                    question_scores.append(score)
                    question_feedback.append(feedback)
                
                # 生成整体反馈
                percentage = (total_score / total_possible_score) * 100 if total_possible_score > 0 else 0
                
                # 基础反馈
                if percentage >= 90:
                    basic_feedback = "优秀！你对课程内容掌握得非常好。"
                elif percentage >= 70:
                    basic_feedback = "良好！你对大部分知识点有较好的理解，但仍有提升空间。"
                elif percentage >= 60:
                    basic_feedback = "及格！你对课程内容有基本的了解，但需要更多练习和复习。"
                else:
                    basic_feedback = "需要加强！建议重新学习课程的核心概念，并多做练习。"
                
                # 使用AI生成更个性化的学习建议
                try:
                    # 获取AI配置
                    api_key, api_base, model_name = get_api_config()
                    
                    if not api_key:
                        current_app.logger.error("API密钥未配置，无法生成个性化学习建议")
                        overall_feedback = basic_feedback
                    else:
                        # 设置API客户端
                        if api_base:
                            client = openai.OpenAI(api_key=api_key, base_url=api_base)
                        else:
                            client = openai.OpenAI(api_key=api_key)
                        
                        # 准备题目和答案的摘要
                        question_summary = []
                        for i, question in enumerate(questions):
                            student_answer = answers[i] if i < len(answers) else ""
                            correct_answer = question.get('answer', '') or question.get('reference_answer', '')
                            question_score = question_scores[i] if i < len(question_scores) else 0
                            
                            question_summary.append({
                                "题目": question.get('stem', '')[:100] + ("..." if len(question.get('stem', '')) > 100 else ""),
                                "类型": question.get('type', ''),
                                "学生答案": student_answer[:50] + ("..." if len(student_answer) > 50 else ""),
                                "正确答案": str(correct_answer)[:50] + ("..." if len(str(correct_answer)) > 50 else ""),
                                "得分": question_score,
                                "满分": question.get('score', 10)
                            })
                        
                        # 获取课程信息
                        course = Course.query.get(quiz_obj.course_id)
                        course_name = course.name if course else "未知课程"
                        course_description = course.description if course else ""
                        
                        # 构建提示
                        prompt = f"""
                        请根据以下学生的测验结果，生成个性化的学习建议。
                        
                        课程名称: {course_name}
                        课程描述: {course_description}
                        
                        测验总分: {total_score}/{total_possible_score} ({percentage:.1f}%)
                        
                        题目摘要:
                        {json.dumps(question_summary, ensure_ascii=False, indent=2)}
                        
                        请提供:
                        1. 对学生表现的整体评价 (1-2句)
                        2. 针对错误或低分题目的具体学习建议 (2-3点)
                        3. 进一步提高的学习方向 (1-2点)
                        
                        建议应当具体、实用、有针对性，总字数控制在200字以内。
                        """
                        
                        # 调用AI API
                        response = client.chat.completions.create(
                            model=model_name or "gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "你是一个专业的教育顾问，擅长根据学生的测验结果提供有针对性的学习建议。"},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7,
                            max_tokens=500
                        )
                        
                        # 提取AI生成的建议
                        ai_feedback = response.choices[0].message.content
                        if ai_feedback:
                            overall_feedback = ai_feedback.strip()
                        else:
                            overall_feedback = basic_feedback
                
                except Exception as e:
                    current_app.logger.error(f"生成个性化学习建议时出错: {str(e)}")
                    overall_feedback = basic_feedback
                
                # 更新测验记录 - 先保存评分结果
                quiz_obj.status = "graded"  # 使用中间状态"graded"表示评分已完成但建议尚未生成
                quiz_obj.completed_at = datetime.utcnow()
                quiz_obj.score = total_score
                quiz_obj.question_scores = json.dumps(question_scores)
                quiz_obj.question_feedback = json.dumps(question_feedback)
                
                db.session.commit()
                current_app.logger.info(f"测验 {quiz_id} 评分完成，开始生成学习建议")
                
                # 在单独的步骤中生成学习建议
                try:
                    # 生成学习建议
                    learning_advice = generate_learning_advice(quiz_obj, questions, answers, question_scores, question_feedback, total_score, total_possible_score)
                    
                    # 更新测验记录 - 添加学习建议
                    quiz_obj.feedback = learning_advice
                    quiz_obj.status = "completed"  # 最终状态为"completed"
                    db.session.commit()
                    current_app.logger.info(f"测验 {quiz_id} 学习建议生成完成")
                    
                except Exception as e:
                    current_app.logger.error(f"生成学习建议时出错: {str(e)}")
                    # 如果生成建议失败，仍然将状态更新为completed，但使用基本建议
                    percentage = (total_score / total_possible_score) * 100 if total_possible_score > 0 else 0
                    basic_feedback = get_basic_feedback(percentage)
                    quiz_obj.feedback = basic_feedback
                    quiz_obj.status = "completed"
                    db.session.commit()
                    current_app.logger.info(f"测验 {quiz_id} 使用基本学习建议完成")
                
            except Exception as e:
                current_app.logger.error(f"评分测验时出错: {str(e)}")
                import traceback
                current_app.logger.error(traceback.format_exc())
    
    # 启动后台线程
    thread = threading.Thread(target=grade_quiz_in_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'status': 'grading',
        'message': '测验评分中，请稍后查询结果'
    })

@student_quiz_bp.route('/student/quizzes/<int:quiz_id>/results', methods=['GET'])
@api_error_handler
def get_quiz_results(quiz_id):
    """获取测验结果"""
    quiz = StudentAIQuiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'error': '找不到测验记录'}), 404
    
    return jsonify(quiz.to_dict())

@student_quiz_bp.route('/student/quizzes/<int:quiz_id>', methods=['DELETE'])
@api_error_handler
def delete_quiz(quiz_id):
    """删除测验记录"""
    quiz = StudentAIQuiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'error': '找不到测验记录'}), 404
    
    db.session.delete(quiz)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '测验记录已删除'
    })

@student_quiz_bp.route('/student/quizzes', methods=['GET'])
@api_error_handler
def get_student_quizzes():
    """获取学生的测验记录列表"""
    # 获取学生ID (如果有JWT则从JWT获取，否则从请求参数中获取)
    try:
        student_id = get_jwt_identity()
    except:
        student_id = request.args.get('student_id')
        
    if not student_id:
        return jsonify({'error': '缺少学生ID'}), 400
    
    # 查询测验记录
    quizzes = StudentAIQuiz.query.filter_by(student_id=student_id).order_by(StudentAIQuiz.created_at.desc()).all()
    
    # 转换为字典列表
    result = [quiz.to_dict() for quiz in quizzes]
    
    return jsonify({
        'quizzes': result,
        'total': len(result)
    })

def get_basic_feedback(percentage):
    """根据得分百分比获取基础反馈"""
    if percentage >= 90:
        return "优秀！你对课程内容掌握得非常好。建议继续深入学习相关知识，拓展应用能力。"
    elif percentage >= 80:
        return "良好！你对大部分知识点有较好的理解。建议复习一下错题，巩固相关概念。"
    elif percentage >= 70:
        return "中等！你对主要知识点有基本理解，但部分细节需要加强。建议重点复习错题并多做练习。"
    elif percentage >= 60:
        return "及格！你对课程内容有基本了解，但需要更多练习和复习。建议系统性地重新学习薄弱环节。"
    else:
        return "需要加强！建议重新学习课程的核心概念，并多做练习。可以寻求老师的帮助，制定针对性的学习计划。"

def generate_learning_advice(quiz_obj, questions, answers, question_scores, question_feedback, total_score, total_possible_score):
    """生成个性化学习建议"""
    try:
        # 获取AI配置
        api_key, api_base, model_name = get_api_config()
        
        if not api_key:
            current_app.logger.error("API密钥未配置，无法生成个性化学习建议")
            percentage = (total_score / total_possible_score) * 100 if total_possible_score > 0 else 0
            return get_basic_feedback(percentage)
        
        # 设置API客户端
        if api_base:
            client = openai.OpenAI(api_key=api_key, base_url=api_base)
        else:
            client = openai.OpenAI(api_key=api_key)
        
        # 获取课程信息
        course = Course.query.get(quiz_obj.course_id)
        course_name = course.name if course else "未知课程"
        course_description = course.description if course else ""
        
        # 分析错题和薄弱环节
        wrong_questions = []
        weak_areas = {}
        
        for i, question in enumerate(questions):
            if i < len(question_scores):
                question_type = question.get('type', '')
                max_score = question.get('score', 10)
                score_percentage = (question_scores[i] / max_score) * 100 if max_score > 0 else 0
                
                # 如果得分低于70%，认为是薄弱环节
                if score_percentage < 70:
                    # 提取题目内容
                    question_content = {
                        "题目": question.get('stem', '')[:100],
                        "类型": get_question_type_text(question_type),
                        "得分率": f"{score_percentage:.1f}%",
                        "正确答案": question.get('answer', '') or question.get('reference_answer', ''),
                        "学生答案": answers[i] if i < len(answers) else "",
                        "评语": question_feedback[i] if i < len(question_feedback) else ""
                    }
                    wrong_questions.append(question_content)
                    
                    # 根据题目类型统计薄弱环节
                    type_text = get_question_type_text(question_type)
                    if type_text in weak_areas:
                        weak_areas[type_text] += 1
                    else:
                        weak_areas[type_text] = 1
        
        # 计算总体得分率
        percentage = (total_score / total_possible_score) * 100 if total_possible_score > 0 else 0
        
        # 构建提示
        prompt = f"""
        请根据以下学生的测验结果，生成详细的个性化学习建议。

        课程名称: {course_name}
        课程描述: {course_description}
        
        测验总分: {total_score}/{total_possible_score} ({percentage:.1f}%)
        
        错题分析:
        {json.dumps(wrong_questions, ensure_ascii=False, indent=2)}
        
        薄弱环节统计:
        {json.dumps(weak_areas, ensure_ascii=False, indent=2)}
        
        请提供以下三部分内容:
        1. 总体评价: 对学生整体表现的评价和鼓励 (2-3句)
        2. 具体建议: 针对错题和薄弱环节的具体学习建议 (3-4点)
        3. 学习资源: 推荐可以帮助学生提高的学习资源或方法 (2-3点)
        
        要求:
        - 建议应当具体、实用、有针对性
        - 语言友好、鼓励性，避免打击学生信心
        - 总字数控制在300字以内
        - 使用分段格式，每部分用标题标明
        - 如果没有错题，着重推荐进阶学习内容
        """
        
        # 调用AI API
        response = client.chat.completions.create(
            model=model_name or "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一个专业的教育顾问，擅长根据学生的测验结果提供有针对性的学习建议。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        # 提取AI生成的建议
        ai_feedback = response.choices[0].message.content
        if ai_feedback:
            return ai_feedback.strip()
        else:
            percentage = (total_score / total_possible_score) * 100 if total_possible_score > 0 else 0
            return get_basic_feedback(percentage)
    
    except Exception as e:
        current_app.logger.error(f"生成个性化学习建议时出错: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        percentage = (total_score / total_possible_score) * 100 if total_possible_score > 0 else 0
        return get_basic_feedback(percentage)

def get_question_type_text(type_code):
    """获取题目类型的中文名称"""
    type_map = {
        'multiple_choice': '选择题',
        'single_choice': '选择题',
        'choice': '选择题',
        'mcq': '选择题',
        'fill_in_blank': '填空题',
        'fill_in_the_blank': '填空题',
        'fill_blank': '填空题',
        'blank_filling': '填空题',
        'short_answer': '简答题',
        'short_answer_question': '简答题',
        'brief_answer': '简答题',
        'open_question': '简答题',
        'essay': '简答题'
    }
    return type_map.get(type_code, type_code)