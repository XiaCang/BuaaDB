// router/index.js
import { createRouter, createWebHistory } from 'vue-router'

import LoginView from '../pages/Login.vue'
import HomeView from '../pages/Home.vue'
import { auth } from '@/hooks/auth'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {requireAuth : true}
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../pages/Profile.vue'),
      meta: {requireAuth : true}
    },
    {
      path: '/orders',
      name: 'orders',
      component: () => import('../pages/MyOrder.vue'),
      meta: {requireAuth : true}
    },
    {
      path: '/favorite',
      name: 'favorite',
      component: () => import('../pages/Favorite.vue'),
      meta: {requireAuth : true}
    },
    {
      path : '/create_product',
      name: 'create_product',
      component: () => import('../pages/CreateProduct.vue'),
      meta: {requireAuth : true}
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: {guestOnly : true}
    },
    {
      path: '/modify_product/:id',
      name: 'modify_product',
      component: () => import('../pages/ModifyProduct.vue'),
      meta: {requireAuth : true}
    },
    {
      path: '/product/:id',
      name: 'product',
      component: () => import('../pages/ProductDetail.vue'),
      meta: {requireAuth : true}
    },
    {
      path: '/messages/:id?',
      name: 'messages',
      component: () => import('../pages/Messages.vue'),
      meta: {requireAuth : true}
    }
  ],
})


router.beforeEach(async (to, from) => {

  if (to.meta.requireAuth && !auth.isAuthenticated()) {
    return { name: 'login' }
  } else if (to.meta.guestOnly && auth.isAuthenticated()) {
    return { name: 'home' }
  } else {  
    return true
  }
})

export default router
