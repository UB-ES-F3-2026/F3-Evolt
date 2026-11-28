import { describe, expect, it } from 'vitest'
import { mockBalance, mockTopup } from './index'
import {
  mockAddSubaccount,
  mockDeleteSubaccount,
  mockRecordSubaccountMovement,
  mockSetSubaccountBalance,
  mockSubaccountMovements,
  mockSubaccounts,
} from './currencies'

// The mock keeps its state for the whole file, like `npm run dev` keeps it until a reload.
// The tests that add sub-accounts are therefore written in order.

describe('currencies mock', () => {
  it('starts with only the EUR sub-account, with the live balance of the mocks', () => {
    expect(mockSubaccounts().items).toEqual([{ id: 'main', currency: 'EUR', balance: mockBalance() }])
  })

  it('returns copies, so a caller cannot change the stored sub-accounts', () => {
    mockSubaccounts().items[0].balance = 0
    mockSubaccounts().items.push({ id: 'sub-99', currency: 'GBP', balance: 100 })

    expect(mockSubaccounts().items.map((subaccount) => subaccount.currency)).toEqual(['EUR'])
    expect(mockSubaccounts().items[0].balance).toBe(mockBalance())
  })
})

describe('mockAddSubaccount (US-25)', () => {
  it.each([
    [{}, 'VALIDATION_ERROR'],
    [{ currency: 42 }, 'VALIDATION_ERROR'],
    [{ currency: null }, 'VALIDATION_ERROR'],
    [{ currency: 'AUD' }, 'CURRENCY_NOT_SUPPORTED'],
    [{ currency: 'usd' }, 'CURRENCY_NOT_SUPPORTED'],
    // Every account already owns EUR, so it is checked before anything is created.
    [{ currency: 'EUR' }, 'CURRENCY_EXISTS'],
  ])('rejects %j with %s and creates nothing', (body, code) => {
    expect(() => mockAddSubaccount(body)).toThrow(expect.objectContaining({ code }) as Error)
    expect(mockSubaccounts().items).toHaveLength(1)
  })

  it('creates the sub-account with balance 0 and the next id, and returns a copy', () => {
    const usd = mockAddSubaccount({ currency: 'USD' })

    // The errors above created nothing and used no id, so this is still the first one (§12.2).
    expect(usd).toEqual({ id: 'sub-01', currency: 'USD', balance: 0 })
    expect(mockSubaccounts().items.at(-1)).toEqual(usd)

    // The answer is a copy: changing it does not change the stored row.
    usd.balance = 999
    expect(mockSubaccounts().items.at(-1)?.balance).toBe(0)
  })

  it('does not add the same currency twice', () => {
    expect(() => mockAddSubaccount({ currency: 'USD' })).toThrow(
      expect.objectContaining({ code: 'CURRENCY_EXISTS' }) as Error,
    )
    expect(mockSubaccounts().items).toHaveLength(2)
  })

  it('reads the EUR row with the live balance after a top-up, and keeps the foreign rows as they were', () => {
    const balanceBefore = mockBalance()
    const foreignBefore = mockSubaccounts().items.filter((subaccount) => subaccount.currency !== 'EUR')

    mockTopup(5000)

    const items = mockSubaccounts().items
    expect(items[0]).toEqual({ id: 'main', currency: 'EUR', balance: balanceBefore + 5000 })
    expect(items.filter((subaccount) => subaccount.currency !== 'EUR')).toEqual(foreignBefore)
  })
})

