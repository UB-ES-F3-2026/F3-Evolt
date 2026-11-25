import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/movements', name: 'movements', component: () => import('@/views/movements/MovementsView.vue') },
  // `props: true` hands the id to the View, so it does not read the route itself.
  { path: '/movements/:movementId', name: 'movement', component: () => import('@/views/movements/MovementDetailView.vue'), props: true },
  { path: '/movements/:movementId/report', name: 'report-movement', component: () => import('@/views/movements/ReportProblemView.vue'), props: true },
]

export { routes }
