/**
 * US-25: the closed list of currency sub-accounts, their € rates and the
 * sub-account mapping. Amounts in minor units (cents, or whole yen for JPY).
 * Display formatting lives in `money.ts` (`formatMinor`).
 */

import { halfUpDiv } from './money'

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

/** `true` only for the five codes in `CURRENCIES` (case sensitive, like the API); safe on untyped data, like `history.state`. */
export function isCurrencyCode(value: unknown): value is CurrencyCode {
  return typeof value === 'string' && CURRENCIES.some((currency) => currency.code === value)
}

/** The `CurrencyInfo` of a known code. Throws on anything else (internal invariant). */
export function currencyByCode(code: CurrencyCode): CurrencyInfo {
  const currency = CURRENCIES.find((candidate) => candidate.code === code)
  if (currency === undefined) throw new Error(`Unknown currency code: ${code}`)
  return currency
}

/** `minor` units of `rateBps` into whole euro cents, rounding halves up. */
export function eurosFromMinor(minor: number, rateBps: number): number {
  return halfUpDiv(minor * rateBps, 10000)
}

/** One currency sub-account of the main account (§12.2). */
export interface Subaccount {
  id: string
  code: CurrencyCode
  balance: number
  isMain: boolean
  rateBps: number
}

/** A subaccount as the API sends it, before `currency` is checked. */
export interface SubaccountJson {
  id: string
  currency: string
  balance: number
  isMain: boolean
  rateBps: number
}

/** GET /api/subaccounts (§12.3): the rows plus the server-computed approximate total. */
export interface SubaccountsJson {
  items: SubaccountJson[]
  totalInEuros: number
}

/** A mapped §12.3 list, ready for the ViewModels: rows and the server's `totalInEuros`. */
export interface SubaccountList {
  items: Subaccount[]
  totalInEuros: number
}

/** Maps one row; unknown currency codes are an API contract break, so it throws. */
export function fromApiSubaccount(json: SubaccountJson): Subaccount {
  if (!isCurrencyCode(json.currency)) {
    throw new Error(`Unknown currency code: ${json.currency}`)
  }
  if (typeof json.isMain !== 'boolean') {
    throw new Error(`Invalid subaccount isMain: expected boolean, got ${typeof json.isMain}`)
  }
  if (!Number.isSafeInteger(json.rateBps)) {
    throw new Error(`Invalid subaccount rateBps: expected safe integer, got ${json.rateBps}`)
  }
  return { id: json.id, code: json.currency, balance: json.balance, isMain: json.isMain, rateBps: json.rateBps }
}

/**
 * Maps the list, dropping rows whose currency is not a known code. `totalInEuros`
 * passes through untouched: the server computes it (§12.1), no screen recomputes it.
 */
export function fromApiSubaccountsList(json: SubaccountsJson | null | undefined): SubaccountList {
  if (json === null || json === undefined) return { items: [], totalInEuros: 0 }
  // A payload without `items` degrades to the empty list, like null/undefined above.
  const rows = Array.isArray(json.items) ? json.items : []
  const items = rows.filter((row) => isCurrencyCode(row.currency)).map(fromApiSubaccount)
  return { items, totalInEuros: json.totalInEuros }
}

/**
 * The server's approximate-total algorithm (§12.1), used by the mock: every row
 * is converted to euro cents and rounded on its own, and only then summed.
 */
export function totalInEurosMinor(subaccounts: readonly { code: CurrencyCode; balance: number }[]): number {
  return subaccounts.reduce((total, subaccount) => {
    return total + eurosFromMinor(subaccount.balance, currencyByCode(subaccount.code).rateBps)
  }, 0)
}

/** One subaccount of the «Canviar» pickers (US-27 View), derived from a `Subaccount`. */
export interface SubaccountOption {
  code: CurrencyCode
  name: string
  balanceMinor: number
  isMain: boolean
}

/** EUR is the main currency (US-25): every account owns it and it holds the main balance. */
export function isMainCurrency(code: CurrencyCode): boolean {
  return code === 'EUR'
}

/** Maps a service `Subaccount` (id, code, balance in minor units) to a picker option. */
export function toSubaccountOption(subaccount: Subaccount): SubaccountOption {
  return {
    code: subaccount.code,
    name: currencyByCode(subaccount.code).name,
    balanceMinor: subaccount.balance,
    isMain: isMainCurrency(subaccount.code),
  }
}
