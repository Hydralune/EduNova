<template>
  <div>
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>

    <div v-else-if="showMaterialPreview" class="bg-white rounded-lg shadow-md overflow-hidden">
      <MaterialPreview 
        :courseId="courseId" 
        :initialMaterialId="previewMaterialId"
        @close="showMaterialPreview = false"
      />
    </div>

    <div v-else-if="course" class="bg-white rounded-lg shadow-md overflow-hidden">
      <!-- 课程头部信息 -->
      <div class="p-6 border-b">
        <div class="flex justify-between items-start">
          <div>
            <h1 class="text-2xl font-bold mb-2">{{ course.name }}</h1>
            <p class="text-gray-600 mb-4">{{ course.description }}</p>
            <div class="flex flex-wrap gap-2 mb-2">
              <span class="px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-800">
                {{ course.category }}
              </span>
              <span :class="[
                'px-3 py-1 rounded-full text-sm', 
                difficultyClass(course.difficulty)
              ]">
                {{ difficultyText(course.difficulty) }}
              </span>
            </div>
            <p class="text-sm text-gray-500">
              教师: {{ course.teacher_name }}
            </p>
          </div>
        </div>
      </div>

      <!-- 选项卡导航 -->
      <div class="border-b">
        <nav class="flex">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-6 py-3 text-center border-b-2 font-medium',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <!-- 选项卡内容 -->
      <div class="tab-content">
        <!-- 章节内容 -->
        <div v-if="activeTab === 'chapters'" class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold">章节内容</h3>
            <button 
              v-if="canEdit" 
              @click="showAddChapterModal = true"
              class="px-4 py-2 bg-blue-600 text-white rounded-md"
            >
              添加章节
            </button>
          </div>

          <div v-if="course.chapters && course.chapters.length > 0" class="space-y-4">
            <div v-for="(chapter, index) in course.chapters" :key="index" class="border rounded-md overflow-hidden">
              <div class="flex justify-between items-center p-4 bg-gray-50">
                <h4 class="font-medium">{{ chapter.title }}</h4>
                <span class="text-sm text-gray-500">{{ chapter.duration }}分钟</span>
              </div>
              <div v-if="chapter.sections && chapter.sections.length > 0" class="divide-y">
                <div v-for="(section, sectionIndex) in chapter.sections" :key="sectionIndex" class="p-4 pl-8 flex justify-between items-center">
                  <span>{{ section.title }}</span>
                  <span class="text-sm text-gray-500">{{ section.duration }}分钟</span>
                </div>
              </div>
              <div v-else class="p-4 pl-8 text-gray-500 italic">
                暂无小节内容
              </div>
            </div>
          </div>
          <div v-else class="text-center py-10">
            <p class="text-gray-500">暂无章节内容</p>
            <button 
              v-if="canEdit" 
              @click="showAddChapterModal = true"
              class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md"
            >
              添加章节
            </button>
          </div>
        </div>

        <!-- 课件资源 -->
        <div v-else-if="activeTab === 'materials'" class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold">课件资源</h3>
            <button 
              @click="showAddMaterialModal = true"
              class="px-4 py-2 bg-blue-600 text-white rounded-md"
            >
              上传课件
            </button>
          </div>

          <div v-if="materials.length > 0" class="space-y-4">
            <div v-for="material in materials" :key="material.id" class="flex items-center justify-between p-4 border rounded-md">
              <div class="flex items-center">
                <span class="mr-3" v-html="getMaterialIcon(material.material_type)"></span>
                <div>
                  <p class="font-medium">{{ material.title }}</p>
                  <p class="text-sm text-gray-500">{{ material.material_type }} · {{ material.size }}</p>
                  <!-- 知识库状态显示 -->
                  <div v-if="material.file_path" class="mt-1">
                    <span v-if="isSupportedForKnowledgeBase(material)" class="text-xs px-2 py-1 rounded-full bg-green-100 text-green-800">
                      支持知识库
                    </span>
                    <span v-else class="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600">
                      不支持知识库
                    </span>
                  </div>
                </div>
              </div>
              <div class="flex space-x-3">
                <button @click="previewMaterial(material.id)" class="text-blue-600 hover:text-blue-800">预览</button>
                <button @click="downloadMaterial(material.id)" class="text-blue-600 hover:text-blue-800">下载</button>
                <button 
                  v-if="isSupportedForKnowledgeBase(material)"
                  @click="addToKnowledgeBase(material)"
                  class="text-green-600 hover:text-green-800 disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="isProcessingKnowledgeBase(material) || knowledgeBaseProcessing[material.id]"
                >
                  {{ getKnowledgeBaseButtonText(material) }}
                </button>
                <button @click="confirmDeleteMaterial(material)" class="text-red-600 hover:text-red-800">删除</button>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-10">
            <p class="text-gray-500">暂无课件资源</p>
          </div>
        </div>

        <!-- 评估测验 -->
        <div v-else-if="activeTab === 'assessments'" class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold">评估测验</h3>
            <button 
              v-if="canEdit" 
              @click="createNewAssessment"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              创建评估
            </button>
          </div>

          <div v-if="assessments.length > 0" class="space-y-4">
            <div 
              v-for="assessment in assessments" 
              :key="assessment.id" 
              class="bg-white p-6 rounded-lg shadow-md border border-gray-200"
            >
              <div class="flex justify-between items-start">
                <div>
                  <h4 class="text-lg font-semibold">{{ assessment.title }}</h4>
                  <p class="text-sm text-gray-600">{{ assessment.description }}</p>
                  <div class="mt-2 flex flex-wrap gap-x-4 gap-y-2 text-sm text-gray-500">
                    <span>总分: {{ assessment.total_score }}</span>
                    <span>题目数: {{ getTotalQuestions(assessment) }}</span>
                    <span>时间限制: {{ assessment.duration || '无限制' }}</span>
                    <span>截止日期: {{ formatDate(assessment.due_date) }}</span>
                    <span>尝试次数: {{ assessment.max_attempts || '无限制' }}</span>
                  </div>
                </div>
                
                <div class="flex flex-col gap-2">
                  <span 
                    :class="getStatusClass(assessment)"
                    class="px-2 py-1 text-xs rounded-full"
                  >
                    {{ getStatusText(assessment) }}
                  </span>
                  
                  <div class="flex gap-2 mt-2">
                    <router-link 
                      :to="`/assessments/${assessment.id}`" 
                      class="text-blue-600 hover:text-blue-800"
                    >
                      查看
                    </router-link>
                    
                    <button 
                      v-if="canEdit"
                      @click="editAssessment(assessment)"
                      class="text-green-600 hover:text-green-800"
                    >
                      编辑
                    </button>
                    
                    <button 
                      v-if="canEdit"
                      @click="confirmDeleteAssessment(assessment)"
                      class="text-red-600 hover:text-red-800"
                    >
                      删除
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-10">
            <p class="text-gray-500">暂无评估测验</p>
            <button 
              v-if="canEdit"
              @click="createNewAssessment"
              class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              创建评估
            </button>
          </div>
        </div>

        <!-- 学生列表 -->
        <div v-else-if="activeTab === 'students'" class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold">学生列表</h3>
            <button 
              v-if="canEdit" 
              @click="showAddStudentsModal = true"
              class="px-4 py-2 bg-blue-600 text-white rounded-md"
            >
              添加学生
            </button>
          </div>

          <div v-if="loading" class="flex justify-center py-10">
            <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>

          <div v-else-if="students.length > 0">
            <div class="overflow-x-auto">
              <table class="min-w-full bg-white">
                <thead>
                  <tr>
                    <th class="py-2 px-4 border-b text-left">学号</th>
                    <th class="py-2 px-4 border-b text-left">姓名</th>
                    <th class="py-2 px-4 border-b text-left">邮箱</th>
                    <th class="py-2 px-4 border-b text-left">加入时间</th>
                    <th class="py-2 px-4 border-b text-left">操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="student in students" :key="student.id" class="hover:bg-gray-50">
                    <td class="py-2 px-4 border-b">{{ student.id }}</td>
                    <td class="py-2 px-4 border-b">{{ student.full_name }}</td>
                    <td class="py-2 px-4 border-b">{{ student.email }}</td>
                    <td class="py-2 px-4 border-b">{{ formatDate(student.enrollment_date) }}</td>
                    <td class="py-2 px-4 border-b">
                      <button 
                        v-if="canEdit"
                        @click="confirmRemoveStudent(student)"
                        class="text-red-600 hover:text-red-800"
                      >
                        移除
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div v-else class="text-center py-10">
            <p class="text-gray-500">暂无学生</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加课件模态框 -->
    <div v-if="showAddMaterialModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-lg">
        <h3 class="text-xl font-bold mb-4">上传课件资源</h3>
        <form @submit.prevent="uploadMaterial">
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">课件标题</label>
            <input v-model="materialTitle" type="text" class="w-full px-3 py-2 border rounded-md" placeholder="输入课件标题（可选，默认使用文件名）" />
          </div>
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">选择文件 <span class="text-red-500">*</span></label>
            <input type="file" @change="handleFileChange" class="w-full px-3 py-2 border rounded-md" required />
            <p v-if="materialFile" class="mt-2 text-sm text-gray-500">
              已选择: {{ materialFile.name }} ({{ (materialFile.size / 1024).toFixed(1) }}KB)
            </p>
          </div>
          
          <div v-if="materialUploadProgress > 0 && materialUploadProgress < 100" class="mb-4">
            <div class="w-full bg-gray-200 rounded-full h-2.5">
              <div class="bg-blue-600 h-2.5 rounded-full" :style="`width: ${materialUploadProgress}%`"></div>
            </div>
            <p class="text-sm text-gray-500 mt-1">上传中... {{ materialUploadProgress }}%</p>
          </div>
          
          <p v-if="materialUploadError" class="text-red-500 mb-4">{{ materialUploadError }}</p>
          
          <div class="flex justify-end gap-2 mt-6">
            <button type="button" @click="showAddMaterialModal = false" class="px-4 py-2 border rounded-md">取消</button>
            <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md">上传</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 添加学生模态框 -->
    <div v-if="showAddStudentsModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-lg">
        <h3 class="text-xl font-bold mb-4">添加学生到课程</h3>
        
        <div v-if="availableStudents.length === 0" class="text-center py-10">
          <p class="text-gray-500">没有可添加的学生</p>
        </div>
        
        <div v-else>
          <div class="mb-4">
            <p class="text-sm text-gray-600 mb-2">选择要添加到课程的学生：</p>
            <div class="max-h-60 overflow-y-auto border rounded-md p-2">
              <div 
                v-for="student in availableStudents" 
                :key="student.id"
                class="flex items-center p-2 hover:bg-gray-100 rounded-md cursor-pointer"
                @click="toggleStudentSelection(student.id)"
              >
                <input 
                  type="checkbox" 
                  :checked="selectedStudents.includes(student.id)" 
                  class="mr-3"
                />
                <div>
                  <div class="font-medium">{{ student.full_name }}</div>
                  <div class="text-sm text-gray-500">{{ student.email }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="flex justify-between items-center mt-4">
            <div class="text-sm text-gray-600">已选择 {{ selectedStudents.length }} 名学生</div>
            <div class="flex gap-2">
              <button type="button" @click="showAddStudentsModal = false" class="px-4 py-2 border rounded-md">取消</button>
              <button 
                @click="addStudents" 
                :disabled="selectedStudents.length === 0"
                :class="[
                  'px-4 py-2 text-white rounded-md',
                  selectedStudents.length === 0 ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
                ]"
              >
                添加
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../../stores/auth';
import { courseAPI, materialAPI, assessmentAPI } from '../../api';
import MaterialPreview from './MaterialPreview.vue';
import MarkdownViewer from './MarkdownViewer.vue';
import PdfViewer from './PdfViewer.vue';
import AIAssistant from '../ai/AIAssistant.vue';

