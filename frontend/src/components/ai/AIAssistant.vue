<template>
  <div class="ai-assistant">
    <!-- 对话列表侧边栏 -->
    <div v-if="showConversations" class="fixed inset-0 bg-black bg-opacity-50 flex z-40" @click="showConversations = false">
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
      <div class="px-6 py-4 border-b flex justify-between items-center">
        <div class="flex items-center">
          <button 
            @click="showConversations = true" 
            class="mr-3 text-gray-500 hover:text-gray-700"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
            </svg>
          </button>
          <h3 class="text-lg font-semibold">智能助手</h3>
        </div>
        <div class="flex items-center">
          <span class="inline-block w-2 h-2 rounded-full bg-green-500 mr-2"></span>
          <span class="text-sm text-gray-500">在线</span>
        </div>
      </div>
      
      <div class="h-[calc(100vh-300px)] p-4 overflow-y-auto" ref="chatContainer">
        <div class="space-y-4">
          <!-- 系统消息 -->
          <div v-if="chatMessages.length === 0" class="flex items-start">
            <div class="flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center overflow-hidden">
              <img src="/src/assets/images/atom.png" alt="AI" class="h-full w-full object-cover" />
            </div>
            <div class="ml-3 bg-gray-100 rounded-lg py-2 px-4 max-w-[80%]">
              <p class="text-gray-800">你好！我是智能学习助手。有什么可以帮助你的吗？</p>
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
                  <img :src="userAvatarUrl" alt="User" class="h-full w-full object-cover" />
                </template>
                <template v-else>
                  <span class="text-white font-medium">{{ userInitial }}</span>
                </template>
              </div>
            </div>
            
            <!-- 系统回复 -->
            <div v-else class="flex items-start mt-4">
              <div class="flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center overflow-hidden">
                <img src="/src/assets/images/atom.png" alt="AI" class="h-full w-full object-cover" />
              </div>
              <div class="ml-3 bg-gray-100 rounded-lg py-2 px-4 max-w-[80%]">
                <p v-if="message.content" class="text-gray-800 whitespace-pre-wrap">{{ message.content }}</p>
                
                <!-- 加载中指示器 - 当消息为空时显示 -->
                <div v-else class="flex space-x-1">
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                  <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                </div>
                
                <!-- 如果有引用来源 -->
                <div v-if="message.sources && message.sources.length > 0" class="mt-2 pt-2 border-t border-gray-200">
                  <p class="text-xs text-gray-500 font-medium">参考来源:</p>
                  <ul class="mt-1 space-y-1">
                    <li v-for="(source, sIdx) in message.sources" :key="sIdx" class="text-xs">
                      <a :href="source.url" class="text-blue-600 hover:underline" target="_blank">{{ source.title }}</a>
                    </li>
                  </ul>
                </div>
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
            :disabled="loading || !userInput.trim()"
          >
            发送
          </button>
        </form>
        
        <div class="flex flex-wrap gap-2 mt-3">
          <button 
            v-for="(suggestion, index) in suggestions" 
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
import { ref, onMounted, nextTick, watch } from 'vue';
import axios from 'axios';

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
  userId: {
    type: [Number, String],
    required: true
  }
});

const API_BASE_URL = '/api';

const chatContainer = ref<HTMLElement | null>(null);
const userInput = ref('');
const loading = ref(false);
const chatMessages = ref<ChatMessage[]>([]);
const conversationId = ref('');
const userAvatarUrl = ref('');
const userInitial = ref('');

// 对话历史相关
const showConversations = ref(false);
const loadingConversations = ref(false);
const conversations = ref<Conversation[]>([]);

// 提问建议
const suggestions = [
  '什么是机器学习？',
  '如何提高学习效率？',
  '推荐一些学习资源',
  '这门课程的难点是什么？',
  '如何准备考试？'
];

onMounted(async () => {
  // 获取用户信息
  try {
    // 尝试获取用户信息，包括头像
    const userResponse = await axios.get(`${API_BASE_URL}/users/${props.userId}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    if (userResponse.data.status === 'success') {
      const userData = userResponse.data.user;
      // 设置用户头像URL
      if (userData.avatar_url) {
        userAvatarUrl.value = userData.avatar_url;
      } else {
        // 如果没有头像，使用用户名的首字母
        userInitial.value = userData.username ? userData.username.charAt(0).toUpperCase() : 'U';
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
    const statusResponse = await axios.get(`${API_BASE_URL}/rag/status`);
    console.log('AI模块状态:', statusResponse.data);
    
    if (!statusResponse.data.ai_enabled) {
      chatMessages.value.push({
        role: 'assistant',
        content: '注意：智能助手功能目前不可用。请确保已配置API密钥。'
      });
    } else {
      // AI模块可用，添加欢迎消息
      chatMessages.value.push({
        role: 'assistant',
        content: '你好！我是智能学习助手。有什么可以帮助你的吗？'
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
  
  // 滚动到底部
  scrollToBottom();
});

watch(chatMessages, () => {
  // 消息更新后滚动到底部
  nextTick(() => {
    scrollToBottom();
  });
});

function scrollToBottom() {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
}

async function sendMessage() {
  if (!userInput.value.trim()) return;
  
  // 添加用户消息
  const userMessage = userInput.value;
  chatMessages.value.push({
    role: 'user',
    content: userMessage
  });
  
  // 清空输入框
  userInput.value = '';
  
  // 添加一个空的AI回复消息，用于流式更新
  const aiMessageIndex = chatMessages.value.length;
  chatMessages.value.push({
    role: 'assistant',
    content: '',
    sources: []
  });
  
  // 显示加载状态
  loading.value = true;
  
  try {
    // 构建请求URL，包含授权令牌
    const token = localStorage.getItem('token');
    const url = `${API_BASE_URL}/rag/chat?` + new URLSearchParams({
      message: userMessage,
      conversation_id: conversationId.value || '',
      stream: 'true'
    }).toString();
    
    // 使用fetch API进行流式请求，而不是EventSource
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
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
              if (!chatMessages.value[aiMessageIndex].content) {
                chatMessages.value[aiMessageIndex].content = data.content.trimStart();
              } else {
                chatMessages.value[aiMessageIndex].content += data.content;
              }
            }
            
            // 处理完成信号
            if (data.status === 'done') {
              // 保存对话ID
              if (data.conversation_id) {
                conversationId.value = data.conversation_id;
              }
              
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
    if (aiMessageIndex < chatMessages.value.length) {
      chatMessages.value[aiMessageIndex].content = '抱歉，我遇到了一些问题。请稍后再试。';
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
    const response = await axios.get(`${API_BASE_URL}/rag/conversations`, {
      params: { course_id: props.courseId },
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    if (response.data.status === 'success') {
      conversations.value = response.data.conversations;
    } else {
      throw new Error(response.data.message || '未知错误');
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
    const response = await axios.get(`${API_BASE_URL}/rag/history`, {
      params: { conversation_id: convId },
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    if (response.data.status === 'success') {
      chatMessages.value = response.data.history.map((msg: any) => ({
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp
      }));
      conversationId.value = convId;
      showConversations.value = false;
    } else {
      throw new Error(response.data.message || '未知错误');
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
</script> 