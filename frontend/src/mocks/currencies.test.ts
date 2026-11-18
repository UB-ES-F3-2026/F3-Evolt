import { describe, expect, it } from 'vitest'
import { mockBalance, mockTopup } from './index'
import { mockAddSubaccount, createCurrenciesState, mockGetSubaccounts, mockSubaccounts } from './currencies'

// The mock keeps its state for the whole file, like `npm run dev` keeps it until a reload.
// The tests that add sub-accounts are therefore written in order.

describe('currencies mock', () => {
  it('starts with only the EUR sub-account, with the live balance of the mocks', () => {
    expect(mockSubaccounts().items).toEqual([{ id: 'sub-01', currency: 'EUR', balance: mockBalance() }])
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

    // The errors above created nothing and used no id, so this is still the second one.
    expect(usd).toEqual({ id: 'sub-02', currency: 'USD', balance: 0 })
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
    expect(items[0]).toEqual({ id: 'sub-01', currency: 'EUR', balance: balanceBefore + 5000 })
    expect(items.filter((subaccount) => subaccount.currency !== 'EUR')).toEqual(foreignBefore)
  })
})

describe('createCurrenciesState (US-27 seed)', () => {
  it('seeds EUR + USD with the given balances, and returns to the EUR-only default', () => {
    createCurrenciesState(['EUR', 'USD'], { USD: 31755 })
    expect(mockSubaccounts().items).toEqual([
      { id: 'sub-01', currency: 'EUR', balance: mockBalance() },
      { id: 'sub-02', currency: 'USD', balance: 31755 },
    ])
    expect(mockGetSubaccounts()).toEqual([
      { code: 'EUR', balanceMinor: mockBalance(), isMain: true },
      { code: 'USD', balanceMinor: 31755, isMain: false },
    ])
    createCurrenciesState()
    expect(mockSubaccounts().items).toEqual([{ id: 'sub-01', currency: 'EUR', balance: mockBalance() }])
  })
})
