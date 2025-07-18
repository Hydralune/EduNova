<template>
  <div class="markdown-viewer">
    <div v-if="loading" class="flex justify-center items-center p-8">
      <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
      <span class="ml-2 text-gray-500">加载中...</span>
    </div>
    <div v-else-if="error" class="p-6 bg-red-50 text-red-500 rounded-md">
      <p class="mb-4">{{ error }}</p>
      <p class="mb-4">此文件可能是Markdown文件但无法正确加载。您可以尝试以下操作：</p>
      <div class="flex space-x-4">
        <a :href="url" download class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
          下载文件
        </a>
        <button @click="retryLoad" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300">
          重试加载
        </button>
      </div>
      <div class="mt-4 p-4 bg-gray-100 rounded text-xs overflow-auto max-h-40">
        <p class="font-bold">调试信息：</p>
        <p>URL: {{ url }}</p>
        <p>错误信息: {{ debugInfo }}</p>
      </div>
    </div>
    <div v-else-if="markdownContent" class="markdown-body p-6 bg-white rounded-md" v-html="renderedContent"></div>
    <div v-else class="p-6 bg-gray-50 text-gray-500 rounded-md">
      无内容可显示
      <div v-if="url" class="mt-4">
        <p>请求上传文件: {{ url }}</p>
        <a :href="url" download class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 inline-block mt-2">
          下载文件
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import DOMPurify from 'dompurify';
import 'github-markdown-css/github-markdown.css';
import 'highlight.js/styles/github.css';

const props = defineProps({
  content: {
    type: String,
    default: ''
  },
  url: {
    type: String,
    default: ''
  }
});

const loading = ref(false);
const error = ref<string | null>(null);
const debugInfo = ref<string>('');
const markdownContent = ref<string>('');

// 初始化markdown-it实例，配置代码高亮
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str: string, lang: string): string {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code>' +
               hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
               '</code></pre>';
      } catch (__) {}
    }
    return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>';
  }
});

// 计算属性：渲染后的内容
const renderedContent = computed(() => {
  if (!markdownContent.value) return '';
  try {
    // 预处理Markdown内容
    let processedContent = preprocessMarkdown(markdownContent.value);
    
    // 渲染处理后的内容
    const html = md.render(processedContent);
    return DOMPurify.sanitize(html);
  } catch (err) {
    console.error('Markdown渲染错误:', err);
    error.value = '无法渲染Markdown内容';
    debugInfo.value = err instanceof Error ? err.message : String(err);
    return '';
  }
});

// Markdown预处理函数
function preprocessMarkdown(content: string): string {
  // 移除开头的```markdown标记
  let processed = content.replace(/^\s*```markdown\s*\n/i, '');
  
  // 移除结尾的```标记
  processed = processed.replace(/\n\s*```\s*$/i, '');
  
  // 移除内容中可能导致渲染问题的说明部分
  processed = processed.replace(/\n\s*说明[\s\S]*$/, '');
  
  // 移除其他可能的元信息标记
  processed = processed.replace(/\n\s*结构设计:[\s\S]*$/, '');
  processed = processed.replace(/\n\s*内容适配:[\s\S]*$/, '');
  processed = processed.replace(/\n\s*引用处理:[\s\S]*$/, '');
  
  return processed;
}

// 监听props变化
watch(() => props.content, (newContent) => {
  if (newContent) {
    markdownContent.value = newContent;
    error.value = null;
    debugInfo.value = '';
  }
});

watch(() => props.url, (newUrl) => {
  if (newUrl) {
    fetchMarkdownFromUrl(newUrl);
  }
});

onMounted(() => {
  if (props.content) {
    markdownContent.value = props.content;
  } else if (props.url) {
    fetchMarkdownFromUrl(props.url);
  }
});

async function fetchMarkdownFromUrl(url: string) {
  loading.value = true;
  error.value = null;
  debugInfo.value = '';
  
  try {
    console.log(`正在从URL获取Markdown: ${url}`);
    
    // 使用简单的fetch请求，不添加额外参数
    const response = await fetch(url);
    
    console.log(`响应状态: ${response.status} ${response.statusText}`);
    
    // 记录响应头信息
    const headers: Record<string, string> = {};
    response.headers.forEach((value, key) => {
      headers[key] = value;
    });
    console.log('响应头:', headers);
    
    if (response.ok) {
      // 直接使用文本内容
      const text = await response.text();
      console.log(`获取到的内容长度: ${text.length}字节`);
      
      if (text.length > 0) {
        console.log(`内容预览: ${text.substring(0, 100)}...`);
        markdownContent.value = text;
        console.log('成功加载Markdown内容');
      } else {
        error.value = '获取到的Markdown内容为空';
        debugInfo.value = `响应码: ${response.status}, 内容长度: 0`;
      }
    } else {
      error.value = `无法加载Markdown内容: ${response.status} ${response.statusText}`;
      debugInfo.value = `响应码: ${response.status}, 状态文本: ${response.statusText}`;
      console.error(`无法加载Markdown内容: ${response.status} ${response.statusText}`);
    }
  } catch (err) {
    console.error('加载Markdown内容失败:', err);
    error.value = '加载Markdown内容失败，请检查网络连接';
    debugInfo.value = err instanceof Error ? err.message : String(err);
  } finally {
    loading.value = false;
  }
}

function retryLoad() {
  if (props.url) {
    fetchMarkdownFromUrl(props.url);
  }
}
</script>

<style>
.markdown-viewer {
  width: 100%;
  max-width: 100%;
  overflow: auto;
}

/* 覆盖github-markdown-css的一些样式 */
.markdown-body {
  box-sizing: border-box;
  min-width: 200px;
  max-width: 100%;
  margin: 0 auto;
  color: #24292e;
}

.markdown-body pre {
  background-color: #f6f8fa;
  border-radius: 3px;
  font-size: 85%;
  line-height: 1.45;
  overflow: auto;
  padding: 16px;
}

.markdown-body code {
  background-color: rgba(27,31,35,.05);
  border-radius: 3px;
  font-size: 85%;
  margin: 0;
  padding: 0.2em 0.4em;
}

.markdown-body img {
  max-width: 100%;
  box-sizing: content-box;
}

@media (prefers-color-scheme: dark) {
  .markdown-body {
    color: #c9d1d9;
    background-color: #0d1117;
  }
  
  .markdown-body a {
    color: #58a6ff;
  }
  
  .markdown-body hr {
    border-color: #30363d;
  }
  
  .markdown-body pre {
    background-color: #161b22;
  }
  
  .markdown-body code {
    background-color: rgba(240,246,252,0.15);
  }
}
</style> 