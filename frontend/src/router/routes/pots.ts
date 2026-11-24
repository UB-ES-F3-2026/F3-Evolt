import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/pots', name: 'pots', component: () => import('@/views/pots/PotsView.vue') },
  { path: '/pots/new', name: 'create-pot', component: () => import('@/views/pots/CreatePotView.vue') },
  { path: '/pots/:potId', name: 'pot', component: () => import('@/views/pots/PotView.vue'), props: true },
  { path: '/pots/:potId/contribute', name: 'contribute', component: () => import('@/views/pots/ContributeView.vue'), props: true },
  { path: '/pots/:potId/withdraw', name: 'withdraw', component: () => import('@/views/pots/WithdrawView.vue'), props: true },
  {
    path: '/pots/:potId/withdraw/cancelled',
    name: 'withdraw-cancelled',
    component: () => import('@/views/pots/WithdrawCancelledView.vue'),
    props: true,
  },
]

export { routes }
