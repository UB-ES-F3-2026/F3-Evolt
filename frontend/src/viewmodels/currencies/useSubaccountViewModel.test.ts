import { describe, expect, it, vi } from 'vitest'
import type { ApiError } from '@/models/apiError'
import type { Subaccount, SubaccountMovement } from '@/models/currency'
import type { MovementsPage } from '@/models/movement'
import { useSubaccountViewModel, type SubaccountDependencies } from './useSubaccountViewModel'

const EUR: Subaccount = { id: 'main', code: 'EUR', balance: 125050 }
const USD_EMPTY: Subaccount = { id: 'sub-01', code: 'USD', balance: 0 }
const USD_FULL: Subaccount = { id: 'sub-01', code: 'USD', balance: 31755 }
const USD_ONE_CENT: Subaccount = { id: 'sub-01', code: 'USD', balance: 1 }

const USD_HISTORY: SubaccountMovement[] = [
  { id: 'smov-02', amount: 31755, concept: 'Canvi USD → EUR', date: '2026-11-19T11:00:00+01:00', type: 'expense' },
  { id: 'smov-01', amount: 31755, concept: 'Canvi EUR → USD', date: '2026-11-19T10:00:00+01:00', type: 'income' },
]

const EURO_PAGE: MovementsPage = {
  items: [
    { id: 'mov-32', amount: 28542, concept: 'Canvi USD → EUR', date: '2026-11-19T11:00:00+01:00', type: 'income', icon: 'transfer' },
    { id: 'mov-31', amount: 29405, concept: 'Canvi EUR → USD', date: '2026-11-19T10:00:00+01:00', type: 'expense', icon: 'transfer' },
  ],
  nextOffset: null,
}

function apiError(code: ApiError['code']): ApiError {
  return { code, message: 'del servidor' }
}

