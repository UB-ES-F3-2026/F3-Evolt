import { describe, expect, it, vi } from 'vitest'
import { messageForCode } from '@/models/errorMessages'
import type { ExchangeDraft } from '@/models/exchange'
import type { ExchangeResultJson, SubaccountJson } from '@/services/exchangeService'
import {
  CONFIRMATION_MS,
  useExchangeSummaryViewModel,
  type ExchangeSummaryDependencies,
} from './useExchangeSummaryViewModel'

const eurToUsd: ExchangeDraft = { srcCurrency: 'EUR', tgtCurrency: 'USD', amountMinor: 10000 }

// What the backend answers to 100,00 € to USD (US-27, criterion 9).
const exchanged: ExchangeResultJson = { srcBalanceMinor: 114900, tgtBalanceMinor: 42716 }

function subaccounts(eurBalanceMinor: number): SubaccountJson[] {
  return [
    { code: 'EUR', balanceMinor: eurBalanceMinor, isMain: true },
    { code: 'USD', balanceMinor: 31755, isMain: false },
  ]
}

function fakeDependencies(overrides: Partial<ExchangeSummaryDependencies> = {}) {
  return {
    draft: eurToUsd,
    getSubaccounts: vi.fn(() => Promise.resolve(subaccounts(125050))),
    confirmExchange: vi.fn(() => Promise.resolve(exchanged)),
    goHome: vi.fn(() => Promise.resolve()),
    goToExchange: vi.fn(() => Promise.resolve()),
    pause: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
}

describe('useExchangeSummaryViewModel', () => {
  it('shows the rate, the commission, the charge and the exact amount (US-27, special cases)', async () => {
    const viewModel = useExchangeSummaryViewModel(fakeDependencies())

    await viewModel.start()

    expect(viewModel.isLoading.value).toBe(false)
    expect(viewModel.loadError.value).toBeNull()
    expect(viewModel.originLine.value).toMatch(/^100,00\s€ → USD$/)
    expect(viewModel.rateLabel.value).toBe('1 € =')
    expect(viewModel.rateValue.value).toMatch(/^1,10\s\$$/)
    expect(viewModel.commissionText.value).toMatch(/^Comissió: 1,50\s€$/)
    expect(viewModel.chargeNote.value).toMatch(
      /^Se't descomptaran 101,50\s€ del subcompte d'origen$/,
    )
    expect(viewModel.exactLine.value).toMatch(/^Rebràs exactament 109,61\s\$$/)
    expect(viewModel.insufficient.value).toBe(false)
    expect(viewModel.balanceNotLoaded.value).toBe(false)
  })

  it('quotes the rate per 100 ¥ when the origin is JPY and keeps whole yen', async () => {
    const viewModel = useExchangeSummaryViewModel(
      fakeDependencies({
        draft: { srcCurrency: 'JPY', tgtCurrency: 'EUR', amountMinor: 10000 },
        getSubaccounts: vi.fn(() =>
          Promise.resolve<SubaccountJson[]>([{ code: 'JPY', balanceMinor: 20000, isMain: true }]),
        ),
      }),
    )

    await viewModel.start()

    expect(viewModel.rateLabel.value).toBe('100 ¥ =')
    expect(viewModel.rateValue.value).toMatch(/^0,57\s€$/)
  })

  it('says "No tens prou saldo" and sends nothing when amount + commission does not fit (US-27)', async () => {
    // 101,49 € cannot pay a 101,50 € charge.
    const dependencies = fakeDependencies({
      getSubaccounts: vi.fn(() => Promise.resolve(subaccounts(10149))),
    })
    const viewModel = useExchangeSummaryViewModel(dependencies)

    await viewModel.start()

    expect(viewModel.insufficient.value).toBe(true)

    await viewModel.confirm()

    expect(dependencies.confirmExchange).not.toHaveBeenCalled()
    expect(dependencies.pause).not.toHaveBeenCalled()
    expect(dependencies.goHome).not.toHaveBeenCalled()
  })

  it('keeps the button disabled while the origin balance is not loaded', async () => {
    const dependencies = fakeDependencies({
      getSubaccounts: vi.fn(() => Promise.reject({ code: 'NETWORK_ERROR', message: 'x' })),
    })
    const viewModel = useExchangeSummaryViewModel(dependencies)

    await viewModel.start()

    expect(viewModel.loadError.value).toBe(messageForCode('NETWORK_ERROR'))
    expect(viewModel.balanceNotLoaded.value).toBe(true)

    await viewModel.confirm()

    expect(dependencies.confirmExchange).not.toHaveBeenCalled()
  })

  it('exchanges once, shows the tick and only then goes back to Home (US-27, criterion 9)', async () => {
    // Recorded by hand: the tick has to stay on screen before the ViewModel navigates.
    const order: string[] = []
    const dependencies = fakeDependencies({
      pause: vi.fn(() => {
        order.push('pause')
        return Promise.resolve()
      }),
      goHome: vi.fn(() => {
        order.push('goHome')
        return Promise.resolve()
      }),
    })
    const viewModel = useExchangeSummaryViewModel(dependencies)
    await viewModel.start()

    await viewModel.confirm()

    expect(dependencies.confirmExchange).toHaveBeenCalledOnce()
    expect(dependencies.confirmExchange).toHaveBeenCalledWith({
      srcCurrency: 'EUR',
      tgtCurrency: 'USD',
      amountMinor: 10000,
    })
    expect(viewModel.confirmed.value).toBe(true)
    expect(viewModel.newBalances.value).toEqual(exchanged)
    expect(viewModel.newBalanceRows.value.map((row) => row.label)).toEqual([
      'EUR · Euro',
      'USD · Dòlar nord-americà',
    ])
    expect(viewModel.newBalanceRows.value[0]?.value).toMatch(/^1\.149,00\s€$/)
    expect(viewModel.newBalanceRows.value[1]?.value).toMatch(/^427,16\s\$$/)
    expect(dependencies.pause).toHaveBeenCalledWith(CONFIRMATION_MS)
    expect(order).toEqual(['pause', 'goHome'])
    expect(dependencies.goHome).toHaveBeenCalledOnce()
    expect(dependencies.goToExchange).not.toHaveBeenCalled()
  })

  it('keeps the summary and shows the reason when the server rejects the exchange', async () => {
    const dependencies = fakeDependencies({
      confirmExchange: vi.fn(() =>
        Promise.reject({ code: 'INSUFFICIENT_BALANCE', message: 'x' }),
      ),
    })
    const viewModel = useExchangeSummaryViewModel(dependencies)
    await viewModel.start()

    await viewModel.confirm()

    // The shared text speaks of a pot contribution: the summary says it without the pot copy.
    expect(viewModel.submitError.value).toBe('No tens prou saldo')
    expect(viewModel.confirmed.value).toBe(false)
    expect(viewModel.newBalances.value).toBeNull()
    expect(viewModel.isConfirming.value).toBe(false)
    expect(dependencies.goHome).not.toHaveBeenCalled()
  })

  it('sends one request when the button is clicked twice', async () => {
    const dependencies = fakeDependencies()
    const viewModel = useExchangeSummaryViewModel(dependencies)
    await viewModel.start()

    const first = viewModel.confirm()
    const second = viewModel.confirm()
    await Promise.all([first, second])

    expect(dependencies.confirmExchange).toHaveBeenCalledOnce()
  })

  it('goes back to «Canviar» when the draft is missing, and cannot confirm', async () => {
    const dependencies = fakeDependencies({ draft: null })
    const viewModel = useExchangeSummaryViewModel(dependencies)

    await viewModel.start()

    expect(dependencies.goToExchange).toHaveBeenCalledOnce()
    expect(dependencies.getSubaccounts).not.toHaveBeenCalled()

    await viewModel.confirm()

    expect(dependencies.confirmExchange).not.toHaveBeenCalled()
  })

  it('treats a draft with the same origin and target as missing (SAME_CURRENCY)', async () => {
    const dependencies = fakeDependencies({
      draft: { srcCurrency: 'EUR', tgtCurrency: 'EUR', amountMinor: 10000 },
    })
    const viewModel = useExchangeSummaryViewModel(dependencies)

    expect(viewModel.draft).toBeNull()

    await viewModel.start()

    expect(dependencies.goToExchange).toHaveBeenCalledOnce()
    expect(dependencies.getSubaccounts).not.toHaveBeenCalled()
    // Never two success rows for the same subaccount.
    expect(viewModel.newBalanceRows.value).toEqual([])

    await viewModel.confirm()

    expect(dependencies.confirmExchange).not.toHaveBeenCalled()
  })
})
