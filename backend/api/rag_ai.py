from flask import Blueprint, request, jsonify, current_app, Response, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import time
import requests
import json
import sys
import logging
from dotenv import load_dotenv
from backend.models.learning import ChatHistory, KnowledgeBaseQueue
from backend.extensions import db
from backend.models.course import Course

# 禁用 ChromaDB telemetry 以防止崩溃
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

# 设置日志记录
logger = logging.getLogger(__name__)

# 定义全局变量
RAG_AVAILABLE = False
hybrid_retriever = None
format_docs = None

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

rag_api = Blueprint('rag_api', __name__)

def initialize_rag():
    """在应用上下文中初始化RAG模块"""
    global RAG_AVAILABLE, hybrid_retriever, format_docs
    
    try:
        # 检查路径
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 检查可能的知识库路径
        possible_paths = [
            os.path.join(project_root, "uploads", "knowledge_base"),
            os.path.join(project_root, "backend", "uploads", "knowledge_base")
        ]
        
        vectordb_path = None
        for path in possible_paths:
            if os.path.exists(path):
                vectordb_path = path
                logger.info(f"找到知识库路径: {path}")
                
                # 检查向量数据库
                vdb_path = os.path.join(path, "vectordb")
                if os.path.exists(vdb_path):
                    logger.info(f"找到向量数据库: {vdb_path}")
                    vectordb_path = vdb_path
                    break
        
        if not vectordb_path:
            logger.warning("无法找到有效的知识库路径")
        
        # 导入RAG模块
        try:
            from backend.rag.rag_query import hybrid_retriever, format_docs
            RAG_AVAILABLE = True
            logger.info("RAG模块已成功导入")
            return True
        except ImportError as e:
            logger.error(f"无法导入RAG模块: {str(e)}")
            
            # 尝试从其他可能的路径导入
            try:
                import sys
                sys.path.append(project_root)
                from backend.rag.rag_query import hybrid_retriever, format_docs
                RAG_AVAILABLE = True
                logger.info("通过调整路径成功导入RAG模块")
                return True
            except ImportError as e2:
                logger.error(f"尝试调整路径后仍无法导入RAG模块: {str(e2)}")
                RAG_AVAILABLE = False
                return False
    except Exception as e:
        logger.error(f"初始化RAG模块时出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        RAG_AVAILABLE = False
        return False

@rag_api.route('/status', methods=['GET'])
def get_module_status_api():
    """获取RAG和AI模块状态"""
    global RAG_AVAILABLE
    
    # 尝试初始化RAG模块
    if not RAG_AVAILABLE:
        initialize_rag()
    
    api_key, api_base, _ = get_api_config()
    
    # 检查RAG模块是否可用
    rag_status = "可用" if RAG_AVAILABLE else "不可用"
    logger.info(f"RAG模块状态: {rag_status}")
    
    # 检查AI API是否配置
    ai_status = "可用" if (api_key and api_base) else "未配置"
    logger.info(f"AI API状态: {ai_status}")
    
    return jsonify({
        'status': 'success',
        'rag_enabled': RAG_AVAILABLE,  # 根据是否成功导入RAG模块来确定
        'ai_enabled': bool(api_key and api_base),
        'message': '模块状态获取成功'
    })

@rag_api.route('/chat', methods=['GET', 'POST'])
@jwt_required()
def chat_with_ai():
    """与AI聊天（支持RAG增强）"""
    global RAG_AVAILABLE
    
    # 在应用上下文中尝试初始化RAG模块
    if not RAG_AVAILABLE:
        initialize_rag()
    
    # 在应用上下文中记录日志
    app_logger = current_app.logger
    
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
    use_rag = data.get('use_rag', True)  # 是否使用RAG，默认为True
    
    # 对于GET请求，将stream和use_rag参数转换为布尔值
    if request.method == 'GET':
        if stream == 'true':
            stream = True
        if use_rag == 'false':
            use_rag = False
    
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
        
        # 准备API请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # 判断是否使用RAG
        retrieved_docs = []
        context = ""
        sources = []
        
        if use_rag and course_id:
            # 确保RAG模块已初始化
            if not RAG_AVAILABLE:
                initialize_rag()
            
            if RAG_AVAILABLE:
                try:
                    # 获取课程信息
                    course = Course.query.get(course_id)
                    course_info = ""
                    
                    if course:
                        course_info = f"""
                                    课程名称: {course.name}
                                    课程简介: {course.description or '无简介'}
                                    课程类别: {course.category or '未分类'}
                                    难度级别: {course.difficulty or '未指定'}
                                    课程时长: {course.duration or 0} 小时
                                    """
                        app_logger.info(f"获取到课程信息: {course.name}")
                    else:
                        app_logger.warning(f"未找到课程信息，课程ID: {course_id}")
                    
                    # 使用RAG检索相关文档
                    app_logger.info(f"使用RAG检索，课程ID: {course_id}")
                    retrieved_docs = hybrid_retriever(message, str(course_id))
                    
                    # 格式化检索到的文档
                    if retrieved_docs:
                        context = format_docs(retrieved_docs)
                        
                        # 提取文档源信息
                        for doc in retrieved_docs:
                            if 'source' in doc.metadata and doc.metadata['source'] not in [s.get('url') for s in sources]:
                                sources.append({
                                    'title': doc.metadata.get('title', os.path.basename(doc.metadata['source'])),
                                    'url': doc.metadata['source']
                                })
                    
                    # 构建带有上下文的系统提示
                    system_prompt = f"""你是一个智能教育助手，名为EduNova。你的任务是帮助学生解答问题、提供学习建议和解释复杂概念。
你正在辅助以下课程的学习：
{course_info}

请基于以下参考资料回答用户的问题。如果参考资料中信息有限或没有相关信息，请：

1. 明确指出参考资料中的局限性，但不要仅仅停留在"无法找到信息"
2. 根据课程名称、简介和类别，利用你自身的专业知识推断可能的课程内容
3. 为该课程主题生成一个合理、结构化的大纲或内容框架
4. 提供与课程主题相关的核心概念解释和实际例子
5. 推荐学习资源、练习方法或项目创意
6. 如果是编程类课程，提供代码示例；如果是理论课程，提供概念框架

你的目标是即使在参考资料有限的情况下，也能为学生提供最大价值的回答。请保持回答友好、专业且易于理解。

参考资料:
{context}"""
                    
                    # 准备API请求体
                    payload = {
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            *history[-5:]  # 只使用最近5条对话历史，避免token过多
                        ],
                        "temperature": 0.7,
                        "max_tokens": 4000,
                        "stream": stream
                    }
                    
                    app_logger.info("成功构建RAG增强的请求")
                except Exception as e:
                    app_logger.error(f"RAG检索失败: {str(e)}")
                    # 如果RAG检索失败，回退到普通对话
                    use_rag = False
            else:
                app_logger.warning("RAG模块不可用，回退到普通对话")
                use_rag = False
        
        # 如果不使用RAG或RAG检索失败
        if not use_rag or not RAG_AVAILABLE or not course_id:
            # 准备普通对话的API请求体
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": """你是一个智能教育助手，名为EduNova。你的任务是帮助学生解答问题、提供学习建议和解释复杂概念。

