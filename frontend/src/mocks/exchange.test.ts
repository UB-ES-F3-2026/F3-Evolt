// @vitest-environment jsdom
import { describe, expect, it } from 'vitest'
import type { ApiErrorCode } from '@/models/apiError'
import { formatCents, formatSignedCents } from '@/models/money'
import type { ExchangeRequestJson } from '@/models/exchange'
import { mockBalance, mockHome } from './index'
import { mockGetSubaccounts, mockPostExchange } from './exchange'
import { setMockCurrentUser } from './mockUser'

// The mock keeps its state for the whole file, like `npm run dev` keeps it until a reload.
// The tests that exchange money are therefore written in order.

describe('mockGetSubaccounts (US-27)', () => {
  it('starts with the EUR main account and 317,55 $ for the demo user', () => {
    expect(mockGetSubaccounts()).toEqual([
      { code: 'EUR', balanceMinor: 379521, isMain: true },
      { code: 'USD', balanceMinor: 31755, isMain: false },
    ])
  })

  it('reads the EUR balance from the main account, never from its own state', () => {
    expect(mockGetSubaccounts()[0].balanceMinor).toBe(mockBalance())
  })
})

describe('mockPostExchange validations (US-27)', () => {
  it.each<[ExchangeRequestJson, ApiErrorCode]>([
    // body format → SAME_CURRENCY → owned sub-accounts → AMOUNT_TOO_SMALL → INSUFFICIENT_BALANCE.
    [{ srcCurrency: 'EUR', tgtCurrency: 'EUR', amountMinor: 10000 }, 'SAME_CURRENCY'],
    // 1 cèntim de dòlar no arriba ni a 1 cèntim d'euro amb el tipus real (US-27).
    [{ srcCurrency: 'USD', tgtCurrency: 'EUR', amountMinor: 1 }, 'AMOUNT_TOO_SMALL'],
    [{ srcCurrency: 'EUR', tgtCurrency: 'USD', amountMinor: 379000 }, 'INSUFFICIENT_BALANCE'],
    [{ srcCurrency: 'EUR', tgtCurrency: 'USD', amountMinor: 0 }, 'VALIDATION_ERROR'],
    [{ srcCurrency: 'EUR', tgtCurrency: 'USD', amountMinor: 30.5 }, 'VALIDATION_ERROR'],
    [{ srcCurrency: 'XXX', tgtCurrency: 'EUR', amountMinor: 10000 } as unknown as ExchangeRequestJson, 'VALIDATION_ERROR'],
  ])('rejects %j with %s and changes nothing (US-27)', (request, code) => {
    const before = { home: mockHome(), subaccounts: mockGetSubaccounts() }

    expect(() => mockPostExchange(request)).toThrow(expect.objectContaining({ code }) as Error)

    expect(mockHome()).toEqual(before.home)
    expect(mockGetSubaccounts()).toEqual(before.subaccounts)
  })

  it('rejects a currency the person has no sub-account for, without opening it', () => {
    const before = { home: mockHome(), subaccounts: mockGetSubaccounts() }

    expect(() => mockPostExchange({ srcCurrency: 'EUR', tgtCurrency: 'GBP', amountMinor: 10000 })).toThrow(
      expect.objectContaining({ code: 'VALIDATION_ERROR' }) as Error,
    )

    // The demo user owns EUR and USD only: GBP must not appear as a new sub-account.
    expect(mockHome()).toEqual(before.home)
    expect(mockGetSubaccounts()).toEqual(before.subaccounts)
  })
})

describe('mockPostExchange (US-27)', () => {
  it('changes 100,00 € into 109,61 $, charging the 1,50 € commission to the main account', () => {
    const result = mockPostExchange({ srcCurrency: 'EUR', tgtCurrency: 'USD', amountMinor: 10000 })

    // The charge is amount + commission (10150), not the raw amount.
    expect(result).toEqual({ srcBalanceMinor: 369371, tgtBalanceMinor: 42716 })
    expect(mockGetSubaccounts()).toEqual([
      { code: 'EUR', balanceMinor: 369371, isMain: true },
      { code: 'USD', balanceMinor: 42716, isMain: false },
    ])
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
    const before = { home: mockHome(), subaccounts: mockGetSubaccounts() }

    // 369000 + 5535 of commission = 374535, which is 5164 minor units (51,64 €) over
    // the 369371 left after the exchange above.
    expect(() => mockPostExchange({ srcCurrency: 'EUR', tgtCurrency: 'USD', amountMinor: 369000 })).toThrow(
      expect.objectContaining({ code: 'INSUFFICIENT_BALANCE' }) as Error,
    )

    expect(mockHome()).toEqual(before.home)
    expect(mockGetSubaccounts()).toEqual(before.subaccounts)
  })

  it('changes 100,00 $ back into euros: the sub-account pays and the main account receives', () => {
    const result = mockPostExchange({ srcCurrency: 'USD', tgtCurrency: 'EUR', amountMinor: 10000 })

    // 10000 $ + 150 of commission (1,50 $) leaves 32566 $; 9123 minor units arrive in EUR.
    expect(result).toEqual({ srcBalanceMinor: 32566, tgtBalanceMinor: 378494 })
    expect(mockHome().lastMovements[0]).toMatchObject({
      concept: 'Canvi de Dòlar nord-americà',
      type: 'income',
      amount: 9123,
    })
  })
})

describe('each account sees its own sub-accounts (US-27)', () => {
  it('an account without data has only the EUR sub-account, and the demo seed comes back on a user change', () => {
    setMockCurrentUser('buit@evolt.test')

    // Single sub-account: the «Canviar» screen has nothing to exchange with.
    expect(mockGetSubaccounts()).toEqual([{ code: 'EUR', balanceMinor: 0, isMain: true }])

    setMockCurrentUser(null)

    expect(mockGetSubaccounts()).toEqual([
      { code: 'EUR', balanceMinor: 379521, isMain: true },
      { code: 'USD', balanceMinor: 31755, isMain: false },
    ])
  })
})
