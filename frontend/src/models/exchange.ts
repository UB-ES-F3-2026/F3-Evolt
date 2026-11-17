/**
 * Currency exchange (US-27). All the money math of a currency change lives
 * here, in integer minor units: a conversion is
 * `amount × RATE_BPS[from] / RATE_BPS[to]`, computed with integer half-up
 * rounding so no float ever decides an amount.
 *
 * `RATE_BPS` is "basis points": the minor units of EUR one unit of the
 * currency costs, ×10000 (so 9123 = 0,9123 € per $). The display rate is the
 * rounded 2-decimal version (`rateRoundedMinor`); exact conversions always use
 * the raw rate, never the rounded one.
 *
 * `money.ts` imports only the `CurrencyCode` TYPE from here, so there is no
 * runtime cycle; this file imports the formatting functions from `money.ts`.
 */

import { formatMinor } from './money'

export type CurrencyCode = 'EUR' | 'USD' | 'GBP' | 'CHF' | 'JPY'

export interface CurrencyMeta {
  code: CurrencyCode
  name: string
}

export const CURRENCIES: Record<CurrencyCode, CurrencyMeta> = {
  EUR: { code: 'EUR', name: 'Euro' },
  USD: { code: 'USD', name: 'Dòlar nord-americà' },
  GBP: { code: 'GBP', name: 'Lliura esterlina' },
  CHF: { code: 'CHF', name: 'Franc suís' },
  JPY: { code: 'JPY', name: 'Ien japonès' },
}

/** Minor units of EUR one unit of the currency costs, ×10000 (docs US-27). */
export const RATE_BPS: Record<CurrencyCode, number> = {
  EUR: 10000,
  USD: 9123,
  GBP: 11680,
  CHF: 10355,
  JPY: 5700,
}

const CURRENCY_CODES = Object.keys(RATE_BPS) as CurrencyCode[]

/** Runtime guard for data that travels as text, like `history.state`. */
export function isCurrencyCode(value: unknown): value is CurrencyCode {
  return typeof value === 'string' && CURRENCY_CODES.includes(value as CurrencyCode)
}

/**
 * Exact integer half-up division: `Math.floor((2n + d) / 2d)` for `n, d ≥ 0`.
 * Same result as the non-integer `n / d` rounded half up, without floats.
 */
export function halfUpDiv(n: number, d: number): number {
  return Math.floor((2 * n + d) / (2 * d))
}

/**
 * `amountMinor` of `from` into minor units of `to`, with integer half-up:
 * `amountMinor × RATE_BPS[from] / RATE_BPS[to]`.
 * Example: `convertMinor(10000, 'EUR', 'USD')` → `10961` (100,00 € = 109,61 $).
 */
export function convertMinor(amountMinor: number, from: CurrencyCode, to: CurrencyCode): number {
  return halfUpDiv(amountMinor * RATE_BPS[from], RATE_BPS[to])
}

/** A subaccount of «Divises», as the ViewModel of «Canviar» lists it. */
export interface SubaccountOption {
  code: CurrencyCode
  name: string
  balanceMinor: number
  isMain: boolean
}

/** What the «Canviar» screen keeps while the person types. */
export interface ExchangeDraft {
  srcCurrency: CurrencyCode
  tgtCurrency: CurrencyCode
  amountMinor: number
}

// The contract objects of US-27 (docs/api.md, issue #166). They live here, next
// to the currency data they carry, and the service only re-exports them.

/** One owned sub-account, as `GET /api/currencies` returns it. */
export interface SubaccountJson {
  code: CurrencyCode
  balanceMinor: number
  isMain: boolean
}

/** The body of `POST /api/exchanges`. */
export interface ExchangeRequestJson {
  srcCurrency: CurrencyCode
  tgtCurrency: CurrencyCode
  amountMinor: number
}

/** What `POST /api/exchanges` answers: both balances after the exchange. */
export interface ExchangeResultJson {
  srcBalanceMinor: number
  tgtBalanceMinor: number
}

