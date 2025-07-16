import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useRoute } from 'vue-router'
import { h } from 'vue'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import AdminView from '../views/AdminView.vue'
import ProfileView from '../views/ProfileView.vue'
import StudentView from '../views/StudentView.vue'
import TeacherView from '../views/TeacherView.vue'
import CourseDetailView from '../views/CourseDetailView.vue'
import NotFoundView from '../views/NotFoundView.vue'
import TestAssessmentView from '../views/TestAssessmentView.vue'
import AssessmentPlayerView from '../views/AssessmentPlayerView.vue'

// 导入评估相关视图
import AssessmentList from '../components/assessment/AssessmentList.vue'
import AssessmentView from '../components/assessment/AssessmentView.vue'
import AssessmentCreator from '../components/assessment/AssessmentCreator.vue'
import SubmissionList from '../components/assessment/SubmissionList.vue'
import SubmissionGrader from '../components/assessment/SubmissionGrader.vue'

// 导入AI助手组件
import AIAssistant from '../components/ai/AIAssistant.vue'
import TestAIAssistantView from '../views/TestAIAssistantView.vue'
import SimpleTestView from '../views/SimpleTestView.vue'
import LearningView from '../views/LearningView.vue'

// 定义路由历史位置状态接口
interface ScrollPositionNormalized {
  left: number
  top: number
}

interface PositionResult {
  x: number
  y: number
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true }
    },
    {
      path: '/student',
      name: 'student',
      component: StudentView,
      meta: { requiresAuth: true, requiresStudent: true }
    },
    {
      path: '/teacher',
      name: 'teacher',
      component: TeacherView,
      meta: { requiresAuth: true, requiresTeacher: true }
    },
    {
      path: '/course/:id',
      name: 'courseDetail',
      component: CourseDetailView,
      meta: { requiresAuth: true }
    },
    // AI助手路由 - 现已集成到课程详情页面，但保留此路由用于直接访问
    {
      path: '/ai-assistant',
      name: 'aiAssistant',
      component: AIAssistant,
      props: route => ({ 
        userId: parseInt(localStorage.getItem('userId') || '0'),
        courseId: route.query.courseId
      }),
      meta: { requiresAuth: true }
    },
    // 智能备课路由 - 用于直接访问
    {
      path: '/lesson-planner',
      name: 'lessonPlanner',
      component: () => import('../components/ai/LessonPlanner.vue'),
      meta: { requiresAuth: true, requiresTeacher: true }
    },
    // 评估相关路由
    {
      path: '/test-assessment',
      name: 'testAssessment',
      component: TestAssessmentView
    },
    {
      path: '/assessments',
      name: 'assessments',
      component: AssessmentList,
      meta: { requiresAuth: true }
    },
    {
      path: '/assessments/create',
      name: 'AssessmentCreate',
      component: AssessmentCreator,
      props: route => ({ courseId: parseInt(route.query.courseId as string) }),
      meta: { requiresAuth: true }
    },
    {
      path: '/assessments/:id/edit',
      name: 'AssessmentEdit',
      component: AssessmentCreator,
      props: route => ({ 
        assessmentId: parseInt(route.params.id as string),
        isEditing: true
      }),
      meta: { requiresAuth: true }
    },
    {
      path: '/assessments/:id',
      name: 'assessmentDetail',
      component: AssessmentView,
      props: route => ({ assessmentId: parseInt(route.params.id) }),
      meta: { requiresAuth: true }
    },
    {
      path: '/assessments/:id/take',
      name: 'assessmentTake',
      component: AssessmentPlayerView,
      meta: { requiresAuth: false } // 暂时禁用权限检查以便测试
    },
    {
      path: '/assessments/:id/submissions',
      name: 'assessmentSubmissions',
      component: SubmissionList,
      meta: { requiresAuth: true }
    },
    // 添加批改路由
    {
      path: '/submissions/:id/grade',
      name: 'submissionGrader',
      component: SubmissionGrader,
      props: route => ({ submissionId: parseInt(route.params.id as string) }),
      meta: { requiresAuth: true, requiresTeacher: true }
    },
    {
      path: '/test-ai-assistant',
      name: 'testAIAssistant',
      component: TestAIAssistantView,
      meta: { requiresAuth: true }
    },
    {
      path: '/simple-test',
      name: 'simpleTest',
      component: SimpleTestView,
      meta: { requiresAuth: true }
    },
    {
      path: '/learning/:courseId',
      name: 'learning',
      component: LearningView,
      meta: { requiresAuth: true }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'notFound',
      component: NotFoundView
    }
  ],
  // 添加滚动行为，保存滚动位置
  scrollBehavior(to, from, savedPosition) {
    // 如果有保存的位置，则返回保存的位置
    if (savedPosition) {
      return savedPosition;
    }
    
    // 如果有锚点，则滚动到锚点
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' };
    }
    
    // 默认滚动到顶部
    return { top: 0 };
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 注意：因为这是在路由守卫中，在应用初始化之前，
  // 我们需要从localStorage获取认证信息，而不是依赖Pinia存储
  const token = localStorage.getItem('token')
  
  // 从auth存储中获取用户信息
  let user = null
  try {
    const authData = localStorage.getItem('auth')
    if (authData) {
      const parsedAuth = JSON.parse(authData)
      user = parsedAuth.user
    }
  } catch (error) {
    console.error('Failed to parse auth data:', error)
  }
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)
  const requiresTeacher = to.matched.some(record => record.meta.requiresTeacher)
  const requiresStudent = to.matched.some(record => record.meta.requiresStudent)
  
  // 首页重定向逻辑
  if (to.path === '/' && token && user) {
    if (user.role === 'admin') {
      return next('/admin')
    } else if (user.role === 'teacher') {
      return next('/teacher')
    } else if (user.role === 'student') {
      return next('/student')
    }
  }

  // 需要认证但没有登录
  if (requiresAuth && !token) {
    return next('/login')
  }

  // 需要管理员权限
  if (requiresAdmin && (!user || user.role !== 'admin')) {
    return next('/dashboard')
  }

  // 需要教师权限
  if (requiresTeacher && (!user || user.role !== 'teacher')) {
    return next('/dashboard')
  }

  // 需要学生权限
  if (requiresStudent && (!user || user.role !== 'student')) {
    return next('/dashboard')
  }

  next()
})

export default router 