import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  // US-12: reached from the menu of every screen.
  { path: '/account', name: 'account-details', component: () => import('@/views/account/AccountDetailsView.vue') },
]

export { routes }
