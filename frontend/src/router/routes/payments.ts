import type { RouteRecordRaw } from 'vue-router'
import { queryText } from '../queryText'

const routes: RouteRecordRaw[] = [
  { path: '/pagaments', name: 'payments', component: () => import('@/views/payments/PaymentsView.vue') },
  // The recipient travels in `?to=<id>`, so a reload keeps it (US-13).
  {
    path: '/pagaments/enviar',
    name: 'send-payment',
    component: () => import('@/views/payments/SendPaymentView.vue'),
    props: (route) => ({ to: queryText(route.query.to) }),
  },
  // What «Enviar» chose travels in the URL too, so «Confirmar» survives a reload (US-14).
  {
    path: '/pagaments/confirmar',
    name: 'confirm-payment',
    component: () => import('@/views/payments/ConfirmPaymentView.vue'),
    props: (route) => ({
      to: queryText(route.query.to),
      amount: queryText(route.query.amount),
      concept: queryText(route.query.concept),
    }),
  },
]

export { routes }
