// @vitest-environment jsdom
import { describe, expect, it } from 'vitest'
import type { ApiErrorCode } from '@/models/apiError'
import { formatCents, formatSignedCents } from '@/models/money'
import { mockBalance, mockHome } from './index'
import { mockPostExchange } from './exchange'
import { createCurrenciesState, mockSubaccounts } from './currencies'
import { setMockCurrentUser } from './mockUser'

// The mock keeps its state for the whole file, like `npm run dev` keeps it until a reload.
// The tests that exchange money are therefore written in order.

/** The untrusted body the mock receives, exactly as the service forwards it (§12.7). */
type ExchangeBody = Parameters<typeof mockPostExchange>[0]

createCurrenciesState(['EUR', 'USD'], { USD: 31755 })

/**
 * Runs a rejected exchange and asserts the two invariants of «tot o res»: the error
 * code, and that neither the main account nor any sub-account moved.
 */
function expectRejected(body: ExchangeBody, code: ApiErrorCode): void {
  const before = { home: mockHome(), subaccounts: mockSubaccounts().items }

  expect(() => mockPostExchange(body)).toThrow(expect.objectContaining({ code }) as Error)

  expect(mockHome()).toEqual(before.home)
  expect(mockSubaccounts().items).toEqual(before.subaccounts)
}

describe('the seeded sub-accounts (US-27)', () => {
  it('starts with the EUR main account and 317,55 $ for the demo user', () => {
    expect(mockSubaccounts().items).toEqual([
      {
        id: 'main',
        code: 'EUR',
        balance: 379521,
        isMain: true,
        rateBps: 10000,
      },
      {
        id: 'sub-01',
        code: 'USD',
        balance: 31755,
        isMain: false,
        rateBps: 9123,
      },
    ])
  })

  it('reads the EUR balance from the main account, never from its own state', () => {
    expect(mockSubaccounts().items[0].balance).toBe(mockBalance())
  })
})

describe('mockPostExchange validations (§12.7 order, US-27)', () => {
  // Each case pins one step of the order and its code; the steps stop at the first error.
  it.each<{ case: string; body: ExchangeBody; code: ApiErrorCode }>([
    // 1. Body format (CV-17): a missing field, a currency that is not a string, and an
    //    amount that is not a strict JSON integer.
    {
      case: 'a body without amount (CV-17)',
      body: { fromCurrency: 'EUR', toCurrency: 'USD' },
      code: 'VALIDATION_ERROR',
    },
    {
      case: 'an amount sent as a string (CV-17)',
      body: { fromCurrency: 'EUR', toCurrency: 'USD', amount: '1000' },
      code: 'VALIDATION_ERROR',
    },
    {
      case: 'a non-integer amount (CV-17)',
      body: { fromCurrency: 'EUR', toCurrency: 'USD', amount: 10.5 },
      code: 'VALIDATION_ERROR',
    },
    {
      case: 'a currency sent as a number (CV-17)',
      body: { fromCurrency: 978, toCurrency: 'USD', amount: 1000 },
      code: 'VALIDATION_ERROR',
    },
    // 2. The pair goes before the amount: CV-18 sends EUR → EUR with 0.
    {
      case: 'the same currency with amount 0 (CV-18)',
      body: { fromCurrency: 'EUR', toCurrency: 'EUR', amount: 0 },
      code: 'SAME_CURRENCY',
    },
    // 3. A currency with no sub-account of this user, known code or not (CV-08).
    {
      case: 'a currency with no sub-account (CV-08)',
      body: { fromCurrency: 'EUR', toCurrency: 'GBP', amount: 1000 },
      code: 'SUBACCOUNT_NOT_FOUND',
    },
    {
      case: 'the code "BTC", outside the catalogue (CV-08)',
      body: { fromCurrency: 'EUR', toCurrency: 'BTC', amount: 1000 },
      code: 'SUBACCOUNT_NOT_FOUND',
    },
    // 3 before 4: an unowned pair with amount 0 reads SUBACCOUNT_NOT_FOUND, not INVALID_AMOUNT.
    {
      case: 'an unowned pair with amount 0 (CV-08 · CV-09)',
      body: { fromCurrency: 'GBP', toCurrency: 'USD', amount: 0 },
      code: 'SUBACCOUNT_NOT_FOUND',
    },
    // 4. Zero or negative on an owned pair (CV-09).
    {
      case: 'amount 0 (CV-09)',
      body: { fromCurrency: 'EUR', toCurrency: 'USD', amount: 0 },
      code: 'INVALID_AMOUNT',
    },
    {
      case: 'a negative amount (CV-09)',
      body: { fromCurrency: 'EUR', toCurrency: 'USD', amount: -100 },
      code: 'INVALID_AMOUNT',
    },
    // 5 and 6, on an owned pair with a positive amount (CV-10, CV-12).
    {
      case: '0,01 $ to euros (CV-10)',
      body: { fromCurrency: 'USD', toCurrency: 'EUR', amount: 1 },
      code: 'AMOUNT_TOO_SMALL',
    },
    {
      case: 'the whole balance, without room for the commission (CV-12)',
      body: { fromCurrency: 'EUR', toCurrency: 'USD', amount: 379521 },
      code: 'INSUFFICIENT_BALANCE',
    },
  ])('rejects $case with $code and changes nothing (US-27)', ({ body, code }) => {
    expectRejected(body, code)
  })
})

