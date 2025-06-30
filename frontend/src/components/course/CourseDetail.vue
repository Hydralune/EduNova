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
                    
                    <span v-if="canEdit" class="text-gray-300">|</span>
                    
                  <button 
                      v-if="canEdit"
                      @click="editAssessment(assessment)" 
                      class="text-blue-600 hover:text-blue-800"
                  >
                      编辑
                  </button>
                    
                    <span v-if="canEdit" class="text-gray-300">|</span>
                    
                  <button 
                      v-if="canEdit"
                      @click="deleteAssessment(assessment)" 
                      class="text-red-600 hover:text-red-800"
                  >
                      删除
                  </button>
                </div>
              </div>
              </div>
              
              <!-- 学生提交状态 -->
              <div v-if="!canEdit && assessment.submissions" class="mt-4 pt-4 border-t">
                <div class="flex justify-between items-center">
                  <div>
                    <p class="text-sm">
                      <span class="font-medium">提交状态:</span>
                      {{ assessment.submissions.length > 0 ? `已提交 ${assessment.submissions.length} 次` : '未提交' }}
                    </p>
                    <p v-if="assessment.submissions && assessment.submissions.length > 0" class="text-sm">
                      <span class="font-medium">最高分:</span>
                      {{ getHighestScore(assessment.submissions) }} / {{ assessment.total_score }}
                    </p>
              </div>
                <div>
                    <button 
                      v-if="canTakeAssessment(assessment)"
                      @click="takeAssessment(assessment)" 
                      class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      {{ assessment.submissions && assessment.submissions.length > 0 ? '重新尝试' : '开始' }}
                    </button>
                    <button 
                      v-else-if="assessment.submissions && assessment.submissions.length > 0"
                      @click="viewSubmissions(assessment)" 
                      class="px-4 py-2 border rounded-md hover:bg-gray-50"
                    >
                      查看提交
                    </button>
                  </div>
                </div>
              </div>
              
              <!-- 教师查看提交 -->
              <div v-if="canEdit" class="mt-4 pt-4 border-t">
                <div class="flex justify-between items-center">
                  <p class="text-sm">
                    <span class="font-medium">提交数:</span>
                    {{ assessment.submission_count || 0 }}
                  </p>
                  <button 
                    v-if="assessment.submission_count > 0"
                    @click="viewAllSubmissions(assessment)" 
                    class="px-4 py-2 border rounded-md hover:bg-gray-50"
                  >
                    查看提交
                  </button>
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
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">评估完成情况</th>
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
                  <td class="px-6 py-4">
                    <div v-if="student.assessments && student.assessments.length > 0" class="space-y-2">
                      <div v-for="assessment in student.assessments" :key="assessment.assessment_id" class="flex items-center gap-2">
                        <span class="text-sm truncate max-w-xs" :title="assessment.title">{{ assessment.title }}:</span>
                        <span v-if="assessment.completed" class="text-sm text-green-600">
                          {{ assessment.score }}/{{ assessment.total_score }}
                        </span>
                        <span v-else class="text-sm text-gray-500">未完成</span>
                    </div>
                    </div>
                    <div v-else class="text-sm text-gray-500">暂无评估</div>
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
        
        <!-- 智能助手 -->
        <div v-else-if="activeTab === 'ai-assistant'" class="p-6">
          <AIAssistant :courseId="courseId" :userId="authStore.user?.id || 0" />
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
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '../../stores/auth';
import { courseAPI, materialAPI } from '../../api';
import MaterialPreview from './MaterialPreview.vue';
import AIAssistant from '../ai/AIAssistant.vue';
import { useRouter } from 'vue-router';
import { assessmentAPI } from '@/api';

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

interface Assessment {
  assessment_id: number;
  title: string;
  completed: boolean;
  score: number;
  total_score: number;
}

interface Student {
  id: number;
  name: string;
  email: string;
  assessments: Assessment[];
  last_activity: string;
}

interface AvailableStudent {
  id: number;
  name: string;
  email: string;
  role: string;
}

interface Assessment {
  id: number;
  title: string;
  description: string;
  course_id: number;
  type: string;
  total_score: number;
  duration: string | null;
  due_date: string | null;
  start_date: string | null;
  max_attempts: number;
  is_published: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  questions: any[];
  submission_count: number;
  submissions?: any[];
}

interface Question {
  id: number;
  type: string;
  content: string;
  options?: string[];
  answer?: string | string[];
}

