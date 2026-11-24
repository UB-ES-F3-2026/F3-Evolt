// @vitest-environment jsdom
import { flushPromises, mount, RouterLinkStub } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ref } from 'vue'
import type { Pot } from '@/models/pot'
import { useWithdrawCancelledViewModel } from '@/viewmodels/pots/useWithdrawCancelledViewModel'
import WithdrawCancelledView from './WithdrawCancelledView.vue'

vi.mock('@/viewmodels/pots/useWithdrawCancelledViewModel', () => ({ useWithdrawCancelledViewModel: vi.fn() }))

const vacances: Pot = { id: 'pot-01', name: 'Vacances', balance: 15000, target: 100000, color: 'blue' }

function viewModel() {
  return {
    pot: ref<Pot | null>(vacances),
    balance: ref<number | null>(379521),
    isLoading: ref(false),
    error: ref<string | null>(null),
    load: vi.fn(() => Promise.resolve()),
    backToPot: vi.fn(() => Promise.resolve()),
    returnAutomatically: vi.fn(() => Promise.resolve()),
    stop: vi.fn(),
  }
}

function mountWith(state: ReturnType<typeof viewModel>) {
  vi.mocked(useWithdrawCancelledViewModel).mockReturnValue(state)
  return mount(WithdrawCancelledView, {
    props: { potId: 'pot-01' },
    global: { stubs: { RouterLink: RouterLinkStub } },
  })
}

beforeEach(() => {
  vi.mocked(useWithdrawCancelledViewModel).mockReset()
})

describe('WithdrawCancelledView', () => {
  it('REP-12: says «Retirada cancel·lada» with the text and both balances, without an amount or a tick', () => {
    const screen = mountWith(viewModel())
    const notice = screen.find('[role="status"]')

    expect(notice.find('h2').text()).toBe('Retirada cancel·lada')
    expect(notice.text()).toContain("No s'ha retirat res i cap dels dos saldos canvia.")
    expect(notice.text()).toMatch(/Saldo disponible: 3\.795,21\s€ · Vacances: 150,00\s€/)
    expect(notice.find('svg').exists()).toBe(false)
  })

  it('REP-12: keeps the header of «Retirar de Vacances», with «← Inici»', () => {
    const screen = mountWith(viewModel())

    expect(screen.find('h1').text()).toBe('Retirar de Vacances')
    expect(screen.findAllComponents(RouterLinkStub).some((link) => link.text() === '← Inici')).toBe(true)
  })

  it('REP-12: starts the automatic return, and «Tornar a la guardiola» goes back earlier', async () => {
    const state = viewModel()
    const screen = mountWith(state)
    await flushPromises()

    expect(state.returnAutomatically).toHaveBeenCalledOnce()
    await screen.find('button').trigger('click')
    expect(state.backToPot).toHaveBeenCalledOnce()
  })

  it('stops the automatic return when the screen is left', () => {
    const state = viewModel()
    const screen = mountWith(state)

    screen.unmount()

    expect(state.stop).toHaveBeenCalledOnce()
  })
})
