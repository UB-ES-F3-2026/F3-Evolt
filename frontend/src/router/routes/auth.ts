import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/login', name: 'login', component: () => import('@/views/auth/LoginView.vue'), meta: { public: true } },
  { path: '/register', name: 'register', component: () => import('@/views/auth/RegisterView.vue'), meta: { public: true } },
  { path: '/verify', name: 'verify', component: () => import('@/views/auth/VerifyView.vue'), meta: { public: true } },
  { path: '/forgot-password', name: 'forgot-password', component: () => import('@/views/auth/ForgotPasswordView.vue'), meta: { public: true } },
  // This path is in the recovery link the backend sends (docs/api.md §8.10).
  { path: '/nova-contrasenya', name: 'new-password', component: () => import('@/views/auth/NewPasswordView.vue'), meta: { public: true } },
]

export { routes }
