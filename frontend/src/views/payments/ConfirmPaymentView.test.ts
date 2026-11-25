// @vitest-environment jsdom
import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, h } from 'vue'
import { createMemoryHistory, createRouter, type RouteLocationNormalized, RouterView, type Router } from 'vue-router'
import { mockBalance } from '@/mocks'
import { setMockCurrentUser } from '@/mocks/mockUser'
import { DEMO_IDENTIFIER } from '@/mocks/seed'
import ConfirmPaymentView from './ConfirmPaymentView.vue'
import HomeView from '@/views/home/HomeView.vue'
import MovementsView from '@/views/movements/MovementsView.vue'

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
  // Twice on purpose: each call fires the mock-user change notification that wipes the
  // mock session (mocks/index.ts, mocks/transfers.ts), so leftovers from another test
  // are reset whichever user they belong to. Ending as `null` still reads the demo
  // account because `null` counts as the demo user in mocks/seed.ts (hasDemoData).
  setMockCurrentUser(DEMO_IDENTIFIER)
  setMockCurrentUser(null)
})

afterEach(() => {
  vi.useRealTimers()
})

describe('T14.4 — cada text literal ha de quedar fixat per un test (D6, US-14)', () => {
  it('after a successful send the tick reads «Has enviat 20,00 € a Usuari nou», the viewmodel alone goes back to Inici, and Inici and Moviments show the fresh data just by mounting again, with no manual reload (ENP-04 summary, ENP-05 tick + 1,5 s return, ENP-06 Inici updated)', async () => {
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

    // D6: the exact literals of ENP-04, not just that something looks similar.
    expect(view.get('button.button').text()).toBe('Confirmar enviament')
    expect(view.findAll('.summary dt').map((dt) => dt.text())).toEqual([
      'Destinatari',
      'Import',
      'Concepte',
      'Saldo disponible',
    ])

    const balanceBefore = mockBalance()

    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] })
    // The click handler runs synchronously: it flips isSubmitting before the send
    // resolves, so the button re-renders «Enviant…» on the very next tick.
    const click = view.get('button.button').trigger('click')
    await view.vm.$nextTick()
    expect(view.get('button.button').text()).toBe('Enviant…')
    await click
    await flushPromises()

    // D6: the green tick is the literal of the success (mockup US-14-exit-tic-verd),
    // already with the new balance of the same response (§13.4), as ENP-05 reads it.
    const status = view.get('[role="status"]')
    expect(status.get('.success-text').text()).toMatch(/^Has enviat 20,00\s€ a Usuari nou$/)
    expect(plain(status.get('.success-balance').text())).toMatch(/^Saldo disponible:\s*3\.775,21\s€$/)

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
    // Display literals, not recomputed values: the seed balance after sending 20,00 €.
    expect(homeText).toContain('3.775,21 €')
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

  it('with a recipient that does not exist the screen reads «Torna a triar el destinatari» and renders neither a summary nor «Confirmar enviament» (US-14.md, casos especials: destinatari inexistent)', async () => {
    const router = makeRouter()
    await router.push('/pagaments/confirmar?to=usr-99&amount=2000')
    await router.isReady()
    const view = mount(Host, { global: { plugins: [router] } })
    await flushPromises()

    // The message and the way out, exactly as US-14 writes them.
    expect(view.text()).toContain('No hem trobat aquest destinatari.')
    expect(view.text()).toContain('Torna a triar el destinatari')
    // Nothing to confirm and nothing sent: the seed balance is untouched because
    // no movement was recorded (the mocks expose no submission counter).
    expect(view.find('.summary').exists()).toBe(false)
    expect(view.find('button.button').exists()).toBe(false)
    expect(mockBalance()).toBe(379521)
  })
})
