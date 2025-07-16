<template>
  <div class="ai-assistant">
    <!-- 复制成功提示 -->
    <div 
      v-if="showCopyNotification" 
      class="fixed bottom-4 right-4 bg-gray-800 text-white px-4 py-2 rounded-md shadow-lg z-50 transition-opacity"
    >
      已复制到剪贴板
    </div>
    
    <!-- 对话列表侧边栏 -->
    <div v-if="!minimal && showConversations" class="fixed inset-0 bg-black bg-opacity-50 flex z-40" @click="showConversations = false">
      <div class="bg-white w-80 h-full overflow-y-auto p-4" @click.stop>
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">对话历史</h3>
          <button @click="showConversations = false" class="text-gray-500 hover:text-gray-700">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div v-if="loadingConversations" class="flex justify-center py-10">
          <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
        </div>
        
        <div v-else-if="conversations.length === 0" class="text-center py-10 text-gray-500">
          没有历史对话
        </div>
        
        <div v-else class="space-y-2">
          <div 
            v-for="conv in conversations" 
            :key="conv.conversation_id" 
            @click="loadConversation(conv.conversation_id)"
            class="p-3 border rounded-md cursor-pointer hover:bg-gray-50"
            :class="{'bg-blue-50 border-blue-300': conv.conversation_id === conversationId}"
          >
            <div class="font-medium">{{ conv.title }}</div>
            <div class="flex justify-between text-xs text-gray-500 mt-1">
              <span>{{ formatDate(conv.last_time) }}</span>
              <span>{{ conv.message_count }}条消息</span>
            </div>
          </div>
        </div>
        
        <div class="mt-4 pt-4 border-t">
          <button 
            @click="startNewConversation" 
            class="w-full py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            新建对话
          </button>
        </div>
      </div>
    </div>
    
    <div class="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
      <!-- 聊天页面头部 -->
      <div
        :class="['border-b', minimal ? 'px-4 py-2' : 'px-6 py-4', 'cursor-pointer']"
        @click.stop="emit('collapseRequest')"
      >
        <div class="flex justify-between items-center mb-2">
          <div class="flex items-center">
            <button 
              v-if="!minimal"
              @click="showConversations = true" 
              class="mr-3 text-gray-500 hover:text-gray-700"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
              </svg>
            </button>
            <h3 class="text-lg font-semibold whitespace-nowrap flex items-center space-x-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M2 5a2 2 0 012-2h16a2 2 0 012 2v9a2 2 0 01-2 2H8l-6 6V5z" />
              </svg>
              <span>智能助手</span>
            </h3>
          </div>
          <div v-if="!minimal" class="flex items-center">
            <span class="inline-block w-2 h-2 rounded-full mr-2" 
                  :class="statusIndicatorClass"></span>
            <span class="text-sm text-gray-500">{{ statusText }}</span>
          </div>
        </div>
        
        <!-- 模式选择和课程选择 -->
        <div v-if="!minimal" class="flex flex-wrap items-center gap-4">
          <!-- 模式选择 -->
          <div class="flex items-center">
            <label class="text-sm text-gray-600 mr-2 whitespace-nowrap">模式:</label>
            <select 
              v-model="chatMode" 
              class="px-3 py-1.5 border rounded-md text-sm bg-white min-w-[120px]"
              @change="onModeChange"
            >
              <option value="general">普通AI问答</option>
              <option value="rag">知识库增强</option>
            </select>
          </div>
          
          <!-- 课程选择 - 仅在RAG模式下显示 -->
          <div v-if="chatMode === 'rag'" class="flex items-center">
            <label class="text-sm text-gray-600 mr-2 whitespace-nowrap">选择课程:</label>
            <select 
              v-model="selectedCourseId" 
              class="px-3 py-1.5 border rounded-md text-sm bg-white min-w-[200px]"
            >
              <option value="">请选择课程</option>
              <option v-for="course in courses" :key="course.id" :value="course.id">
                {{ course.name }} (ID: {{ course.id }})
              </option>
            </select>
            <!-- 调试信息 -->
            <div v-if="courses.length === 0 && !loadingCourses" class="ml-2 text-xs text-red-500">
              无可用课程
            </div>
            <div v-if="courses.length > 0" class="ml-2 text-xs text-green-500">
              {{ courses.length }}个课程可用
            </div>
            <div v-if="loadingCourses" class="ml-2 text-xs text-blue-500">
              加载中...
            </div>
            <!-- 当前选择显示 -->
            <div v-if="selectedCourseId" class="ml-2 text-xs text-gray-600">
              已选择: {{ selectedCourseId }}
            </div>
          </div>
          
          <!-- 加载状态 -->
          <div v-if="loadingCourses" class="flex items-center text-sm text-gray-500">
            <div class="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-blue-500 mr-2"></div>
            加载课程中...
          </div>
        </div>
      </div>
      
      <div :class="[minimal ? 'h-[calc(100vh-240px)]' : 'h-[calc(100vh-300px)]', 'p-4 overflow-y-auto']" ref="chatContainer">
        <div class="space-y-4">
          <!-- 系统消息 -->
          <div v-if="chatMessages.length === 0" class="flex items-start">
            <div class="flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center overflow-hidden mt-1">
              <img src="@/assets/images/atom.png" alt="AI" class="h-full w-full object-cover" />
            </div>
            <div class="ml-3 pl-2 max-w-[80%]">
              <p class="text-gray-800 font-medium">你好！我是智能学习助手。有什么可以帮助你的吗？</p>
            </div>
          </div>
          
          <!-- 用户消息和系统回复 -->
          <div v-for="(message, index) in chatMessages" :key="index">
            <!-- 用户消息 -->
            <div v-if="message.role === 'user'" class="flex items-start justify-end">
              <div class="mr-3 bg-blue-500 text-white rounded-lg py-2 px-4 max-w-[80%]">
                <p>{{ message.content }}</p>
              </div>
              <div class="flex-shrink-0 h-8 w-8 rounded-full bg-gray-300 overflow-hidden flex items-center justify-center">
                <template v-if="userAvatarUrl">
                  <img :src="formatAvatarUrl(userAvatarUrl)" alt="User" class="h-full w-full object-cover" />
                </template>
                <template v-else>
                  <span class="text-white font-medium">{{ userInitial }}</span>
                </template>
              </div>
            </div>
            
            <!-- 系统回复 -->
            <div v-else class="flex items-start mt-4">
              <div class="flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center overflow-hidden mt-1">
                <img src="@/assets/images/atom.png" alt="AI" class="h-full w-full object-cover" />
              </div>
              <div class="ml-3 pl-2 max-w-[80%] relative group">
                <!-- 使用v-if/v-else来区分是否有内容 -->
                <div v-if="message.content" class="text-gray-800 font-medium bg-gray-100 rounded-lg py-3 px-4 shadow-sm">
                  <div class="whitespace-pre-wrap">{{ message.content }}</div>
                  
                  <!-- 如果有引用来源 -->
                  <div v-if="message.sources && message.sources.length > 0" class="mt-3 pt-2 border-t border-gray-200">
                    <p class="text-xs text-gray-500 font-medium">参考来源:</p>
                    <ul class="mt-1 space-y-1">
                      <li v-for="(source, sIdx) in message.sources" :key="sIdx" class="text-xs">
                        <a :href="source.url" class="text-blue-600 hover:underline" target="_blank">{{ source.title }}</a>
                      </li>
                    </ul>
                  </div>
                </div>
                
                <!-- 加载中指示器 - 当消息为空时显示 -->
                <div v-else class="flex items-center">
                  <span class="text-sm text-gray-500 mr-2">思考中</span>
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                </div>
                
                <!-- 复制按钮 - 使用group-hover使其仅在悬停时显示 -->
                <button 
                  @click="copyMessageContent(message.content)"
                  class="absolute bottom-2 right-2 bg-gray-200 text-gray-600 p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                  title="复制内容"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="px-4 py-3 border-t">
        <form @submit.prevent="sendMessage" class="flex items-center">
          <input 
            type="text" 
            v-model="userInput" 
            placeholder="输入你的问题..." 
            class="flex-1 px-4 py-2 border rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            :disabled="loading"
          />
          <button 
            type="submit" 
            class="bg-blue-600 text-white px-4 py-2 rounded-r-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            :disabled="loading || !userInput.trim() || (chatMode === 'rag' && !selectedCourseId)"
          >
            {{ loading ? '发送中...' : '发送' }}
          </button>
        </form>
        
        <div class="flex flex-wrap gap-2 mt-3">
          <button 
            v-for="(suggestion, index) in currentSuggestions" 
            :key="index"
            @click="useSuggestion(suggestion)"
            class="text-xs bg-gray-100 hover:bg-gray-200 text-gray-800 px-2 py-1 rounded-md"
          >
            {{ suggestion }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch, computed, defineEmits } from 'vue';