describe('mockPostExchange (§12.7 response, US-27)', () => {
  it('changes 100,00 € into 109,61 $, charging the 1,50 € commission to the main account', () => {
    const result = mockPostExchange({
      fromCurrency: 'EUR',
      toCurrency: 'USD',
      amount: 10000,
    })

    // CV-01: both accounts with their new balance, plus the figures already applied.
    // The main account pays amount + commission (10150), not the raw amount.
    expect(result).toEqual({
      from: {
        id: 'main',
        code: 'EUR',
        balance: 369371,
        isMain: true,
        rateBps: 10000,
      },
      to: {
        id: 'sub-01',
        code: 'USD',
        balance: 42716,
        isMain: false,
        rateBps: 9123,
      },
      amount: 10000,
      commission: 150,
      received: 10961,
    })
    // The next read of the list reports the same two balances.
    expect(mockSubaccounts().items).toEqual([result.from, result.to])
  })

  it('shows «Canvi a Dòlar nord-americà» first in home and in the list, as an expense', () => {
    const movement = mockHome().lastMovements[0]

    expect(movement.concept).toBe('Canvi a Dòlar nord-americà')
    expect(movement.type).toBe('expense')
    // The total charge (amount + commission), shown with a minus sign in the row.
    expect(movement.amount).toBe(10150)
    expect(formatSignedCents(movement.amount, 'negative')).toBe(`−${formatCents(10150)}`)
  })

  it('rejects an exchange just over the balance, leaving both balances unchanged', () => {
    // 369000 + 5535 of commission = 374535, which is 5164 minor units (51,64 €) over
    // the 369371 left after the exchange above.
    expectRejected({ fromCurrency: 'EUR', toCurrency: 'USD', amount: 369000 }, 'INSUFFICIENT_BALANCE')
  })

  it('changes 100,00 $ back into euros: the sub-account pays and the main account receives', () => {
    const result = mockPostExchange({
      fromCurrency: 'USD',
      toCurrency: 'EUR',
      amount: 10000,
    })

    // 10000 $ + 150 of commission (1,50 $) leaves 32566 $; 9123 minor units arrive in EUR.
    expect(result).toEqual({
      from: {
        id: 'sub-01',
        code: 'USD',
        balance: 32566,
        isMain: false,
        rateBps: 9123,
      },
      to: {
        id: 'main',
        code: 'EUR',
        balance: 378494,
        isMain: true,
        rateBps: 10000,
      },
      amount: 10000,
      commission: 150,
      received: 9123,
    })
    expect(mockHome().lastMovements[0]).toMatchObject({
      concept: 'Canvi de Dòlar nord-americà',
      type: 'income',
      amount: 9123,
    })
  })

  it('charges the 0,50 € minimum on a small amount (CV-05)', () => {
    // 1,5 % of 10,00 € would be 0,15 €, so the floor applies: 50 minor units.
    const result = mockPostExchange({
      fromCurrency: 'EUR',
      toCurrency: 'USD',
      amount: 1000,
    })

    expect(result.commission).toBe(50)
    expect(result.received).toBe(1096)
    expect(result.from.balance).toBe(377444)
    expect(result.to.balance).toBe(33662)
  })
})

describe('each account sees its own sub-accounts (US-27)', () => {
  it('an account without data has only the EUR sub-account, and the demo seed comes back on a user change', () => {
    setMockCurrentUser('buit@evolt.test')

    // Single sub-account: the «Canviar» screen has nothing to exchange with.
    expect(mockSubaccounts().items).toEqual([
      { id: 'main', code: 'EUR', balance: 0, isMain: true, rateBps: 10000 },
    ])

    setMockCurrentUser(null)

    // The demo reset yields the EUR-only default seed (US-25); re-seed US-27's demo state
    // so the post-conditions of this file stay stable.
    expect(mockSubaccounts().items).toEqual([
      {
        id: 'main',
        code: 'EUR',
        balance: 379521,
        isMain: true,
        rateBps: 10000,
      },
    ])
    createCurrenciesState(['EUR', 'USD'], { USD: 31755 })
  })
})

describe('the commission is charged in the source currency (§12.7)', () => {
  it('charges 1,5 % of 10.000 ¥ → 150 ¥, above the 88 ¥ minimum', () => {
    createCurrenciesState(['EUR', 'USD', 'JPY'], { USD: 31755, JPY: 100000 })

    const result = mockPostExchange({
      fromCurrency: 'JPY',
      toCurrency: 'EUR',
      amount: 10000,
    })

    // max(arrodonir(10000 × 150 / 10000), mínim[JPY]) = max(150, 88) = 150.
    expect(result.commission).toBe(150)
    expect(result.received).toBe(5700)
    // The foreign sub-account pays amount + commission; the main account receives `received`.
    expect(result.from).toEqual({
      id: 'sub-02',
      code: 'JPY',
      balance: 89850,
      isMain: false,
      rateBps: 5700,
    })
    expect(result.to).toEqual({
      id: 'main',
      code: 'EUR',
      balance: 385221,
      isMain: true,
      rateBps: 10000,
    })
    expect(mockSubaccounts().items).toContainEqual(result.from)
  })
})
