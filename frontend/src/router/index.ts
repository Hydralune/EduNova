import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/teacher',
      name: 'teacher',
      component: () => import('../views/TeacherView.vue'),
      meta: { requiresAuth: true, requiresTeacher: true }
    },
    {
      path: '/student',
      name: 'student',
      component: () => import('../views/StudentView.vue'),
      meta: { requiresAuth: true, requiresStudent: true }
    },
    {
      path: '/course/:id',
      name: 'course-detail',
      component: () => import('../views/CourseDetailView.vue'),
      meta: { requiresAuth: true },
      props: true
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFoundView.vue')
    }
  ]
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
  
  if (requiresAuth && !token) {
    // 未登录，重定向到登录页
    next('/login')
  } else if (requiresAdmin && user?.role !== 'admin') {
    // 需要管理员权限但用户不是管理员
    if (user?.role === 'teacher') {
      next('/teacher')
    } else if (user?.role === 'student') {
      next('/student')
    } else {
      next('/dashboard')
    }
  } else if (requiresTeacher && user?.role !== 'teacher') {
    // 需要教师权限但用户不是教师
    if (user?.role === 'admin') {
      next('/admin')
    } else if (user?.role === 'student') {
      next('/student')
    } else {
      next('/dashboard')
    }
  } else if (requiresStudent && user?.role !== 'student') {
    // 需要学生权限但用户不是学生
    if (user?.role === 'admin') {
      next('/admin')
    } else if (user?.role === 'teacher') {
      next('/teacher')
    } else {
      next('/dashboard')
    }
  } else {
    // 放行
    next()
  }
})

export default router 