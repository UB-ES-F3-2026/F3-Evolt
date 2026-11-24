import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/canviar', name: 'exchange', component: () => import('@/views/exchange/ExchangeView.vue') },
  { path: '/canviar/resum', name: 'exchange-summary', component: () => import('@/views/exchange/ExchangeSummaryView.vue') },
]

export { routes }
