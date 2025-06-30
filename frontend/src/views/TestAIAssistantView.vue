<template>
  <div class="test-ai-assistant">
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-8 text-center">AI助手功能测试</h1>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- 普通模式测试 -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-semibold mb-4">普通AI问答模式</h2>
          <p class="text-gray-600 mb-4">测试基本的AI对话功能，不涉及知识库检索。</p>
          <AIAssistant />
        </div>
        
        <!-- RAG模式测试 -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-semibold mb-4">知识库增强模式</h2>
          <p class="text-gray-600 mb-4">测试RAG功能，需要选择课程并确保该课程有知识库。</p>
          <AIAssistant :courseId="1" />
        </div>
      </div>
      
      <!-- 功能说明 -->
      <div class="mt-8 bg-blue-50 rounded-lg p-6">
        <h3 class="text-lg font-semibold mb-4">功能说明</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 class="font-medium text-blue-800">普通AI问答模式</h4>
            <ul class="text-sm text-gray-700 mt-2 space-y-1">
              <li>• 基本的AI对话功能</li>
              <li>• 不依赖知识库</li>
              <li>• 响应速度快</li>
              <li>• 适合一般性问题</li>
            </ul>
          </div>
          <div>
            <h4 class="font-medium text-blue-800">知识库增强模式</h4>
            <ul class="text-sm text-gray-700 mt-2 space-y-1">
              <li>• 基于课程知识库的智能问答</li>
              <li>• 支持向量检索和语义搜索</li>
              <li>• 提供更准确的课程相关回答</li>
              <li>• 显示参考来源</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AIAssistant from '../components/ai/AIAssistant.vue'
</script>

<style scoped>
.test-ai-assistant {
  min-height: 100vh;
  background-color: #f8fafc;
}
</style> 