import axios from 'axios';
import { courseAPI, ragAiAPI } from '../../api';

// 定义接口
interface ChatMessage {
  role: string;
  content: string;
  sources?: Source[];
  timestamp?: number;
}

interface Source {
  title: string;
  url: string;
}

interface Conversation {
  conversation_id: string;
  title: string;
  start_time: number;
  last_time: number;
  message_count: number;
}

const props = defineProps({
  courseId: {
    type: [Number, String],
    default: null
  },
  // 当 minimal 为 true 时：
  // 1) 默认启用 RAG 并锁定到传入的 courseId
  // 2) 隐藏对话历史、模式/课程选择等额外 UI
  minimal: {
    type: Boolean,
    default: false
  }
});

const chatContainer = ref<HTMLElement | null>(null);
const userInput = ref('');
const loading = ref(false);
const chatMessages = ref<ChatMessage[]>([]);
const conversationId = ref('');
const userAvatarUrl = ref('');
const userInitial = ref('');
const showCopyNotification = ref(false);

// 对话历史相关
const showConversations = ref(false);
const loadingConversations = ref(false);
const conversations = ref<Conversation[]>([]);

// 课程相关
const courses = ref<any[]>([]);
const selectedCourseId = ref<string | number>('');
const useRag = ref<boolean>(true);
const loadingCourses = ref<boolean>(false);