当回答问题时，请遵循以下指导：
1. 提供详细且准确的解释，包括相关概念和原理
2. 使用实际例子来说明抽象概念
3. 如果被问到课程内容，尝试生成可能的课程大纲或内容结构
4. 提供学习建议和额外的资源推荐
5. 鼓励批判性思考和实践应用

请保持回答友好、专业且易于理解。如果你不确定某个问题的答案，请坦诚说明，并提供相关的替代信息或建议。"""},
                    *history
                ],
                "temperature": 0.7,
                "max_tokens": 4000,
                "stream": stream
            }
        
        # 如果请求流式输出
        if stream:
            def generate():
                # 流式请求
                with requests.post(
                    f"{api_base}/chat/completions",  # 直接使用API基础URL，不添加额外路径前缀
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=120  # 增加超时时间到120秒
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
                
                # 发送结束信号，包含引用源
                yield f"data: {json.dumps({'status': 'done', 'conversation_id': conversation_id, 'sources': sources})}\n\n"
            
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
                    'sources': sources,  # 包含引用来源
                    'conversation_id': conversation_id
                }
            })
        
    except Exception as e:
        app_logger.error(f"AI chat error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'处理请求时出错: {str(e)}'
        }), 500

@rag_api.route('/history', methods=['GET'])
@jwt_required()
def get_chat_history():
    """获取聊天历史"""
    app_logger = current_app.logger
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
        app_logger.error(f"Get chat history error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取聊天历史失败: {str(e)}'
        }), 500

@rag_api.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """获取用户的所有对话"""
    app_logger = current_app.logger
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
            
            # 处理标题，如果first_message为None，使用默认标题
            title = '新对话'
            if first_message and first_message.message:
                title = first_message.message[:30] + '...' if len(first_message.message) > 30 else first_message.message
            
            result.append({
                'conversation_id': conv_id,
                'title': title,
                'start_time': start_time,
                'last_time': last_time,
                'message_count': message_count
            })
        
        return jsonify({
            'status': 'success',
            'conversations': result
        })
        
    except Exception as e:
        app_logger.error(f"Get conversations error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取对话列表失败: {str(e)}'
        }), 500

@rag_api.route('/recommendations', methods=['GET'])
@jwt_required()
def get_learning_recommendations():
    """获取学习建议"""
    app_logger = current_app.logger
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
        app_logger.error(f"AI recommendations error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'处理请求时出错: {str(e)}'
        }), 500

@rag_api.route('/knowledge/add', methods=['POST'])
def add_to_knowledge_base():
    """Add a file to the knowledge base processing queue"""
    # 本地导入以避免循环导入
    from backend.tasks.rag_processor import start_processing_queue_item
    
    data = request.json
    course_id = data.get('course_id')
    file_path = data.get('file_path')
    
    if not course_id or not file_path:
        return jsonify({'status': 'error', 'message': '参数不完整'}), 400
    
    # Validate file exists
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_path.lstrip('/'))
    if not os.path.exists(full_path):
        return jsonify({'status': 'error', 'message': '文件不存在'}), 404
    
    # Check if file is already in queue or processed
    existing_queue = KnowledgeBaseQueue.query.filter_by(
        course_id=course_id,
        file_path=file_path
    ).first()
    
    if existing_queue:
        # If it's completed, we can reprocess it
        if existing_queue.status == 'completed':
            existing_queue.status = 'pending'
            existing_queue.progress = 0.0
            existing_queue.error_message = None
            existing_queue.completed_at = None
            db.session.commit()
            
            # Start processing in background
            start_processing_queue_item(existing_queue.id)
            
            return jsonify({
                'status': 'success',
                'message': '文件已重新添加到知识库处理队列',
                'queue_id': existing_queue.id
            })
        # If it's pending or processing, return error
        elif existing_queue.status in ['pending', 'processing']:
            return jsonify({
                'status': 'error',
                'message': '文件已在处理队列中',
                'queue_id': existing_queue.id,
                'progress': existing_queue.progress
            }), 409
    
    # Add to queue
    queue_item = KnowledgeBaseQueue(
        course_id=course_id,
        file_path=file_path
    )
    db.session.add(queue_item)
    db.session.commit()
    
    # Start processing in background
    start_processing_queue_item(queue_item.id)
    
    return jsonify({
        'status': 'success',
        'message': '文件已添加到知识库处理队列',
        'queue_id': queue_item.id
    })

@rag_api.route('/knowledge/status', methods=['GET'])
def get_knowledge_base_status():
    """Get the status of the knowledge base processing queue"""
    course_id = request.args.get('course_id')
    
    if not course_id:
        return jsonify({'status': 'error', 'message': '参数不完整'}), 400
    
    # Get all queue items for the course
    queue_items = KnowledgeBaseQueue.query.filter_by(course_id=course_id).all()
    
    result = []
    for item in queue_items:
        result.append(item.to_dict())
    
    return jsonify({
        'status': 'success',
        'items': result
    })

@rag_api.route('/knowledge/supported-types', methods=['GET'])
def get_supported_file_types():
    """Get the list of file types supported for knowledge base processing"""
    supported_types = [
        {'extension': '.pdf', 'description': 'PDF文档'},
        {'extension': '.docx', 'description': 'Word文档'},
        {'extension': '.doc', 'description': 'Word文档'},
        {'extension': '.txt', 'description': '文本文件'},
        {'extension': '.md', 'description': 'Markdown文件'},
    ]
    
    return jsonify({
        'status': 'success',
        'supported_types': supported_types
    })

@rag_api.route('/knowledge/process_now', methods=['POST'])
def process_knowledge_now():
    """立即处理文件并添加到知识库，不使用队列"""
    try:
        data = request.json
        course_id = data.get('course_id')
        file_path = data.get('file_path')
        
        if not course_id or not file_path:
            return jsonify({'status': 'error', 'message': '缺少必要参数'}), 400
        
        # 确保文件存在
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_path)
        if not os.path.exists(full_path):
            return jsonify({'status': 'error', 'message': f'文件不存在: {file_path}'}), 404
        
        # 获取当前用户
        # current_user_id = get_jwt_identity()
        
        try:
            # 直接处理文件
            from backend.rag.create_db import process_document_with_progress
            
            # 创建一个简单的进度回调函数
            def progress_callback(progress):
                print(f"处理进度: {progress}%")
            
            # 直接处理文件
            success = process_document_with_progress(
                str(course_id), 
                full_path, 
                progress_callback=progress_callback
            )
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': '文件已成功处理并添加到知识库'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': '文件处理失败'
                }), 500
                
        except Exception as e:
            current_app.logger.error(f"处理文件时出错: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'处理文件时出错: {str(e)}'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"处理请求时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'处理请求时出错: {str(e)}'
        }), 500

@rag_api.route('/knowledge/remove', methods=['DELETE'])
def remove_from_knowledge_base():
    """Remove a file from the knowledge base"""
    try:
        data = request.json
        queue_id = data.get('queue_id')
        
        if not queue_id:
            return jsonify({'status': 'error', 'message': '缺少队列ID'}), 400
        
        # 查找队列项
        queue_item = db.session.get(KnowledgeBaseQueue, queue_id)
        if not queue_item:
            return jsonify({'status': 'error', 'message': '队列项不存在'}), 404
        
        # 如果文件已完成处理，需要从向量数据库中删除
        if queue_item.status == 'completed':
            try:
                # 删除向量数据库中的相关数据
                from backend.rag.create_db import remove_document_from_knowledge_base
                success = remove_document_from_knowledge_base(
                    str(queue_item.course_id), 
                    queue_item.file_path
                )
                
                if not success:
                    current_app.logger.warning(f"删除向量数据库数据失败: {queue_item.file_path}")
            except Exception as e:
                current_app.logger.error(f"删除向量数据库数据时出错: {str(e)}")
                # 继续删除队列项，即使向量数据库删除失败
        
        # 删除队列项
        db.session.delete(queue_item)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '文件已从知识库中删除'
        })
        
    except Exception as e:
        current_app.logger.error(f"删除文件时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'删除文件时出错: {str(e)}'
        }), 500

@rag_api.route('/knowledge/clear-queue', methods=['DELETE'])
def clear_knowledge_base_queue():
    """Clear the knowledge base processing queue for a course"""
    try:
        data = request.json
        course_id = data.get('course_id')
        
        if not course_id:
            return jsonify({'status': 'error', 'message': '缺少课程ID'}), 400
        
        # 查找所有待处理和处理中的队列项
        queue_items = KnowledgeBaseQueue.query.filter_by(course_id=course_id).filter(
            KnowledgeBaseQueue.status.in_(['pending', 'processing'])
        ).all()
        
        if not queue_items:
            return jsonify({
                'status': 'success',
                'message': '没有待处理的队列项',
                'count': 0
            })
        
        # 删除所有队列项
        count = 0
        for item in queue_items:
            db.session.delete(item)
            count += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'成功清空{count}个队列项',
            'count': count
        })
        
    except Exception as e:
        current_app.logger.error(f"清空队列时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'清空队列时出错: {str(e)}'
        }), 500

@rag_api.route('/knowledge/batch-remove', methods=['DELETE'])
def batch_remove_from_knowledge_base():
    """Batch remove files from the knowledge base"""
    try:
        data = request.json
        queue_ids = data.get('queue_ids', [])
        
        if not queue_ids:
            return jsonify({'status': 'error', 'message': '缺少队列ID列表'}), 400
        
        deleted_count = 0
        failed_count = 0
        
        for queue_id in queue_ids:
            try:
                # 查找队列项
                queue_item = db.session.get(KnowledgeBaseQueue, queue_id)
                if not queue_item:
                    failed_count += 1
                    continue
                
                # 如果文件已完成处理，需要从向量数据库中删除
                if queue_item.status == 'completed':
                    try:
                        # 删除向量数据库中的相关数据
                        from backend.rag.create_db import remove_document_from_knowledge_base
                        success = remove_document_from_knowledge_base(
                            str(queue_item.course_id), 
                            queue_item.file_path
                        )
                        
                        if not success:
                            current_app.logger.warning(f"删除向量数据库数据失败: {queue_item.file_path}")
                    except Exception as e:
                        current_app.logger.error(f"删除向量数据库数据时出错: {str(e)}")
                
                # 删除队列项
                db.session.delete(queue_item)
                deleted_count += 1
                
            except Exception as e:
                current_app.logger.error(f"删除队列项 {queue_id} 时出错: {str(e)}")
                failed_count += 1
        
        db.session.commit()
        
        message = f'批量删除完成，成功删除 {deleted_count} 个项目'
        if failed_count > 0:
            message += f'，失败 {failed_count} 个项目'
        
        return jsonify({
            'status': 'success',
            'message': message,
            'deleted_count': deleted_count,
            'failed_count': failed_count
        })
        
    except Exception as e:
        current_app.logger.error(f"批量删除知识库文件时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'批量删除失败: {str(e)}'
        }), 500

@rag_api.route('/generate-lesson-plan', methods=['POST'])
@jwt_required()
def generate_lesson_plan():
    """生成课程教案或总纲"""
    # 在应用上下文中记录日志
    app_logger = current_app.logger
    app_logger.info("收到生成教案/总纲的请求")
    
    # 获取请求数据
    data = request.json
    if not data:
        app_logger.error("无效的请求数据")
        return jsonify({'status': 'error', 'message': '无效的请求数据'}), 400
    
    # 获取用户ID
    user_id = get_jwt_identity()
    app_logger.info(f"用户ID: {user_id}")
    
    # 获取请求参数
    outline_type = data.get('outlineType', 'course')  # 'course'或'class'
    course_id = data.get('courseId')
    chapter_id = data.get('chapterId')
    grade_subject = data.get('gradeSubject')
    duration = data.get('duration', '')
    learning_objectives = data.get('learningObjectives', '')
    key_points = data.get('keyPoints', '')
    student_level = data.get('studentLevel', '')
    custom_student_level = data.get('customStudentLevel', '')
    activities = data.get('activities', [])
    teaching_style = data.get('teachingStyle', '')
    assessment_methods = data.get('assessmentMethods', [])
    detail_level = data.get('detailLevel', 2)  # 默认为2级详细度
    
    # 验证必填参数
    if not grade_subject:
        app_logger.error("缺少必填参数: gradeSubject")
        return jsonify({'status': 'error', 'message': '缺少必填参数: 学段/年级/学科'}), 400
    
    app_logger.info(f"开始生成{outline_type}，学科: {grade_subject}")
    
    try:
        # 获取API配置
        api_key, api_base, model_name = get_api_config()
        
        if not api_key or not api_base:
            app_logger.error("API密钥或基础URL未配置")
            return jsonify({
                'status': 'error',
                'message': 'API密钥或基础URL未配置'
            }), 500
        
        model_name = "deepseek-ai/DeepSeek-R1"
        app_logger.info(f"生成教案使用模型: {model_name}")
        
        # 获取课程和章节信息（如果有）
        course_info = ""
        chapter_info = ""
        selected_chapter_title = ""
        
        if course_id:
            course = Course.query.get(course_id)
            if course:
                course_info = f"\n- 课程名称：{course.name}"
                if course.description:
                    course_info += f"\n- 课程描述：{course.description}"
                
                # 如果是课堂教案且指定了章节
                if outline_type == 'class' and chapter_id:
                    try:
                        # 获取章节文件路径
                        chapters_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'chapters')
                        course_chapters_folder = os.path.join(chapters_folder, str(course_id))
                        chapters_file_path = os.path.join(course_chapters_folder, 'chapters.json')
                        
                        # 如果章节文件存在，则读取指定章节
                        if os.path.exists(chapters_file_path):
                            with open(chapters_file_path, 'r', encoding='utf-8') as f:
                                chapters_data = json.load(f)
                            
                            # 在前端，章节ID是从1开始的索引，这里需要转换为基于0的索引
                            try:
                                idx = int(chapter_id) - 1
                                if 0 <= idx < len(chapters_data):
                                    chapter = chapters_data[idx]
                                    selected_chapter_title = chapter.get('title', '')
                                    chapter_info = f"\n- 选择章节：{selected_chapter_title}"
                                    
                                    # 添加小节信息
                                    if 'sections' in chapter and chapter['sections']:
                                        chapter_info += "\n- 章节小节："
                                        for section in chapter['sections']:
                                            chapter_info += f"\n  * {section.get('title', '')}"
                                            if 'content' in section:
                                                chapter_info += f"：{section.get('content', '')}"
                            except (ValueError, IndexError):
                                app_logger.warning(f"无法获取章节信息，ID: {chapter_id}")
                    except Exception as e:
                        app_logger.error(f"获取章节信息失败: {str(e)}")
        
        # 学生学情
        student_level_text = student_level or custom_student_level
        
        # 构建活动类型字符串
        activities_text = "、".join(activities) if activities else ""
        
        # 构建评估方式字符串
        assessment_text = "、".join(assessment_methods) if assessment_methods else ""
        
        # 构建系统提示词
        system_prompt = f"""你是一位专业的教育教学专家，精通课程设计和教案编写。