// 定义接口
interface Course {
  id: number;
  name: string;
  description: string;
  category?: string;
  difficulty?: string;
  teacher_id?: number;
  teacher_name?: string;
  chapters?: Chapter[];
  is_public?: boolean;
  cover_image?: string;
}

interface Chapter {
  id?: number;
  title: string;
  duration: number;
  sections?: Section[];
}

interface Section {
  id?: number;
  title: string;
  duration: number;
  content?: string;
}

interface Material {
  id: number;
  title: string;
  description: string;
  file_path: string;
  material_type: string;
  size: string;
  upload_date: string;
  knowledge_base_status?: string;
}

interface Student {
  id: number;
  full_name: string;
  email: string;
  enrollment_date: string;
}

interface Assessment {
  id: number;
  title: string;
  description: string;
  course_id: number;
  total_score: number;
  duration?: number;
  start_date?: string;
  due_date?: string;
  max_attempts?: number;
  is_published: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  sections?: any[];
  questions?: any[];
  submission_count?: number;
}

// 路由参数
const route = useRoute();
const router = useRouter();
const courseId = computed(() => Number(route.params.id));

// 状态
const authStore = useAuthStore();
const loading = ref(true);
const course = ref<Course | null>(null);
const materials = ref<Material[]>([]);
const students = ref<Student[]>([]);
const availableStudents = ref<Student[]>([]);
const selectedStudents = ref<number[]>([]);
const isLoadingStudents = ref(false);
const studentError = ref<string | null>(null);
const activeTab = ref('chapters');
const assessments = ref<Assessment[]>([]);

