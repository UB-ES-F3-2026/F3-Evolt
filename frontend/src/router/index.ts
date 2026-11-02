import { createRouter, createWebHistory } from 'vue-router'
import CreatePotView from '@/views/CreatePotView.vue'
import HomeView from '@/views/HomeView.vue'
import MovementsView from '@/views/MovementsView.vue'
import PotsView from '@/views/PotsView.vue'
import RegisterView from '@/views/RegisterView.vue'
import TopUpView from '@/views/TopUpView.vue'
import VerifyView from '@/views/VerifyView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/movements', name: 'movements', component: MovementsView },
    { path: '/topup', name: 'topup', component: TopUpView },
    { path: '/pots', name: 'pots', component: PotsView },
    { path: '/pots/new', name: 'create-pot', component: CreatePotView },
    { path: '/register', name: 'register', component: RegisterView },
    { path: '/verify', name: 'verify', component: VerifyView },
  ],
})

export default router