现在，你需要为教师生成一个{'课程总纲' if outline_type == 'course' else '课堂教案'}，请确保内容专业、实用且格式美观。

请根据以下提供的信息，生成完整的{'课程总纲' if outline_type == 'course' else '课堂教案'}:
{course_info}
{chapter_info}

{'课程总纲应包含整体课程规划、学习目标、教学方法和评价方式等内容。' if outline_type == 'course' else '课堂教案应包含本节课的教学设计、活动安排、教学流程和时间分配等内容。'}

请按照Markdown格式输出，确保层次清晰，内容详实。
"""

        # 构建用户提示词
        user_prompt = f"""请为以下条件生成一个专业的{'课程总纲' if outline_type == 'course' else '课堂教案'}:

- 学段/年级/学科：{grade_subject}
{f"- 课时长度：{duration}" if duration else ""}
{f"- 核心教学目标/学习目标：{learning_objectives}" if learning_objectives else ""}
{f"- 教学重点与难点：{key_points}" if key_points else ""}
{f"- 学生学情预设：{student_level_text}" if student_level_text else ""}
{f"- 所需课堂活动类型：{activities_text}" if activities_text else ""}
{f"- 教学风格/模式倾向：{teaching_style}" if teaching_style else ""}
{f"- 评估方式：{assessment_text}" if assessment_text else ""}
- 详细程度：{detail_level}（1-简洁，3-详细）

