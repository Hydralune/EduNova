<template>
  <div class="ai-assistant">
    <div class="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
      <div class="px-6 py-4 border-b flex justify-between items-center">
        <h3 class="text-lg font-semibold">智能助手</h3>
        <div class="flex items-center">
          <span class="inline-block w-2 h-2 rounded-full bg-green-500 mr-2"></span>
          <span class="text-sm text-gray-500">在线</span>
        </div>
      </div>
      
      <div class="h-96 p-4 overflow-y-auto" ref="chatContainer">
        <div class="space-y-4">
          <!-- 系统消息 -->
          <div class="flex items-start">
            <div class="flex-shrink-0 h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white">
              AI
            </div>
            <div class="ml-3 bg-gray-100 rounded-lg py-2 px-4 max-w-[80%]">
              <p class="text-gray-800">你好！我是你的智能学习助手。我可以回答你的问题、提供学习建议、解释概念，或者帮你找到相关的学习资源。请问有什么可以帮助你的吗？</p>
            </div>
          </div>
          
          <!-- 用户消息和系统回复 -->
          <div v-for="(message, index) in chatMessages" :key="index">
            <!-- 用户消息 -->
            <div v-if="message.role === 'user'" class="flex items-start justify-end">
              <div class="mr-3 bg-blue-500 text-white rounded-lg py-2 px-4 max-w-[80%]">
                <p>{{ message.content }}</p>
              </div>
              <div class="flex-shrink-0 h-8 w-8 rounded-full bg-gray-300"></div>
            </div>
            
            <!-- 系统回复 -->
            <div v-else class="flex items-start mt-4">
              <div class="flex-shrink-0 h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white">
                AI
              </div>
              <div class="ml-3 bg-gray-100 rounded-lg py-2 px-4 max-w-[80%]">
                <p class="text-gray-800 whitespace-pre-wrap">{{ message.content }}</p>
                
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
          
          <!-- 加载中指示器 -->
          <div v-if="loading" class="flex items-start mt-4">
            <div class="flex-shrink-0 h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white">
              AI
            </div>
            <div class="ml-3 bg-gray-100 rounded-lg py-3 px-4">
              <div class="flex space-x-1">
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
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
            @click="usesuggestion(suggestion)"
            class="text-xs bg-gray-100 hover:bg-gray-200 text-gray-800 px-2 py-1 rounded-md"
          >
            {{ suggestion }}
          </button>
        </div>
      </div>
    </div>
    
    <div class="mt-6 bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <h3 class="text-lg font-semibold mb-4">学习建议</h3>
      
      <div v-if="loadingRecommendations" class="flex justify-center py-10">
        <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
      </div>
      
      <div v-else class="space-y-4">
        <div v-for="(recommendation, index) in recommendations" :key="index" class="border rounded-md p-4">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div class="ml-3">
              <h4 class="font-medium">{{ recommendation.title }}</h4>
              <p class="text-sm text-gray-600 mt-1">{{ recommendation.description }}</p>
              <div class="mt-2">
                <a 
                  v-if="recommendation.link" 
                  :href="recommendation.link" 
                  class="text-sm text-blue-600 hover:text-blue-800"
                >
                  查看详情
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, watch } from 'vue';

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

const chatContainer = ref(null);
const userInput = ref('');
const loading = ref(false);
const loadingRecommendations = ref(true);
const chatMessages = ref([]);
const conversationId = ref('');

// 提问建议
const suggestions = [
  '什么是机器学习？',
  '如何提高学习效率？',
  '推荐一些学习资源',
  '这门课程的难点是什么？',
  '如何准备考试？'
];

// 学习建议
const recommendations = ref([]);

onMounted(async () => {
  // 滚动到底部
  scrollToBottom();
  
  // 加载学习建议
  await fetchRecommendations();
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
  
  // 显示加载状态
  loading.value = true;
  
  try {
    // 这里应该调用API发送消息
    // const response = await api.sendChatMessage({
    //   message: userMessage,
    //   course_id: props.courseId,
    //   conversation_id: conversationId.value,
    //   user_id: props.userId
    // });
    
    // 模拟API响应
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // 模拟回复
    let aiResponse;
    if (userMessage.toLowerCase().includes('机器学习')) {
      aiResponse = {
        content: '机器学习是人工智能的一个分支，它使计算机能够在没有明确编程的情况下学习和改进。机器学习算法通过使用数学模型从样本数据中学习，这些模型可以用来做预测或决策，而不需要被明确地编程来执行任务。\n\n机器学习的主要类型包括：\n\n1. 监督学习：算法从标记的训练数据中学习\n2. 无监督学习：算法从未标记的数据中找出模式\n3. 强化学习：算法通过与环境互动来学习最佳行动',
        sources: [
          { title: '机器学习基础', url: '#' },
          { title: '人工智能导论', url: '#' }
        ]
      };
    } else if (userMessage.toLowerCase().includes('学习效率')) {
      aiResponse = {
        content: '提高学习效率的几个关键策略：\n\n1. 采用间隔重复法：定期复习已学内容，而不是一次性大量学习\n2. 实践测试：通过自我测试来加强记忆\n3. 多样化学习：结合不同的学习方法和材料\n4. 适当休息：保持充足的睡眠和定期休息\n5. 创建专注的学习环境：减少干扰\n6. 设定具体的学习目标：明确每次学习的具体目标\n7. 使用思维导图或笔记系统：组织和可视化信息',
        sources: [
          { title: '有效学习方法', url: '#' }
        ]
      };
    } else {
      aiResponse = {
        content: '感谢你的问题！我会尽力帮助你。\n\n' + userMessage + ' 是一个很好的问题。基于你的学习情况，我建议你可以参考课程中的相关章节，或者查看推荐的学习资源。如果你有更具体的问题，请随时告诉我。',
        sources: []
      };
    }
    
    // 添加AI回复
    chatMessages.value.push({
      role: 'assistant',
      content: aiResponse.content,
      sources: aiResponse.sources
    });
    
    // 如果是新对话，保存对话ID
    if (!conversationId.value) {
      conversationId.value = 'conv_' + Date.now();
    }
  } catch (error) {
    console.error('发送消息失败:', error);
    
    // 添加错误消息
    chatMessages.value.push({
      role: 'assistant',
      content: '抱歉，我遇到了一些问题。请稍后再试。'
    });
  } finally {
    loading.value = false;
  }
}

function usesuggestion(suggestion) {
  userInput.value = suggestion;
}

async function fetchRecommendations() {
  loadingRecommendations.value = true;
  
  try {
    // 这里应该调用API获取学习建议
    // const response = await api.getLearningRecommendations(props.userId, props.courseId);
    
    // 模拟API响应
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    recommendations.value = [
      {
        title: '复习机器学习基础概念',
        description: '根据你的学习进度，建议你复习机器学习的基本概念，特别是监督学习和无监督学习的区别。',
        link: '#'
      },
      {
        title: '完成"数据预处理"练习',
        description: '你已经学习了数据预处理的理论知识，现在是时候通过实践练习来巩固这些知识了。',
        link: '#'
      },
      {
        title: '参加下周的在线讨论',
        description: '下周二将有一个关于深度学习的在线讨论，这对你的学习会很有帮助。',
        link: '#'
      }
    ];
  } catch (error) {
    console.error('获取学习建议失败:', error);
    recommendations.value = [];
  } finally {
    loadingRecommendations.value = false;
  }
}
</script> 