// 新增：聊天模式相关
const chatMode = ref<'general' | 'rag'>('general');

// 提问建议
const suggestions = [
  '什么是机器学习？',
  '如何提高学习效率？',
  '推荐一些学习资源',
  '这门课程的难点是什么？',
  '如何准备考试？'
];

// RAG模式专用建议
const ragSuggestions = [
  '这门课程的主要内容是什么？',
  '课程中的重点概念有哪些？',
  '如何理解课程中的难点？',
  '课程相关的实践项目有哪些？',
  '这门课程与其他课程有什么联系？'
];

// 计算当前应该显示的建议
const currentSuggestions = computed(() => {
  return chatMode.value === 'rag' ? ragSuggestions : suggestions;
});

// 状态指示器
const statusIndicatorClass = computed(() => {
  if (chatMode.value === 'rag' && !selectedCourseId.value) {
    return 'bg-yellow-500'; // 黄色：需要选择课程
  }
  return 'bg-green-500'; // 绿色：就绪
});

const statusText = computed(() => {
  if (chatMode.value === 'rag' && !selectedCourseId.value) {
    return '请选择课程';
  }
  if (chatMode.value === 'rag' && selectedCourseId.value) {
    return '知识库模式（如无知识库将使用普通模式）';
  }
  return '普通模式';
});

const API_BASE_URL = 'http://localhost:5001/api';

// 复制消息内容
function copyMessageContent(content: string): void {
  if (!content) return;
  
  navigator.clipboard.writeText(content)
    .then(() => {
      // 显示复制成功提示
      showCopyNotification.value = true;
      setTimeout(() => {
        showCopyNotification.value = false;
      }, 2000);
    })
    .catch(err => {
      console.error('复制失败:', err);
    });
}

// 格式化头像URL
function formatAvatarUrl(url: string): string {
  if (!url) return '';
  
  // 如果已经是完整URL，直接返回
  if (url.startsWith('http')) {
    return url;
  }
  
  // 如果是相对路径，添加基础URL
  return `http://localhost:5001${url}`;
}

