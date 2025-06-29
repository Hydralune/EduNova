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
                </div>
              </div>
              <div class="flex space-x-3">
                <button @click="previewMaterial(material.id)" class="text-blue-600 hover:text-blue-800">预览</button>
                <button @click="downloadMaterial(material.id)" class="text-blue-600 hover:text-blue-800">下载</button>
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
              @click="showAddAssessmentModal = true"
              class="px-4 py-2 bg-blue-600 text-white rounded-md"
            >
              创建评估
            </button>
          </div>

          <div v-if="assessments.length > 0" class="space-y-4">
            <div v-for="assessment in assessments" :key="assessment.id" class="p-4 border rounded-md">
              <div class="flex items-center justify-between">
                <div>
                  <h4 class="font-medium">{{ assessment.title }}</h4>
                  <p class="text-sm text-gray-500">{{ assessment.type }} · {{ assessment.question_count }}题 · {{ assessment.time_limit }}分钟</p>
                </div>
                <button class="px-4 py-2 border rounded-md">开始</button>
              </div>
              <div class="mt-2">
                <p class="text-sm text-gray-700">{{ assessment.description }}</p>
              </div>
              <div class="mt-2 flex items-center text-sm text-gray-500">
                <span>截止日期: {{ assessment.due_date || '无' }}</span>
                <span class="mx-2">|</span>
                <span>尝试次数: {{ assessment.attempts || 0 }}/{{ assessment.max_attempts || '无限制' }}</span>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-10">
            <p class="text-gray-500">暂无评估测验</p>
          </div>
        </div>

        <!-- 学生管理 -->
        <div v-else-if="activeTab === 'students'" class="p-6">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-semibold">学生管理</h3>
            <div class="flex gap-2">
              <button 
                @click="openAddStudentModal"
                class="px-4 py-2 bg-blue-600 text-white rounded-md"
              >
                添加学生
              </button>
            </div>
          </div>

          <div class="mb-4">
            <div class="flex">
              <input 
                type="text" 
                v-model="studentSearch" 
                placeholder="搜索学生..." 
                class="flex-1 px-4 py-2 border rounded-l-md"
                @keyup.enter="filterStudents"
              />
              <button 
                @click="filterStudents"
                class="px-4 py-2 bg-gray-200 border-t border-r border-b rounded-r-md"
              >
                搜索
              </button>
            </div>
          </div>

          <div v-if="isLoadingStudents" class="flex justify-center py-10">
            <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>

          <div v-else-if="studentError" class="text-center py-10">
            <p class="text-red-500">{{ studentError }}</p>
            <button @click="fetchStudents" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md">重试</button>
          </div>

          <div v-else-if="students.length > 0" class="border rounded-md overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">学生</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">进度</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">最后活动</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="student in students" :key="student.id">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="flex-shrink-0 h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-500">
                        {{ student.name.charAt(0) }}
                      </div>
                      <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">{{ student.name }}</div>
                        <div class="text-sm text-gray-500">{{ student.email }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                      <div class="bg-blue-600 h-2.5 rounded-full" :style="`width: ${student.progress}%`"></div>
                    </div>
                    <div class="text-xs text-gray-500 mt-1">{{ student.progress }}%</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ student.last_activity }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <button @click="removeStudent(student.id)" class="text-red-600 hover:text-red-800">移除</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="text-center py-10">
            <p class="text-gray-500">暂无学生</p>
            <button @click="openAddStudentModal" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md">添加学生</button>
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
    <div v-if="showAddStudentModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
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
                  <div class="font-medium">{{ student.name }}</div>
                  <div class="text-sm text-gray-500">{{ student.email }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="flex justify-between items-center mt-4">
            <div class="text-sm text-gray-600">已选择 {{ selectedStudents.length }} 名学生</div>
            <div class="flex gap-2">
              <button type="button" @click="showAddStudentModal = false" class="px-4 py-2 border rounded-md">取消</button>
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
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '../../stores/auth';
import { courseAPI, materialAPI } from '../../api';
import MaterialPreview from './MaterialPreview.vue';

// 定义Course接口
interface CourseSection {
  title: string;
  duration: number;
}

interface CourseChapter {
  title: string;
  duration: number;
  sections: CourseSection[];
}

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

interface Student {
  id: number;
  name: string;
  email: string;
  progress: number;
  last_activity: string;
}

interface AvailableStudent {
  id: number;
  name: string;
  email: string;
  role: string;
}

interface Course {
  id: number;
  name: string;
  description: string;
  category: string;
  difficulty: string;
  teacher_id: number;
  teacher_name: string;
  student_count: number;
  material_count: number;
  assessment_count: number;
  is_public?: boolean;
  cover_image?: string;
  chapters?: CourseChapter[];
  created_at?: string;
  updated_at?: string;
}

const props = defineProps({
  id: {
    type: [Number, String],
    required: true
  }
});

const authStore = useAuthStore();
const courseId = computed(() => props.id);
const userRole = computed(() => authStore.user?.role || '');

const loading = ref(true);
const course = ref<Course | null>(null);
const activeTab = ref('chapters');
const studentSearch = ref('');
const showAddChapterModal = ref(false);
const showAddMaterialModal = ref(false);
const showAddAssessmentModal = ref(false);
const showAddStudentModal = ref(false);
const showMaterialPreview = ref(false);
const previewMaterialId = ref(0);

const tabs = [
  { id: 'chapters', name: '章节内容' },
  { id: 'materials', name: '课件资源' },
  { id: 'assessments', name: '评估测验' },
  { id: 'students', name: '学生管理' },
];

const canEdit = computed(() => {
  return userRole.value === 'admin' || 
         userRole.value === 'teacher' && course.value?.teacher_id === authStore.user?.id;
});

// 材料数据
const materials = ref<Material[]>([]);
const materialFile = ref<File | null>(null);
const materialTitle = ref('');
const materialUploadProgress = ref(0);
const materialUploadError = ref('');

const assessments = ref([
  {
    id: 1,
    title: '第一章测验',
    type: '测验',
    question_count: 10,
    time_limit: 30,
    description: '测试对第一章内容的理解',
    due_date: '2025-07-15',
    attempts: 0,
    max_attempts: 3,
  },
]);

const students = ref<Student[]>([]);
const availableStudents = ref<AvailableStudent[]>([]);
const selectedStudents = ref<number[]>([]);
const isLoadingStudents = ref(false);
const studentError = ref('');

onMounted(async () => {
  await fetchCourseDetail();
  if (course.value) {
    await fetchMaterials();
    await fetchStudents();
  }
});

async function fetchCourseDetail() {
  loading.value = true;
  try {
    // 调用API获取课程详情
    const response = await courseAPI.getCourse(Number(courseId.value));
    
    // 处理API响应 - 根据API文档，response已经是解析后的数据
    course.value = response as unknown as Course;
    loading.value = false;
  } catch (error) {
    console.error('获取课程详情失败:', error);
    loading.value = false;
  }
}

async function fetchMaterials() {
  try {
    if (!course.value) return;
    
    const response = await materialAPI.getMaterials(course.value.id);
    // 处理API响应
    const responseData = response as any;
    materials.value = responseData.materials as Material[];
  } catch (error) {
    console.error('获取课件资源失败:', error);
  }
}

function difficultyClass(difficulty: string): string {
  switch (difficulty) {
    case 'beginner': return 'bg-green-100 text-green-800';
    case 'intermediate': return 'bg-yellow-100 text-yellow-800';
    case 'advanced': return 'bg-red-100 text-red-800';
    default: return 'bg-gray-100 text-gray-800';
  }
}

function difficultyText(difficulty: string): string {
  switch (difficulty) {
    case 'beginner': return '初级';
    case 'intermediate': return '中级';
    case 'advanced': return '高级';
    default: return '未知';
  }
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    materialFile.value = target.files[0];
    if (!materialTitle.value) {
      materialTitle.value = materialFile.value.name;
    }
  }
}

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
    
    const response = await materialAPI.uploadMaterial(course.value.id, formData);
    
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

