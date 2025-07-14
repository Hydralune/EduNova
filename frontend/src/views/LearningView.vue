<template>
  <!-- Overall container -->
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- Top navigation bar -->
    

    <!-- Main split layout -->
    <div class="flex flex-1">
  <!-- Material preview with integrated sidebar -->
  <main class="flex-1 overflow-y-auto">
    <MaterialPreview :courseId="courseId" :hideBackButton="true" />
  </main>
 
  <!-- Right AI sidebar -->
  <aside :class="[
      'hidden xl:flex flex-col border-l bg-white relative overflow-visible',
      rightCollapsed ? 'w-12' : 'w-96'
    ]">
    <template v-if="rightCollapsed">
      <div class="flex flex-col items-center justify-start pt-3 flex-1 cursor-pointer" @click="toggleRightSidebar">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M2 5a2 2 0 012-2h16a2 2 0 012 2v9a2 2 0 01-2 2H8l-6 6V5z" />
        </svg>
      </div>
    </template>
    <template v-else>
      <AIAssistant :courseId="courseId" minimal class="flex-1" @collapseRequest="toggleRightSidebar" />
    </template>
  </aside>
</div>
</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { courseAPI } from '@/api'
import MaterialPreview from '@/components/course/MaterialPreview.vue'
import AIAssistant from '@/components/ai/AIAssistant.vue'
import { materialAPI } from '@/api'

// route /learning/:courseId
const route = useRoute()
const router = useRouter()
const courseId = Number(route.params.courseId)

// dark mode state
const isDarkMode = ref(false)
function toggleDarkMode () {
  isDarkMode.value = !isDarkMode.value
  document.documentElement.classList.toggle('dark', isDarkMode.value)
}

// study timer
const studyTime = ref(0)
// 右侧折叠状态
const rightCollapsed = ref(false)
function toggleRightSidebar () {
  rightCollapsed.value = !rightCollapsed.value
}
let timerId: number | undefined

onMounted(() => {
  timerId = window.setInterval(() => { studyTime.value += 1 }, 1000)
  window.addEventListener('scroll', updateReadingProgress)
  fetchCourse()
})

onUnmounted(() => {
  if (timerId) window.clearInterval(timerId)
  window.removeEventListener('scroll', updateReadingProgress)
})

const formattedStudyTime = computed(() => {
  const m = Math.floor(studyTime.value / 60).toString().padStart(2, '0')
  const s = (studyTime.value % 60).toString().padStart(2, '0')
  return `${m}:${s}`
})

// reading progress
const readingProgress = ref(0)
function updateReadingProgress () {
  const scrolled = window.scrollY
  const maxScroll = document.documentElement.scrollHeight - window.innerHeight
  const progress = maxScroll > 0 ? (scrolled / maxScroll) * 100 : 0
  readingProgress.value = Math.min(progress, 100)
}

interface Material {
  id: number
  title: string
  material_type?: string
  file_path?: string
}
interface Course {
  id: number
  title: string
  description?: string
  materials: Material[]
}

const course = ref<Course | null>(null)
const materials = computed(() => course.value?.materials || [])
const currentMatIdx = ref(0)

const currentMaterial = computed<Material | null>(() => materials.value[currentMatIdx.value] || null)

async function fetchCourse () {
  try {
    const [courseRes, materialsRes] = await Promise.all([
      courseAPI.getCourse(courseId),
      materialAPI.getMaterials(courseId)
    ])
    const courseData: any = (courseRes as any).data ?? courseRes
    const materialsData: any = (materialsRes as any).data ?? materialsRes
    const mats: Material[] = (materialsData?.materials || []).map((m: any) => ({
      id: m.id,
      title: m.title || m.filename || `资源 ${m.id}`,
      material_type: m.material_type,
      file_path: m.file_path,
    }))

    course.value = {
      id: courseData.id || courseId,
      title: courseData.title || courseData.name || '课程',
      description: courseData.description || '',
      materials: mats
    }
  } catch (err) {
    console.error('获取课件资源失败', err)
    course.value = {
      id: courseId,
      title: '示例课程',
      description: '示例描述',
      materials: [
        { id: 1, title: '第一章：Python编程基础入门' },
        { id: 2, title: '第二章：数据类型与结构' },
        { id: 3, title: '第三章：流程控制' },
        { id: 4, title: '第四章：函数编程' },
      ]
    }
  }
}

function handleMaterialSelect (idx: number) {
  currentMatIdx.value = idx
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goAI () {
  router.push({ name: 'aiAssistant', query: { courseId } })
}

function goAssessments () {
  router.push({ name: 'assessments', query: { courseId } })
}

// sample markdown fallback
const sampleMarkdown = ``;
</script>

<style scoped>
/* optional scoped styles */
</style>
