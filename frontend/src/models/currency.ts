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
export function isCurrencyCode(value: unknown): value is CurrencyCode {
  return CURRENCIES.some((currency) => currency.code === value)
}

/** `true` for the euro code: the main account, the only one that is not a sub-account (§12.2). */
export function isMainCurrency(code: CurrencyCode): boolean {
  return code === 'EUR'
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

/** A sub-account ready to be listed in a picker (US-27): its code, its name and its balance. */
export interface SubaccountOption {
  code: CurrencyCode
  name: string
  balanceMinor: number
}

/** Adds the display fields of a picker row: the currency name and the balance in minor units. */
export function toSubaccountOption(subaccount: Subaccount): SubaccountOption {
  return {
    code: subaccount.code,
    name: currencyByCode(subaccount.code).name,
    balanceMinor: subaccount.balance,
  }
}

/** A subaccount as the API sends it, before `currency` is checked. */
export interface SubaccountJson {
  id: string
  currency: string
  balance: number
}

/** GET /api/subaccounts (docs/api.md §12.3): the rows plus the server-computed total. */
export interface SubaccountsJson {
  items: SubaccountJson[]
  totalInEuros: number
}

/** A mapped §12.3 list: the rows plus the server-computed total, in euro cents. */
export interface SubaccountList {
  items: Subaccount[]
  totalInEuros: number
}

/** The id of the main euro account in every multi-currency answer (docs/api.md §12.2). */
export const MAIN_SUBACCOUNT_ID = 'main'

/**
 * One entry of a currency sub-account's history (US-26, docs/api.md §12.6).
 * `amount` is in the minor unit of the sub-account's currency, always > 0;
 * `type` says whether money came in or went out of the sub-account.
 */
export interface SubaccountMovement {
  id: string
  amount: number
  concept: string
  date: string
  type: 'income' | 'expense'
}

/** GET /api/subaccounts/{subaccountId}/movements (docs/api.md §12.6). */
export interface SubaccountMovementsJson {
  items: SubaccountMovement[]
}

/** POST /api/subaccounts/{subaccountId}/delete (docs/api.md §12.5). */
export interface DeleteSubaccountJson {
  status: 'ok'
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
 * Maps a §12.3 list: the rows through `fromApiSubaccounts`, and `totalInEuros`
 * passes through untouched — the server computes it (§12.3), no screen recomputes it.
 */
export function fromApiSubaccountsList(json: SubaccountsJson | null | undefined): SubaccountList {
  if (json === null || json === undefined) return { items: [], totalInEuros: 0 }
  return { items: fromApiSubaccounts(json.items), totalInEuros: json.totalInEuros }
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