// 模态框状态
const showAddChapterModal = ref(false);
const showAddMaterialModal = ref(false);
const showAddStudentsModal = ref(false);
const showMaterialPreview = ref(false);
const previewMaterialId = ref<number | undefined>();

// 知识库相关
const supportedKnowledgeBaseTypes = ref<string[]>([]);
const knowledgeBaseProcessing = ref<Record<number, boolean>>({});

// 添加缺失的材料上传相关属性
const materialTitle = ref('');
const materialFile = ref<File | null>(null);
const materialUploadProgress = ref(0);
const materialUploadError = ref('');

// 选项卡定义
const tabs = [
  { id: 'chapters', name: '章节内容' },
  { id: 'materials', name: '课件资源' },
  { id: 'assessments', name: '评估测验' },
  { id: 'students', name: '学生列表' },
];

// 是否可以编辑课程
const canEdit = computed(() => {
  const user = authStore.user;
  if (!user || !course.value) return false;
  return user.role === 'admin' || user.id === course.value.teacher_id;
});

// 监听选项卡变化
watch(activeTab, async (newTab) => {
  if (newTab === 'materials' && course.value?.id) {
    fetchKnowledgeBaseStatus();
  } else if (newTab === 'assessments' && course.value?.id) {
    await fetchAssessments();
  } else if (newTab === 'students' && course.value?.id) {
    await fetchStudents();
  }
});

