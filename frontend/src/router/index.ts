import { createRouter, createWebHistory } from 'vue-router'
import ContributeView from '@/views/ContributeView.vue'
import CreatePotView from '@/views/CreatePotView.vue'
import HomeView from '@/views/HomeView.vue'
import MovementDetailView from '@/views/MovementDetailView.vue'
import MovementsView from '@/views/MovementsView.vue'
import PotView from '@/views/PotView.vue'
import PotsView from '@/views/PotsView.vue'
import RegisterView from '@/views/RegisterView.vue'
import ReportProblemView from '@/views/ReportProblemView.vue'
import TopUpView from '@/views/TopUpView.vue'
import VerifyView from '@/views/VerifyView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/movements', name: 'movements', component: MovementsView },
    // `props: true` hands the id to the View, so it does not read the route itself.
    { path: '/movements/:movementId', name: 'movement', component: MovementDetailView, props: true },
    { path: '/movements/:movementId/report', name: 'report-movement', component: ReportProblemView, props: true },
    { path: '/topup', name: 'topup', component: TopUpView },
    { path: '/pots', name: 'pots', component: PotsView },
    { path: '/pots/new', name: 'create-pot', component: CreatePotView },
    { path: '/pots/:potId', name: 'pot', component: PotView, props: true },
    { path: '/pots/:potId/contribute', name: 'contribute', component: ContributeView, props: true },
    { path: '/register', name: 'register', component: RegisterView },
    { path: '/verify', name: 'verify', component: VerifyView },
  ],
})

export default router
