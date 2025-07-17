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
            <div class="flex space-x-2">
              <button 
                v-if="canEdit && course.chapters && course.chapters.length > 0" 
                @click="openEditChapterModal"
                class="px-4 py-2 bg-blue-600 text-white rounded-md flex items-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                </svg>
                修改章节
              </button>
              <button 
                v-if="canEdit && course.chapters && course.chapters.length > 0" 
                @click="generateChaptersWithAI"
                class="px-4 py-2 bg-green-600 text-white rounded-md flex items-center"
                :disabled="isGeneratingChapters"
              >
                <span v-if="isGeneratingChapters" class="mr-1">
                  <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </span>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10 3.5a1.5 1.5 0 013 0V4a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-.5a1.5 1.5 0 000 3h.5a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-.5a1.5 1.5 0 00-3 0v.5a1 1 0 01-1 1H6a1 1 0 01-1-1v-3a1 1 0 011-1h.5a1.5 1.5 0 000-3H6a1 1 0 01-1-1V6a1 1 0 011-1h3a1 1 0 001-1v-.5z" />
                </svg>
                {{ isGeneratingChapters ? '生成中...' : '使用AI重新生成' }}
              </button>
            </div>
          </div>

          <div v-if="course.chapters && course.chapters.length > 0" class="space-y-4">
            <div v-for="(chapter, index) in course.chapters" :key="index" class="border rounded-md overflow-hidden cursor-pointer hover:bg-gray-50" @click="goLearning(index)">
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
            <div class="flex justify-center mt-4 space-x-3">
              <button 
                v-if="canEdit" 
                @click="showAddChapterModal = true"
                class="px-4 py-2 bg-blue-600 text-white rounded-md flex items-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                </svg>
                添加章节
              </button>
              <button 
                v-if="canEdit" 
                @click="generateChaptersWithAI"
                class="px-4 py-2 bg-green-600 text-white rounded-md flex items-center"
                :disabled="isGeneratingChapters"
              >
                <span v-if="isGeneratingChapters" class="mr-1">
                  <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </span>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10 3.5a1.5 1.5 0 013 0V4a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-.5a1.5 1.5 0 000 3h.5a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-.5a1.5 1.5 0 00-3 0v.5a1 1 0 01-1 1H6a1 1 0 01-1-1v-3a1 1 0 011-1h.5a1.5 1.5 0 000-3H6a1 1 0 01-1-1V6a1 1 0 011-1h3a1 1 0 001-1v-.5z" />
                </svg>
                {{ isGeneratingChapters ? '生成中...' : '使用AI生成章节' }}
              </button>
            </div>
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
            <div class="w-full border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-all cursor-pointer"
              @click="triggerFileInput" 
              @dragover.prevent 
              @drop.prevent="handleFileDrop">
              <input type="file" @change="handleFileChange" class="hidden" ref="fileInput" required />
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p class="mt-2 text-sm text-gray-600">点击或拖拽文件到此处上传</p>
              <p class="text-xs text-gray-500 mt-1">支持 PDF、Word、PPT、图片等格式</p>
            </div>
            <p v-if="materialFile" class="mt-2 text-sm text-gray-500 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-green-500" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
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

    <!-- 添加章节模态框 -->
    <div v-if="showAddChapterModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl">
        <h3 class="text-xl font-bold mb-4">添加章节</h3>
        <div class="mb-6">
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">章节标题</label>
            <input 
              v-model="newChapter.title" 
              type="text" 
              class="w-full px-3 py-2 border rounded-md" 
              placeholder="输入章节标题"
              required
            />
          </div>
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">章节时长（分钟）</label>
            <input 
              v-model="newChapter.duration" 
              type="number" 
              class="w-full px-3 py-2 border rounded-md" 
              placeholder="输入章节时长"
              min="1"
            />
          </div>
          
          <div class="mb-2">
            <div class="flex justify-between items-center">
              <label class="block text-gray-700 text-sm font-bold mb-2">小节列表</label>
              <button 
                @click="addSection" 
                class="text-sm px-2 py-1 bg-blue-600 text-white rounded-md flex items-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                </svg>
                添加小节
              </button>
            </div>
            
            <div v-if="newChapter.sections.length > 0" class="space-y-4 mt-2">
              <div v-for="(section, index) in newChapter.sections" :key="index" class="border p-4 rounded-md relative">
                <button 
                  @click="removeSection(index)" 
                  class="absolute top-2 right-2 text-red-500 hover:text-red-700"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                  </svg>
                </button>
                <div class="mb-2">
                  <label class="block text-gray-700 text-sm font-bold mb-1">小节标题</label>
                  <input 
                    v-model="section.title" 
                    type="text" 
                    class="w-full px-3 py-2 border rounded-md" 
                    placeholder="输入小节标题"
                  />
                </div>
                <div class="mb-2">
                  <label class="block text-gray-700 text-sm font-bold mb-1">小节时长（分钟）</label>
                  <input 
                    v-model="section.duration" 
                    type="number" 
                    class="w-full px-3 py-2 border rounded-md" 
                    placeholder="输入小节时长"
                    min="1"
                  />
                </div>
                <div>
                  <label class="block text-gray-700 text-sm font-bold mb-1">内容简介</label>
                  <textarea 
                    v-model="section.content" 
                    class="w-full px-3 py-2 border rounded-md" 
                    placeholder="输入小节内容简介"
                    rows="2"
                  ></textarea>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-4 border rounded-md bg-gray-50">
              <p class="text-gray-500">暂无小节，请添加小节</p>
            </div>
          </div>
        </div>
        
        <div class="flex justify-end gap-2">
          <button 
            type="button" 
            @click="cancelAddChapter" 
            class="px-4 py-2 border rounded-md"
          >
            取消
          </button>
          <button 
            type="submit" 
            @click="saveChapter" 
            class="px-4 py-2 bg-blue-600 text-white rounded-md"
            :disabled="!isChapterValid"
          >
            保存
          </button>
        </div>
      </div>
    </div>
    
    <!-- 修改章节模态框 -->
    <div v-if="showEditChapterModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-bold mb-4">修改章节</h3>
        <div class="mb-6 space-y-6">
          <div v-for="(chapter, chapterIndex) in editChapters" :key="`chapter-${chapterIndex}`" class="border p-4 rounded-md">
            <div class="flex justify-between items-center mb-3">
              <h4 class="font-bold">章节 {{ chapterIndex + 1 }}</h4>
              <div class="space-x-2">
                <button
                  v-if="editChapters.length > 1"
                  @click="removeChapter(chapterIndex)"
                  class="text-red-600 hover:text-red-800"
                >
                  删除章节
                </button>
              </div>
            </div>
            
            <div class="mb-4">
              <label class="block text-gray-700 text-sm font-bold mb-2">章节标题</label>
              <input 
                v-model="chapter.title" 
                type="text" 
                class="w-full px-3 py-2 border rounded-md" 
                placeholder="输入章节标题"
                required
              />
            </div>
            <div class="mb-4">
              <label class="block text-gray-700 text-sm font-bold mb-2">章节时长（分钟）</label>
              <input 
                v-model="chapter.duration" 
                type="number" 
                class="w-full px-3 py-2 border rounded-md" 
                placeholder="输入章节时长"
                min="1"
              />
            </div>
            
            <div class="mb-2">
              <div class="flex justify-between items-center">
                <label class="block text-gray-700 text-sm font-bold mb-2">小节列表</label>
                <button 
                  @click="addSectionToChapter(chapterIndex)" 
                  class="text-sm px-2 py-1 bg-blue-600 text-white rounded-md flex items-center"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                  </svg>
                  添加小节
                </button>
              </div>
              
              <div v-if="chapter.sections && chapter.sections.length > 0" class="space-y-4 mt-2">
                <div 
                  v-for="(section, sectionIndex) in chapter.sections" 
                  :key="`section-${chapterIndex}-${sectionIndex}`" 
                  class="border p-4 rounded-md relative"
                >
                  <button 
                    @click="removeSectionFromChapter(chapterIndex, sectionIndex)" 
                    class="absolute top-2 right-2 text-red-500 hover:text-red-700"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                    </svg>
                  </button>
                  <div class="mb-2">
                    <label class="block text-gray-700 text-sm font-bold mb-1">小节标题</label>
                    <input 
                      v-model="section.title" 
                      type="text" 
                      class="w-full px-3 py-2 border rounded-md" 
                      placeholder="输入小节标题"
                    />
                  </div>
                  <div class="mb-2">
                    <label class="block text-gray-700 text-sm font-bold mb-1">小节时长（分钟）</label>
                    <input 
                      v-model="section.duration" 
                      type="number" 
                      class="w-full px-3 py-2 border rounded-md" 
                      placeholder="输入小节时长"
                      min="1"
                    />
                  </div>
                  <div>
                    <label class="block text-gray-700 text-sm font-bold mb-1">内容简介</label>
                    <textarea 
                      v-model="section.content" 
                      class="w-full px-3 py-2 border rounded-md" 
                      placeholder="输入小节内容简介"
                      rows="2"
                    ></textarea>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-4 border rounded-md bg-gray-50">
                <p class="text-gray-500">暂无小节，请添加小节</p>
              </div>
            </div>
          </div>
          
          <div class="flex justify-center">
            <button 
              @click="addNewChapter" 
              class="px-4 py-2 bg-green-600 text-white rounded-md flex items-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
              </svg>
              添加新章节
            </button>
          </div>
        </div>
        
        <div class="flex justify-end gap-2">
          <button 
            type="button" 
            @click="showEditChapterModal = false" 
            class="px-4 py-2 border rounded-md"
          >
            取消
          </button>
          <button 
            type="submit" 
            @click="saveEditedChapters" 
            class="px-4 py-2 bg-blue-600 text-white rounded-md"
            :disabled="!isEditChaptersValid"
          >
            保存
          </button>
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