// 初始化
onMounted(async () => {
  try {
    loading.value = true;
    await Promise.all([
      fetchCourse(),
      fetchMaterials(),
      fetchStudents(),
      fetchAssessments()
    ]);
  } catch (error) {
    console.error('加载数据失败:', error);
  } finally {
    loading.value = false;
  }
});

// 获取课程详情
async function fetchCourse() {
  try {
    const response = await courseAPI.getCourse(courseId.value);
    course.value = response as any;
  } catch (error) {
    console.error('获取课程详情失败:', error);
  }
}

// 获取课程材料
async function fetchMaterials() {
  try {
    const response = await materialAPI.getMaterials(courseId.value);
    materials.value = (response as any).materials || [];
  } catch (error) {
    console.error('获取课程材料失败:', error);
  }
}

// 获取课程学生
async function fetchStudents() {
  try {
    isLoadingStudents.value = true;
    studentError.value = null;
    const response = await courseAPI.getCourseStudents(courseId.value);
    students.value = (response as any).students || [];
  } catch (error) {
    console.error('获取学生列表失败:', error);
    studentError.value = '获取学生列表失败';
  } finally {
    isLoadingStudents.value = false;
  }
}

// 获取可添加的学生
async function fetchAvailableStudents() {
  try {
    isLoadingStudents.value = true;
    const response = await courseAPI.getAvailableStudents(courseId.value);
    availableStudents.value = (response as any).students || [];
  } catch (error) {
    console.error('获取可用学生失败:', error);
  } finally {
    isLoadingStudents.value = false;
  }
}

// 添加学生到课程
async function addStudents() {
  if (selectedStudents.value.length === 0) {
    alert('请选择至少一名学生');
    return;
  }
  
  try {
    await courseAPI.addStudentsToCourse(courseId.value, selectedStudents.value);
    
    // 关闭模态框
    showAddStudentsModal.value = false;
    
    // 重新获取学生列表
    fetchStudents();
  } catch (error) {
    console.error('添加学生失败:', error);
    alert('添加学生失败');
  }
}

// 打开添加学生模态框
function openAddStudentsModal() {
  showAddStudentsModal.value = true;
  selectedStudents.value = [];
  fetchAvailableStudents();
}

