import { describe, expect, it, vi } from 'vitest'
import type { CurrencyCode, Subaccount, SubaccountList } from '@/models/currency'
import { messageForCode } from '@/models/errorMessages'
import { useAddCurrencyViewModel, type AddCurrencyDependencies } from './useAddCurrencyViewModel'

const rateBps: Record<CurrencyCode, number> = { EUR: 10000, USD: 9123, GBP: 11680, CHF: 10355, JPY: 5700 }

function row(code: CurrencyCode, balance: number, isMain: boolean): Subaccount {
  return { id: `sub-${code.toLowerCase()}`, code, balance, isMain, rateBps: rateBps[code] }
}

const ownedEur: SubaccountList = { items: [row('EUR', 125050, true)], totalInEuros: 125050 }
const ownedEurAndUsd: SubaccountList = {
  items: [...ownedEur.items, row('USD', 0, false)],
  totalInEuros: 125050,
}

function fakeDependencies(overrides: Partial<AddCurrencyDependencies> = {}) {
  return {
    getSubaccounts: vi.fn(() => Promise.resolve(ownedEur)),
    addSubaccount: vi.fn((code: CurrencyCode) =>
      Promise.resolve(row(code, 0, false)),
    ),
    goHome: vi.fn(() => Promise.resolve()),
    pause: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
}

describe('useAddCurrencyViewModel', () => {
  it('starts loading with the five currencies and none owned yet', () => {
    const viewModel = useAddCurrencyViewModel(fakeDependencies())

    expect(viewModel.isLoading.value).toBe(true)
    expect(viewModel.rows.value.map((row) => row.code)).toEqual(['EUR', 'USD', 'GBP', 'CHF', 'JPY'])
    expect(viewModel.rows.value.every((row) => !row.owned && !row.disabled)).toBe(true)
  })

  it('marks the owned currencies and leaves the rest selectable', async () => {
    const viewModel = useAddCurrencyViewModel(fakeDependencies())

    await viewModel.load()

    const eur = viewModel.rows.value.find((row) => row.code === 'EUR')
    const usd = viewModel.rows.value.find((row) => row.code === 'USD')
    expect(eur).toMatchObject({ name: 'Euro', symbol: '€', owned: true, disabled: true })
    expect(usd).toMatchObject({ owned: false, disabled: false })
    expect(viewModel.isLoading.value).toBe(false)
  })

  it('creates the sub-account, confirms, pauses and goes back to Home', async () => {
    // The reload after the POST is the call that brings the new USD row.
    const dependencies = fakeDependencies({
      getSubaccounts: vi.fn(() => Promise.resolve(ownedEurAndUsd)),
    })
    const viewModel = useAddCurrencyViewModel(dependencies)

    const created = await viewModel.add('USD')

    expect(created).toBe(true)
    expect(dependencies.addSubaccount).toHaveBeenCalledWith('USD')
    expect(viewModel.confirmation.value).toBe('Subcompte en USD creat')
    expect(dependencies.pause).toHaveBeenCalledWith(1500)
    expect(dependencies.goHome).toHaveBeenCalledTimes(1)
    // The list was reloaded, so USD now reads as owned and disabled.
    expect(dependencies.getSubaccounts).toHaveBeenCalledTimes(1)
    expect(viewModel.rows.value.find((row) => row.code === 'USD')).toMatchObject({
      owned: true,
      disabled: true,
    })
  })

  it('shows the fixed message of an existing currency and stays on the screen', async () => {
    const failure = { code: 'CURRENCY_EXISTS', message: 'x' }
    const dependencies = fakeDependencies({ addSubaccount: vi.fn(() => Promise.reject(failure)) })
    const viewModel = useAddCurrencyViewModel(dependencies)

    const created = await viewModel.add('USD')

    expect(created).toBe(false)
    expect(viewModel.error.value).toBe('Ja tens un subcompte en aquesta divisa.')
    expect(viewModel.error.value).toBe(messageForCode('CURRENCY_EXISTS'))
    expect(dependencies.pause).not.toHaveBeenCalled()
    expect(dependencies.goHome).not.toHaveBeenCalled()
    expect(viewModel.isSubmitting.value).toBe(false)
    expect(viewModel.confirmation.value).toBeNull()
  })

  it('keeps the confirmation when the reload after the POST fails (the sub-account exists)', async () => {
    // The POST worked; only the follow-up GET broke, so the add must not read as a failure.
    const dependencies = fakeDependencies({
      getSubaccounts: vi.fn(() => Promise.reject({ code: 'NETWORK_ERROR', message: 'x' })),
    })
    const viewModel = useAddCurrencyViewModel(dependencies)

    const created = await viewModel.add('USD')

    expect(created).toBe(true)
    expect(viewModel.confirmation.value).toBe('Subcompte en USD creat')
    expect(viewModel.error.value).toBeNull()
    expect(dependencies.pause).toHaveBeenCalledWith(1500)
    expect(dependencies.goHome).toHaveBeenCalledTimes(1)
  })

  it('sends once while the first request is in flight', async () => {
    let finish!: (subaccount: Subaccount) => void
    const dependencies = fakeDependencies({
      addSubaccount: vi.fn(() => new Promise<Subaccount>((resolve) => (finish = resolve))),
    })
    const viewModel = useAddCurrencyViewModel(dependencies)

    const first = viewModel.add('USD')
    expect(viewModel.isSubmitting.value).toBe(true)
    const second = await viewModel.add('GBP')

    expect(second).toBe(false)
    expect(dependencies.addSubaccount).toHaveBeenCalledTimes(1)

    finish(row('USD', 0, false))
    await first
  })

  it('does not send a currency that is already owned', async () => {
    const dependencies = fakeDependencies()
    const viewModel = useAddCurrencyViewModel(dependencies)
    await viewModel.load()

    const created = await viewModel.add('EUR')

    expect(created).toBe(false)
    expect(dependencies.addSubaccount).not.toHaveBeenCalled()
    expect(viewModel.confirmation.value).toBeNull()
  })
})
