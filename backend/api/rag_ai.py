from flask import Blueprint, request, jsonify, current_app, Response, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import time
import requests
import json
from dotenv import load_dotenv
from backend.models.learning import ChatHistory
from backend.extensions import db

# 加载环境变量
load_dotenv()  # 首先尝试加载backend/.env
rag_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'RAG', '.env')
if os.path.exists(rag_env_path):
    load_dotenv(rag_env_path)  # 如果存在，加载RAG/.env

# 尝试获取API密钥，优先使用LLM配置，如果不存在则使用DEEPSEEK配置
def get_api_config():
    api_key = os.getenv("LLM_API_KEY")
    api_base = os.getenv("LLM_API_BASE")
    model_name = os.getenv("LLM_MODEL")
    
    # 如果LLM配置不存在，尝试使用DEEPSEEK配置
    if not api_key:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        api_base = os.getenv("DEEPSEEK_API_BASE")
        model_name = os.getenv("DEEPSEEK_MODEL")
    
    return api_key, api_base, model_name

rag_ai_bp = Blueprint('rag_ai', __name__)

@rag_ai_bp.route('/status', methods=['GET'])
def get_module_status_api():
    """获取RAG和AI模块状态"""
    api_key, api_base, _ = get_api_config()
    
    return jsonify({
        'status': 'success',
        'rag_enabled': False,  # 暂时不启用RAG
        'ai_enabled': bool(api_key and api_base),
        'message': '模块状态获取成功'
    })

@rag_ai_bp.route('/chat', methods=['GET', 'POST'])
@jwt_required()
def chat_with_ai():
    """与AI聊天（不使用RAG）"""
    # 根据请求方法获取数据
    if request.method == 'POST':
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': '无效的请求数据'}), 400
    else:  # GET请求
        data = request.args
    
    user_id = get_jwt_identity()
    message = data.get('message')
    course_id = data.get('course_id')  # 可选参数
    conversation_id = data.get('conversation_id')  # 可选参数
    stream = data.get('stream', False)  # 是否使用流式输出，默认为False
    
    # 对于GET请求，将stream参数转换为布尔值
    if request.method == 'GET' and stream == 'true':
        stream = True
    
    if not message:
        return jsonify({'status': 'error', 'message': '消息不能为空'}), 400
    
    try:
        # 获取API密钥和基础URL
        api_key, api_base, model_name = get_api_config()
        
        if not api_key or not api_base:
            return jsonify({
                'status': 'error',
                'message': 'API密钥或基础URL未配置'
            }), 500
        
        if not model_name:
            model_name = "deepseek-chat"  # 默认模型
        
        # 获取历史对话记录
        history = []
        if conversation_id:
            chat_history = ChatHistory.query.filter_by(
                conversation_id=conversation_id,
                user_id=user_id
            ).order_by(ChatHistory.timestamp.asc()).all()
            
            for chat in chat_history:
                if chat.role == 'user':
                    history.append({"role": "user", "content": chat.message})
                else:
                    history.append({"role": "assistant", "content": chat.message})
        
        # 添加当前消息
        history.append({"role": "user", "content": message})
        
        # 直接使用requests调用API，而不是使用OpenAI客户端
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "你是一个智能教育助手，名为EduNova。你的任务是帮助学生解答问题、提供学习建议和解释复杂概念。请保持回答友好、专业且易于理解。"},
                *history
            ],
            "temperature": 0.7,
            "max_tokens": 800,
            "stream": stream  # 是否使用流式输出
        }
        
        # 生成或使用现有的对话ID
        if not conversation_id:
            conversation_id = f"conv_{user_id}_{int(time.time())}"
        
        # 保存用户消息到数据库
        user_chat = ChatHistory(
            user_id=user_id,
            course_id=course_id,  # 可能为None
            conversation_id=conversation_id,
            role='user',
            message=message,
            timestamp=int(time.time())
        )
        db.session.add(user_chat)
        db.session.commit()
        
        # 如果请求流式输出
        if stream:
            def generate():
                # 流式请求
                with requests.post(
                    f"{api_base}/chat/completions", 
                    headers=headers, 
                    json=payload,
                    stream=True,
                    timeout=60
                ) as response:
                    
                    if response.status_code != 200:
                        yield f"data: {json.dumps({'status': 'error', 'message': f'API调用失败: {response.text}'})}\n\n"
                        return
                    
                    # 初始化变量，用于收集完整的回复
                    full_response = ""
                    
                    # 处理流式响应
                    for line in response.iter_lines():
                        if line:
                            line_text = line.decode('utf-8')
                            if line_text.startswith('data: '):
                                line_json = line_text[6:]  # 移除 'data: ' 前缀
                                if line_json.strip() == '[DONE]':
                                    break
                                
                                try:
                                    chunk = json.loads(line_json)
                                    if 'choices' in chunk and len(chunk['choices']) > 0:
                                        if 'delta' in chunk['choices'][0] and 'content' in chunk['choices'][0]['delta']:
                                            content = chunk['choices'][0]['delta']['content']
                                            if content:
                                                full_response += content
                                                # 发送数据到客户端
                                                yield f"data: {json.dumps({'content': content})}\n\n"
                                except json.JSONDecodeError:
                                    continue
                
                # 流式响应结束后，保存完整回复到数据库
                ai_response = full_response.lstrip()
                ai_chat = ChatHistory(
                    user_id=user_id,
                    course_id=course_id,
                    conversation_id=conversation_id,
                    role='assistant',
                    message=ai_response,
                    timestamp=int(time.time())
                )
                db.session.add(ai_chat)
                db.session.commit()
                
                # 发送结束信号
                yield f"data: {json.dumps({'status': 'done', 'conversation_id': conversation_id})}\n\n"
            
            return Response(stream_with_context(generate()), content_type='text/event-stream')
        
        # 非流式请求
        else:
            # 发送请求
            response = requests.post(
                f"{api_base}/chat/completions", 
                headers=headers, 
                json=payload,
                timeout=60  # 设置超时时间
            )
            
            # 检查响应
            if response.status_code != 200:
                return jsonify({
                    'status': 'error',
                    'message': f'API调用失败: {response.text}'
                }), 500
                
            # 解析响应
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            # 去除开头的空行
            ai_response = ai_response.lstrip()
            
            # 保存AI回复到数据库
            ai_chat = ChatHistory(
                user_id=user_id,
                course_id=course_id,  # 可能为None
                conversation_id=conversation_id,
                role='assistant',
                message=ai_response,
                timestamp=int(time.time())
            )
            db.session.add(ai_chat)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'response': {
                    'content': ai_response,
                    'sources': [],  # 不使用RAG，所以没有引用来源
                    'conversation_id': conversation_id
                }
            })
        
    except Exception as e:
        current_app.logger.error(f"AI chat error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'处理请求时出错: {str(e)}'
        }), 500