// 移除学生
async function confirmRemoveStudent(student: Student) {
  if (confirm(`确定要将学生 ${student.full_name} 从课程中移除吗？`)) {
    try {
      await courseAPI.removeStudentFromCourse(courseId.value, student.id);
      fetchStudents();
    } catch (error) {
      console.error('移除学生失败:', error);
      alert('移除学生失败');
    }
  }
}

// 获取课程评估
async function fetchAssessments() {
  try {
    const response = await assessmentAPI.getAssessments(courseId.value);
    assessments.value = (response as any).assessments || [];
  } catch (error) {
    console.error('获取评估列表失败:', error);
  }
}

// 创建新评估
function createNewAssessment() {
  router.push({
    name: 'AssessmentCreate',
    query: { courseId: courseId.value.toString() }
  });
}

// 编辑评估
function editAssessment(assessment: Assessment) {
  router.push({
    name: 'AssessmentEdit',
    params: { id: assessment.id.toString() }
  });
}

// 获取知识库支持的文件类型
async function fetchKnowledgeBaseStatus() {
  try {
    const response = await fetch('http://localhost:5001/api/rag/supported-types');
    const data = await response.json();
    supportedKnowledgeBaseTypes.value = data.supported_types || [];
  } catch (error) {
    console.error('获取知识库支持的文件类型失败:', error);
  }
}

// 判断文件是否支持添加到知识库
function isSupportedForKnowledgeBase(material: Material): boolean {
  const fileExtension = material.file_path.split('.').pop()?.toLowerCase();
  return supportedKnowledgeBaseTypes.value.includes(fileExtension || '');
}

// 获取知识库按钮文本
function getKnowledgeBaseButtonText(material: Material): string {
  if (knowledgeBaseProcessing.value[material.id]) {
    return '处理中...';
  }
  
  switch (material.knowledge_base_status) {
    case 'processing':
      return '处理中...';
    case 'completed':
      return '已添加';
    case 'failed':
      return '重新添加';
    default:
      return '添加到知识库';
  }
}

// 判断是否正在处理知识库
function isProcessingKnowledgeBase(material: Material): boolean {
  return material.knowledge_base_status === 'processing';
}

// 添加到知识库
async function addToKnowledgeBase(material: Material) {
  try {
    knowledgeBaseProcessing.value[material.id] = true;
    
    const response = await fetch('http://localhost:5001/api/rag/add-to-knowledge-base', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        file_path: material.file_path,
        title: material.title,
        course_id: courseId.value
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      // 更新材料状态
      const updatedMaterials = materials.value.map(m => {
        if (m.id === material.id) {
          return { ...m, knowledge_base_status: 'processing' };
        }
        return m;
      });
      materials.value = updatedMaterials;
    } else {
      alert('添加到知识库失败: ' + result.message);
    }
  } catch (error) {
    console.error('添加到知识库失败:', error);
    alert('添加到知识库失败');
  } finally {
    knowledgeBaseProcessing.value[material.id] = false;
  }
}

// 预览材料
function previewMaterial(materialId: number) {
  previewMaterialId.value = materialId;
  showMaterialPreview.value = true;
}

// 下载材料
function downloadMaterial(materialId: number) {
  materialAPI.downloadMaterial(materialId);
}

// 确认删除材料
function confirmDeleteMaterial(material: Material) {
  if (confirm(`确定要删除材料 "${material.title}" 吗？`)) {
    deleteMaterial(material.id);
  }
}

// 删除材料
async function deleteMaterial(materialId: number) {
  try {
    await materialAPI.deleteMaterial(materialId);
    materials.value = materials.value.filter(m => m.id !== materialId);
  } catch (error) {
    console.error('删除材料失败:', error);
    alert('删除材料失败');
  }
}

