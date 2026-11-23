/**
 * In-memory currency sub-accounts (US-25 and US-26). Every account owns EUR; the foreign ones start empty.
 * Same ids as the backend (docs/api.md §12.2): the main euro account is `main`,
 * and the foreign sub-accounts are `sub-01`, `sub-02`… in creation order.
 */

import {
  MAIN_SUBACCOUNT_ID,
  isCurrencyCode,
  type DeleteSubaccountJson,
  type SubaccountJson,
  type SubaccountMovement,
  type SubaccountMovementsJson,
  type SubaccountsJson,
} from '@/models/currency'
import { mockBalance, mockError } from './index'
import { onMockUserChange } from './mockUser'

interface StoredMovement {
  subaccountId: string
  entry: SubaccountMovement
  /** Creation order, for the tie-break when two dates are equal (P4). */
  seq: number
}

let subaccounts: SubaccountJson[] = []
let nextNumber = 1
// Kept when a sub-account is deleted (§12.11): only the route stops showing them.
let history: StoredMovement[] = []
let nextMovementNumber = 1
startSubaccounts()
onMockUserChange(startSubaccounts)

/** Every account starts with only the main EUR account, with the live balance of the mocks. */
function startSubaccounts(): void {
  subaccounts = [{ id: MAIN_SUBACCOUNT_ID, currency: 'EUR', balance: mockBalance() }]
  nextNumber = 1
  history = []
  nextMovementNumber = 1
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

/**
 * POST /api/subaccounts/{subaccountId}/delete (US-26, docs/api.md §12.5), in the
 * contract's order: the main account → not deletable, whatever its balance;
 * unknown → not found; any balance but exactly 0 → not empty.
 * Only the sub-account goes: its history stays stored, and the currency can be added again.
 */
export function mockDeleteSubaccount(subaccountIdToDelete: string): DeleteSubaccountJson {
  if (subaccountIdToDelete === MAIN_SUBACCOUNT_ID) {
    throw mockError('MAIN_ACCOUNT_NOT_DELETABLE', 'El compte en euros no es pot eliminar.')
  }
  const index = subaccounts.findIndex((subaccount) => subaccount.id === subaccountIdToDelete)
  if (index === -1) {
    throw mockError('SUBACCOUNT_NOT_FOUND', "No s'ha trobat el subcompte.")
  }
  if (subaccounts[index].balance !== 0) {
    throw mockError('SUBACCOUNT_NOT_EMPTY', 'Només pots eliminar un subcompte amb saldo 0.')
  }
  subaccounts.splice(index, 1)
  return { status: 'ok' }
}

/**
 * GET /api/subaccounts/{subaccountId}/movements (US-26, docs/api.md §12.6): newest
 * first, and the later one first on a tie (P4). Only for foreign sub-accounts:
 * `main`, an unknown id or a deleted one → not found.
 */
export function mockSubaccountMovements(subaccountIdToRead: string): SubaccountMovementsJson {
  const exists = subaccounts.some(
    (subaccount) => subaccount.id === subaccountIdToRead && subaccount.id !== MAIN_SUBACCOUNT_ID,
  )
  if (!exists) {
    throw mockError('SUBACCOUNT_NOT_FOUND', "No s'ha trobat el subcompte.")
  }
  const items = history
    .filter((stored) => stored.subaccountId === subaccountIdToRead)
    .sort((a, b) => Date.parse(b.entry.date) - Date.parse(a.entry.date) || b.seq - a.seq)
    .map((stored) => ({ ...stored.entry }))
  return { items }
}

/**
 * Without «Aportar» (#189) and before the exchange (US-27), no API call puts money
 * in a sub-account. Tests (and anyone trying the screens with the mocks) use this
 * to stand in for an exchange: it sets the balance and records the entry.
 */
export function mockRecordSubaccountMovement(
  subaccountIdToChange: string,
  entry: Omit<SubaccountMovement, 'id'>,
): SubaccountMovement {
  const subaccount = subaccounts.find((candidate) => candidate.id === subaccountIdToChange)
  if (subaccount === undefined || subaccount.id === MAIN_SUBACCOUNT_ID) {
    throw new Error(`Not a foreign sub-account: ${subaccountIdToChange}`)
  }
  const balance = subaccount.balance + (entry.type === 'income' ? entry.amount : -entry.amount)
  if (balance < 0) throw new Error('A sub-account never goes below 0')
  subaccount.balance = balance
  const stored: StoredMovement = {
    subaccountId: subaccount.id,
    entry: { id: `smov-${String(nextMovementNumber).padStart(2, '0')}`, ...entry },
    seq: nextMovementNumber,
  }
  nextMovementNumber += 1
  history.push(stored)
  return { ...stored.entry }
}

/** Same opaque id format as the backend. */
function subaccountId(number: number): string {
  return `sub-${String(number).padStart(2, '0')}`
}
