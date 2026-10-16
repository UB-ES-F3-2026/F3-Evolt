/**
 * In-memory mock data, shaped exactly like the API responses in docs/api.md.
 * The data copies the backend seed (see ./seed.ts) and `VITE_DEMO_USER=2`
 * gives the empty user, like the `X-User-Id` header does with the backend.
 * On by default so the UI works before the backend exists; only an explicit
 * VITE_USE_MOCKS=false turns them off (so no .env copy is needed to run dev).
 */

import type { ApiError } from '@/models/apiError'
import type { HomeJson } from '@/models/home'
import type { MovementJson, MovementsPageJson } from '@/models/movement'
import type { TopupJson } from '@/models/topup'
import { madridDayKey, madridDaysAgoAt, toContractDate } from './madridTime'
import { DEMO_MOVEMENTS, DEMO_TOTAL_SAVED, EMPTY_USER_ID } from './seed'

// Limits from docs/api.md §4.3, in cents.
const MAX_TOPUP = 50000
const DAILY_TOPUP_LIMIT = 100000
const LAST_MOVEMENTS = 5

interface StoredMovement {
  json: MovementJson
  /** Instant in ms, to sort and to find today's top-ups. */
  at: number
  /** Creation order, for the tie-break when two dates are equal (P4). */
  seq: number
}

// One user per `npm run dev` run, so a single in-memory state is enough.
const isEmptyUser = (import.meta.env.VITE_DEMO_USER ?? '1') === EMPTY_USER_ID

const movements: StoredMovement[] = isEmptyUser ? [] : buildDemoMovements(new Date())
let balance = movements.reduce((sum, { json }) => sum + signedAmount(json), 0)
const totalSaved = isEmptyUser ? 0 : DEMO_TOTAL_SAVED
let nextNumber = DEMO_MOVEMENTS.length + 1

export function useMocks(): boolean {
  const value = import.meta.env.VITE_USE_MOCKS
  // Missing (no .env copied) → mocks on, so `npm run dev` works out of the box.
  if (value === undefined || value === '') return true
  return String(value).toLowerCase() !== 'false'
}

/** GET /api/home */
export function mockHome(): HomeJson {
  return {
    balance,
    totalSaved,
    lastMovements: sortedMovements().slice(0, LAST_MOVEMENTS),
  }
}

/** GET /api/movements?offset=&limit= */
export function mockMovements(offset = 0, limit = 20): MovementsPageJson {
  const all = sortedMovements()
  const items = all.slice(offset, offset + limit)
  const nextOffset = offset + items.length < all.length ? offset + items.length : null
  return { items, nextOffset }
}

/** POST /api/topups — same validations, order and errors as docs/api.md §4.3. */
export function mockTopup(amountCents: number): TopupJson {
  const now = new Date()

  if (!Number.isInteger(amountCents)) {
    throw mockError('VALIDATION_ERROR', "L'import ha de ser un enter en cèntims.")
  }
  if (amountCents <= 0) {
    throw mockError('INVALID_AMOUNT', "L'import ha de ser més gran que 0.")
  }
  if (amountCents > MAX_TOPUP) {
    throw mockError('AMOUNT_OVER_LIMIT', "L'import màxim per recàrrega és de 500,00 €.")
  }
  const toppedUpToday = toppedUpOn(madridDayKey(now))
  if (toppedUpToday + amountCents > DAILY_TOPUP_LIMIT) {
    const remainingToday = Math.max(0, DAILY_TOPUP_LIMIT - toppedUpToday)
    throw mockError(
      'DAILY_LIMIT_EXCEEDED',
      `Has superat el límit diari de recàrrega. Avui encara pots recarregar ${(remainingToday / 100).toFixed(2).replace('.', ',')} €.`,
      { remainingToday },
    )
  }

  const stored = toStored(nextNumber++, now, 'Recàrrega', 'income', 'topup', amountCents)
  balance += amountCents
  movements.push(stored)
  return { balance, movement: { ...stored.json } }
}

function buildDemoMovements(now: Date): StoredMovement[] {
  return DEMO_MOVEMENTS.map(([daysAgo, hhmm, concept, type, icon, amount], index) =>
    toStored(index + 1, madridDaysAgoAt(now, daysAgo, hhmm), concept, type, icon, amount),
  )
}

function toStored(
  number: number,
  at: Date,
  concept: string,
  type: MovementJson['type'],
  icon: MovementJson['icon'],
  amount: number,
): StoredMovement {
  const date = toContractDate(at)
  return {
    // Same opaque id format as `movement_id()` in seed.py.
    json: { id: `mov-${String(number).padStart(2, '0')}`, amount, concept, date, type, icon },
    at: Date.parse(date),
    seq: number,
  }
}

/** Newest first; equal dates → the one created later first (docs/api.md §4.2, P4). Copies. */
function sortedMovements(): MovementJson[] {
  return [...movements]
    .sort((a, b) => b.at - a.at || b.seq - a.seq)
    .map(({ json }) => ({ ...json }))
}

/** Sum of the top-ups made on a Madrid calendar day (the backend uses `kind == "topup"`). */
function toppedUpOn(dayKey: string): number {
  return movements
    .filter(({ json, at }) => json.icon === 'topup' && madridDayKey(new Date(at)) === dayKey)
    .reduce((sum, { json }) => sum + json.amount, 0)
}

function signedAmount(movement: MovementJson): number {
  return movement.type === 'income' ? movement.amount : -movement.amount
}

function mockError(code: ApiError['code'], message: string, details?: ApiError['details']): ApiError {
  return details === undefined ? { code, message } : { code, message, details }
}
