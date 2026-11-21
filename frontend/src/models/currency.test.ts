import { describe, expect, it } from 'vitest'
import {
  CURRENCIES,
  eurosFromMinor,
  fromApiSubaccount,
  fromApiSubaccountsList,
  isCurrencyCode,
  totalInEurosMinor,
} from './currency'
import { formatMinor } from './money'

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

describe('formatMinor (US-25)', () => {
  it.each([
    ['USD', 31755, '317,55\u00A0$'],
    ['JPY', 1234, '1.234\u00A0¥'],
    ['JPY', 7, '7\u00A0¥'],
    ['GBP', 123455, '1.234,55\u00A0£'],
    ['CHF', 123455, '1.234,55\u00A0CHF'],
  ] as const)('shows %s %i as %j', (code, minor, text) => {
    expect(formatMinor(minor, code)).toBe(text)
  })

  it('formats EUR through the shared cents formatter', () => {
    expect(formatMinor(125050, 'EUR')).toMatch(/^1\.250,50\s€$/)
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

describe('fromApiSubaccountsList', () => {
  it('maps known rows and drops unknown currencies', () => {
    expect(
      fromApiSubaccountsList({
        items: [
          { id: '1', currency: 'USD', balance: 31755, isMain: false, rateBps: 9123 },
          { id: '2', currency: 'AUD', balance: 100, isMain: false, rateBps: 10000 },
          { id: '3', currency: 'JPY', balance: 1234, isMain: false, rateBps: 5700 },
        ],
        totalInEuros: 154020,
      }),
    ).toEqual({
      items: [
        { id: '1', code: 'USD', balance: 31755, isMain: false, rateBps: 9123 },
        { id: '3', code: 'JPY', balance: 1234, isMain: false, rateBps: 5700 },
      ],
      totalInEuros: 154020,
    })
  })

  it('maps isMain and rateBps onto every row (§12.2)', () => {
    expect(
      fromApiSubaccountsList({
        items: [
          { id: 'main', currency: 'EUR', balance: 125050, isMain: true, rateBps: 10000 },
          { id: 'sub-01', currency: 'USD', balance: 31755, isMain: false, rateBps: 9123 },
        ],
        totalInEuros: 154020,
      }).items,
    ).toEqual([
      { id: 'main', code: 'EUR', balance: 125050, isMain: true, rateBps: 10000 },
      { id: 'sub-01', code: 'USD', balance: 31755, isMain: false, rateBps: 9123 },
    ])
  })

  it('passes totalInEuros through untouched: the server computes it (§12.3)', () => {
    // Even a total that does not match the rows goes through: no screen recomputes it.
    expect(fromApiSubaccountsList({ items: [], totalInEuros: 154020 }).totalInEuros).toBe(154020)
    expect(
      fromApiSubaccountsList({
        items: [{ id: 'main', currency: 'EUR', balance: 125050, isMain: true, rateBps: 10000 }],
        totalInEuros: 999999,
      }).totalInEuros,
    ).toBe(999999)
  })

  it('treats a missing list as an empty one', () => {
    expect(fromApiSubaccountsList(null)).toEqual({ items: [], totalInEuros: 0 })
    expect(fromApiSubaccountsList(undefined)).toEqual({ items: [], totalInEuros: 0 })
  })

  it('throws on a row whose isMain is not a boolean', () => {
    const bad = {
      id: 'main',
      currency: 'EUR',
      balance: 125050,
      isMain: 'true',
      rateBps: 10000,
    } as unknown as Parameters<typeof fromApiSubaccount>[0]
    expect(() => fromApiSubaccount(bad)).toThrow(/isMain/)
  })

  it('throws on a row whose rateBps is not a safe integer', () => {
    // 91.23 is a valid `number` in TS: only the runtime guard catches it.
    const bad = { id: 'sub-01', currency: 'USD', balance: 31755, isMain: false, rateBps: 91.23 }
    expect(() => fromApiSubaccount(bad)).toThrow(/rateBps/)
  })
})

describe('fromApiSubaccount', () => {
  it('throws on a single row with an unknown currency', () => {
    expect(() =>
      fromApiSubaccount({ id: '1', currency: 'AUD', balance: 100, isMain: false, rateBps: 10000 }),
    ).toThrow()
  })
})
