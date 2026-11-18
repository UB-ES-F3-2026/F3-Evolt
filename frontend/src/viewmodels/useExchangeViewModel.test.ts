import { nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'
import { messageForCode } from '@/models/errorMessages'
import type { CurrencyCode } from '@/models/exchange'
import type { Subaccount } from '@/models/currency'
import { useExchangeViewModel, type ExchangeDependencies } from './useExchangeViewModel'

const EUR_MAIN: Subaccount = { id: 'sub-01', code: 'EUR', balance: 125050 }
const USD: Subaccount = { id: 'sub-02', code: 'USD', balance: 31755 }
const GBP: Subaccount = { id: 'sub-03', code: 'GBP', balance: 48000 }

// Screen copy of the keypad: the shared message says «en euros», wrong outside EUR.
const FORMAT_MESSAGE_CASES: [CurrencyCode, string][] = [
  ['USD', 'Escriu un import vàlid, amb 2 decimals com a màxim.'],
  ['JPY', 'Escriu un import vàlid.'],
]

function fakeDependencies(overrides: Partial<ExchangeDependencies> = {}) {
  return {
    getSubaccounts: vi.fn(() => Promise.resolve([EUR_MAIN, USD])),
    goToSummary: vi.fn(() => Promise.resolve()),
    goToCurrencies: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
}

async function loadedViewModel(overrides: Partial<ExchangeDependencies> = {}) {
  const dependencies = fakeDependencies(overrides)
  const viewModel = useExchangeViewModel(dependencies)
  await viewModel.load()
  return { viewModel, dependencies }
}

describe('useExchangeViewModel', () => {
  it('loads the subaccounts and starts from the main one as origin (US-27)', async () => {
    const { viewModel } = await loadedViewModel()

    expect(viewModel.isLoading.value).toBe(false)
    expect(viewModel.loadError.value).toBeNull()
    expect(viewModel.srcCurrency.value).toBe('EUR')
    expect(viewModel.tgtCurrency.value).toBe('USD')
    expect(viewModel.needsTwoSubaccounts.value).toBe(false)
    expect(viewModel.options.value).toEqual([
      { code: 'EUR', name: 'Euro', balanceMinor: 125050, isMain: true },
      { code: 'USD', name: 'Dòlar nord-americà', balanceMinor: 31755, isMain: false },
    ])
  })

  it('shows the shared message for the error code and queries again on retry (US-27)', async () => {
    const dependencies = fakeDependencies({
      getSubaccounts: vi.fn(() => Promise.reject({ code: 'NETWORK_ERROR', message: 'x' })),
    })
    const viewModel = useExchangeViewModel(dependencies)

    await viewModel.load()

    expect(viewModel.loadError.value).toBe(messageForCode('NETWORK_ERROR'))
    expect(viewModel.isLoading.value).toBe(false)
    expect(viewModel.canContinue.value).toBe(false)

    await viewModel.retry()

    expect(dependencies.getSubaccounts).toHaveBeenCalledTimes(2)
  })

  it('does not complain about an empty amount, but cannot continue (US-27)', async () => {
    const { viewModel } = await loadedViewModel()

    expect(viewModel.amountError.value).toBeNull()
    expect(viewModel.estimateText.value).toBeNull()
    expect(viewModel.canContinue.value).toBe(false)
  })

  it.each(['0', '0,00'])('rejects the amount %j before continuing (US-27)', async (typed) => {
    const { viewModel, dependencies } = await loadedViewModel()

    viewModel.amount.value = typed
    await viewModel.proceed()

    expect(viewModel.amountError.value).toBe(messageForCode('INVALID_AMOUNT'))
    expect(viewModel.canContinue.value).toBe(false)
    expect(dependencies.goToSummary).not.toHaveBeenCalled()
  })

  it('rejects an amount that reaches less than one cent of the target (US-27)', async () => {
    const { viewModel, dependencies } = await loadedViewModel()
    viewModel.srcCurrency.value = 'USD'
    await nextTick()

    viewModel.amount.value = '0,01'
    await viewModel.proceed()

    expect(viewModel.amountError.value).toBe("L'import és massa petit per canviar.")
    expect(viewModel.canContinue.value).toBe(false)
    // The mockup keeps the approximation on screen next to the error.
    expect(viewModel.estimateText.value).toMatch(/^Rebràs aproximadament 0,01\s€$/)
    expect(dependencies.goToSummary).not.toHaveBeenCalled()
  })

  it('says there is not enough balance when the amount plus commission exceeds it (US-27)', async () => {
    const { viewModel, dependencies } = await loadedViewModel({
      getSubaccounts: vi.fn(() =>
        Promise.resolve([{ id: 'sub-01', code: 'EUR', balance: 10149 }, USD] as Subaccount[]),
      ),
    })

    viewModel.amount.value = '100,00'
    await viewModel.proceed()

    expect(viewModel.amountError.value).toBe('No tens prou saldo')
    expect(viewModel.canContinue.value).toBe(false)
    expect(dependencies.goToSummary).not.toHaveBeenCalled()
  })

  it('flags the shortfall so the view can place the message under the button (US-27)', async () => {
    const { viewModel } = await loadedViewModel({
      getSubaccounts: vi.fn(() =>
        Promise.resolve([{ id: 'sub-01', code: 'EUR', balance: 10149 }, USD] as Subaccount[]),
      ),
    })

    expect(viewModel.insufficient.value).toBe(false)

    viewModel.amount.value = '100,00'

    expect(viewModel.insufficient.value).toBe(true)
    expect(viewModel.amountError.value).toBe('No tens prou saldo')
  })

  it('approximates what the person receives and opens the summary with the draft (US-27)', async () => {
    const { viewModel, dependencies } = await loadedViewModel()

    viewModel.amount.value = '100,00'

    expect(viewModel.estimateText.value).toMatch(/^Rebràs aproximadament 110,00\s\$$/)
    expect(viewModel.amountError.value).toBeNull()
    expect(viewModel.canContinue.value).toBe(true)

    await viewModel.proceed()

    expect(dependencies.goToSummary).toHaveBeenCalledTimes(1)
    expect(dependencies.goToSummary).toHaveBeenCalledWith({
      srcCurrency: 'EUR',
      tgtCurrency: 'USD',
      amountMinor: 10000,
    })
  })

  it.each(FORMAT_MESSAGE_CASES)(
    'asks for a valid amount without mentioning euros when the origin is %s (US-27)',
    async (origin, expected) => {
      const { viewModel } = await loadedViewModel({
        getSubaccounts: vi.fn(() =>
          Promise.resolve([
            { id: 'sub-01', code: 'EUR', balance: 125050 },
            { id: 'sub-02', code: origin, balance: 31755 },
          ] as Subaccount[]),
        ),
      })

      viewModel.srcCurrency.value = origin
      await nextTick()
      viewModel.amount.value = 'abc'

      expect(viewModel.amountError.value).toBe(expected)
    },
  )

  it('never leaves origin and target on the same subaccount (US-27)', async () => {
    const { viewModel } = await loadedViewModel({
      getSubaccounts: vi.fn(() => Promise.resolve([EUR_MAIN, USD, GBP])),
    })

    viewModel.srcCurrency.value = 'USD'
    await nextTick()

    expect(viewModel.srcCurrency.value).toBe('USD')
    expect(viewModel.tgtCurrency.value).not.toBe('USD')
    expect(viewModel.tgtCurrency.value).toBe('EUR')
  })

  it('asks for a second subaccount when only one is loaded (US-27)', async () => {
    const { viewModel, dependencies } = await loadedViewModel({
      getSubaccounts: vi.fn(() => Promise.resolve([EUR_MAIN])),
    })

    expect(viewModel.needsTwoSubaccounts.value).toBe(true)
    expect(viewModel.canContinue.value).toBe(false)

    await viewModel.goToCurrencies()

    expect(dependencies.goToCurrencies).toHaveBeenCalledTimes(1)
  })
})
