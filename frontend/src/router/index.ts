import { createRouter, createWebHistory } from 'vue-router'
import { onSessionEnded, touchSession } from '@/services/session'
import { accessGuard } from './accessGuard'
import { routes as homeRoutes } from './routes/home'
import { routes as movementsRoutes } from './routes/movements'
import { routes as topupRoutes } from './routes/topup'
import { routes as exchangeRoutes } from './routes/exchange'
import { routes as potsRoutes } from './routes/pots'
import { routes as paymentsRoutes } from './routes/payments'
import { routes as requestsRoutes } from './routes/requests'
import { routes as currenciesRoutes } from './routes/currencies'
import { routes as authRoutes } from './routes/auth'
import { routes as accountRoutes } from './routes/account'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    ...homeRoutes,
    ...movementsRoutes,
    ...topupRoutes,
    ...exchangeRoutes,
    ...potsRoutes,
    ...paymentsRoutes,
    ...requestsRoutes,
    ...currenciesRoutes,
    ...authRoutes,
    ...accountRoutes,
  ],
})

router.beforeEach(accessGuard)

// With the mocks no request reaches the apiClient, so changing screen must count as activity too.
router.afterEach(() => touchSession())

onSessionEnded((reason) => {
  void router.push({ name: 'login', query: reason === 'inactivity' ? { expired: '1' } : {} })
})

export default router
