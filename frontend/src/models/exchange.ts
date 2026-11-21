/**
 * Currency exchange (US-27). All the money math of a currency change lives
 * here, in integer minor units: a conversion is
 * `amount × rateBps[from] / rateBps[to]`, computed with integer half-up
 * rounding so no float ever decides an amount.
 *
 * Rates are "basis points": the minor units of EUR one unit of the currency
 * costs, ×10000 (so 9123 = 0,9123 € per $). The display rate is the rounded
 * 2-decimal version (`rateRoundedMinor`); exact conversions always use the
 * raw rate, never the rounded one.
 *
 * The rate table (`CURRENCIES[].rateBps`) lives in `currency.ts`; `money.ts`
 * imports only the `CurrencyCode` TYPE from there, so there is no runtime
 * cycle. This file imports the helpers it needs from `currency.ts` and
 * `money.ts`.
 */

import { currencyByCode, type CurrencyCode, type Subaccount, type SubaccountJson } from './currency'
import { formatMinor, halfUpDiv } from './money'
// Backward-compat type re-exports only — no second definition anywhere:
export type { CurrencyCode, SubaccountOption } from './currency'

/**
 * `amountMinor` of `from` into minor units of `to`, with integer half-up:
 * `amountMinor × rateBps(from) / rateBps(to)`.
 * Example: `convertMinor(10000, 'EUR', 'USD')` → `10961` (100,00 € = 109,61 $).
 */
export function convertMinor(amountMinor: number, from: CurrencyCode, to: CurrencyCode): number {
  return halfUpDiv(amountMinor * currencyByCode(from).rateBps, currencyByCode(to).rateBps)
}

/** What the «Canviar» screen keeps while the person types. */
export interface ExchangeDraft {
  srcCurrency: CurrencyCode
  tgtCurrency: CurrencyCode
  amountMinor: number
}

// The exchange contract objects (docs/api.md §12.7, T27.1) — US-27 is the
// screen that uses them. They live here, next to the currency data they carry,
// and the service only re-exports them.

/** The body of `POST /api/exchanges` (§12.7): `amount` is minor units of `fromCurrency`. */
export interface ExchangeRequestJson {
  fromCurrency: CurrencyCode
  toCurrency: CurrencyCode
  amount: number
}

/**
 * What `POST /api/exchanges` answers (§12.7), exactly as it travels on the wire:
 * both accounts as the API rows (`currency`, not `code`), with their new balance,
 * plus the figures already applied (`amount` and `commission` in the source minor
 * unit, `received` in the target one).
 */
export interface ExchangeResultJson {
  from: SubaccountJson
  to: SubaccountJson
  amount: number
  commission: number
  received: number
}

/**
 * The app-level result of `POST /api/exchanges`: what the app works with after
 * mapping the wire rows through `fromApiSubaccount` — the same fields, with each
 * account carrying `code`. The screen shows these numbers (the confirmed balances
 * included); it never recomputes them.
 */
export interface ExchangeResult {
  from: Subaccount
  to: Subaccount
  amount: number
  commission: number
  received: number
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
 * The 0,50 € minimum in source minor units, rounded UP so it never dips below
 * 0,50 € (§12.7): `⌈50 × 10000 / rateBps[origen]⌉`, computed with integer
 * ceiling math (`⌊(n + d - 1) / d⌋`) so no float decides a minimum.
 * `minimumCommissionSrcMinor('CHF')` → `49` (0,49 CHF ja valen 0,5074 €).
 */
export function minimumCommissionSrcMinor(src: CurrencyCode): number {
  const rateBps = currencyByCode(src).rateBps
  return Math.floor((50 * 10000 + rateBps - 1) / rateBps)
}

/**
 * The exchange commission, in SOURCE minor units: 1,5 % of the amount or the
 * per-currency minimum, whichever is larger (§12.7).
 *
 * It is computed straight in the source currency — never converted to euros and
 * back — because the 0,50 € floor must be worth at least 0,50 € *before*
 * rounding: the round trip would drift the floor by a minor unit (48 CHF cents
 * instead of 49).
 *
 * The backend service owns this rule; this is the frontend's copy for the
 * «Continuar» preview and the mock (skill middle-services). If §12.7 changes,
 * both move together.
 */
export function commissionSrcMinor(amountMinor: number, src: CurrencyCode): number {
  return Math.max(halfUpDiv(amountMinor * 150, 10000), minimumCommissionSrcMinor(src))
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
 * `tooSmall` compares RAW rates (`a × currencyByCode(src).rateBps <
 * currencyByCode(tgt).rateBps`), never the half-up result: 0,01 $ → EUR must
 * be rejected even though the rounding of 0,9123 € would say 1 ¢.
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
    tooSmall: a * currencyByCode(src).rateBps < currencyByCode(tgt).rateBps,
    insufficient: a + commission > srcBalanceMinor,
  }
}

/** The commission line of the summary: «Comissió: 1,50 €» or «Sense comissió». */
export function formatCommissionLabel(commissionMinor: number, code: CurrencyCode): string {
  if (commissionMinor === 0) return 'Sense comissió'
  return `Comissió: ${formatMinor(commissionMinor, code)}`
}