describe('mockDeleteSubaccount (US-26, docs/api.md §12.5)', () => {
  // Continues the state above: EUR (`main`) and USD (`sub-01`) at 0,00 $.

  it('never deletes the main account, whatever its balance (EL-03)', () => {
    expect(() => mockDeleteSubaccount('main')).toThrow(
      expect.objectContaining({ code: 'MAIN_ACCOUNT_NOT_DELETABLE', message: 'El compte en euros no es pot eliminar.' }) as Error,
    )
  })

  it('answers not found for an unknown id (EL-05)', () => {
    expect(() => mockDeleteSubaccount('sub-99')).toThrow(
      expect.objectContaining({ code: 'SUBACCOUNT_NOT_FOUND', message: "No s'ha trobat el subcompte." }) as Error,
    )
  })

  it('refuses a sub-account with only 0,01 $ (EL-04)', () => {
    mockRecordSubaccountMovement('sub-01', {
      amount: 1,
      concept: 'Canvi EUR → USD',
      date: '2026-11-19T10:00:00+01:00',
      type: 'income',
    })

    expect(() => mockDeleteSubaccount('sub-01')).toThrow(
      expect.objectContaining({
        code: 'SUBACCOUNT_NOT_EMPTY',
        message: 'Només pots eliminar un subcompte amb saldo 0.',
      }) as Error,
    )
    expect(mockSubaccounts().items.at(-1)).toEqual({ id: 'sub-01', currency: 'USD', balance: 1 })
  })

  it('lists the history newest first, the later one first on a tie (§12.6, P4)', () => {
    mockRecordSubaccountMovement('sub-01', {
      amount: 1,
      concept: 'Canvi USD → EUR',
      date: '2026-11-19T10:00:00+01:00',
      type: 'expense',
    })

    expect(mockSubaccountMovements('sub-01').items).toEqual([
      { id: 'smov-02', amount: 1, concept: 'Canvi USD → EUR', date: '2026-11-19T10:00:00+01:00', type: 'expense' },
      { id: 'smov-01', amount: 1, concept: 'Canvi EUR → USD', date: '2026-11-19T10:00:00+01:00', type: 'income' },
    ])
  })

  it('has no subaccount history for the main account (EL-10)', () => {
    expect(() => mockSubaccountMovements('main')).toThrow(
      expect.objectContaining({ code: 'SUBACCOUNT_NOT_FOUND' }) as Error,
    )
  })

  it('deletes it at 0, frees the currency and hides its history (EL-01, EL-02, EL-07, EL-08)', () => {
    expect(mockDeleteSubaccount('sub-01')).toEqual({ status: 'ok' })

    expect(mockSubaccounts().items.map((subaccount) => subaccount.id)).toEqual(['main'])
    expect(() => mockSubaccountMovements('sub-01')).toThrow(
      expect.objectContaining({ code: 'SUBACCOUNT_NOT_FOUND' }) as Error,
    )
    expect(() => mockDeleteSubaccount('sub-01')).toThrow(
      expect.objectContaining({ code: 'SUBACCOUNT_NOT_FOUND' }) as Error,
    )
    // The currency is free again, with a new id and an empty history.
    expect(mockAddSubaccount({ currency: 'USD' })).toEqual({ id: 'sub-02', currency: 'USD', balance: 0 })
    expect(mockSubaccountMovements('sub-02').items).toEqual([])
  })

  it('only records movements on foreign sub-accounts, and never below 0', () => {
    const entry = { amount: 5, concept: 'x', date: '2026-11-19T10:00:00+01:00', type: 'expense' as const }

    expect(() => mockRecordSubaccountMovement('main', entry)).toThrow()
    expect(() => mockRecordSubaccountMovement('sub-02', entry)).toThrow()
    expect(mockSubaccounts().items.at(-1)?.balance).toBe(0)
  })
})

describe('mockSubaccounts total (§12.3)', () => {
  // Continues the state above: EUR (`main`) at the live balance, and USD (`sub-02`) at 0.

  it('answers §12.3: totalInEuros computed with the server algorithm (§12.1)', () => {
    // 31755 USD at 9123 bps → 28970 euro cents, rounded on its own (§12.1).
    mockSetSubaccountBalance('USD', 31755)

    expect(mockSubaccounts().totalInEuros).toBe(mockBalance() + 28970)
  })

  it('a new sub-account at 0 does not move the total (§12.3)', () => {
    const totalBefore = mockSubaccounts().totalInEuros

    expect(mockAddSubaccount({ currency: 'GBP' }).balance).toBe(0)

    expect(mockSubaccounts().totalInEuros).toBe(totalBefore)
  })
})
