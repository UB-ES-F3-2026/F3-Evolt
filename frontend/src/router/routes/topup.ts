import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/topup', name: 'topup', component: () => import('@/views/topup/TopUpView.vue') },
]

export { routes }
