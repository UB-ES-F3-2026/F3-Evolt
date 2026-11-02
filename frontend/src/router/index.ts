import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import MovementsView from '@/views/MovementsView.vue'
import PotsView from '@/views/PotsView.vue'
import TopUpView from '@/views/TopUpView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/movements', name: 'movements', component: MovementsView },
    { path: '/topup', name: 'topup', component: TopUpView },
    { path: '/pots', name: 'pots', component: PotsView },
  ],
})

export default router
