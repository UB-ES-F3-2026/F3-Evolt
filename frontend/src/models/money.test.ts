import { describe, expect, it } from 'vitest'
import { currencyDecimals, currencySymbol, eurosToCents, formatCents, formatMinor, formatSignedCents } from './money'
import type { CurrencyCode } from './exchange'

describe('formatSignedCents', () => {
  it('puts «+» on an income and «−» on an expense', () => {
    expect(formatSignedCents(1500, 'positive')).toBe(`+${formatCents(1500)}`)
    expect(formatSignedCents(1000, 'negative')).toBe(`−${formatCents(1000)}`)
  })
})

describe('eurosToCents', () => {
  it.each([
    ['12', 1200],
    ['12,5', 1250],
    ['12.50', 1250],
    [' 7 ', 700],
    ['0', 0],
    ['0,01', 1],
    ['500', 50000],
    ['500,01', 50001],
  ])('reads %j as %i cents', (text, cents) => {
    expect(eurosToCents(text)).toBe(cents)
  })

  it.each(['', 'abc', '12,345', '-5', '12,', ',5', '1.000,00', '1e3', '99999999999999999'])(
    'rejects %j',
    (text) => {
      expect(eurosToCents(text)).toBeNull()
    },
  )
})

describe('formatCents', () => {
  it('shows cents as euros in Catalan format', () => {
    expect(formatCents(125050)).toMatch(/^1\.250,50\s€$/)
  })
})

describe('currencyDecimals and currencySymbol (US-25, US-27)', () => {
  it('has 0 decimals only for the whole-yen JPY', () => {
    expect(currencyDecimals('JPY')).toBe(0)
    expect(currencyDecimals('EUR')).toBe(2)
    expect(currencyDecimals('USD')).toBe(2)
    expect(currencyDecimals('GBP')).toBe(2)
    expect(currencyDecimals('CHF')).toBe(2)
  })

  it.each<[CurrencyCode, string]>([
    ['EUR', '€'],
    ['USD', '$'],
    ['GBP', '£'],
    ['CHF', 'CHF'],
    ['JPY', '¥'],
  ])('shows %s with the symbol %s', (code, symbol) => {
    expect(currencySymbol(code)).toBe(symbol)
  })
})

describe('formatMinor (US-25, US-27)', () => {
  it('formats any currency after its amount, with an NBSP before the symbol', () => {
    expect(formatMinor(31755, 'USD')).toBe('317,55\u00A0$')
    expect(formatMinor(3905, 'GBP')).toBe('39,05\u00A0£')
    expect(formatMinor(123456, 'CHF')).toBe('1.234,56\u00A0CHF')
  })

  it('formats JPY minor units, which are whole yen', () => {
    expect(formatMinor(1234, 'JPY')).toBe('1.234\u00A0¥')
    expect(formatMinor(100, 'JPY')).toBe('100\u00A0¥')
  })

  it('formats EUR exactly like formatCents, NBSP included', () => {
    expect(formatMinor(125050, 'EUR')).toBe(formatCents(125050))
    expect(formatMinor(125050, 'EUR')).toMatch(/^1\.250,50\s€$/)
  })
})