interface Submission {
  id: number;
  assessment_id: number;
  student_id: number;
  status: 'pending' | 'in_progress' | 'completed';
  score: number;
  submitted_at: string;
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

const props = defineProps<{
  id: string | number;
}>();

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
const previewMaterialId = ref<number | undefined>();

const tabs = [
  { id: 'chapters', name: '章节内容' },
  { id: 'materials', name: '课件资源' },
  { id: 'assessments', name: '评估测验' },
  { id: 'students', name: '学生管理' },
  { id: 'ai-assistant', name: '智能助手' },
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

// 评估数据
const assessments = ref<Assessment[]>([]);

const router = useRouter();

onMounted(async () => {
  try {
    loading.value = true;
    // 首先获取课程信息
    await fetchCourse();
    // 然后并行获取其他数据
    await Promise.all([
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

async function fetchCourse() {
  try {
    // 调用API获取课程详情
    const response = await courseAPI.getCourse(Number(courseId.value));
    
    // 处理API响应 - 根据API文档，response已经是解析后的数据
    course.value = response as unknown as Course;
  } catch (error) {
    console.error('获取课程详情失败:', error);
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

import { debounce } from 'lodash-es';

const students = ref<Student[]>([]);
const availableStudents = ref<AvailableStudent[]>([]);
const selectedStudents = ref<number[]>([]);
const isLoadingStudents = ref(false);
const studentError = ref('');

// 添加 watch 处理器
watch(studentSearch, debounce(() => {
  filterStudents();
}, 300));

async function fetchStudents() {
  if (!course.value?.id) {
    console.error('课程信息不存在，无法获取学生列表');
    return;
  }
  
  isLoadingStudents.value = true;
  studentError.value = '';
  
  try {
    const response = await courseAPI.getCourseStudents(course.value.id);
    const responseData = response as any;
    if (responseData && Array.isArray(responseData.students)) {
      const allStudents = responseData.students as Student[];
      
      // 如果有搜索关键词，进行本地过滤
      if (studentSearch.value.trim()) {
        const searchTerm = studentSearch.value.toLowerCase().trim();
        students.value = allStudents.filter(student => 
          student.name.toLowerCase().includes(searchTerm) ||
          student.email.toLowerCase().includes(searchTerm)
        );
      } else {
        students.value = allStudents;
      }
    } else {
      console.error('获取学生列表返回的数据格式不正确:', responseData);
      studentError.value = '获取学生列表失败';
      students.value = [];
    }
  } catch (error) {
    console.error('获取学生列表失败:', error);
    studentError.value = '获取学生列表失败';
    students.value = [];
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
    await fetchCourse();
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
      await fetchCourse();
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

async function filterStudents() {
  if (!course.value) return;
  
  isLoadingStudents.value = true;
  studentError.value = '';
  
  try {
    const response = await courseAPI.getCourseStudents(course.value.id);
    const responseData = response as any;
    const allStudents = responseData.students as Student[];
    
    // 如果有搜索关键词，进行本地过滤
    if (studentSearch.value.trim()) {
      const searchTerm = studentSearch.value.toLowerCase().trim();
      students.value = allStudents.filter(student => 
        student.name.toLowerCase().includes(searchTerm) ||
        student.email.toLowerCase().includes(searchTerm)
      );
    } else {
      students.value = allStudents;
    }
  } catch (error) {
    console.error('获取学生列表失败:', error);
    studentError.value = '获取学生列表失败';
  } finally {
    isLoadingStudents.value = false;
  }
}

function previewMaterial(materialId: number) {
  previewMaterialId.value = materialId;
  showMaterialPreview.value = true;
}

// 评估相关方法
const createNewAssessment = () => {
  router.push(`/assessments/create?courseId=${courseId}`);
};

const getTotalQuestions = (assessment: Assessment): number => {
  return assessment.questions?.length || 0;
};

const getStatusClass = (assessment: Assessment): string => {
  if (!assessment.submissions || assessment.submissions.length === 0) {
    return 'bg-blue-100 text-blue-800';
  }
  const latestSubmission = assessment.submissions[assessment.submissions.length - 1];
  if (latestSubmission.status === 'completed') {
    return 'bg-green-100 text-green-800';
  }
  return 'bg-yellow-100 text-yellow-800';
};

const getStatusText = (assessment: Assessment): string => {
  if (!assessment.submissions || assessment.submissions.length === 0) {
    return '未开始';
  }
  const latestSubmission = assessment.submissions[assessment.submissions.length - 1];
  if (latestSubmission.status === 'completed') {
    return '已完成';
  }
  return '进行中';
};

const editAssessment = (assessment: Assessment): void => {
  router.push(`/assessments/${assessment.id}/edit`);
};

const deleteAssessment = async (assessment: Assessment): Promise<void> => {
  if (confirm('确定要删除这个评估吗？')) {
    try {
      await assessmentAPI.deleteAssessment(assessment.id);
      // 重新加载评估列表
      await fetchAssessments();
    } catch (error) {
      console.error('删除评估失败:', error);
    }
  }
};

const canTakeAssessment = (assessment: Assessment): boolean => {
  if (!assessment.max_attempts) return true;
  return !assessment.submissions || assessment.submissions.length < assessment.max_attempts;
};

const takeAssessment = (assessment: Assessment): void => {
  router.push(`/assessments/${assessment.id}/take`);
};

const viewSubmissions = (assessment: Assessment): void => {
  router.push(`/assessments/${assessment.id}/submissions`);
};

const viewAllSubmissions = (assessment: Assessment): void => {
  router.push(`/assessments/${assessment.id}/all-submissions`);
};

const getHighestScore = (submissions: Submission[]): number => {
  if (!submissions || submissions.length === 0) return 0;
  return Math.max(...submissions.map(s => s.score || 0));
};

const formatDate = (date: string | null): string => {
  if (!date) return '无限制';
  return new Date(date).toLocaleDateString();
};

// 获取评估列表
const fetchAssessments = async () => {
  try {
    loading.value = true;
    const response = await assessmentAPI.getCourseAssessments(Number(courseId.value));
    assessments.value = response.assessments || [];
  } catch (error) {
    console.error('获取评估列表失败:', error);
    assessments.value = [];
  } finally {
    loading.value = false;
  }
};
</script> 