/**
 * In-memory currency sub-accounts (US-25/US-27, §12). This state is the single source of
 * truth for the owned sub-accounts: `./exchange.ts` reads and writes it and keeps
 * nothing of its own.
 */

import {
  currencyByCode,
  fromApiSubaccount,
  isCurrencyCode,
  totalInEurosMinor,
  type CurrencyCode,
  type Subaccount,
  type SubaccountList,
} from '@/models/currency'
import { mockBalance, mockError } from './index'
import { onMockUserChange } from './mockUser'
import { messageForCode } from '@/models/errorMessages'

/** One stored row; `isMain` and `rateBps` are derived from the currency at read time. */
interface SubaccountRow {
  id: string
  currency: CurrencyCode
  balance: number
}

let subaccounts: SubaccountRow[] = []
let nextNumber = 0
startSubaccounts()
onMockUserChange(startSubaccounts)

/**
 * Test seed (US-27): rebuilds the whole state with the owned currencies and their
 * starting balances. EUR is always owned (US-25): it is prepended when missing,
 * and its balance is always read live from `mockBalance()`, so a `balances`
 * entry for EUR is ignored.
 *
 * Ids follow §12.2: the EUR row is `main` and never consumes a `sub-` number;
 * the foreign rows are `sub-01, sub-02…` in creation order.
 */
export function createCurrenciesState(
  owned: readonly CurrencyCode[] = ['EUR'],
  balances: Partial<Record<CurrencyCode, number>> = {},
): void {
  const codes: CurrencyCode[] = ['EUR', ...owned.filter((code) => code !== 'EUR')]
  let idNumber = 1
  subaccounts = codes.map((code) => ({
    id: code === 'EUR' ? 'main' : subaccountId(idNumber++),
    currency: code,
    balance: code === 'EUR' ? mockBalance() : (balances[code] ?? 0),
  }))
  nextNumber = idNumber
}

/** Every account starts with only the EUR main account, with the live balance of the mocks. */
function startSubaccounts(): void {
  createCurrenciesState(['EUR'])
}

/**
 * GET /api/subaccounts (§12.3), mapped like `fromApiSubaccountsList` would. Copies,
 * so callers cannot change the state. The EUR row is rebuilt on every read with the
 * live balance of the mocks, so a top-up made elsewhere never leaves it stale; the
 * foreign rows keep theirs. The mock is the server here: it derives `isMain`/`rateBps`
 * from the currency and computes `totalInEuros` with the §12.1 algorithm
 * (`totalInEurosMinor`), so no screen computes a different total.
 */
export function mockSubaccounts(): SubaccountList {
  const items = subaccounts.map((row) =>
    fromApiSubaccount({
      id: row.id,
      currency: row.currency,
      balance: row.currency === 'EUR' ? mockBalance() : row.balance,
      isMain: row.currency === 'EUR',
      rateBps: currencyByCode(row.currency).rateBps,
    }),
  )
  return { items, totalInEuros: totalInEurosMinor(items) }
}

/**
 * POST /api/subaccounts (§12.4) — same validations, order and errors as the contract
 * (US-25): body format → unknown currency → already owned. An error creates nothing
 * and uses no id.
 */
export function mockAddSubaccount(body: { currency?: unknown }): Subaccount {
  const { currency } = body

  if (typeof currency !== 'string') {
    throw mockError('VALIDATION_ERROR', messageForCode('VALIDATION_ERROR'))
  }
  if (!isCurrencyCode(currency)) {
    throw mockError('CURRENCY_NOT_SUPPORTED', messageForCode('CURRENCY_NOT_SUPPORTED'))
  }
  if (subaccounts.some((subaccount) => subaccount.currency === currency)) {
    throw mockError('CURRENCY_EXISTS', messageForCode('CURRENCY_EXISTS'))
  }
  // Defensive: unreachable with the current closed list (max 5 = EUR + 4 foreign).
  if (subaccounts.length >= 5) {
    throw mockError('CURRENCY_EXISTS', 'Ja tens un subcompte en aquesta divisa.')
  }

  const row: SubaccountRow = {
    id: subaccountId(nextNumber++),
    currency,
    balance: 0,
  }
  subaccounts.push(row)
  // The §12.4 `201` body: a fresh sub-account is never the main one and carries the currency's fixed rate.
  return fromApiSubaccount({ ...row, isMain: false, rateBps: currencyByCode(currency).rateBps })
}

/** Writes the stored balance of one sub-account row (never EUR — the main account is read live). */
export function mockSetSubaccountBalance(code: CurrencyCode, balanceMinor: number): void {
  const row = subaccounts.find((s) => s.currency === code)
  if (row === undefined) throw new Error(`No sub-account to write: ${code}`)
  row.balance = balanceMinor
}

/** Same opaque id format as the backend (§12.2): `sub-01`, `sub-02`… */
function subaccountId(number: number): string {
  return `sub-${String(number).padStart(2, '0')}`
}