interface Section {
  id?: number;
  title: string;
  duration: number;
  content: string;
}

interface Chapter {
  id?: number;
  title: string;
  duration: number;
  sections: Section[];
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

// 定义文件类型接口
interface FileType {
  extension: string;
  description: string;
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
const previewMaterialId = ref<number | null>(null);

// 知识库相关
const supportedKnowledgeBaseTypes = ref<FileType[]>([]);
const knowledgeBaseProcessing = ref<Record<number, boolean>>({});

// 添加缺失的材料上传相关属性
const materialTitle = ref('');
const materialFile = ref<File | null>(null);
const materialUploadProgress = ref(0);
const materialUploadError = ref('');
const fileInput = ref<HTMLInputElement | null>(null);

// 在状态部分添加
const isGeneratingChapters = ref(false);
const showEditChapterModal = ref(false);

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
    await fetchCourse(); // 先获取课程信息
    
    // 课程加载完成后，再获取其他数据
    if (course.value) {
      await Promise.all([
        fetchMaterials(),
        fetchStudents(),
        fetchAssessments(),
        fetchChapters()
      ]);
    }
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
    const response = await fetch('http://localhost:5001/api/rag/knowledge/supported-types');
    const data = await response.json();
    supportedKnowledgeBaseTypes.value = data.supported_types || [];
  } catch (error) {
    console.error('获取知识库支持的文件类型失败:', error);
  }
}

