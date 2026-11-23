/**
 * Money for display. Amounts travel as integer cents (docs/api.md §1) and
 * become euros only at the presentation edge, through this module.
 * Turning a typed euro amount into cents (T09.4) belongs here too, so every
 * euro ↔ cent conversion lives in one file.
 */

// Type-only on purpose: `currency.ts` value-imports `formatCents` from this
// module, so a value import here would create a runtime cycle (US-27).
import type { CurrencyCode } from './currency'

/**
 * Exact integer half-up division: `Math.floor((2n + d) / 2d)` for `n, d ≥ 0`.
 * Same result as the non-integer `n / d` rounded half up, without floats.
 */
export function halfUpDiv(n: number, d: number): number {
  return Math.floor((2 * n + d) / (2 * d))
}

const EUROS = new Intl.NumberFormat('ca-ES', { style: 'currency', currency: 'EUR' })

/** `125050` → `"1.250,50 €"` */
export function formatCents(cents: number): string {
  return EUROS.format(cents / 100)
}

export type AmountSign = 'positive' | 'negative'

const SIGN_TEXT: Record<AmountSign, string> = { positive: '+', negative: '−' }

/** For amounts with a direction (income / expense): `1000, 'negative'` → `"−10,00 €"` */
export function formatSignedCents(cents: number, sign: AmountSign): string {
  return `${SIGN_TEXT[sign]}${formatCents(cents)}`
}

// What a person types: digits, then optionally a comma or a dot and 1 or 2 decimals.
const TYPED_EUROS = /^(\d+)(?:[.,](\d{1,2}))?$/

/** `"12,5"` → `1250`. `null` when the text is not an amount with at most 2 decimals. */
export function eurosToCents(text: string): number | null {
  const match = TYPED_EUROS.exec(text.trim())
  if (match === null) return null
  const [, euros, decimals = ''] = match
  const cents = Number(euros) * 100 + Number(decimals.padEnd(2, '0'))
  return Number.isSafeInteger(cents) ? cents : null
}

// Symbol shown after the amount for each currency (US-25 mockup). CHF has no
// symbol, its code is the symbol.
const SYMBOLS: Record<CurrencyCode, string> = {
  EUR: '€',
  USD: '$',
  GBP: '£',
  CHF: 'CHF',
  JPY: '¥',
}

/** Minor units per whole unit: 100 for every currency except JPY (whole yen). */
export function currencyDecimals(code: CurrencyCode): number {
  return code === 'JPY' ? 0 : 2
}

/** € $ £ CHF ¥ */
export function currencySymbol(code: CurrencyCode): string {
  return SYMBOLS[code]
}

/**
 * Formats any currency's minor units the way the app shows them (US-25/US-27):
 * `"317,55 $", "1.234 ¥", "1.234,56 CHF"` (NBSP before the symbol, like EUR),
 * so the amount never wraps away from its currency. EUR delegates to
 * `formatCents`, so its output is exactly the euro formatting already used.
 */
export function formatMinor(minor: number, code: CurrencyCode): string {
  if (code === 'EUR') return formatCents(minor)
  const decimals = currencyDecimals(code)
  const amount = numberFormatter(decimals).format(minor / 10 ** decimals)
  return `${amount}\u00A0${SYMBOLS[code]}`
}

const FORMATTERS: Record<number, Intl.NumberFormat> = {}

function numberFormatter(decimals: number): Intl.NumberFormat {
  let formatter = FORMATTERS[decimals]
  if (formatter === undefined) {
    formatter = new Intl.NumberFormat('ca-ES', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    })
    FORMATTERS[decimals] = formatter
  }
  return formatter
}
