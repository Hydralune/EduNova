import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/auth/LoginView.vue'),
      meta: { requiresAuth: false, hideForAuth: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/auth/RegisterView.vue'),
      meta: { requiresAuth: false, hideForAuth: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true }
    },
    // 学生路由
    {
      path: '/student',
      name: 'student',
      component: () => import('../views/student/StudentLayout.vue'),
      meta: { requiresAuth: true, roles: ['student'] },
      children: [
        {
          path: '',
          name: 'student-dashboard',
          component: () => import('../views/student/StudentDashboard.vue')
        },
        {
          path: 'courses',
          name: 'student-courses',
          component: () => import('../views/student/StudentCourses.vue')
        },
        {
          path: 'courses/:id',
          name: 'student-course-detail',
          component: () => import('../views/student/StudentCourseDetail.vue')
        },
        {
          path: 'chat',
          name: 'student-chat',
          component: () => import('../views/student/StudentChat.vue')
        },
        {
          path: 'practice',
          name: 'student-practice',
          component: () => import('../views/student/StudentPractice.vue')
        },
        {
          path: 'answers',
          name: 'student-answers',
          component: () => import('../views/student/StudentAnswers.vue')
        }
      ]
    },
    // 教师路由
    {
      path: '/teacher',
      name: 'teacher',
      component: () => import('../views/teacher/TeacherLayout.vue'),
      meta: { requiresAuth: true, roles: ['teacher', 'admin'] },
      children: [
        {
          path: '',
          name: 'teacher-dashboard',
          component: () => import('../views/teacher/TeacherDashboard.vue')
        },
        {
          path: 'courses',
          name: 'teacher-courses',
          component: () => import('../views/teacher/TeacherCourses.vue')
        },
        {
          path: 'courses/:id',
          name: 'teacher-course-detail',
          component: () => import('../views/teacher/TeacherCourseDetail.vue')
        },
        {
          path: 'courses/:id/materials',
          name: 'teacher-materials',
          component: () => import('../views/teacher/TeacherMaterials.vue')
        },
        {
          path: 'courses/:id/assessments',
          name: 'teacher-assessments',
          component: () => import('../views/teacher/TeacherAssessments.vue')
        },
        {
          path: 'grading',
          name: 'teacher-grading',
          component: () => import('../views/teacher/TeacherGrading.vue')
        },
        {
          path: 'analytics',
          name: 'teacher-analytics',
          component: () => import('../views/teacher/TeacherAnalytics.vue')
        }
      ]
    },
    // 管理员路由
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/admin/AdminLayout.vue'),
      meta: { requiresAuth: true, roles: ['admin'] },
      children: [
        {
          path: '',
          name: 'admin-dashboard',
          component: () => import('../views/admin/AdminDashboard.vue')
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('../views/admin/AdminUsers.vue')
        },
        {
          path: 'courses',
          name: 'admin-courses',
          component: () => import('../views/admin/AdminCourses.vue')
        },
        {
          path: 'system',
          name: 'admin-system',
          component: () => import('../views/admin/AdminSystem.vue')
        },
        {
          path: 'analytics',
          name: 'admin-analytics',
          component: () => import('../views/admin/AdminAnalytics.vue')
        }
      ]
    },
    // 个人资料
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
    // 404页面
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFoundView.vue')
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 初始化认证状态
  if (!authStore.user && authStore.token) {
    authStore.initializeAuth()
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }
  
  // 已登录用户访问登录/注册页面时重定向
  if (to.meta.hideForAuth && authStore.isAuthenticated) {
    const role = authStore.user?.role
    if (role === 'admin') {
      next('/admin')
    } else if (role === 'teacher') {
      next('/teacher')
    } else if (role === 'student') {
      next('/student')
    } else {
      next('/dashboard')
    }
    return
  }
  
  // 检查角色权限
  if (to.meta.roles && authStore.user) {
    const userRole = authStore.user.role
    const allowedRoles = to.meta.roles as string[]
    
    if (!allowedRoles.includes(userRole)) {
      // 根据用户角色重定向到相应页面
      if (userRole === 'admin') {
        next('/admin')
      } else if (userRole === 'teacher') {
        next('/teacher')
      } else if (userRole === 'student') {
        next('/student')
      } else {
        next('/dashboard')
      }
      return
    }
  }
  
  next()
})

export default router

