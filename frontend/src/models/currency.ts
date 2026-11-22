/**
 * US-25: the closed list of currency sub-accounts, their € rates and display
 * formatting. Amounts in minor units (cents, or whole yen for JPY).
 */

import { formatCents } from './money'

/** Every currency the bank offers, in the order the API and the UI list them. */
export type CurrencyCode = 'EUR' | 'USD' | 'GBP' | 'CHF' | 'JPY'

/** One currency: its € rate in basis points (10000 = 1 €) and its minor-unit decimals. */
export interface CurrencyInfo {
  code: CurrencyCode
  name: string
  symbol: string
  rateBps: number
  decimals: number
}

export const CURRENCIES: readonly CurrencyInfo[] = [
  { code: 'EUR', name: 'Euro', symbol: '€', rateBps: 10000, decimals: 2 },
  { code: 'USD', name: 'Dòlar nord-americà', symbol: '$', rateBps: 9123, decimals: 2 },
  { code: 'GBP', name: 'Lliura esterlina', symbol: '£', rateBps: 11680, decimals: 2 },
  { code: 'CHF', name: 'Franc suís', symbol: 'CHF', rateBps: 10355, decimals: 2 },
  { code: 'JPY', name: 'Ien japonès', symbol: '¥', rateBps: 5700, decimals: 0 },
]

/** `true` only for the five codes in `CURRENCIES` (case sensitive, like the API). */
export function isCurrencyCode(value: string): value is CurrencyCode {
  return CURRENCIES.some((currency) => currency.code === value)
}

/** The `CurrencyInfo` of a known code. Throws on anything else (internal invariant). */
export function currencyByCode(code: CurrencyCode): CurrencyInfo {
  const currency = CURRENCIES.find((candidate) => candidate.code === code)
  if (currency === undefined) throw new Error(`Unknown currency code: ${code}`)
  return currency
}

/** `minor` units of `rateBps` into whole euro cents, rounding halves up. */
export function eurosFromMinor(minor: number, rateBps: number): number {
  // Integer-exact equivalent of `Math.floor(minor * rateBps / 10000 + 0.5)`.
  return Math.floor((minor * rateBps + 5000) / 10000)
}

/** One currency sub-account of the main account. */
export interface Subaccount {
  id: string
  code: CurrencyCode
  balance: number
}

/** A subaccount as the API sends it, before `currency` is checked. */
export interface SubaccountJson {
  id: string
  currency: string
  balance: number
}

/** GET /api/subaccounts (docs/api.md). */
export interface SubaccountsJson {
  items: SubaccountJson[]
}

/** Maps one row; unknown currency codes are an API contract break, so it throws. */
export function fromApiSubaccount(json: SubaccountJson): Subaccount {
  if (!isCurrencyCode(json.currency)) {
    throw new Error(`Unknown currency code: ${json.currency}`)
  }
  return { id: json.id, code: json.currency, balance: json.balance }
}

/** Maps the list, dropping rows whose currency is not a known code. */
export function fromApiSubaccounts(list: SubaccountJson[] | null | undefined): Subaccount[] {
  return (list ?? []).filter((json) => isCurrencyCode(json.currency)).map(fromApiSubaccount)
}

/**
 * The total of every subaccount in euro cents: each row is converted and rounded
 * on its own, and only then summed — never the other way around.
 */
export function totalInEurosMinor(subaccounts: readonly { code: CurrencyCode; balance: number }[]): number {
  return subaccounts.reduce((total, subaccount) => {
    return total + eurosFromMinor(subaccount.balance, currencyByCode(subaccount.code).rateBps)
  }, 0)
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

/**
 * `31755, 'USD'` → `"317,55 $"`. EUR reuses `formatCents`; the rest avoid
 * Intl's `style: 'currency'`, which renders USD as `US$` in ca-ES.
 */
export function formatCurrencyAmount(minor: number, code: CurrencyCode): string {
  const currency = currencyByCode(code)
  if (code === 'EUR') return formatCents(minor)
  return `${numberFormatter(currency.decimals).format(minor / 10 ** currency.decimals)} ${currency.symbol}`
}
