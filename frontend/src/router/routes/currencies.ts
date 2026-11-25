import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/divises', name: 'currencies', component: () => import('@/views/currencies/CurrenciesView.vue') },
  { path: '/divises/afegir', name: 'add-currency', component: () => import('@/views/currencies/AddCurrencyView.vue') },
  // US-26: one currency account (EUR or a sub-account). The static «afegir» above always wins.
  { path: '/divises/:subaccountId', name: 'subaccount', component: () => import('@/views/currencies/SubaccountView.vue'), props: true },
]

export { routes }
