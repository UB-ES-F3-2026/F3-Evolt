import { createRouter, createWebHistory } from 'vue-router'
import { onSessionEnded, touchSession } from '@/services/session'
import AddCurrencyView from '@/views/AddCurrencyView.vue'
import ContributeView from '@/views/ContributeView.vue'
import CreatePotView from '@/views/CreatePotView.vue'
import CurrenciesView from '@/views/CurrenciesView.vue'
import ForgotPasswordView from '@/views/ForgotPasswordView.vue'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import MovementDetailView from '@/views/MovementDetailView.vue'
import MovementsView from '@/views/MovementsView.vue'
import NewPasswordView from '@/views/NewPasswordView.vue'
import PaymentsView from '@/views/PaymentsView.vue'
import PotView from '@/views/PotView.vue'
import PotsView from '@/views/PotsView.vue'
import RegisterView from '@/views/RegisterView.vue'
import SubaccountView from '@/views/SubaccountView.vue'
import ReportProblemView from '@/views/ReportProblemView.vue'
import SendPaymentView from '@/views/SendPaymentView.vue'
import TopUpView from '@/views/TopUpView.vue'
import VerifyView from '@/views/VerifyView.vue'
import WithdrawView from '@/views/WithdrawView.vue'
import { accessGuard } from './accessGuard'

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
    { path: '/pots/:potId/withdraw', name: 'withdraw', component: WithdrawView, props: true },
    { path: '/pagaments', name: 'payments', component: PaymentsView },
    // The recipient travels in `?to=<id>`, so a reload keeps it (US-13).
    {
      path: '/pagaments/enviar',
      name: 'send-payment',
      component: SendPaymentView,
      props: (route) => ({ to: typeof route.query.to === 'string' ? route.query.to : undefined }),
    },
    { path: '/divises', name: 'currencies', component: CurrenciesView },
    { path: '/divises/afegir', name: 'add-currency', component: AddCurrencyView },
    // US-26: one currency account (EUR or a sub-account). The static «afegir» above always wins.
    { path: '/divises/:subaccountId', name: 'subaccount', component: SubaccountView, props: true },
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
