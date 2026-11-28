// @vitest-environment jsdom
import { flushPromises, mount, type VueWrapper } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import type { SubaccountList } from '@/models/currency'
import { getSubaccounts } from '@/services/subaccountsService'
import CurrenciesView from './CurrenciesView.vue'

// The view is thin over useCurrenciesViewModel, so the service it talks to is
// mocked and the real viewmodel runs: mount triggers `load` onMounted.
vi.mock('@/services/subaccountsService', () => ({ getSubaccounts: vi.fn() }))

const items = [
  { id: 'sub-eur', code: 'EUR' as const, balance: 125050 },
  { id: 'sub-usd', code: 'USD' as const, balance: 42716 },
]

beforeEach(() => {
  document.body.innerHTML = ''
  vi.mocked(getSubaccounts).mockReset()
})

async function mountView(list: SubaccountList): Promise<VueWrapper> {
  vi.mocked(getSubaccounts).mockResolvedValue(list)
  const empty = { template: '<div />' }
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'home', component: empty },
      { path: '/divises', name: 'currencies', component: empty },
      // The screen is mounted by hand below: the routes only have to exist.
      { path: '/divises/afegir', name: 'add-currency', component: empty },
      { path: '/divises/:subaccountId', name: 'subaccount', component: empty },
      { path: '/canviar', name: 'change-currency', component: empty },
    ],
  })
  await router.push('/divises')
  await router.isReady()
  const view = mount(CurrenciesView, { global: { plugins: [router] } })
  await flushPromises()
  return view
}

function plain(text: string): string {
  return text.replace(/[\u00a0\u202f]/g, ' ')
}

describe('CurrenciesView (US-25)', () => {
  it('paints the server total (§12.3), not the recomputed sum of the rows', async () => {
    // The server total deliberately differs from what the rows would sum to
    // (164020): the screen must paint the server's figure untouched.
    const view = await mountView({ items, totalInEuros: 199999 })

    expect(plain(view.text())).toContain('Total ≈ 1.999,99 €')
    expect(plain(view.text())).not.toContain('1.640,20 €')
  })
})
