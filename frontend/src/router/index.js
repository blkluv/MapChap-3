import { createRouter, createWebHistory } from 'vue-router'
import ProfilePage from '../views/ProfilePage.vue'

const routes = [
  {
    path: '/',
    redirect: '/profile'
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfilePage,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: () => import('../views/AnalyticsPage.vue'),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/boost',
    name: 'boost',
    component: () => import('../views/ProfilePage.vue'),
    meta: {
      requiresAuth: true
    }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
