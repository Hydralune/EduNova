<template>
  <div class="material-preview-container">
    <!-- 左侧文件列表 -->
    <div class="file-sidebar">
      <h3 class="text-lg font-semibold mb-4">课程文件</h3>
      <div v-if="materials.length > 0" class="space-y-2">
        <div 
          v-for="material in materials" 
          :key="material.id" 
          @click="selectMaterial(material)"
          class="file-item p-2 rounded-md cursor-pointer flex items-center"
          :class="{'bg-blue-100': selectedMaterial && selectedMaterial.id === material.id}"
        >
          <span class="mr-2" v-html="getMaterialIcon(material.material_type)"></span>
          <div class="truncate">
            <p class="font-medium truncate">{{ material.title }}</p>
            <p class="text-xs text-gray-500">{{ material.material_type }} · {{ material.size }}</p>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-4">
        <p class="text-gray-500">暂无课件资源</p>
      </div>
      <div class="mt-4">
        <button @click="closePreview" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md w-full">
          返回课程
        </button>
      </div>
    </div>

    <!-- 右侧预览区域 -->
    <div class="preview-area">
      <div v-if="selectedMaterial" class="preview-content">
        <div class="preview-header">
          <h2 class="text-xl font-bold">{{ selectedMaterial.title }}</h2>
          <div class="text-sm text-gray-500 mb-4">
            {{ selectedMaterial.material_type }} · {{ selectedMaterial.size }}
          </div>
          <div class="flex space-x-3">
            <button @click="downloadMaterial(selectedMaterial.id)" class="text-blue-600 hover:text-blue-800">
              下载
            </button>
          </div>
        </div>
        
        <div class="preview-body">
          <!-- PDF 预览 -->
          <div v-if="isPdfFile(selectedMaterial)" class="pdf-preview">
            <PdfViewer 
              :pdf-url="getFileUrl(selectedMaterial.file_path || '')" 
              @download="downloadMaterial(selectedMaterial.id)" 
            />
          </div>
          
          <!-- Markdown预览 -->
          <div v-else-if="isMarkdownFile(selectedMaterial)" class="markdown-preview">
            <MarkdownViewer 
              :url="getFileUrl(selectedMaterial.file_path || '')" 
            />
          </div>
          
          <!-- 图片预览 -->
          <div v-else-if="isImageFile(selectedMaterial)" class="image-preview">
            <img :src="getFileUrl(selectedMaterial.file_path)" alt="图片预览" class="max-w-full max-h-[600px] mx-auto" />
          </div>
          
          <!-- 视频预览 -->
          <div v-else-if="isVideoFile(selectedMaterial)" class="video-preview">
            <video 
              :src="getFileUrl(selectedMaterial.file_path)" 
              controls 
              preload="metadata"
              controlsList="nodownload"
              class="w-full max-h-[600px]"
            ></video>
            <div class="mt-4 text-center">
              <p class="text-sm text-gray-500">如果视频加载缓慢或无法播放，请尝试下载后观看</p>
              <div class="flex justify-center space-x-4 mt-2">
                <a 
                  :href="getFileUrl(selectedMaterial.file_path)" 
                  target="_blank" 
                  class="px-4 py-2 bg-blue-600 text-white rounded-md"
                >
                  在新窗口打开
                </a>
                <button 
                  @click="downloadMaterial(selectedMaterial.id)" 
                  class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md"
                >
                  下载视频
                </button>
              </div>
            </div>
          </div>
          
          <!-- 文本预览 -->
          <div v-else-if="isTextFile(selectedMaterial)" class="text-preview">
            <div v-if="textContent" class="p-4 border rounded-md bg-gray-50 whitespace-pre-wrap">
              {{ textContent }}
            </div>
            <div v-else class="flex justify-center items-center h-[400px]">
              <p class="text-gray-500">加载文本内容中...</p>
            </div>
          </div>
          
          <!-- Office文档预览 (Word, PowerPoint, Excel) -->
          <div v-else-if="isOfficeDocument(selectedMaterial.material_type)" class="office-preview">
            <div class="flex flex-col items-center justify-center h-[400px]">
              <div class="text-6xl text-gray-300 mb-4" v-html="getMaterialIcon(selectedMaterial.material_type)"></div>
              <p class="text-xl text-gray-500 mb-2">使用Office Online预览</p>
              <p class="text-gray-400 mb-4">您可以使用Microsoft Office Online预览此文件</p>
              <div class="flex space-x-4">
                <a 
                  :href="getOfficeOnlineViewerUrl(selectedMaterial.file_path)" 
                  target="_blank" 
                  class="px-6 py-2 bg-blue-600 text-white rounded-md"
                >
                  在线预览
                </a>
                <button 
                  @click="downloadMaterial(selectedMaterial.id)" 
                  class="px-6 py-2 bg-gray-200 text-gray-800 rounded-md"
                >
                  下载文件
                </button>
              </div>
            </div>
          </div>
          
          <!-- 不支持预览的文件类型 -->
          <div v-else class="unsupported-preview flex flex-col items-center justify-center h-[400px]">
            <div class="text-6xl text-gray-300 mb-4" v-html="getMaterialIcon(selectedMaterial.material_type)"></div>
            <p class="text-xl text-gray-500 mb-2">无法预览此类型的文件</p>
            <p class="text-gray-400 mb-4">{{ selectedMaterial.material_type }} 文件需要下载后查看</p>
            <button 
              @click="downloadMaterial(selectedMaterial.id)" 
              class="px-6 py-2 bg-blue-600 text-white rounded-md"
            >
              下载文件
            </button>
          </div>
        </div>
      </div>
      <div v-else class="flex items-center justify-center h-full">
        <div class="text-center">
          <p class="text-xl text-gray-500 mb-4">请从左侧选择一个文件进行预览</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, defineProps, defineEmits, watch, computed } from 'vue';