const emit = defineEmits(['collapseRequest']);

onMounted(async () => {
  // 获取用户信息
  try {
    // 使用当前用户的个人资料API而不是按ID获取
    const userResponse = await axios.get(`${API_BASE_URL}/auth/profile`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    if (userResponse.data && userResponse.data.user) {
      const userData = userResponse.data.user;
      console.log('获取到用户信息:', userData);
      
      // 设置用户头像URL
      if (userData.avatar_url) {
        userAvatarUrl.value = userData.avatar_url;
        console.log('设置用户头像URL:', userAvatarUrl.value);
      } else {
        // 如果没有头像，使用用户名的首字母
        userInitial.value = userData.username ? userData.username.charAt(0).toUpperCase() : 'U';
        console.log('设置用户初始字母:', userInitial.value);
      }
    } else {
      // 如果无法获取用户信息，使用默认首字母
      setDefaultUserInitial();
    }
  } catch (error) {
    console.error('无法获取用户信息:', error);
    setDefaultUserInitial();
  }

  // 检查AI模块状态
  try {
    const statusResponse = await ragAiAPI.getStatus();
    console.log('AI模块状态:', statusResponse);
    
    // 由于响应拦截器已经返回response.data，所以这里直接使用response
    const responseData = statusResponse as any;
    if (responseData && !responseData.ai_enabled) {
      chatMessages.value.push({
        role: 'assistant',
        content: '注意：智能助手功能目前不可用。请确保已配置API密钥。'
      });
    }
  } catch (error) {
    console.error('无法获取AI模块状态:', error);
    chatMessages.value.push({
      role: 'assistant',
      content: '注意：智能助手功能目前可能不可用。请稍后再试。'
    });
  }
  
  // 获取对话列表
  await fetchConversations();
  
  // 获取课程列表
  await fetchCourses();
  
  // 初始化聊天模式
  if (props.courseId) {
    // 如果传入了课程ID，默认使用RAG模式
    chatMode.value = 'rag';
    selectedCourseId.value = props.courseId;
  } else {
    // 否则使用普通模式
    chatMode.value = 'general';
  }

  // 如果处于简洁模式，预设聊天模式和课程
  if (props.minimal) {
    chatMode.value = 'rag';
    if (props.courseId) {
      selectedCourseId.value = props.courseId;
    }
  }
  
  // 只有在没有消息时才设置欢迎消息
  if (chatMessages.value.length === 0) {
    updateWelcomeMessage();
  }
  
  // 滚动到底部
  scrollToBottom();
});

watch(chatMessages, () => {
  // 消息更新后滚动到底部
  nextTick(() => {
    scrollToBottom();
  });
});

// 监听课程选择变化
watch(selectedCourseId, (newCourseId) => {
  console.log('课程选择变化:', newCourseId);
  if (chatMode.value === 'rag' && newCourseId) {
    // 当在RAG模式下选择课程时，更新欢迎消息
    updateWelcomeMessage();
  }
});

// 监听课程数据变化
watch(courses, (newCourses) => {
  console.log('课程数据更新:', newCourses);
  // 如果当前选中的课程不在课程列表中，清空选择
  if (selectedCourseId.value && !newCourses.find(c => c.id == selectedCourseId.value)) {
    selectedCourseId.value = '';
  }
});

function scrollToBottom() {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
}

async function sendMessage() {
  if (!userInput.value.trim() || loading.value) return;
  
  // 在RAG模式下检查是否选择了课程
  if (chatMode.value === 'rag' && !selectedCourseId.value) {
    alert('请先选择课程以启用知识库增强功能');
    return;
  }
  
  const message = userInput.value;
  userInput.value = '';
  
  // 添加用户消息到聊天记录
  chatMessages.value.push({
    role: 'user',
    content: message,
    timestamp: Date.now()
  });
  
  // 添加一个空的系统回复作为占位符
  chatMessages.value.push({
    role: 'assistant',
    content: '',
    timestamp: Date.now()
  });
  
  // 滚动到底部
  await nextTick();
  scrollToBottom();
  
  loading.value = true;
  
  try {
    // 构建请求参数
    const params: any = {
      message,
      stream: true
    };
    
    // 根据模式设置参数
    if (chatMode.value === 'rag' && selectedCourseId.value) {
      params.course_id = selectedCourseId.value;
      params.use_rag = true; // 尝试使用RAG，如果失败会自动回退到普通模式
    } else {
      params.use_rag = false;
    }
    
    // 如果有对话ID，添加到参数中
    if (conversationId.value) {
      params.conversation_id = conversationId.value;
    }
    
    console.log('发送聊天请求:', params);
    
    const response = await fetch(`${API_BASE_URL}/rag/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(params)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    // 获取响应的reader
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('无法获取响应流');
    }
    
    // 处理流式响应
    const decoder = new TextDecoder();
    let buffer = '';
    let lastRenderTime = Date.now();
    const renderInterval = 500; // 每500毫秒渲染一次
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      // 解码二进制数据
      buffer += decoder.decode(value, { stream: true });
      
      // 处理接收到的数据行
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.substring(6));
            
            // 处理内容更新
            if (data.content) {
              // 如果是第一个内容块且消息当前为空，去除开头的空白
              if (!chatMessages.value[chatMessages.value.length - 1].content) {
                chatMessages.value[chatMessages.value.length - 1].content = data.content.trimStart();
              } else {
                chatMessages.value[chatMessages.value.length - 1].content += data.content;
              }
              
              // 实时渲染Markdown：每隔一定时间或内容达到一定长度时渲染
              const now = Date.now();
              if (now - lastRenderTime > renderInterval) {
                // 强制Vue更新视图
                chatMessages.value = [...chatMessages.value];
                lastRenderTime = now;
                
                // 滚动到底部
                nextTick(() => {
                  scrollToBottom();
                });
              }
            }
            
            // 处理完成信号
            if (data.status === 'done') {
              // 保存对话ID
              if (data.conversation_id) {
                conversationId.value = data.conversation_id;
              }
              
              // 添加引用来源
              if (data.sources && Array.isArray(data.sources) && data.sources.length > 0) {
                chatMessages.value[chatMessages.value.length - 1].sources = data.sources;
              }
              
              // 最后一次渲染，确保所有内容都已渲染
              chatMessages.value = [...chatMessages.value];
              
              loading.value = false;
              return;
            }
          } catch (error) {
            console.error('解析流式响应失败:', error);
          }
        }
      }
    }
    
    loading.value = false;
  } catch (error) {
    console.error('发送消息失败:', error);
    
    // 如果已经添加了AI消息，更新为错误消息
    if (chatMessages.value.length > 1) {
      chatMessages.value[chatMessages.value.length - 1].content = '抱歉，我遇到了一些问题。请稍后再试。';
    } else {
      // 如果没有添加AI消息，添加一个错误消息
      chatMessages.value.push({
        role: 'assistant',
        content: '抱歉，我遇到了一些问题。请稍后再试。'
      });
    }
    
    loading.value = false;
  }
}

function useSuggestion(suggestion: string): void {
  userInput.value = suggestion;
}

// 格式化日期
function formatDate(timestamp: number): string {
  if (!timestamp) return '';
  const date = new Date(timestamp * 1000);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// 获取对话列表
async function fetchConversations() {
  loadingConversations.value = true;
  
  try {
    const response = await ragAiAPI.getConversations(props.courseId);
    
    // 由于响应拦截器已经返回response.data，所以这里直接使用response
    const responseData = response as any;
    if (responseData && responseData.status === 'success') {
      conversations.value = responseData.conversations || [];
    } else {
      throw new Error(responseData?.message || '未知错误');
    }
  } catch (error) {
    console.error('获取对话列表失败:', error);
    conversations.value = [];
  } finally {
    loadingConversations.value = false;
  }
}

// 加载指定对话
async function loadConversation(convId: string): Promise<void> {
  if (convId === conversationId.value) {
    showConversations.value = false;
    return;
  }
  
  try {
    const response = await ragAiAPI.getChatHistory(convId);
    
    // 由于响应拦截器已经返回response.data，所以这里直接使用response
    const responseData = response as any;
    if (responseData && responseData.status === 'success') {
      chatMessages.value = responseData.history.map((msg: any) => ({
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp
      }));
      conversationId.value = convId;
      showConversations.value = false;
    } else {
      throw new Error(responseData?.message || '未知错误');
    }
  } catch (error) {
    console.error('加载对话历史失败:', error);
    chatMessages.value.push({
      role: 'assistant',
      content: '加载对话历史失败，请稍后再试。'
    });
  }
}

// 开始新对话
function startNewConversation() {
  conversationId.value = '';
  chatMessages.value = [];
  showConversations.value = false;
}

function setDefaultUserInitial() {
  // 尝试从localStorage获取用户信息
  try {
    const userDataStr = localStorage.getItem('user');
    if (userDataStr) {
      const userData = JSON.parse(userDataStr);
      if (userData && userData.username) {
        userInitial.value = userData.username.charAt(0).toUpperCase();
        return;
      }
    }
  } catch (e) {
    console.error('解析localStorage中的用户信息失败:', e);
  }
  
  // 如果无法从localStorage获取，使用默认值
  userInitial.value = 'U';
}

// 获取课程列表
async function fetchCourses() {
  loadingCourses.value = true;
  try {
    const response = await courseAPI.getCourses();
    console.log('课程API响应:', response);
    
    // 检查响应格式并正确提取课程数据
    if (response && typeof response === 'object' && 'courses' in response) {
      courses.value = (response as any).courses || [];
    } else if (Array.isArray(response)) {
      courses.value = response;
    } else {
      console.warn('课程API响应格式异常:', response);
      courses.value = [];
    }
    
    console.log('获取到课程列表:', courses.value);
    
    // 如果传入了课程ID但课程不在列表中，添加一个占位符
    if (props.courseId && !courses.value.find(c => c.id == props.courseId)) {
      courses.value.push({
        id: props.courseId,
        name: `课程 #${props.courseId}`,
        description: '课程信息加载中...'
      });
    }
  } catch (error) {
    console.error('获取课程列表失败:', error);
    courses.value = [];
    
    // 如果传入了课程ID，至少添加一个占位符
    if (props.courseId) {
      courses.value.push({
        id: props.courseId,
        name: `课程 #${props.courseId}`,
        description: '课程信息加载失败'
      });
    }
  } finally {
    loadingCourses.value = false;
  }
}

