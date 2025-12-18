// router/index.js
import { createRouter, createWebHistory } from 'vue-router'

import LoginView from '../pages/Login.vue'
import HomeView from '../pages/Home.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      children: [
        {
          path: 'user',
          name: 'user',
          component: () => import('../pages/Profile.vue')
        },
        {
          path: 'order',
          name: 'order',
          component: () => import('../pages/MyOrder.vue')
        },
        {
          path: 'favorite',
          name: 'favorite',
          component: () => import('../pages/Favorite.vue')
        },
        {
          path : 'create_product',
          name: 'create_product',
          component: () => import('../pages/CreateProduct.vue')
        }
      ]
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
  ],
})


router.beforeEach(async (to, from) => {
  if (to.name !== 'login' && !localStorage.getItem('token')) {
    return {
      name: 'login',
    }
  } else if (to.name === 'login' && localStorage.getItem('token')) {
    return {
      name: 'home',
    }
  }
})

export default router