// 格式化日期
function formatDate(dateString?: string): string {
  if (!dateString) return '无';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// 获取材料图标
function getMaterialIcon(type: string): string {
  const icons: Record<string, string> = {
    'pdf': '<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd"></path></svg>',
    'doc': '<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd"></path></svg>',
    'docx': '<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd"></path></svg>',
    'ppt': '<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd"></path></svg>',
    'pptx': '<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd"></path></svg>',
    'xls': '<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd"></path></svg>',
    'xlsx': '<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd"></path></svg>',
    'txt': '<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd"></path></svg>',
    'md': '<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd"></path></svg>',
    'image': '<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd"></path></svg>',
    'video': '<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"></path><path d="M14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z"></path></svg>',
    'audio': '<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217z" clip-rule="evenodd"></path><path d="M14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.984 5.984 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.983 3.983 0 00-1.172-2.828 1 1 0 010-1.415z" clip-rule="evenodd"></path></svg>',
  };
  
  // 根据文件类型返回相应图标
  if (type.includes('image')) return icons['image'];
  if (type.includes('video')) return icons['video'];
  if (type.includes('audio')) return icons['audio'];
  
  // 根据文件扩展名返回图标
  const extension = type.split('/').pop()?.toLowerCase();
  return icons[extension as string] || '<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd"></path></svg>';
}

// 获取难度文本
function difficultyText(difficulty?: string): string {
  const map: Record<string, string> = {
    'beginner': '初级',
    'intermediate': '中级',
    'advanced': '高级'
  };
  return map[difficulty || 'beginner'] || '初级';
}

// 获取难度样式
function difficultyClass(difficulty?: string): string {
  const map: Record<string, string> = {
    'beginner': 'bg-green-100 text-green-800',
    'intermediate': 'bg-yellow-100 text-yellow-800',
    'advanced': 'bg-red-100 text-red-800'
  };
  return map[difficulty || 'beginner'] || 'bg-green-100 text-green-800';
}

// 获取评估状态文本
const getStatusText = (assessment: Assessment): string => {
  if (!assessment.is_published) return '草稿';
  if (!assessment.is_active) return '未激活';
  
  const now = new Date();
  const startDate = assessment.start_date ? new Date(assessment.start_date) : null;
  const dueDate = assessment.due_date ? new Date(assessment.due_date) : null;
  
  if (startDate && now < startDate) return '未开始';
  if (dueDate && now > dueDate) return '已结束';
  return '进行中';
};

// 获取评估状态样式
const getStatusClass = (assessment: Assessment): string => {
  const status = getStatusText(assessment);
  const classes: Record<string, string> = {
    '草稿': 'bg-gray-100 text-gray-800',
    '未激活': 'bg-gray-100 text-gray-800',
    '未开始': 'bg-yellow-100 text-yellow-800',
    '进行中': 'bg-green-100 text-green-800',
    '已结束': 'bg-red-100 text-red-800'
  };
  return classes[status] || 'bg-gray-100 text-gray-800';
};

const getTotalQuestions = (assessment: Assessment): number => {
  return assessment.questions?.length || 0;
};

const confirmDeleteAssessment = (assessment: Assessment): void => {
  if (confirm('确定要删除这个评估吗？')) {
    try {
      assessmentAPI.deleteAssessment(assessment.id);
      assessments.value = assessments.value.filter(a => a.id !== assessment.id);
    } catch (error) {
      console.error('删除评估失败:', error);
      alert('删除评估失败');
    }
  }
};

// 处理文件选择
function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    materialFile.value = target.files[0];
    if (!materialTitle.value) {
      materialTitle.value = materialFile.value.name;
    }
  }
}

// 上传材料
async function uploadMaterial() {
  if (!materialFile.value || !course.value) {
    materialUploadError.value = '请选择文件';
    return;
  }
  
  try {
    materialUploadProgress.value = 10;
    materialUploadError.value = '';
    
    const formData = new FormData();
    formData.append('file', materialFile.value);
    formData.append('title', materialTitle.value || materialFile.value.name);
    
    materialUploadProgress.value = 30;
    
    const response = await materialAPI.uploadMaterial(courseId.value, formData);
    
    materialUploadProgress.value = 100;
    
    // 清空表单
    materialFile.value = null;
    materialTitle.value = '';
    
    // 关闭模态框
    showAddMaterialModal.value = false;
    
    // 重新获取材料列表
    await fetchMaterials();
  } catch (error) {
    console.error('上传课件失败:', error);
    materialUploadError.value = '上传失败，请重试';
    materialUploadProgress.value = 0;
  }
}

// 切换学生选择状态
function toggleStudentSelection(studentId: number) {
  const index = selectedStudents.value.indexOf(studentId);
  if (index === -1) {
    selectedStudents.value.push(studentId);
  } else {
    selectedStudents.value.splice(index, 1);
  }
}
</script> 