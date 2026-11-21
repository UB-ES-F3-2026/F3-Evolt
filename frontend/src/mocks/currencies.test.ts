import { beforeEach, describe, expect, it } from 'vitest'
import { mockBalance, mockTopup } from './index'
import { createCurrenciesState, mockAddSubaccount, mockSubaccounts } from './currencies'
import { totalInEurosMinor } from '@/models/currency'

// The mock keeps its state for the whole file, like `npm run dev` keeps it until a reload.
// The tests that add sub-accounts are therefore written in order.

describe('currencies mock', () => {
  it('starts with only the EUR main account: id "main", isMain, rateBps and the live balance of the mocks', () => {
    expect(mockSubaccounts().items).toEqual([
      { id: 'main', code: 'EUR', balance: mockBalance(), isMain: true, rateBps: 10000 },
    ])
  })

  it('answers §12.3: totalInEuros present and equal to the server algorithm (§12.1)', () => {
    createCurrenciesState(['EUR', 'USD'], { USD: 31755 })

    const response = mockSubaccounts()
    // The EUR balance is the live main balance (the demo seed here); 317,55 $ at
    // 9123 bps round to 289,70 € (§12.1). The exact contract example (125050 + 31755
    // → 154020) is pinned in models/currency.test.ts.
    expect(response.totalInEuros).toBe(mockBalance() + 28970)
    expect(response.totalInEuros).toBe(totalInEurosMinor(response.items))
  })

  it('numbers the foreign rows sub-01, sub-02… in creation order; EUR never consumes a number', () => {
    createCurrenciesState(['EUR', 'USD', 'GBP'], { USD: 31755 })

    const items = mockSubaccounts().items
    expect(items.map((subaccount) => subaccount.id)).toEqual(['main', 'sub-01', 'sub-02'])
    // Every row carries the §12.2 derived fields, taken from the fixed CURRENCIES table.
    expect(items.map((subaccount) => subaccount.isMain)).toEqual([true, false, false])
    expect(items.map((subaccount) => subaccount.rateBps)).toEqual([10000, 9123, 11680])
  })

  it('returns copies, so a caller cannot change the stored sub-accounts', () => {
    createCurrenciesState()

    mockSubaccounts().items[0].balance = 0
    mockSubaccounts().items.push({ id: 'sub-99', code: 'GBP', balance: 100, isMain: false, rateBps: 11680 })

    expect(mockSubaccounts().items.map((subaccount) => subaccount.code)).toEqual(['EUR'])
    expect(mockSubaccounts().items[0].balance).toBe(mockBalance())
  })

  it('reads the EUR row with the live balance after a top-up, and keeps the foreign rows as they were', () => {
    createCurrenciesState(['EUR', 'USD'], { USD: 31755 })
    const balanceBefore = mockBalance()
    const foreignBefore = mockSubaccounts().items.filter((subaccount) => subaccount.code !== 'EUR')

    mockTopup(5000)

    const items = mockSubaccounts().items
    expect(items[0]).toEqual({ id: 'main', code: 'EUR', balance: balanceBefore + 5000, isMain: true, rateBps: 10000 })
    expect(items.filter((subaccount) => subaccount.code !== 'EUR')).toEqual(foreignBefore)
  })
})

describe('mockAddSubaccount (US-25)', () => {
  beforeEach(() => createCurrenciesState())

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

  it('returns the created subaccount in app shape: balance 0, isMain false, rateBps, next id', () => {
    const usd = mockAddSubaccount({ currency: 'USD' })

    // The errors above created nothing and used no id, so the first foreign row is sub-01.
    expect(usd).toEqual({ id: 'sub-01', code: 'USD', balance: 0, isMain: false, rateBps: 9123 })
    expect(mockSubaccounts().items.at(-1)).toEqual(usd)

    // The answer is a copy: changing it does not change the stored row.
    usd.balance = 999
    expect(mockSubaccounts().items.at(-1)?.balance).toBe(0)
  })

  it('keeps numbering the foreign rows across creations: sub-01, sub-02, sub-03', () => {
    mockAddSubaccount({ currency: 'USD' })
    mockAddSubaccount({ currency: 'GBP' })
    mockAddSubaccount({ currency: 'CHF' })

    expect(mockSubaccounts().items.map((subaccount) => subaccount.id)).toEqual(['main', 'sub-01', 'sub-02', 'sub-03'])
  })

  it('does not add the same currency twice', () => {
    mockAddSubaccount({ currency: 'USD' })
    expect(() => mockAddSubaccount({ currency: 'USD' })).toThrow(
      expect.objectContaining({ code: 'CURRENCY_EXISTS' }) as Error,
    )
    expect(mockSubaccounts().items).toHaveLength(2)
  })

  it('a new 0-balance sub-account does not move the total (§12.3)', () => {
    createCurrenciesState(['EUR', 'USD'], { USD: 31755 })
    const totalBefore = mockSubaccounts().totalInEuros

    mockAddSubaccount({ currency: 'GBP' })

    expect(mockSubaccounts().totalInEuros).toBe(totalBefore)
  })
})

describe('createCurrenciesState (US-27 seed)', () => {
  it('seeds EUR + USD with the given balances, and returns to the EUR-only default', () => {
    createCurrenciesState(['EUR', 'USD'], { USD: 31755 })
    expect(mockSubaccounts().items).toEqual([
      { id: 'main', code: 'EUR', balance: mockBalance(), isMain: true, rateBps: 10000 },
      { id: 'sub-01', code: 'USD', balance: 31755, isMain: false, rateBps: 9123 },
    ])
    createCurrenciesState()
    expect(mockSubaccounts().items).toEqual([
      { id: 'main', code: 'EUR', balance: mockBalance(), isMain: true, rateBps: 10000 },
    ])
  })
})
