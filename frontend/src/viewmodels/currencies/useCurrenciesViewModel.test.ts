import { describe, expect, it, vi } from 'vitest'
import { type Subaccount, type SubaccountList } from '@/models/currency'
import { messageForCode } from '@/models/errorMessages'
import { useCurrenciesViewModel, type CurrenciesDependencies } from './useCurrenciesViewModel'

const owned: Subaccount[] = [
  { id: 'sub-eur', code: 'EUR', balance: 125050 },
  { id: 'sub-usd', code: 'USD', balance: 42716 },
]

// A §12.3 list: the rows plus the total the server already computed.
function fakeList(totalInEuros: number): SubaccountList {
  return { items: owned, totalInEuros }
}

function fakeDependencies(overrides: Partial<CurrenciesDependencies> = {}) {
  return {
    // A well-behaved server: the total matches what the rows sum to (§12.1).
    getSubaccounts: vi.fn(() => Promise.resolve(fakeList(164020))),
    goToAdd: vi.fn(),
    goChange: vi.fn(),
    goToSubaccount: vi.fn(),
    ...overrides,
  }
}

describe('useCurrenciesViewModel', () => {
  it('starts loading, so a zero total never flashes', () => {
    const viewModel = useCurrenciesViewModel(fakeDependencies())

    expect(viewModel.isLoading.value).toBe(true)
    expect(viewModel.error.value).toBeNull()
    expect(viewModel.rows.value).toEqual([])
    expect(viewModel.totalCents.value).toBe(0)
  })

  it('lists only the owned sub-accounts, in CURRENCIES order (EUR first)', async () => {
    const viewModel = useCurrenciesViewModel(fakeDependencies())

    await viewModel.load()

    expect(viewModel.isLoading.value).toBe(false)
    expect(viewModel.error.value).toBeNull()
    expect(viewModel.rows.value.map((row) => row.code)).toEqual(['EUR', 'USD'])
    expect(viewModel.rows.value[0]).toMatchObject({ code: 'EUR', name: 'Euro', symbol: '€' })
    expect(viewModel.rows.value[0].amountText).toMatch(/^1\.250,50\s€$/)
    expect(viewModel.rows.value[1]).toMatchObject({
      code: 'USD',
      name: 'Dòlar nord-americà',
      symbol: '$',
    })
    expect(viewModel.rows.value[1].amountText).toMatch(/^427,16\s\$$/)
  })

  it('shows the server total instead of recomputing it from the rows', async () => {
    // The server total deliberately differs from what the rows would sum to
    // (164020): the screen must display the server's figure untouched (§12.3).
    const viewModel = useCurrenciesViewModel(
      fakeDependencies({ getSubaccounts: vi.fn(() => Promise.resolve(fakeList(199999))) }),
    )

    await viewModel.load()

    expect(viewModel.totalCents.value).toBe(199999)
  })

  it('shows the user message of a rejected load and no rows', async () => {
    const failure = { code: 'INTERNAL_ERROR', message: 'x' }
    const viewModel = useCurrenciesViewModel(
      fakeDependencies({ getSubaccounts: vi.fn(() => Promise.reject(failure)) }),
    )

    await viewModel.load()

    expect(viewModel.error.value).toBe(messageForCode('INTERNAL_ERROR'))
    expect(viewModel.rows.value).toEqual([])
    expect(viewModel.isLoading.value).toBe(false)
  })

  it('delegates adding and changing currencies to the injected navigation', () => {
    const dependencies = fakeDependencies()
    const viewModel = useCurrenciesViewModel(dependencies)

    viewModel.goToAdd()
    viewModel.goChange()

    expect(dependencies.goToAdd).toHaveBeenCalledTimes(1)
    expect(dependencies.goChange).toHaveBeenCalledTimes(1)
  })

  it('US-26: each row carries its account id, and opens its detail', async () => {
    const dependencies = fakeDependencies()
    const viewModel = useCurrenciesViewModel(dependencies)

    await viewModel.load()
    viewModel.goToSubaccount(viewModel.rows.value[1].id)

    expect(viewModel.rows.value.map((row) => row.id)).toEqual(['sub-eur', 'sub-usd'])
    expect(dependencies.goToSubaccount).toHaveBeenCalledWith('sub-usd')
  })
})
