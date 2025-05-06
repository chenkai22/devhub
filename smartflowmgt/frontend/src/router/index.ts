import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import { formContextKey } from 'element-plus'


const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: '主页',
      component: () => import('../layout/index.vue'),
      redirect: '/index',
      children: [
        {
          path: '/index',
          name: '首页',
          component: () => import('../views/index/index.vue'),
        },
        {
          path: '/user/users',
          name: '用户管理',
          component: () => import('../views/sys/user/index.vue'),
        },
        {
          path: '/ticket/tickets',
          name: '工单中心',
          component: () => import('../views/sys/ticket/index.vue'),
        },
        {
          path: '/ticket/kanban',
          name: '时效看板',
          component: () => import('../views/sys/ticket/kanban.vue'),
        },
        {
          path: '/ticket/warning',
          name: '超时预警',
          component: () => import('../views/sys/ticket/warning.vue'),
        },
        {
          path: '/ticket/report',
          name: '报表中心',
          component: () => import('../views/sys/ticket/report.vue'),
        },
        {
          path: '/ticket/anncment',
          name: '排行榜',
          component: () => import('../views/sys/ticket/anncment.vue'),
        },
      ]
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    // {
    //   path: '/about',
    //   name: 'about',
    //   // route level code-splitting
    //   // this generates a separate chunk (About.[hash].js) for this route
    //   // which is lazy-loaded when the route is visited.
    //   component: () => import('../views/AboutView.vue'),
    // },
  ],
})

router.beforeEach((to, form, next) => {
  const token = window.sessionStorage.getItem('token')

  const whiteList = ['/login']

  if (token) {
    // 已登录状态
    if (to.path === '/login') {
      next('/')
    } else {
      next()
    }
  } else {
    // 未登录状态
    if (whiteList.includes(to.path)) {
      next()
    } else {
      next('/login?redirect=' + to.fullPath)
    }
  }
})

export default router