@rag_ai_bp.route('/history', methods=['GET'])
@jwt_required()
def get_chat_history():
    """获取聊天历史"""
    user_id = get_jwt_identity()
    conversation_id = request.args.get('conversation_id')
    
    if not conversation_id:
        return jsonify({'status': 'error', 'message': '对话ID不能为空'}), 400
    
    try:
        # 获取历史对话记录
        chat_history = ChatHistory.query.filter_by(
            conversation_id=conversation_id,
            user_id=user_id
        ).order_by(ChatHistory.timestamp.asc()).all()
        
        # 格式化历史记录
        history = []
        for chat in chat_history:
            history.append({
                'role': chat.role,
                'content': chat.message,
                'timestamp': chat.timestamp
            })
        
        return jsonify({
            'status': 'success',
            'history': history
        })
        
    except Exception as e:
        current_app.logger.error(f"Get chat history error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取聊天历史失败: {str(e)}'
        }), 500

@rag_ai_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """获取用户的所有对话"""
    user_id = get_jwt_identity()
    course_id = request.args.get('course_id')
    
    try:
        # 构建查询
        query = db.session.query(
            ChatHistory.conversation_id,
            db.func.min(ChatHistory.timestamp).label('start_time'),
            db.func.max(ChatHistory.timestamp).label('last_time')
        ).filter(ChatHistory.user_id == user_id)
        
        # 如果指定了课程ID，则过滤
        if course_id:
            query = query.filter(ChatHistory.course_id == course_id)
        
        # 按对话ID分组并按最后时间排序
        conversations = query.group_by(
            ChatHistory.conversation_id
        ).order_by(db.desc('last_time')).all()
        
        # 获取每个对话的第一条消息作为标题
        result = []
        for conv_id, start_time, last_time in conversations:
            # 获取第一条用户消息作为标题
            first_message = ChatHistory.query.filter_by(
                conversation_id=conv_id,
                role='user'
            ).order_by(ChatHistory.timestamp.asc()).first()
            
            # 获取消息数量
            message_count = ChatHistory.query.filter_by(
                conversation_id=conv_id
            ).count()
            
            result.append({
                'conversation_id': conv_id,
                'title': first_message.message[:30] + '...' if len(first_message.message) > 30 else first_message.message,
                'start_time': start_time,
                'last_time': last_time,
                'message_count': message_count
            })
        
        return jsonify({
            'status': 'success',
            'conversations': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Get conversations error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取对话列表失败: {str(e)}'
        }), 500

@rag_ai_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_learning_recommendations():
    """获取学习建议"""
    user_id = get_jwt_identity()
    course_id = request.args.get('course_id')
    
    try:
        # 如果有课程ID，返回特定课程的建议
        if course_id:
            recommendations = [
                {
                    'title': '复习关键概念',
                    'description': '根据你的学习进度，建议你复习本课程的关键概念。',
                    'link': f'/course/{course_id}/materials'
                },
                {
                    'title': '完成练习',
                    'description': '你已经学习了理论知识，现在可以通过练习来巩固这些知识。',
                    'link': f'/course/{course_id}/assessments'
                },
                {
                    'title': '参加讨论',
                    'description': '参与课程讨论可以帮助你更好地理解课程内容。',
                    'link': f'/course/{course_id}/discussions'
                }
            ]
        # 如果没有课程ID，返回通用建议
        else:
            recommendations = [
                {
                    'title': '探索课程',
                    'description': '浏览可用的课程，找到你感兴趣的主题。',
                    'link': '/courses'
                },
                {
                    'title': '制定学习计划',
                    'description': '规划你的学习路径，设定明确的学习目标。',
                    'link': '/dashboard'
                },
                {
                    'title': '查看学习资源',
                    'description': '探索平台提供的各种学习资源。',
                    'link': '/resources'
                }
            ]
        
        return jsonify({
            'status': 'success',
            'recommendations': recommendations
        })
        
    except Exception as e:
        current_app.logger.error(f"AI recommendations error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'处理请求时出错: {str(e)}'
        }), 500