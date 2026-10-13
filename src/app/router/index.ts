import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/features/home/view/HomeView.vue'
import MovementsView from '@/features/movements/view/MovementsView.vue'
import TopUpView from '@/features/topup/view/TopUpView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/movements', name: 'movements', component: MovementsView },
    { path: '/topup', name: 'topup', component: TopUpView },
  ],
})

export default router
