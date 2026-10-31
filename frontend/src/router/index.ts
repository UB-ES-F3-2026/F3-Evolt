import { createRouter, createWebHistory } from 'vue-router'
import { onSessionEnded, touchSession } from '@/services/session'
import ForgotPasswordView from '@/views/ForgotPasswordView.vue'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import MovementsView from '@/views/MovementsView.vue'
import NewPasswordView from '@/views/NewPasswordView.vue'
import RegisterView from '@/views/RegisterView.vue'
import TopUpView from '@/views/TopUpView.vue'
import VerifyView from '@/views/VerifyView.vue'
import { accessGuard } from './accessGuard'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/movements', name: 'movements', component: MovementsView },
    { path: '/topup', name: 'topup', component: TopUpView },
    { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
    { path: '/register', name: 'register', component: RegisterView, meta: { public: true } },
    { path: '/verify', name: 'verify', component: VerifyView, meta: { public: true } },
    { path: '/forgot-password', name: 'forgot-password', component: ForgotPasswordView, meta: { public: true } },
    // This path is in the recovery link the backend sends (docs/api.md §8.10).
    { path: '/nova-contrasenya', name: 'new-password', component: NewPasswordView, meta: { public: true } },
  ],
})

router.beforeEach(accessGuard)

// With the mocks no request reaches the apiClient, so changing screen must count as activity too.
router.afterEach(() => touchSession())

onSessionEnded((reason) => {
  void router.push({ name: 'login', query: reason === 'inactivity' ? { expired: '1' } : {} })
})

export default router
