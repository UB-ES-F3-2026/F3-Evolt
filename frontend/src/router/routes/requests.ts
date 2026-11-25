import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  // US-15: reached from the menu of every screen; «Demanar diners» lives inside the list.
  { path: '/requests', name: 'money-requests', component: () => import('@/views/requests/MoneyRequestsView.vue') },
  { path: '/requests/new', name: 'new-money-request', component: () => import('@/views/requests/NewMoneyRequestView.vue') },
]

export { routes }