// What the keypad can produce: digits and at most a decimal mark with 1 or 2
// digits (decimals 2), or plain digits (decimals 0, whole yen).
const TYPED_2_DECIMALS = /^(\d+)(?:[.,](\d{1,2}))?$/
const TYPED_0_DECIMALS = /^\d+$/

/**
 * A typed amount string → minor units. With `decimals 2` it follows the
 * `eurosToCents` semantics (`"100,5"` → `10050`); with `decimals 0` the text
 * must be plain digits (JPY has no decimals, so a comma is never valid).
 * Anything else — including `''` — reads as `null`.
 */
export function parseKeypadAmount(text: string, decimals: 0 | 2): number | null {
  if (decimals === 0) {
    if (!TYPED_0_DECIMALS.test(text)) return null
    const amount = Number(text)
    return Number.isSafeInteger(amount) ? amount : null
  }
  const match = TYPED_2_DECIMALS.exec(text)
  if (match === null) return null
  const [, major, fraction = ''] = match
  const amount = Number(major) * 100 + Number(fraction.padEnd(2, '0'))
  return Number.isSafeInteger(amount) ? amount : null
}

/**
 * The 2-decimal displayed rate: target minor units per 100 source minor units.
 * `rateRoundedMinor('EUR', 'USD')` → `110`, read as «1 € = 1,10 $».
 */
export function rateRoundedMinor(from: CurrencyCode, to: CurrencyCode): number {
  return convertMinor(100, from, to)
}

/**
 * Whole source units the rate row is quoted for: 1 for every 2-decimal
 * currency, but 100 for JPY — `rateRoundedMinor` is per 100 source minor
 * units, so quoting the JPY rate as «1 ¥» would be wrong by 100×.
 */
export function rateLabelCount(from: CurrencyCode): number {
  return from === 'JPY' ? 100 : 1
}

/**
 * What the person will approximately receive, using the rounded 2-decimal
 * rate of the screen: `halfUpDiv(amountMinor × rateRoundedMinor, 100)`.
 * `estimateMinor(10000, 'EUR', 'USD')` → `11000` («aproximadament 110,00 $»).
 */
export function estimateMinor(amountMinor: number, src: CurrencyCode, tgt: CurrencyCode): number {
  return halfUpDiv(amountMinor * rateRoundedMinor(src, tgt), 100)
}

/**
 * The exchange commission, in SOURCE minor units: 1,5 % of the amount, with a
 * minimum of 0,50 €, always computed in euros and converted back.
 */
export function commissionSrcMinor(amountMinor: number, src: CurrencyCode): number {
  const amountEur = convertMinor(amountMinor, src, 'EUR')
  const commissionEur = Math.max(Math.floor((150 * amountEur + 5000) / 10000), 50)
  return convertMinor(commissionEur, 'EUR', src)
}

/** What the «Continuar» summary screen shows, before any API call. */
export interface ExchangePreview {
  exactReceivedMinor: number
  commissionSrcMinor: number
  totalChargeMinor: number
  tooSmall: boolean
  insufficient: boolean
}

/**
 * Everything the summary screen needs from one pure computation.
 * `tooSmall` compares RAW rates (`a × RATE_BPS[src] < RATE_BPS[tgt]`), never
 * the half-up result: 0,01 $ → EUR must be rejected even though the rounding
 * of 0,9123 € would say 1 ¢.
 */
export function exchangePreview(
  a: number,
  src: CurrencyCode,
  tgt: CurrencyCode,
  srcBalanceMinor: number,
): ExchangePreview {
  const commission = commissionSrcMinor(a, src)
  return {
    exactReceivedMinor: convertMinor(a, src, tgt),
    commissionSrcMinor: commission,
    totalChargeMinor: a + commission,
    tooSmall: a * RATE_BPS[src] < RATE_BPS[tgt],
    insufficient: a + commission > srcBalanceMinor,
  }
}

/** The commission line of the summary: «Comissió: 1,50 €» or «Sense comissió». */
export function formatCommissionLabel(commissionMinor: number, code: CurrencyCode): string {
  if (commissionMinor === 0) return 'Sense comissió'
  return `Comissió: ${formatMinor(commissionMinor, code)}`
}
