import { describe, expect, it, vi } from 'vitest'
import { messageForCode } from '@/models/errorMessages'
import type { Home } from '@/models/home'
import type { Pot } from '@/models/pot'
import { useWithdrawCancelledViewModel, type WithdrawCancelledDependencies } from './useWithdrawCancelledViewModel'

const vacances: Pot = { id: 'pot-01', name: 'Vacances', balance: 15000, target: 100000, color: 'blue' }
const home: Home = { balance: 379521, totalSaved: 30000, lastMovements: [] }

function setUp(overrides: Partial<WithdrawCancelledDependencies> = {}) {
  const dependencies = {
    getHome: vi.fn(() => Promise.resolve(home)),
    getPots: vi.fn(() => Promise.resolve([vacances])),
    goToPot: vi.fn(() => Promise.resolve()),
    pause: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
  return { viewModel: useWithdrawCancelledViewModel('pot-01', dependencies), dependencies }
}

describe('useWithdrawCancelledViewModel', () => {
  it('REP-12: shows both balances unchanged, read again from the API', async () => {
    const { viewModel } = setUp()

    await viewModel.load()

    expect(viewModel.balance.value).toBe(379521)
    expect(viewModel.pot.value).toEqual(vacances)
    expect(viewModel.error.value).toBeNull()
  })

  it('REP-12: goes back to the pot by itself after 1,5 s', async () => {
    const { viewModel, dependencies } = setUp()

    await viewModel.returnAutomatically()

    expect(dependencies.pause).toHaveBeenCalledWith(1500)
    expect(dependencies.goToPot).toHaveBeenCalledOnce()
  })

  it('REP-12: «Tornar a la guardiola» goes back earlier, and the timer does not navigate again', async () => {
    let endPause: () => void = () => undefined
    const pause = vi.fn(() => new Promise<void>((resolve) => (endPause = resolve)))
    const { viewModel, dependencies } = setUp({ pause })

    const automatic = viewModel.returnAutomatically()
    await viewModel.backToPot()
    endPause()
    await automatic

    expect(dependencies.goToPot).toHaveBeenCalledOnce()
  })

  it('does not go back to the pot by itself once the screen is gone (left through «← Inici»)', async () => {
    let endPause: () => void = () => undefined
    const pause = vi.fn(() => new Promise<void>((resolve) => (endPause = resolve)))
    const { viewModel, dependencies } = setUp({ pause })

    const automatic = viewModel.returnAutomatically()
    viewModel.stop()
    endPause()
    await automatic

    expect(dependencies.goToPot).not.toHaveBeenCalled()
  })

  it('cannot show the notice of a pot that is not there', async () => {
    const { viewModel } = setUp({ getPots: vi.fn(() => Promise.resolve([])) })

    await viewModel.load()

    expect(viewModel.error.value).toBe(messageForCode('POT_NOT_FOUND'))
  })
})
