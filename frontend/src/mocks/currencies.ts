/**
 * In-memory currency sub-accounts (US-25/US-27). This state is the single source of
 * truth for the owned sub-accounts: `./exchange.ts` reads and writes it and keeps
 * nothing of its own.
 */

import {
  fromApiSubaccount,
  isCurrencyCode,
  type CurrencyCode,
  type SubaccountJson,
  type SubaccountsJson,
} from '@/models/currency'
import type { SubaccountJson as CurrencySubaccountJson } from '@/models/exchange'
import { mockBalance, mockError } from './index'
import { onMockUserChange } from './mockUser'

let subaccounts: SubaccountJson[] = []
let nextNumber = 0
startSubaccounts()
onMockUserChange(startSubaccounts)

/**
 * Test seed (US-27): rebuilds the whole state with the owned currencies and their
 * starting balances. EUR is always owned (US-25): it is prepended when missing,
 * and its balance is always read live from `mockBalance()`, so a `balances`
 * entry for EUR is ignored.
 */
export function createCurrenciesState(
  owned: readonly CurrencyCode[] = ['EUR'],
  balances: Partial<Record<CurrencyCode, number>> = {},
): void {
  const codes: CurrencyCode[] = ['EUR', ...owned.filter((code) => code !== 'EUR')]
  let idNumber = 1
  subaccounts = codes.map((code) => ({
    id: subaccountId(idNumber++),
    currency: code,
    balance: code === 'EUR' ? mockBalance() : (balances[code] ?? 0),
  }))
  nextNumber = idNumber
}

/** Every account starts with only the EUR sub-account, with the live balance of the mocks. */
function startSubaccounts(): void {
  createCurrenciesState(['EUR'])
}

/**
 * GET /api/subaccounts (US-25). Copies, so callers cannot change the state.
 * The EUR row is rebuilt on every read with the live balance of the mocks, so a
 * top-up made elsewhere never leaves it stale; the foreign rows keep theirs.
 */
export function mockSubaccounts(): SubaccountsJson {
  return {
    items: subaccounts.map((subaccount) =>
      subaccount.currency === 'EUR'
        ? { ...subaccount, balance: mockBalance() }
        : { ...subaccount },
    ),
  }
}

/**
 * POST /api/subaccounts — same validations, order and errors as the contract (US-25):
 * body format → unknown currency → already owned. An error creates nothing and
 * uses no id.
 */
export function mockAddSubaccount(body: { currency?: unknown }): SubaccountJson {
  const { currency } = body

  if (typeof currency !== 'string') {
    throw mockError('VALIDATION_ERROR', 'Les dades de la petició no són vàlides.')
  }
  if (!isCurrencyCode(currency)) {
    throw mockError('CURRENCY_NOT_SUPPORTED', 'Aquesta divisa no és a la llista de divises disponibles.')
  }
  if (subaccounts.some((subaccount) => subaccount.currency === currency)) {
    throw mockError('CURRENCY_EXISTS', 'Ja tens un subcompte en aquesta divisa.')
  }
  // Defensive: unreachable with the current closed list (max 5 = EUR + 4 foreign).
  if (subaccounts.length >= 5) {
    throw mockError('CURRENCY_EXISTS', 'Ja tens un subcompte en aquesta divisa.')
  }

  const subaccount: SubaccountJson = {
    id: subaccountId(nextNumber++),
    currency,
    balance: 0,
  }
  subaccounts.push(subaccount)
  return { ...subaccount }
}

/** The owned sub-accounts in the shape GET /api/currencies will answer (US-27, issue #166): EUR, the main account, first. */
export function mockGetSubaccounts(): CurrencySubaccountJson[] {
  // The state only ever holds owned, validated codes (factory input + `mockAddSubaccount`
  // narrowing), so `fromApiSubaccount` never throws here: it is the type bridge, not a check.
  return subaccounts.map((subaccount) => ({
    code: fromApiSubaccount(subaccount).code,
    balanceMinor: subaccount.currency === 'EUR' ? mockBalance() : subaccount.balance,
    isMain: subaccount.currency === 'EUR',
  }))
}

/** Stored minor units of one sub-account: the live main balance for EUR, the row for the rest. */
export function mockSubaccountBalance(code: CurrencyCode): number {
  return code === 'EUR' ? mockBalance() : (subaccounts.find((s) => s.currency === code)?.balance ?? 0)
}

/** Writes the stored balance of one sub-account row (never EUR — the main account is read live). */
export function mockSetSubaccountBalance(code: CurrencyCode, balanceMinor: number): void {
  const row = subaccounts.find((s) => s.currency === code)
  if (row === undefined) throw new Error(`No sub-account to write: ${code}`)
  row.balance = balanceMinor
}

/** Same opaque id format as the backend. */
function subaccountId(number: number): string {
  return `sub-${String(number).padStart(2, '0')}`
}
