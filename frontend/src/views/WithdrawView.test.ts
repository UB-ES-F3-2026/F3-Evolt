// @vitest-environment jsdom
import { mount, RouterLinkStub } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ref } from 'vue'
import type { Pot } from '@/models/pot'
import { useWithdrawViewModel } from '@/viewmodels/useWithdrawViewModel'
import WithdrawView from './WithdrawView.vue'

vi.mock('@/viewmodels/useWithdrawViewModel', () => ({ useWithdrawViewModel: vi.fn() }))

const vacances: Pot = { id: 'pot-01', name: 'Vacances', balance: 15000, target: 100000, color: 'blue' }

/** The ViewModel state the screen draws: a loaded pot and a valid amount, unless overridden. */
function viewModel(overrides: { amountError?: string | null; submitError?: string | null } = {}) {
  return {
    pot: ref<Pot | null>(vacances),
    balance: ref<number | null>(null),
    title: ref('Retirar de Vacances'),
    isLoading: ref(false),
    loadError: ref<string | null>(null),
    amount: ref('30'),
    amountError: ref(overrides.amountError ?? null),
    submitError: ref(overrides.submitError ?? null),
    canSubmit: ref(true),
    isSubmitting: ref(false),
    confirmation: ref<string | null>(null),
    load: vi.fn(() => Promise.resolve()),
    submit: vi.fn(() => Promise.resolve(true)),
  }
}

function mountWith(state: ReturnType<typeof viewModel>) {
  vi.mocked(useWithdrawViewModel).mockReturnValue(state as unknown as ReturnType<typeof useWithdrawViewModel>)
  return mount(WithdrawView, { props: { potId: 'pot-01' }, global: { stubs: { RouterLink: RouterLinkStub } } })
}

function linkTo(screen: ReturnType<typeof mountWith>, text: string) {
  return screen.findAllComponents(RouterLinkStub).find((link) => link.text() === text)?.props('to')
}

beforeEach(() => {
  vi.mocked(useWithdrawViewModel).mockReset()
})

describe('WithdrawView', () => {
  it('US-19 «Pantalles»: «← Inici» at the top goes back to the home screen', () => {
    const screen = mountWith(viewModel())

    expect(linkTo(screen, '← Inici')).toBe('/')
  })

  it('REP-12: «Cancel·lar» opens the «Retirada cancel·lada» notice without withdrawing', () => {
    const state = viewModel()
    const screen = mountWith(state)

    expect(linkTo(screen, 'Cancel·lar')).toEqual({ name: 'withdraw-cancelled', params: { potId: 'pot-01' } })
    expect(state.submit).not.toHaveBeenCalled()
  })

  it('REP-04: an amount error goes under the field, which turns red', () => {
    const screen = mountWith(viewModel({ amountError: 'La guardiola no té prou saldo per aquesta retirada.' }))

    expect(screen.find('.field').classes()).toContain('invalid')
    expect(screen.find('input').attributes('aria-invalid')).toBe('true')
    expect(screen.find('#withdrawal-amount-error').text()).toBe('La guardiola no té prou saldo per aquesta retirada.')
    expect(screen.find('.submit-error').exists()).toBe(false)
  })

  it('REP-08: a server error goes under «Confirmar» and leaves the field as it is', () => {
    const message = "S'ha produït un error inesperat. Torna-ho a provar més tard."
    const screen = mountWith(viewModel({ submitError: message }))

    const button = screen.find('button[type="submit"]').element
    const error = screen.find('.submit-error').element
    expect(error.textContent).toBe(message)
    // DOCUMENT_POSITION_FOLLOWING: the message comes after the button.
    expect(button.compareDocumentPosition(error) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(screen.find('.field').classes()).not.toContain('invalid')
    expect(screen.find('input').attributes('aria-invalid')).toBe('false')
  })
})