function downloadMaterial(materialId: number) {
  materialAPI.downloadMaterial(materialId);
}

async function confirmDeleteMaterial(material: Material) {
  if (confirm(`确定要删除课件 "${material.title}" 吗？此操作不可恢复。`)) {
    try {
      await materialAPI.deleteMaterial(material.id);
      // 重新获取材料列表
      await fetchMaterials();
    } catch (error) {
      console.error('删除课件失败:', error);
      alert('删除课件失败，请重试');
    }
  }
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

async function fetchStudents() {
  if (!course.value) return;
  
  isLoadingStudents.value = true;
  studentError.value = '';
  
  try {
    const response = await courseAPI.getCourseStudents(course.value.id);
    const responseData = response as any;
    students.value = responseData.students as Student[];
  } catch (error) {
    console.error('获取学生列表失败:', error);
    studentError.value = '获取学生列表失败';
  } finally {
    isLoadingStudents.value = false;
  }
}

async function fetchAvailableStudents() {
  if (!course.value) return;
  
  try {
    const response = await courseAPI.getAvailableStudents(course.value.id);
    const responseData = response as any;
    availableStudents.value = responseData.students as AvailableStudent[];
  } catch (error) {
    console.error('获取可添加学生列表失败:', error);
  }
}

async function addStudents() {
  if (!course.value || selectedStudents.value.length === 0) {
    return;
  }
  
  try {
    await courseAPI.addStudentsToCourse(course.value.id, selectedStudents.value);
    
    // 清空选择
    selectedStudents.value = [];
    
    // 关闭模态框
    showAddStudentModal.value = false;
    
    // 重新获取学生列表
    await fetchStudents();
    
    // 更新课程信息
    await fetchCourseDetail();
  } catch (error) {
    console.error('添加学生失败:', error);
    alert('添加学生失败，请重试');
  }
}

async function removeStudent(studentId: number) {
  if (!course.value) return;
  
  if (confirm('确定要从课程中移除该学生吗？')) {
    try {
      await courseAPI.removeStudentFromCourse(course.value.id, studentId);
      
      // 重新获取学生列表
      await fetchStudents();
      
      // 更新课程信息
      await fetchCourseDetail();
    } catch (error) {
      console.error('移除学生失败:', error);
      alert('移除学生失败，请重试');
    }
  }
}

function toggleStudentSelection(studentId: number) {
  const index = selectedStudents.value.indexOf(studentId);
  if (index === -1) {
    selectedStudents.value.push(studentId);
  } else {
    selectedStudents.value.splice(index, 1);
  }
}

function openAddStudentModal() {
  showAddStudentModal.value = true;
  selectedStudents.value = [];
  fetchAvailableStudents();
}

function filterStudents() {
  if (!course.value) return;
  
  // 使用搜索参数重新获取学生列表
  fetchStudents();
}

function previewMaterial(materialId: number) {
  previewMaterialId.value = materialId;
  showMaterialPreview.value = true;
}
</script> 