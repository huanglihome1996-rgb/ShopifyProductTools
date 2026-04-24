import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { title: '仪表盘' },
    },
    {
      path: '/stores',
      name: 'stores',
      component: () => import('@/views/Stores.vue'),
      meta: { title: '店铺管理' },
    },
    {
      path: '/products',
      name: 'products',
      component: () => import('@/views/Products.vue'),
      meta: { title: '产品管理' },
    },
    {
      path: '/import',
      name: 'import',
      component: () => import('@/views/Import.vue'),
      meta: { title: '数据导入' },
    },
    {
      path: '/optimize',
      name: 'optimize',
      component: () => import('@/views/Optimize.vue'),
      meta: { title: 'AI优化' },
    },
    {
      path: '/history',
      name: 'history',
      component: () => import('@/views/History.vue'),
      meta: { title: '历史记录' },
    },
  ],
})

export default router
