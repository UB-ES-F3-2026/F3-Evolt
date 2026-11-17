/**
 * In-memory currency sub-accounts (US-25). Every account owns EUR; the foreign ones start empty.
 */

import { isCurrencyCode, type SubaccountJson, type SubaccountsJson } from '@/models/currency'
import { mockBalance, mockError } from './index'
import { onMockUserChange } from './mockUser'

let subaccounts: SubaccountJson[] = []
let nextNumber = 0
startSubaccounts()
onMockUserChange(startSubaccounts)

/** Every account starts with only the EUR sub-account, with the live balance of the mocks. */
function startSubaccounts(): void {
  subaccounts = [{ id: subaccountId(1), currency: 'EUR', balance: mockBalance() }]
  nextNumber = 2
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

/** Same opaque id format as the backend. */
function subaccountId(number: number): string {
  return `sub-${String(number).padStart(2, '0')}`
}