请提供结构化、专业的{'课程总纲' if outline_type == 'course' else '课堂教案'}，使用Markdown格式，包含清晰的标题、列表和合适的结构安排。
"""

        # 准备API请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # 准备API请求体
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000,
            "stream": True  # 启用流式响应
        }
        
        app_logger.info(f"向API发送请求, 基础URL: {api_base}, 模型: {model_name}")
        
        # 创建会话ID
        conversation_id = f"lesson_plan_{user_id}_{int(time.time())}"
        
        # 采用流式响应
        def generate():
            # 流式请求API
            full_response = ""
            try:
                with requests.post(
                    f"{api_base}/chat/completions",  # 直接使用API基础URL，不添加额外路径前缀
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=120  # 增加超时时间到120秒
                ) as response:
                    
                    if response.status_code != 200:
                        error_msg = f"API请求失败: {response.status_code}, {response.text}"
                        app_logger.error(error_msg)
                        yield f"data: {json.dumps({'status': 'error', 'message': error_msg})}\n\n"
                        return
                    
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
                                                yield f"data: {json.dumps({'status': 'chunk', 'content': content})}\n\n"
                                except json.JSONDecodeError:
                                    continue
                
                # 保存用户请求到数据库
                user_message = ChatHistory(
                    user_id=user_id,
                    course_id=course_id,
                    conversation_id=conversation_id,
                    role='user',
                    message=user_prompt,
                    timestamp=int(time.time())
                )
                db.session.add(user_message)
                
                # 保存AI回复到数据库
                ai_message = ChatHistory(
                    user_id=user_id,
                    course_id=course_id,
                    conversation_id=conversation_id,
                    role='assistant',
                    message=full_response,
                    timestamp=int(time.time())
                )
                db.session.add(ai_message)
                db.session.commit()
                
                # 发送结束信号
                yield f"data: {json.dumps({'status': 'done', 'conversation_id': conversation_id, 'outline_type': outline_type, 'selected_chapter': selected_chapter_title})}\n\n"
                
            except requests.exceptions.Timeout:
                error_msg = "请求超时，请稍后再试"
                app_logger.error(f"生成教案时出错: {error_msg}")
                yield f"data: {json.dumps({'status': 'error', 'message': error_msg})}\n\n"
            except Exception as e:
                error_msg = f"生成教案时出错: {str(e)}"
                app_logger.error(error_msg)
                yield f"data: {json.dumps({'status': 'error', 'message': error_msg})}\n\n"
        
        # 设置CORS头并返回流式响应
        response = Response(stream_with_context(generate()), content_type='text/event-stream')
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['X-Accel-Buffering'] = 'no'  # 禁用Nginx缓冲
        response.headers['Access-Control-Allow-Origin'] = '*'  # 允许任何源访问
        return response
    
    except Exception as e:
        app_logger.error(f"生成教案时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'生成教案失败: {str(e)}'
        }), 500