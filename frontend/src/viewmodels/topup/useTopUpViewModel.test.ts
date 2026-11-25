import { nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'
import type { TopupResult } from '@/models/topup'
import { useTopUpViewModel, type TopUpDependencies } from './useTopUpViewModel'

function topupResult(amount: number): TopupResult {
  return {
    balance: 125050 + amount,
    movement: {
      id: 'mov-topup-1',
      amount,
      concept: 'Recàrrega',
      date: '2026-10-17T12:00:00+02:00',
      type: 'income',
      icon: 'topup',
    },
  }
}

function fakeDependencies(overrides: Partial<TopUpDependencies> = {}) {
  return {
    createTopup: vi.fn((amount: number) => Promise.resolve(topupResult(amount))),
    goHome: vi.fn(() => Promise.resolve()),
    pause: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
}

describe('useTopUpViewModel', () => {
  it('starts empty: no error and nothing to send', () => {
    const viewModel = useTopUpViewModel(fakeDependencies())

    expect(viewModel.error.value).toBeNull()
    expect(viewModel.canSubmit.value).toBe(false)
  })

  it.each([
    ['abc', /2 decimals com a màxim/],
    ['12,345', /2 decimals com a màxim/],
    ['0', /més gran que 0/],
    ['500,01', /màxim per recàrrega és de 500,00\s€/],
  ])('rejects %j before sending', (typed, message) => {
    const viewModel = useTopUpViewModel(fakeDependencies())

    viewModel.amount.value = typed

    expect(viewModel.error.value).toMatch(message)
    expect(viewModel.canSubmit.value).toBe(false)
  })

  it('accepts exactly 500 €', () => {
    const viewModel = useTopUpViewModel(fakeDependencies())

    viewModel.amount.value = '500'

    expect(viewModel.error.value).toBeNull()
    expect(viewModel.canSubmit.value).toBe(true)
  })

  it('sends the amount in cents, confirms and then goes back to Home', async () => {
    const dependencies = fakeDependencies()
    const viewModel = useTopUpViewModel(dependencies)
    viewModel.amount.value = '12,5'

    const sent = await viewModel.submit()

    expect(sent).toBe(true)
    expect(dependencies.createTopup).toHaveBeenCalledWith(1250)
    expect(viewModel.confirmation.value).toMatch(/Recàrrega feta: \+12,50\s€/)
    expect(dependencies.pause).toHaveBeenCalledWith(1500)
    expect(dependencies.goHome).toHaveBeenCalledTimes(1)
    expect(viewModel.isSubmitting.value).toBe(false)
  })

  it('stays disabled while sending, so a double click sends once', async () => {
    const dependencies = fakeDependencies()
    const viewModel = useTopUpViewModel(dependencies)
    viewModel.amount.value = '20'

    const first = viewModel.submit()
    expect(viewModel.isSubmitting.value).toBe(true)
    expect(viewModel.canSubmit.value).toBe(false)
    const second = await viewModel.submit()
    await first

    expect(second).toBe(false)
    expect(dependencies.createTopup).toHaveBeenCalledTimes(1)
  })

  it('shows the daily limit with what is left today and stays on the screen', async () => {
    const failure = { code: 'DAILY_LIMIT_EXCEEDED', message: 'x', details: { remainingToday: 10000 } }
    const dependencies = fakeDependencies({ createTopup: vi.fn(() => Promise.reject(failure)) })
    const viewModel = useTopUpViewModel(dependencies)
    viewModel.amount.value = '100,01'

    const sent = await viewModel.submit()

    expect(sent).toBe(false)
    expect(viewModel.error.value).toMatch(/Avui encara pots recarregar 100,00\s€/)
    expect(viewModel.isSubmitting.value).toBe(false)
    expect(viewModel.confirmation.value).toBeNull()
    expect(dependencies.goHome).not.toHaveBeenCalled()
  })

  it('clears the backend error when the amount changes', async () => {
    const failure = { code: 'NETWORK_ERROR', message: 'x' }
    const viewModel = useTopUpViewModel(fakeDependencies({ createTopup: vi.fn(() => Promise.reject(failure)) }))
    viewModel.amount.value = '50'
    await viewModel.submit()
    expect(viewModel.error.value).toMatch(/connexió/)

    viewModel.amount.value = '40'
    await nextTick()

    expect(viewModel.error.value).toBeNull()
  })

  it('does not send an invalid amount', async () => {
    const dependencies = fakeDependencies()
    const viewModel = useTopUpViewModel(dependencies)
    viewModel.amount.value = '600'

    expect(await viewModel.submit()).toBe(false)
    expect(dependencies.createTopup).not.toHaveBeenCalled()
  })
})
