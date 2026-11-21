import { describe, expect, it } from 'vitest'
import {
  commissionSrcMinor,
  convertMinor,
  estimateMinor,
  exchangePreview,
  formatCommissionLabel,
  minimumCommissionSrcMinor,
  parseKeypadAmount,
  rateLabelCount,
  rateRoundedMinor,
  type CurrencyCode,
} from './exchange'
import { formatMinor, halfUpDiv } from './money'
import { isCurrencyCode } from './currency'

describe('convertMinor (US-27)', () => {
  it.each<[number, CurrencyCode, CurrencyCode, number]>([
    [10000, 'EUR', 'USD', 10961],
    [33755, 'USD', 'EUR', 30795],
    [5000, 'USD', 'GBP', 3905],
    [100, 'EUR', 'JPY', 175],
  ])('converts %i minor of %s into %s', (amount, from, to, received) => {
    expect(convertMinor(amount, from, to)).toBe(received)
  })

  it('returns the same amount when both subaccounts are the same currency', () => {
    expect(convertMinor(33755, 'USD', 'USD')).toBe(33755)
    expect(convertMinor(1, 'JPY', 'JPY')).toBe(1)
  })
})

describe('exchangePreview (US-27)', () => {
  // CV-01: 100,00 € → 109,61 $ with the 1,50 € commission (§12.7).
  it('previews «100,00 € → 109,61 $» with the 1,50 € commission', () => {
    const preview = exchangePreview(10000, 'EUR', 'USD', 125050)
    expect(preview.exactReceivedMinor).toBe(10961)
    expect(preview.commissionSrcMinor).toBe(150)
    expect(preview.totalChargeMinor).toBe(10150)
    expect(preview.tooSmall).toBe(false)
    expect(preview.insufficient).toBe(false)
    expect(formatMinor(preview.exactReceivedMinor, 'USD')).toBe('109,61\u00A0$')
    expect(formatMinor(preview.commissionSrcMinor, 'EUR')).toMatch(/^1,50\s€$/)
  })

  it('rejects 0,01 $ → EUR with the RAW rate, not the rounded one', () => {
    // Half-up of 1 × 9123 / 10000 would say 1 ¢; the raw comparison must say too small.
    expect(exchangePreview(1, 'USD', 'EUR', 100000).tooSmall).toBe(true)
    expect(exchangePreview(10000, 'EUR', 'USD', 125050).tooSmall).toBe(false)
  })

  it('flags the amount plus commission over the source balance (US-27)', () => {
    // 100,00 € + 1,50 € = 101,50 € > 101,49 € of balance.
    expect(exchangePreview(10000, 'EUR', 'USD', 10149).insufficient).toBe(true)
    expect(exchangePreview(10000, 'EUR', 'USD', 10150).insufficient).toBe(false)
  })
})

describe('minimumCommissionSrcMinor (§12.7)', () => {
  // The 0,50 € floor in each currency's minor unit, rounded UP (§12.7 table).
  it.each<[CurrencyCode, number]>([
    ['EUR', 50],
    ['USD', 55],
    ['GBP', 43],
    ['CHF', 49],
    ['JPY', 88],
  ])('converts the 0,50 € floor into %s minor units (%i)', (code, expected) => {
    expect(minimumCommissionSrcMinor(code)).toBe(expected)
  })
})

describe('commissionSrcMinor (§12.7)', () => {
  it('takes 1,5 % of 100,00 € → 1,50 €', () => {
    expect(commissionSrcMinor(10000, 'EUR')).toBe(150)
  })

  it('never charges less than the 0,50 € minimum', () => {
    expect(commissionSrcMinor(2000, 'EUR')).toBe(50)
  })

  it('computes a USD commission in USD minor units', () => {
    // §12.7: 1,5 % of 50,00 $ = 0,75 $ = 75 minor, above the 55 minimum.
    expect(commissionSrcMinor(5000, 'USD')).toBe(75)
  })

  it('charges 1,5 % of 10.000 ¥ → 150 ¥, above the 88 ¥ minimum', () => {
    // §12.7: max(arrodonir(10000 × 150 / 10000), mínim[JPY]) = max(150, 88) = 150.
    // The old EUR round trip drifted to 151; the contract's formula is exact here.
    expect(commissionSrcMinor(10000, 'JPY')).toBe(150)
  })

  it('charges the CHF minimum of 49 cents, not 48', () => {
    // §12.7: 1,5 % of 0,01 CHF rounds to 0, so the floor applies:
    // ⌈50 × 10000 / 10355⌉ = ⌈48,28⌉ = 49 (the old EUR round trip said 48).
    expect(commissionSrcMinor(1, 'CHF')).toBe(49)
  })

  // Commission values pinned by docs/proves-multidivisa.md.
  it.each<[string, number, CurrencyCode, number]>([
    ['CV-05 · 10,00 € stays on the 0,50 € minimum', 1000, 'EUR', 50],
    ['CV-06a · 289,70 € → 4,35 €', 28970, 'EUR', 435],
    ['CV-06b · 312,86 $ → 4,69 $', 31286, 'USD', 469],
    ['CV-12 · 3.795,21 € → 56,93 €', 379521, 'EUR', 5693],
    ['CV-13 · 107,99 $ → 1,62 $', 10799, 'USD', 162],
    ['CV-16 · 100 ¥ stays on the 88 ¥ minimum', 100, 'JPY', 88],
    ['CV-11 · 1 EUR minor unit (1 cèntim) stays on the 0,50 € minimum', 1, 'EUR', 50],
  ])('pins %s', (_case, amount, code, expected) => {
    expect(commissionSrcMinor(amount, code)).toBe(expected)
  })

  it('pins CV-11 · 1 EUR minor unit → 2 ¥', () => {
    // 1 × 10000 / 5700 = 1,75… → half-up = 2.
    expect(convertMinor(1, 'EUR', 'JPY')).toBe(2)
  })
})

