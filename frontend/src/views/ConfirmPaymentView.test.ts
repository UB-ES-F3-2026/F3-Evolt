// @vitest-environment jsdom
import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, h } from 'vue'
import { createMemoryHistory, createRouter, type RouteLocationNormalized, RouterView, type Router } from 'vue-router'
import { mockBalance } from '@/mocks'
import { setMockCurrentUser } from '@/mocks/mockUser'
import { DEMO_IDENTIFIER } from '@/mocks/seed'
import { formatCents } from '@/models/money'
import ConfirmPaymentView from './ConfirmPaymentView.vue'
import HomeView from './HomeView.vue'
import MovementsView from './MovementsView.vue'

// The whole refresh chain of US-14 (T14.4) with the real mocks behind the real
// screens: sending through «Confirmar» records the movement in the same mock
// account that «Inici» and «Moviments» read (mocks/transfers.ts → mocks/index.ts).
// The mocks only hold the sender's account, so the receiver's +amount is proved
// on the backend side; here it shows up as the recipient named in the tick.

const AMOUNT_CENTS = 2000
const CONCEPT = 'El sopar de divendres'
const confirmUrl = `/pagaments/confirmar?to=usr-02&amount=${AMOUNT_CENTS}&concept=${encodeURIComponent(CONCEPT)}`

// jsdom has no IntersectionObserver; an idle one keeps the sentinel quiet, so only
// the first page asked on mount loads.
class IdleObserver {
  constructor(_callback: IntersectionObserverCallback, _options?: IntersectionObserverInit) {}
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
  takeRecords(): IntersectionObserverEntry[] {
    return []
  }
}

function plain(text: string): string {
  return text.replace(/[\u00a0\u202f]/g, ' ')
}

function queryText(value: unknown): string | undefined {
  return typeof value === 'string' ? value : undefined
}

function makeRouter(): Router {
  const nothing = { render: () => null }
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'home', component: HomeView },
      { path: '/movements', name: 'movements', component: MovementsView },
      {
        path: '/pagaments/confirmar',
        name: 'confirm-payment',
        component: ConfirmPaymentView,
        props: (route: RouteLocationNormalized) => ({
          to: queryText(route.query.to),
          amount: queryText(route.query.amount),
          concept: queryText(route.query.concept),
        }),
      },
      { path: '/pagaments', name: 'payments', component: nothing },
      { path: '/recarregar', name: 'topup', component: nothing },
      { path: '/guardioles', name: 'pots', component: nothing },
      { path: '/divises', name: 'currencies', component: nothing },
      { path: '/movements/:movementId', name: 'movement', component: nothing },
    ],
  })
}

const Host = defineComponent({ render: () => h(RouterView) })

beforeEach(() => {
  globalThis.IntersectionObserver = IdleObserver as unknown as typeof IntersectionObserver
  // Rebuild the mock account from the seed and empty today's sends: every test starts fresh.
  setMockCurrentUser(DEMO_IDENTIFIER)
  setMockCurrentUser(null)
})

afterEach(() => {
  vi.useRealTimers()
})

describe('T14.4 — cada text literal ha de quedar fixat per un test (D6, US-14)', () => {
  it('after a successful send the tick reads «Has enviat 20,00 € a Usuari nou», the viewmodel alone goes back to Inici, and Inici and Moviments show the fresh data just by mounting again, with no manual reload', async () => {
    const router = makeRouter()
    await router.push(confirmUrl)
    await router.isReady()
    const view = mount(Host, { global: { plugins: [router] } })
    await flushPromises()

    // The summary before sending: recipient, amount and balance (mockup US-14).
    expect(view.text()).toContain('Usuari nou')
    expect(plain(view.text())).toContain('20,00 €')
    expect(view.text()).toContain(CONCEPT)
    expect(plain(view.text())).toContain('Saldo disponible')

    const balanceBefore = mockBalance()

    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] })
    await view.get('button.button').trigger('click')
    await flushPromises()

    // D6: the green tick is the literal of the success (mockup US-14-exit-tic-verd),
    // already with the new balance of the same response (§13.4).
    const status = view.get('[role="status"]')
    expect(status.get('.success-text').text()).toMatch(/^Has enviat 20,00\s€ a Usuari nou$/)
    expect(plain(status.text())).toContain(plain(formatCents(mockBalance())))

    // The 1,5 s of the confirmation pass and the viewmodel itself replaces the route:
    // nobody clicks or reloads anything.
    vi.advanceTimersByTime(1500)
    await flushPromises()
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('home')

    // The refresh contract: «Inici» is a new mount and its load() on mount brings the
    // state after the transfer — the balance went down by the amount sent.
    const balanceAfter = mockBalance()
    expect(balanceAfter).toBe(balanceBefore - AMOUNT_CENTS)
    const homeText = plain(view.text())
    expect(homeText).toContain(plain(formatCents(balanceAfter)))
    expect(homeText).toContain(CONCEPT)
    expect(homeText).toContain('−20,00 €')

    // The same for «Moviments»: mounted by the router it asks its first page on mount
    // and the new movement is the first row, newest first (docs/api.md §4.2, P4).
    await router.push({ name: 'movements' })
    await flushPromises()

    const rows = view.findAll('li.movement-row')
    expect(rows).toHaveLength(20)
    expect(rows[0].text()).toContain(CONCEPT)
    expect(plain(rows[0].text())).toContain('−20,00 €')
  })
})
