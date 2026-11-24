import { describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { AMOUNT_FORMAT_MESSAGE, messageForCode } from '@/models/errorMessages'
import type { Home } from '@/models/home'
import type { Contribution, Pot } from '@/models/pot'
import { useContributeViewModel, type ContributeDependencies } from './useContributeViewModel'

const vacances: Pot = { id: 'pot-01', name: 'Vacances', balance: 15000, target: 100000, color: 'blue' }
const home: Home = { balance: 379521, totalSaved: 30000, lastMovements: [] }
const done: Contribution = {
  balance: 376521,
  pot: { ...vacances, balance: 18000 },
  movement: {
    id: 'mov-31',
    amount: 3000,
    concept: 'Aportació a Vacances',
    date: '2026-11-03T10:00:00+01:00',
    type: 'expense',
    icon: 'savings',
  },
}

function setUp(overrides: Partial<ContributeDependencies> = {}) {
  const dependencies = {
    getHome: vi.fn(() => Promise.resolve(home)),
    getPots: vi.fn(() => Promise.resolve([vacances])),
    contribute: vi.fn((_potId: string, _cents: number) => Promise.resolve(done)),
    goToPot: vi.fn(() => Promise.resolve()),
    pause: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
  return { viewModel: useContributeViewModel('pot-01', dependencies), dependencies }
}

async function type(field: { value: string }, text: string): Promise<void> {
  field.value = text
  await nextTick()
}

describe('useContributeViewModel', () => {
  it('shows the main balance and the pot at the top, with the pot name in the title (US-18, criteria 1 and 2)', async () => {
    const { viewModel } = setUp()
    expect(viewModel.title.value).toBe('Aportar')

    await viewModel.load()

    expect(viewModel.balance.value).toBe(379521)
    expect(viewModel.pot.value).toEqual(vacances)
    expect(viewModel.title.value).toBe('Aportar a Vacances')
    expect(viewModel.isLoading.value).toBe(false)
  })

  it('cannot contribute to a pot that is not there', async () => {
    const { viewModel } = setUp({ getPots: vi.fn(() => Promise.resolve([])) })

    await viewModel.load()

    expect(viewModel.loadError.value).toBe(messageForCode('POT_NOT_FOUND'))
  })

  it.each([
    ['0', messageForCode('INVALID_AMOUNT')],
    ['-5', messageForCode('INVALID_AMOUNT')],
    ['abc', AMOUNT_FORMAT_MESSAGE],
    ['3795,22', messageForCode('INSUFFICIENT_BALANCE')],
  ])('rejects %j with its reason and keeps "Confirmar" disabled (criterion 3)', async (text, message) => {
    const { viewModel } = setUp()
    await viewModel.load()

    await type(viewModel.amount, text)

    expect(viewModel.error.value).toBe(message)
    expect(viewModel.canSubmit.value).toBe(false)
  })

  it('allows moving exactly the whole main balance', async () => {
    const { viewModel } = setUp()
    await viewModel.load()

    await type(viewModel.amount, '3795,21')

    expect(viewModel.error.value).toBeNull()
    expect(viewModel.canSubmit.value).toBe(true)
  })

  it('sends the amount in cents, shows the green tick text and goes back to the pot (criteria 4 and 5)', async () => {
    const { viewModel, dependencies } = setUp()
    await viewModel.load()
    await type(viewModel.amount, '30')

    const sent = await viewModel.submit()

    expect(sent).toBe(true)
    expect(dependencies.contribute).toHaveBeenCalledWith('pot-01', 3000)
    expect(viewModel.confirmation.value).toMatch(/^Has aportat 30,00\s€ a Vacances$/)
    expect(viewModel.balance.value).toBe(376521)
    expect(viewModel.pot.value?.balance).toBe(18000)
    expect(dependencies.pause).toHaveBeenCalledOnce()
    expect(dependencies.goToPot).toHaveBeenCalledOnce()
  })

  it('shows the error in red and keeps both balances when the server fails (criterion 7)', async () => {
    const { viewModel, dependencies } = setUp({
      contribute: vi.fn(() => Promise.reject({ code: 'INTERNAL_ERROR', message: 'x' })),
    })
    await viewModel.load()
    await type(viewModel.amount, '30')

    const sent = await viewModel.submit()

    expect(sent).toBe(false)
    expect(viewModel.error.value).toBe(messageForCode('INTERNAL_ERROR'))
    expect(viewModel.confirmation.value).toBeNull()
    expect(viewModel.balance.value).toBe(379521)
    expect(viewModel.pot.value?.balance).toBe(15000)
    expect(dependencies.goToPot).not.toHaveBeenCalled()
  })

  it('forgets the server error as soon as the amount changes', async () => {
    const { viewModel } = setUp({
      contribute: vi.fn(() => Promise.reject({ code: 'INSUFFICIENT_BALANCE', message: 'x' })),
    })
    await viewModel.load()
    await type(viewModel.amount, '30')
    await viewModel.submit()
    expect(viewModel.error.value).toBe(messageForCode('INSUFFICIENT_BALANCE'))

    await type(viewModel.amount, '20')

    expect(viewModel.error.value).toBeNull()
  })

  it('does not send anything while the amount is not valid', async () => {
    const { viewModel, dependencies } = setUp()
    await viewModel.load()

    const sent = await viewModel.submit()

    expect(sent).toBe(false)
    expect(dependencies.contribute).not.toHaveBeenCalled()
  })
})