import { materialAPI } from '../../api';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import PdfViewer from './PdfViewer.vue';
import MarkdownViewer from './MarkdownViewer.vue';

interface Material {
  id: number;
  title: string;
  material_type: string;
  file_path?: string;
  size: string;
  course_id: number;
  created_at: string;
  updated_at: string;
}

const props = defineProps({
  courseId: {
    type: [Number, String],
    required: true
  },
  initialMaterialId: {
    type: [Number, String],
    default: null
  }
});

const emit = defineEmits(['close']);

const materials = ref<Material[]>([]);
const selectedMaterial = ref<Material | null>(null);
const textContent = ref<string | null>(null);
const markdownContent = ref<string | null>(null);

const renderedMarkdown = computed(() => {
  if (!markdownContent.value) return '';
  try {
    // 使用marked将Markdown转换为HTML，并使用DOMPurify进行清洁以防止XSS攻击
    const html = marked.parse(markdownContent.value);
    return typeof html === 'string' ? DOMPurify.sanitize(html) : '';
  } catch (error) {
    console.error('Markdown渲染错误:', error);
    return '无法渲染Markdown内容';
  }
});

onMounted(async () => {
  await fetchMaterials();
  if (props.initialMaterialId) {
    const material = materials.value.find(m => m.id === Number(props.initialMaterialId));
    if (material) {
      selectMaterial(material);
    }
  } else if (materials.value.length > 0) {
    selectMaterial(materials.value[0]);
  }
});

async function fetchMaterials() {
  try {
    const response = await materialAPI.getMaterials(Number(props.courseId));
    const responseData = response as any;
    materials.value = responseData.materials as Material[];
  } catch (error) {
    console.error('获取课件资源失败:', error);
  }
}

function selectMaterial(material: Material) {
  selectedMaterial.value = material;
  textContent.value = null;
  markdownContent.value = null;
  
  console.log('选择的文件:', material);
  console.log('文件类型:', material.material_type);
  console.log('文件名:', material.title);
  console.log('文件路径:', material.file_path);
  
  // 检查各种文件类型
  console.log('文件类型检测结果:');
  console.log('- PDF:', isPdfFile(material));
  console.log('- Markdown:', isMarkdownFile(material));
  console.log('- 图片:', isImageFile(material));
  console.log('- 视频:', isVideoFile(material));
  console.log('- 文本:', isTextFile(material));
  
  // 检查是否为Markdown文件
  if (isMarkdownFile(material)) {
    console.log('检测到Markdown文件，加载Markdown内容');
    fetchMarkdownContent(material.file_path || '');
  } 
  // 检查是否为文本文件
  else if (isTextFile(material)) {
    console.log('检测到文本文件，加载文本内容');
    fetchTextContent(material.file_path || '');
  }
}

async function fetchTextContent(filePath: string) {
  try {
    const response = await fetch(getFileUrl(filePath));
    if (response.ok) {
      textContent.value = await response.text();
    } else {
      textContent.value = '无法加载文本内容';
    }
  } catch (error) {
    console.error('加载文本内容失败:', error);
    textContent.value = '加载文本内容失败';
  }
}

async function fetchMarkdownContent(filePath: string) {
  try {
    const response = await fetch(getFileUrl(filePath));
    if (response.ok) {
      markdownContent.value = await response.text();
    } else {
      markdownContent.value = '无法加载Markdown内容';
    }
  } catch (error) {
    console.error('加载Markdown内容失败:', error);
    markdownContent.value = '加载Markdown内容失败';
  }
}

function getFileUrl(filePath: string | undefined): string {
  if (!filePath) return '';
  // 确保文件路径以 / 开头
  if (!filePath.startsWith('/')) {
    filePath = '/' + filePath;
  }
  
  // 检查是否已经是完整URL
  if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
    return filePath;
  }
  
  // 使用API服务器地址
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';
  return `${apiBaseUrl}${filePath}`;
}

function downloadMaterial(materialId: number) {
  materialAPI.downloadMaterial(materialId);
}

function closePreview() {
  emit('close');
}