// 判断文件是否支持添加到知识库
function isSupportedForKnowledgeBase(material: Material): boolean {
  const fileExtension = material.file_path.split('.').pop()?.toLowerCase();
  return supportedKnowledgeBaseTypes.value.some(type => 
    type.extension.toLowerCase().includes(`.${fileExtension}`)
  );
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
    
    const response = await fetch('http://localhost:5001/api/rag/knowledge/add', {
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

// 获取课程章节
async function fetchChapters() {
  if (!courseId.value || !course.value) {
    console.error('课程ID或课程对象为空，无法获取章节');
    return;
  }
  
  try {
    console.log('获取章节数据...', courseId.value);
    const response = await fetch(`http://localhost:5001/api/courses/${courseId.value}/chapters`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      },
      mode: 'cors'
    });
    
    if (!response.ok) {
      console.error('获取章节响应错误:', response.status, response.statusText);
      return;
    }
    
    const data = await response.json();
    console.log('章节数据:', data);
    
    if (data.status === 'success' && data.chapters && data.chapters.length > 0) {
      course.value = {
        ...course.value,
        chapters: data.chapters
      };
      console.log('章节数据已更新:', course.value.chapters);
    } else {
      console.log('没有章节数据或数据为空');
      // 确保chapters至少是空数组
      course.value.chapters = course.value.chapters || [];
    }
  } catch (error) {
    console.error('获取章节失败:', error);
    // 确保chapters至少是空数组
    if (course.value) {
      course.value.chapters = course.value.chapters || [];
    }
  }
}

// 使用AI生成章节
async function generateChaptersWithAI() {
  if (!course.value || isGeneratingChapters.value) {
    console.error('课程对象为空或正在生成中，无法生成章节');
    return;
  }
  
  try {
    isGeneratingChapters.value = true;
    
    // 强制删除已有章节文件，以便重新生成
    console.log('清除已有章节数据...');
    try {
      // 首先尝试删除章节文件
      const deleteResponse = await fetch(`http://localhost:5001/api/courses/${courseId.value}/chapters?force=true`, {
        method: 'DELETE',
        mode: 'cors',
        headers: {
          'Accept': 'application/json'
        }
      });
      console.log('删除章节响应:', deleteResponse.status);
    } catch (error) {
      // 忽略删除错误，继续生成
      console.log('删除章节错误 (忽略):', error);
    }
    
    // 生成新章节
    console.log('开始生成章节...');
    const response = await fetch(`http://localhost:5001/api/courses/${courseId.value}/generate-chapters`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Cache-Control': 'no-cache'
      },
      mode: 'cors',
      body: JSON.stringify({
        course_name: course.value.name,
        description: course.value.description || ''
      })
    });
    
    if (!response.ok) {
      console.error('生成章节响应错误:', response.status, response.statusText);
      throw new Error(`服务器响应错误: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('生成章节响应:', data);
    
    if (data.status === 'success' && data.chapters) {
      course.value = {
        ...course.value,
        chapters: data.chapters
      };
      console.log('章节数据已更新:', course.value.chapters);
      
      // 保存到服务器以确保持久化
      await saveChaptersToServer();
    } else {
      alert('生成章节失败: ' + (data.message || '未知错误'));
    }
  } catch (error) {
    console.error('生成章节失败:', error);
    alert('生成章节失败，请稍后重试: ' + (error instanceof Error ? error.message : String(error)));
  } finally {
    isGeneratingChapters.value = false;
  }
}

// 在script部分的状态定义区域添加
const newChapter = ref<Chapter>({
  title: '',
  duration: 60,
  sections: []
});

const editChapters = ref<Chapter[]>([]);

const isChapterValid = computed(() => {
  return newChapter.value.title.trim() !== '' && 
         newChapter.value.duration > 0 && 
         newChapter.value.sections.length > 0 &&
         newChapter.value.sections.every(section => 
           section.title.trim() !== '' && 
           section.duration > 0
         );
});

const isEditChaptersValid = computed(() => {
  return editChapters.value.length > 0 &&
         editChapters.value.every(chapter => 
           chapter.title.trim() !== '' && 
           chapter.duration > 0 && 
           chapter.sections && 
           chapter.sections.length > 0 &&
           chapter.sections.every(section => 
             section.title.trim() !== '' && 
             section.duration > 0
           )
         );
});

// 重置新章节表单
function resetNewChapter() {
  newChapter.value = {
    title: '',
    duration: 60,
    sections: []
  };
}

// 添加小节到新章节
function addSection() {
  if (!newChapter.value.sections) {
    newChapter.value.sections = [];
  }
  
  newChapter.value.sections.push({
    title: '',
    duration: 20,
    content: ''
  });
}

// 从新章节中移除小节
function removeSection(index: number) {
  if (!newChapter.value.sections) {
    return;
  }
  
  newChapter.value.sections.splice(index, 1);
}

// 取消添加章节
function cancelAddChapter() {
  showAddChapterModal.value = false;
  resetNewChapter();
}

// 保存新章节
async function saveChapter() {
  if (!isChapterValid.value || !course.value) return;
  
  try {
    console.log('保存章节...');
    // 如果课程还没有章节数组，初始化它
    if (!course.value.chapters) {
      course.value.chapters = [];
    }
    
    // 添加新章节
    course.value.chapters.push(JSON.parse(JSON.stringify(newChapter.value)));
    
    // 保存章节到后端
    await saveChaptersToServer();
    console.log('章节保存成功');
    
    // 关闭模态框并重置表单
    showAddChapterModal.value = false;
    resetNewChapter();
  } catch (error) {
    console.error('保存章节失败:', error);
    alert('保存章节失败，请稍后重试');
  }
}

// 打开编辑章节模态框
function openEditChapterModal() {
  if (course.value && course.value.chapters) {
    // 深拷贝章节，避免直接修改
    editChapters.value = JSON.parse(JSON.stringify(course.value.chapters));
    showEditChapterModal.value = true;
  }
}

// 添加小节到指定章节
function addSectionToChapter(chapterIndex: number) {
  if (!editChapters.value[chapterIndex].sections) {
    editChapters.value[chapterIndex].sections = [];
  }
  
  editChapters.value[chapterIndex].sections.push({
    title: '',
    duration: 20,
    content: ''
  });
}

// 从章节中移除小节
function removeSectionFromChapter(chapterIndex: number, sectionIndex: number) {
  if (!editChapters.value[chapterIndex]?.sections) {
    console.error('章节或小节不存在');
    return;
  }
  
  editChapters.value[chapterIndex].sections.splice(sectionIndex, 1);
}

// 添加新章节（编辑模式）
function addNewChapter() {
  editChapters.value.push({
    title: `第${editChapters.value.length + 1}章`,
    duration: 60,
    sections: [{
      title: '第一节',
      duration: 20,
      content: '简介'
    }]
  });
}

// 移除章节（编辑模式）
function removeChapter(chapterIndex: number) {
  if (editChapters.value.length > 1) {
    editChapters.value.splice(chapterIndex, 1);
  }
}

// 保存编辑后的章节
async function saveEditedChapters() {
  if (!isEditChaptersValid.value || !course.value) return;
  
  try {
    console.log('保存编辑后的章节...');
    // 更新课程章节
    course.value.chapters = JSON.parse(JSON.stringify(editChapters.value));
    console.log('章节数据已更新:', course.value.chapters);
    
    // 保存章节到后端
    await saveChaptersToServer();
    console.log('编辑后的章节保存成功');
    
    // 关闭模态框
    showEditChapterModal.value = false;
  } catch (error) {
    console.error('保存章节失败:', error);
    alert('保存章节失败，请稍后重试');
  }
}

// 保存章节到服务器
async function saveChaptersToServer() {
  if (!course.value) {
    console.error('课程对象为空，无法保存');
    alert('无法保存章节：课程信息丢失');
    return;
  }
  
  if (!course.value.chapters) {
    course.value.chapters = [];
  }
  
  if(!courseId.value) {
    console.error('课程ID为空，无法保存');
    alert('无法保存章节：课程ID丢失');
    return;
  }
  
  console.log('保存章节到服务器...', { courseId: courseId.value, chapters: course.value.chapters });
  try {
    const apiUrl = `http://localhost:5001/api/courses/${courseId.value}/chapters`;
    console.log('发送请求到:', apiUrl);
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        chapters: course.value.chapters
      }),
      mode: 'cors'
    });
    
    console.log('服务器响应状态:', response.status, response.statusText);
    
    if (!response.ok) {
      console.error('服务器响应错误:', response.status, response.statusText);
      alert(`保存失败: HTTP错误 ${response.status}`);
      throw new Error(`服务器响应错误: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('服务器响应数据:', data);
    
    if (!data.status || data.status !== 'success') {
      alert(data.message || '保存失败');
      throw new Error(data.message || '保存失败');
    }
    
    // 显示成功提示
    alert('章节保存成功');
    
    // 保存成功后重新获取章节
    await fetchChapters();
    
    return data;
  } catch (error) {
    console.error('保存章节到服务器失败:', error);
    alert(`保存章节到服务器失败: ${error instanceof Error ? error.message : '未知错误'}`);
    throw error;
  }
}

// 触发文件选择框
function triggerFileInput() {
  if (fileInput.value) {
    fileInput.value.click();
  }
}

// 处理拖拽文件
function handleFileDrop(event: DragEvent) {
  if (event.dataTransfer && event.dataTransfer.files.length > 0) {
    materialFile.value = event.dataTransfer.files[0];
    if (!materialTitle.value) {
      materialTitle.value = materialFile.value.name;
    }
  }
}

// in <script setup> section after router const or other functions
function goLearning(idx: number) {
  router.push({ name: 'learning', params: { courseId: courseId.value }, query: { chapter: idx } })
}
</script> 