function onModeChange() {
  // 模式切换时的逻辑
  if (chatMode.value === 'general') {
    // 切换到普通模式时，清空课程选择
    selectedCourseId.value = '';
  } else if (chatMode.value === 'rag') {
    // 切换到RAG模式时，如果有传入的课程ID，自动选择
    if (props.courseId) {
      selectedCourseId.value = props.courseId;
    }
  }
  
  // 只有在有对话ID的情况下才清空对话，表示这是一个新的对话
  if (conversationId.value) {
    conversationId.value = '';
    chatMessages.value = [];
    
    // 更新欢迎消息
    updateWelcomeMessage();
  }
}

function updateWelcomeMessage() {
  // Only update welcome message if there are no existing messages
  if (chatMessages.value.length > 0) return;
  
  let welcomeMessage = '';
  if (chatMode.value === 'general') {
    welcomeMessage = '你好！我是智能学习助手。有什么可以帮助你的吗？';
  } else {
    if (selectedCourseId.value) {
      const course = courses.value.find(c => c.id == selectedCourseId.value);
      const courseName = course ? course.name : `课程 #${selectedCourseId.value}`;
      welcomeMessage = `你好！我是智能学习助手。我已连接到"${courseName}"。我将基于课程的知识库回答，请随时提问！`;
    } else {
      welcomeMessage = '你好！我是智能学习助手。请选择课程以启用知识库增强功能。';
    }
  }
  
  chatMessages.value.push({
    role: 'assistant',
    content: welcomeMessage
  });
}
</script>

<style>
/* 简化的样式，移除所有Markdown相关样式 */
</style> 