function getMaterialIcon(materialType: string) {
  const type = materialType.toLowerCase();
  switch (type) {
    case 'pdf':
      return `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      `;
    case 'powerpoint':
      return `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      `;
    case 'word':
      return `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      `;
    case 'excel':
      return `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      `;
    case 'image':
      return `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      `;
    case 'video':
      return `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-pink-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      `;
    case 'archive':
      return `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
        </svg>
      `;
    case 'text':
      return `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      `;
    default:
      return `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      `;
  }
}

function isMdFile(title: string) {
  // 检查是否为Markdown文件
  return title.toLowerCase().endsWith('.md');
}

function isOfficeDocument(materialType: string) {
  // 检查是否为Office文档类型
  const type = materialType.toLowerCase();
  return type === 'word' || type === 'powerpoint' || type === 'excel' || 
         type === 'docx' || type === 'doc' || type === 'pptx' || type === 'ppt' || 
         type === 'xlsx' || type === 'xls';
}

function getOfficeOnlineViewerUrl(filePath: string | undefined) {
  if (!filePath) return '';
  // 使用Microsoft Office Online Viewer
  const fileUrl = getFileUrl(filePath);
  return `https://view.officeapps.live.com/op/view.aspx?src=${encodeURIComponent(fileUrl)}`;
}

function isPdfFile(material: Material | null) {
  if (!material) return false;
  // 检查文件类型或文件扩展名
  const type = material.material_type.toLowerCase();
  const title = material.title.toLowerCase();
  console.log(`PDF检测: 类型=${type}, 文件名=${title}`);
  return type === 'pdf' || title.endsWith('.pdf');
}

function isImageFile(material: Material | null) {
  if (!material) return false;
  // 检查文件类型或文件扩展名
  const type = material.material_type.toLowerCase();
  const title = material.title.toLowerCase();
  const imageExts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'];
  return type === 'image' || imageExts.some(ext => title.endsWith(ext));
}

function isVideoFile(material: Material | null) {
  if (!material) return false;
  // 检查文件类型或文件扩展名
  const type = material.material_type.toLowerCase();
  const title = material.title.toLowerCase();
  const videoExts = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.3gp'];
  return type === 'video' || videoExts.some(ext => title.endsWith(ext));
}

function isMarkdownFile(material: Material | null) {
  if (!material) return false;
  // 检查文件类型和文件扩展名
  const type = material.material_type.toLowerCase();
  const title = material.title.toLowerCase();
  console.log(`Markdown检测: 类型=${type}, 文件名=${title}`);
  return type === 'markdown' || title.endsWith('.md') || title.endsWith('.markdown');
}

function isTextFile(material: Material | null) {
  if (!material) return false;
  // 检查文件类型或文件扩展名，但排除Markdown
  const type = material.material_type.toLowerCase();
  const title = material.title.toLowerCase();
  // 如果是Markdown，不算作普通文本
  if (isMarkdownFile(material)) return false;
  const textExts = ['.txt', '.log', '.json', '.xml', '.csv', '.html', '.css', '.js'];
  return type === 'text' || textExts.some(ext => title.endsWith(ext));
}
</script>

<style scoped>
.material-preview-container {
  display: grid;
  grid-template-columns: 300px 1fr;
  height: 100%;
  min-height: 600px;
}

.file-sidebar {
  padding: 1.5rem;
  border-right: 1px solid #e5e7eb;
  overflow-y: auto;
  background-color: #f9fafb;
  height: 100%;
}

.file-item {
  transition: all 0.2s;
}

.file-item:hover {
  background-color: #e5e7eb;
}

.preview-area {
  padding: 1.5rem;
  overflow-y: auto;
  height: 100%;
}

.preview-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

/* Markdown样式 */
.markdown-body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 16px;
  line-height: 1.6;
  word-wrap: break-word;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-body h1 {
  font-size: 2em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body h2 {
  font-size: 1.5em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body h3 {
  font-size: 1.25em;
}

.markdown-body p,
.markdown-body blockquote,
.markdown-body ul,
.markdown-body ol,
.markdown-body dl,
.markdown-body table,
.markdown-body pre {
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-body code {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(27, 31, 35, 0.05);
  border-radius: 3px;
}

.markdown-body pre {
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 3px;
}

.markdown-body pre code {
  display: inline;
  padding: 0;
  margin: 0;
  overflow: visible;
  line-height: inherit;
  word-wrap: normal;
  background-color: transparent;
  border: 0;
}

.markdown-body blockquote {
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
}

.markdown-body ul,
.markdown-body ol {
  padding-left: 2em;
}

.markdown-body ul {
  list-style-type: disc;
}

.markdown-body ol {
  list-style-type: decimal;
}

.markdown-body table {
  display: block;
  width: 100%;
  overflow: auto;
  border-spacing: 0;
  border-collapse: collapse;
}

.markdown-body table th,
.markdown-body table td {
  padding: 6px 13px;
  border: 1px solid #dfe2e5;
}

.markdown-body table tr {
  background-color: #fff;
  border-top: 1px solid #c6cbd1;
}

.markdown-body table tr:nth-child(2n) {
  background-color: #f6f8fa;
}

.markdown-body img {
  max-width: 100%;
  box-sizing: content-box;
}
</style> 