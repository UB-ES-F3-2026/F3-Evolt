import { describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { AMOUNT_FORMAT_MESSAGE, messageForCode } from '@/models/errorMessages'
import type { Pot, Withdrawal } from '@/models/pot'
import { useWithdrawViewModel, type WithdrawDependencies } from './useWithdrawViewModel'

const vacances: Pot = { id: 'pot-01', name: 'Vacances', balance: 15000, target: 100000, color: 'blue' }
const done: Withdrawal = {
  balance: 382521,
  pot: { ...vacances, balance: 12000 },
  movement: {
    id: 'mov-31',
    amount: 3000,
    concept: 'Retirada de Vacances',
    date: '2026-11-03T10:00:00+01:00',
    type: 'income',
    icon: 'savings',
  },
}

function setUp(overrides: Partial<WithdrawDependencies> = {}) {
  const dependencies = {
    getPots: vi.fn(() => Promise.resolve([vacances])),
    withdraw: vi.fn((_potId: string, _cents: number) => Promise.resolve(done)),
    goToPot: vi.fn(() => Promise.resolve()),
    pause: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
  return { viewModel: useWithdrawViewModel('pot-01', dependencies), dependencies }
}

async function type(field: { value: string }, text: string): Promise<void> {
  field.value = text
  await nextTick()
}

describe('useWithdrawViewModel', () => {
  it('REP-02: shows the pot balance, with «Retirar de Vacances» as the title', async () => {
    const { viewModel } = setUp()
    expect(viewModel.title.value).toBe('Retirar')

    await viewModel.load()

    expect(viewModel.pot.value).toEqual(vacances)
    expect(viewModel.title.value).toBe('Retirar de Vacances')
    expect(viewModel.isLoading.value).toBe(false)
  })

  it('POT_NOT_FOUND: cannot withdraw from a pot that is not there', async () => {
    const { viewModel } = setUp({ getPots: vi.fn(() => Promise.resolve([])) })

    await viewModel.load()

    expect(viewModel.loadError.value).toBe(messageForCode('POT_NOT_FOUND'))
  })

  it('REP-03: shows no message and keeps "Confirmar" disabled while the amount is empty', async () => {
    const { viewModel } = setUp()
    await viewModel.load()

    expect(viewModel.amountError.value).toBeNull()
    expect(viewModel.canSubmit.value).toBe(false)
  })

  it.each([
    ['0', messageForCode('INVALID_AMOUNT')],
    ['-5', messageForCode('INVALID_AMOUNT')],
    ['abc', AMOUNT_FORMAT_MESSAGE],
    ['150,01', messageForCode('INSUFFICIENT_POT_BALANCE')],
  ])('REP-03, REP-04: rejects %j under the field while typing and keeps "Confirmar" disabled', async (text, message) => {
    const { viewModel } = setUp()
    await viewModel.load()

    await type(viewModel.amount, text)

    expect(viewModel.amountError.value).toBe(message)
    expect(viewModel.submitError.value).toBeNull()
    expect(viewModel.canSubmit.value).toBe(false)
  })

  it('REP-10: allows taking exactly the whole pot balance', async () => {
    const { viewModel } = setUp()
    await viewModel.load()

    await type(viewModel.amount, '150,00')

    expect(viewModel.amountError.value).toBeNull()
    expect(viewModel.canSubmit.value).toBe(true)
  })

  it('REP-05: sends the amount in cents, shows the green tick with both balances and goes back to the pot', async () => {
    const { viewModel, dependencies } = setUp()
    await viewModel.load()
    await type(viewModel.amount, '30')

    const sent = await viewModel.submit()

    expect(sent).toBe(true)
    expect(dependencies.withdraw).toHaveBeenCalledWith('pot-01', 3000)
    expect(viewModel.confirmation.value).toMatch(/^Has retirat 30,00\s€ de Vacances$/)
    expect(viewModel.balance.value).toBe(382521)
    expect(viewModel.pot.value?.balance).toBe(12000)
    expect(dependencies.pause).toHaveBeenCalledWith(1500)
    expect(dependencies.goToPot).toHaveBeenCalledOnce()
  })

  it.each(['INTERNAL_ERROR', 'NETWORK_ERROR', 'INSUFFICIENT_POT_BALANCE'] as const)(
    'REP-08, REP-09: shows %s under the button, keeps the amount typed, the field valid and the pot balance unchanged',
    async (code) => {
      const { viewModel, dependencies } = setUp({
        withdraw: vi.fn(() => Promise.reject({ code, message: 'x' })),
      })
      await viewModel.load()
      await type(viewModel.amount, '30')

      const sent = await viewModel.submit()

      expect(sent).toBe(false)
      expect(viewModel.submitError.value).toBe(messageForCode(code))
      expect(viewModel.amountError.value).toBeNull()
      expect(viewModel.amount.value).toBe('30')
      expect(viewModel.confirmation.value).toBeNull()
      expect(viewModel.pot.value?.balance).toBe(15000)
      expect(dependencies.goToPot).not.toHaveBeenCalled()
    },
  )

  it('forgets the server error as soon as the amount changes', async () => {
    const { viewModel } = setUp({
      withdraw: vi.fn(() => Promise.reject({ code: 'INTERNAL_ERROR', message: 'x' })),
    })
    await viewModel.load()
    await type(viewModel.amount, '30')
    await viewModel.submit()

    await type(viewModel.amount, '20')

    expect(viewModel.submitError.value).toBeNull()
  })

  it('does not send anything while the amount is not valid', async () => {
    const { viewModel, dependencies } = setUp()
    await viewModel.load()

    const sent = await viewModel.submit()

    expect(sent).toBe(false)
    expect(dependencies.withdraw).not.toHaveBeenCalled()
  })
})
