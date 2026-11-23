import { describe, expect, it } from 'vitest'
import {
  CURRENCIES,
  eurosFromMinor,
  formatCurrencyAmount,
  fromApiSubaccount,
  fromApiSubaccounts,
  isCurrencyCode,
  totalInEurosMinor,
} from './currency'

describe('totalInEurosMinor', () => {
  it('is 0 for an empty list', () => {
    expect(totalInEurosMinor([])).toBe(0)
  })

  it('converts nothing when a euro balance is 0', () => {
    expect(totalInEurosMinor([{ code: 'EUR', balance: 0 }])).toBe(0)
  })

  it('rounds every row on its own and then sums', () => {
    // EUR 125050 · 10000 / 10000 = 125050; USD 42716 → ⌊(42716·9123+5000)/10000⌋ = 38970;
    // JPY 1234 → ⌊(1234·5700+5000)/10000⌋ = 703. Total 125050 + 38970 + 703.
    expect(
      totalInEurosMinor([
        { code: 'EUR', balance: 125050 },
        { code: 'USD', balance: 42716 },
        { code: 'JPY', balance: 1234 },
      ]),
    ).toBe(164723)
  })

  it('differs from rounding the sum: two rows that only add up after rounding', () => {
    // USD 3 → ⌊(3·9123+5000)/10000⌋ = ⌊32369/10000⌋ = 3.
    // JPY 1 → ⌊(1·5700+5000)/10000⌋ = ⌊10700/10000⌋ = 1.
    const perRow = eurosFromMinor(3, 9123) + eurosFromMinor(1, 5700)
    // Rounding the sum instead: ⌊(3·9123 + 1·5700)/10000⌋ = ⌊33069/10000⌋ = 3.
    const roundedSum = Math.floor((3 * 9123 + 1 * 5700) / 10000)

    expect(perRow).toBe(4)
    expect(roundedSum).toBe(3)
    expect(totalInEurosMinor([{ code: 'USD', balance: 3 }, { code: 'JPY', balance: 1 }])).toBe(perRow)
    expect(totalInEurosMinor([{ code: 'USD', balance: 3 }, { code: 'JPY', balance: 1 }])).not.toBe(roundedSum)
  })
})

describe('eurosFromMinor', () => {
  it('converts minor units with the exact-.5 halves up', () => {
    expect(eurosFromMinor(5000, 9123)).toBe(4562) // ⌊(5000·9123+5000)/10000⌋
    expect(eurosFromMinor(50, 5700)).toBe(29) // raw 28.5 rounds up
    expect(eurosFromMinor(1, 5700)).toBe(1) // ⌊(1·5700+5000)/10000⌋
    expect(eurosFromMinor(1, 11680)).toBe(1) // ⌊(1·11680+5000)/10000⌋
  })
})

describe('formatCurrencyAmount', () => {
  it.each([
    ['USD', 31755, '317,55 $'],
    ['JPY', 1234, '1.234 ¥'],
    ['JPY', 7, '7 ¥'],
    ['GBP', 123455, '1.234,55 £'],
    ['CHF', 123455, '1.234,55 CHF'],
  ] as const)('shows %s %i as %j', (code, minor, text) => {
    expect(formatCurrencyAmount(minor, code)).toBe(text)
  })

  it('formats EUR through the shared cents formatter', () => {
    expect(formatCurrencyAmount(125050, 'EUR')).toMatch(/^1\.250,50\s€$/)
  })
})

describe('the closed list of currencies', () => {
  it('lists exactly the five codes, in order', () => {
    expect(CURRENCIES.map((currency) => currency.code)).toEqual(['EUR', 'USD', 'GBP', 'CHF', 'JPY'])
  })

  it('carries the agreed € rates and JPY without decimals', () => {
    expect(CURRENCIES.map((currency) => currency.rateBps)).toEqual([10000, 9123, 11680, 10355, 5700])
    expect(CURRENCIES[4]?.decimals).toBe(0)
  })

  it('accepts only exact codes', () => {
    expect(isCurrencyCode('USD')).toBe(true)
    expect(isCurrencyCode('usd')).toBe(false)
    expect(isCurrencyCode('AUD')).toBe(false)
  })
})

describe('fromApiSubaccounts', () => {
  it('maps known rows and drops unknown currencies', () => {
    expect(
      fromApiSubaccounts([
        { id: '1', currency: 'USD', balance: 31755 },
        { id: '2', currency: 'AUD', balance: 100 },
        { id: '3', currency: 'JPY', balance: 1234 },
      ]),
    ).toEqual([
      { id: '1', code: 'USD', balance: 31755 },
      { id: '3', code: 'JPY', balance: 1234 },
    ])
  })

  it('treats a missing list as empty', () => {
    expect(fromApiSubaccounts(null)).toEqual([])
    expect(fromApiSubaccounts(undefined)).toEqual([])
  })

  it('throws on a single row with an unknown currency', () => {
    expect(() => fromApiSubaccount({ id: '1', currency: 'AUD', balance: 100 })).toThrow()
  })
})
