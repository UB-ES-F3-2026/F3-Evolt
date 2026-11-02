import { createRouter, createWebHistory } from 'vue-router'
import ContributeView from '@/views/ContributeView.vue'
import CreatePotView from '@/views/CreatePotView.vue'
import HomeView from '@/views/HomeView.vue'
import MovementsView from '@/views/MovementsView.vue'
import PotView from '@/views/PotView.vue'
import PotsView from '@/views/PotsView.vue'
import TopUpView from '@/views/TopUpView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/movements', name: 'movements', component: MovementsView },
    { path: '/topup', name: 'topup', component: TopUpView },
    { path: '/pots', name: 'pots', component: PotsView },
    { path: '/pots/new', name: 'create-pot', component: CreatePotView },
    // `props: true` hands the id to the View, so it does not read the route itself.
    { path: '/pots/:potId', name: 'pot', component: PotView, props: true },
    { path: '/pots/:potId/contribute', name: 'contribute', component: ContributeView, props: true },
  ],
})

export default router