describe('the GBP row of the summary (US-27)', () => {
  it('shows «50,00 $ → 39,05 £» with its commission', () => {
    expect(commissionSrcMinor(5000, 'USD')).toBe(75)
    expect(convertMinor(5000, 'USD', 'GBP')).toBe(3905)
    expect(formatMinor(3905, 'GBP')).toBe('39,05\u00A0£')
  })
})

describe('rateRoundedMinor, estimateMinor and rateLabelCount (US-27)', () => {
  it('shows the 2-decimal rate «1 € = 1,10 $»', () => {
    expect(rateRoundedMinor('EUR', 'USD')).toBe(110)
    expect(rateLabelCount('EUR')).toBe(1)
  })

  it('quotes the JPY rate per 100 yen, not per yen', () => {
    expect(rateLabelCount('JPY')).toBe(100)
    expect(formatMinor(100, 'JPY')).toBe('100\u00A0¥')
  })

  it('estimates with the rounded rate: 100,00 € ≈ 110,00 $', () => {
    expect(estimateMinor(10000, 'EUR', 'USD')).toBe(11000)
  })
})

describe('halfUpDiv (US-27)', () => {
  // The canonical half-up trick of the conversion (same result as the non-integer
  // Math.round of n / d): dividing by 10000 = Math.floor((n + 5000) / 10000).
  it.each([0, 1, 4561, 4562, 9123, 10000, 307946865])(
    'matches Math.floor((n + 5000) / 10000) for %i',
    (n) => {
      expect(halfUpDiv(n, 10000)).toBe(Math.floor((n + 5000) / 10000))
    },
  )

  it('rounds the exact half up', () => {
    expect(halfUpDiv(1, 2)).toBe(1)
    expect(halfUpDiv(3, 2)).toBe(2)
  })
})

describe('parseKeypadAmount (US-27)', () => {
  it('reads a 2-decimal amount like eurosToCents', () => {
    expect(parseKeypadAmount('100,5', 2)).toBe(10050)
    expect(parseKeypadAmount('100', 2)).toBe(10000)
  })

  it('reads a whole-yen amount as plain digits only', () => {
    expect(parseKeypadAmount('100', 0)).toBe(100)
    expect(parseKeypadAmount('1,5', 0)).toBeNull()
  })

  it.each(['', '12,345', '1.250,50', 'abc', '12,'])(
    'rejects %j as a 2-decimal amount',
    (text) => {
      expect(parseKeypadAmount(text, 2)).toBeNull()
    },
  )

  it.each(['', '1,5', '-5', '12,'])(
    'rejects %j as a whole-yen amount',
    (text) => {
      expect(parseKeypadAmount(text, 0)).toBeNull()
    },
  )
})

describe('isCurrencyCode (US-27)', () => {
  it.each([
    ['EUR', true],
    ['JPY', true],
    ['eur', false],
    [42, false],
    [null, false],
    [undefined, false],
  ])('says %j is a CurrencyCode: %j', (value, expected) => {
    expect(isCurrencyCode(value)).toBe(expected)
  })
})

describe('formatCommissionLabel (US-27)', () => {
  it('says «Sense comissió» only when the commission is 0', () => {
    expect(formatCommissionLabel(0, 'EUR')).toBe('Sense comissió')
    expect(formatCommissionLabel(150, 'EUR')).toMatch(/^Comissió: 1,50\s€$/)
  })
})