function fakeDependencies(accounts: Subaccount[], overrides: Partial<SubaccountDependencies> = {}) {
  return {
    getSubaccounts: vi.fn(() => Promise.resolve(accounts)),
    getSubaccountMovements: vi.fn(() => Promise.resolve<SubaccountMovement[]>([])),
    getMovements: vi.fn(() => Promise.resolve(EURO_PAGE)),
    deleteSubaccount: vi.fn(() => Promise.resolve()),
    goHome: vi.fn(() => Promise.resolve()),
    goToCurrencies: vi.fn(() => Promise.resolve()),
    pause: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
}

// Normalizes the non-breaking spaces of Intl, so the expected texts are written plainly.
function plain(text: string): string {
  return text.replace(/[\u00a0\u202f]/g, ' ')
}

describe('useSubaccountViewModel: the detail (US-26)', () => {
  it('starts loading, so an empty account never flashes', () => {
    const viewModel = useSubaccountViewModel('sub-01', fakeDependencies([EUR, USD_EMPTY]))

    expect(viewModel.isLoading.value).toBe(true)
    expect(viewModel.subaccount.value).toBeNull()
    expect(viewModel.canDelete.value).toBe(false)
  })

  it('ELP-01: «USD · Dòlar nord-americà», its balance, its history and «Eliminar subcompte»', async () => {
    const dependencies = fakeDependencies([EUR, USD_FULL], {
      getSubaccountMovements: vi.fn(() => Promise.resolve(USD_HISTORY)),
    })
    const viewModel = useSubaccountViewModel('sub-01', dependencies)

    await viewModel.load()

    expect(viewModel.title.value).toBe('USD · Dòlar nord-americà')
    expect(plain(viewModel.balanceText.value)).toBe('317,55 $')
    expect(viewModel.canDelete.value).toBe(true)
    expect(dependencies.getSubaccountMovements).toHaveBeenCalledWith('sub-01')
    expect(dependencies.getMovements).not.toHaveBeenCalled()
    expect(viewModel.history.value.map((row) => [row.concept, plain(row.amountText), row.isIncome])).toEqual([
      ['Canvi USD → EUR', '−317,55 $', false],
      ['Canvi EUR → USD', '+317,55 $', true],
    ])
  })

  it('a new sub-account has no history (mockup: «Encara no tens moviments»)', async () => {
    const viewModel = useSubaccountViewModel('sub-01', fakeDependencies([EUR, USD_EMPTY]))

    await viewModel.load()

    expect(plain(viewModel.balanceText.value)).toBe('0,00 $')
    expect(viewModel.hasHistory.value).toBe(false)
  })

  it('ELP-02: the EUR detail has no delete button and reads GET /api/movements, not §12.6', async () => {
    const dependencies = fakeDependencies([EUR, USD_EMPTY])
    const viewModel = useSubaccountViewModel('main', dependencies)

    await viewModel.load()

    expect(viewModel.title.value).toBe('EUR · Euro')
    expect(plain(viewModel.balanceText.value)).toBe('1.250,50 €')
    expect(viewModel.canDelete.value).toBe(false)
    expect(dependencies.getSubaccountMovements).not.toHaveBeenCalled()
    expect(dependencies.getMovements).toHaveBeenCalledWith(0, 5)
    expect(viewModel.history.value.map((row) => plain(row.amountText))).toEqual(['+285,42 €', '−294,05 €'])

    viewModel.askToDelete()
    expect(viewModel.dialog.value).toBeNull()
  })

  it('JPY balances have no decimals', async () => {
    const viewModel = useSubaccountViewModel('sub-02', fakeDependencies([EUR, { id: 'sub-02', code: 'JPY', balance: 1234 }]))

    await viewModel.load()

    expect(plain(viewModel.balanceText.value)).toBe('1.234 ¥')
  })

  it('an unknown or deleted sub-account says «No s\'ha trobat el subcompte.»', async () => {
    const viewModel = useSubaccountViewModel('sub-99', fakeDependencies([EUR]))

    await viewModel.load()

    expect(viewModel.error.value).toBe("No s'ha trobat el subcompte.")
    expect(viewModel.subaccount.value).toBeNull()
  })

  it('a failed load shows the error and can be retried', async () => {
    const dependencies = fakeDependencies([EUR, USD_EMPTY], {
      getSubaccounts: vi
        .fn<() => Promise<Subaccount[]>>()
        .mockRejectedValueOnce(apiError('NETWORK_ERROR'))
        .mockResolvedValueOnce([EUR, USD_EMPTY]),
    })
    const viewModel = useSubaccountViewModel('sub-01', dependencies)

    await viewModel.load()
    expect(viewModel.error.value).toBe('No hi ha connexió amb el servidor. Torna-ho a provar.')

    await viewModel.load()
    expect(viewModel.error.value).toBeNull()
    expect(viewModel.subaccount.value).toEqual(USD_EMPTY)
  })
})

describe('useSubaccountViewModel: «Eliminar subcompte» (US-26)', () => {
  it('ELP-03: with 0,01 $ it opens window 1, and «D\'acord» closes it without deleting', async () => {
    const dependencies = fakeDependencies([EUR, USD_ONE_CENT])
    const viewModel = useSubaccountViewModel('sub-01', dependencies)
    await viewModel.load()

    viewModel.askToDelete()
    expect(viewModel.dialog.value).toBe('not-empty')

    viewModel.closeDialog()
    expect(viewModel.dialog.value).toBeNull()
    expect(dependencies.deleteSubaccount).not.toHaveBeenCalled()
  })

  it('ELP-04: at 0,00 $ it opens window 2, and «Cancel·lar» closes it without deleting', async () => {
    const dependencies = fakeDependencies([EUR, USD_EMPTY])
    const viewModel = useSubaccountViewModel('sub-01', dependencies)
    await viewModel.load()

    viewModel.askToDelete()
    expect(viewModel.dialog.value).toBe('confirm')

    viewModel.closeDialog()
    expect(viewModel.dialog.value).toBeNull()
    expect(dependencies.deleteSubaccount).not.toHaveBeenCalled()
  })

  it('ELP-05: «Eliminar» deletes it, shows «Subcompte eliminat» and goes home after 1,5 s', async () => {
    const dependencies = fakeDependencies([EUR, USD_EMPTY])
    const viewModel = useSubaccountViewModel('sub-01', dependencies)
    await viewModel.load()
    viewModel.askToDelete()

    const deleted = await viewModel.confirmDelete()

    expect(deleted).toBe(true)
    expect(dependencies.deleteSubaccount).toHaveBeenCalledWith('sub-01')
    expect(viewModel.dialog.value).toBeNull()
    expect(viewModel.confirmation.value).toBe('Subcompte eliminat')
    expect(dependencies.pause).toHaveBeenCalledWith(1500)
    expect(dependencies.goHome).toHaveBeenCalledTimes(1)
  })

  it('a second tap while deleting never sends twice', async () => {
    let finish: () => void = () => undefined
    const dependencies = fakeDependencies([EUR, USD_EMPTY], {
      deleteSubaccount: vi.fn(() => new Promise<void>((resolve) => (finish = resolve))),
    })
    const viewModel = useSubaccountViewModel('sub-01', dependencies)
    await viewModel.load()
    viewModel.askToDelete()

    const first = viewModel.confirmDelete()
    expect(viewModel.isDeleting.value).toBe(true)
    expect(await viewModel.confirmDelete()).toBe(false)
    // While it runs, the window does not close either.
    viewModel.closeDialog()
    expect(viewModel.dialog.value).toBe('confirm')
    finish()
    await first

    expect(dependencies.deleteSubaccount).toHaveBeenCalledTimes(1)
  })

  it('never deletes without window 2 open', async () => {
    const dependencies = fakeDependencies([EUR, USD_EMPTY])
    const viewModel = useSubaccountViewModel('sub-01', dependencies)
    await viewModel.load()

    expect(await viewModel.confirmDelete()).toBe(false)
    expect(dependencies.deleteSubaccount).not.toHaveBeenCalled()
  })

  it('SUBACCOUNT_NOT_EMPTY from the server (money arrived meanwhile) switches to window 1 and reloads', async () => {
    const dependencies = fakeDependencies([EUR, USD_EMPTY], {
      deleteSubaccount: vi.fn(() => Promise.reject(apiError('SUBACCOUNT_NOT_EMPTY'))),
    })
    const viewModel = useSubaccountViewModel('sub-01', dependencies)
    await viewModel.load()
    viewModel.askToDelete()

    expect(await viewModel.confirmDelete()).toBe(false)

    expect(viewModel.dialog.value).toBe('not-empty')
    expect(viewModel.confirmation.value).toBeNull()
    expect(dependencies.getSubaccounts).toHaveBeenCalledTimes(2)
    expect(dependencies.goHome).not.toHaveBeenCalled()
  })

  it('SUBACCOUNT_NOT_FOUND (deleted elsewhere) says so and goes back to /divises', async () => {
    const dependencies = fakeDependencies([EUR, USD_EMPTY], {
      deleteSubaccount: vi.fn(() => Promise.reject(apiError('SUBACCOUNT_NOT_FOUND'))),
    })
    const viewModel = useSubaccountViewModel('sub-01', dependencies)
    await viewModel.load()
    viewModel.askToDelete()

    expect(await viewModel.confirmDelete()).toBe(false)

    expect(viewModel.notFound.value).toBe("No s'ha trobat el subcompte.")
    expect(viewModel.dialog.value).toBeNull()
    expect(dependencies.pause).toHaveBeenCalledWith(1500)
    expect(dependencies.goToCurrencies).toHaveBeenCalledTimes(1)
    expect(dependencies.goHome).not.toHaveBeenCalled()
  })

  it('any other failure keeps window 2 open with the error, to try again', async () => {
    const dependencies = fakeDependencies([EUR, USD_EMPTY], {
      deleteSubaccount: vi
        .fn<() => Promise<void>>()
        .mockRejectedValueOnce(apiError('INTERNAL_ERROR'))
        .mockResolvedValueOnce(undefined),
    })
    const viewModel = useSubaccountViewModel('sub-01', dependencies)
    await viewModel.load()
    viewModel.askToDelete()

    expect(await viewModel.confirmDelete()).toBe(false)
    expect(viewModel.dialog.value).toBe('confirm')
    expect(viewModel.deleteError.value).toBe("S'ha produït un error inesperat. Torna-ho a provar més tard.")
    expect(viewModel.isDeleting.value).toBe(false)

    expect(await viewModel.confirmDelete()).toBe(true)
    expect(viewModel.deleteError.value).toBeNull()
  })
})
