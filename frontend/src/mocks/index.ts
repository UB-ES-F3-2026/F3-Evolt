/**
 * In-memory mock data, shaped exactly like the API responses in docs/api.md.
 * On by default so the UI works before the backend exists; only an explicit
 * VITE_USE_MOCKS=false turns them off (so no .env copy is needed to run dev).
 */

import type { ApiError } from '@/models/apiError'
import type { HomeJson } from '@/models/home'
import type { MovementJson, MovementsPageJson } from '@/models/movement'
import type { TopupJson } from '@/models/topup'

// Limits from docs/api.md §4.3, in cents.
const MAX_TOPUP = 50000
const DAILY_TOPUP_LIMIT = 100000

const MOVEMENTS: MovementJson[] = [
  { id: 'mov-20', amount: 2350, concept: 'Restaurant La Plaça', date: '2026-10-11T21:15:00+02:00', type: 'expense', icon: 'food' },
  { id: 'mov-19', amount: 4590, concept: 'Supermercat', date: '2026-10-10T18:42:00+02:00', type: 'expense', icon: 'shopping' },
  { id: 'mov-18', amount: 1200, concept: 'Bitllet de tren', date: '2026-10-09T08:05:00+02:00', type: 'expense', icon: 'transport' },
  { id: 'mov-17', amount: 180000, concept: "Nòmina d'octubre", date: '2026-10-01T09:00:00+02:00', type: 'income', icon: 'salary' },
  { id: 'mov-16', amount: 5000, concept: 'Transferència rebuda', date: '2026-09-28T13:20:00+02:00', type: 'income', icon: 'transfer' },
  { id: 'mov-02', amount: 3999, concept: 'Botiga de roba', date: '2026-09-03T17:10:00+02:00', type: 'expense', icon: 'shopping' },
  { id: 'mov-01', amount: 100000, concept: 'Ingrés inicial', date: '2026-09-01T10:00:00+02:00', type: 'income', icon: 'other' },
]

// Mutable so a top-up shows up in later mockHome / mockMovements calls.
let balance = 125050
let topupCounter = 0
let toppedUpToday = 0
let topupDay = new Date().toDateString()

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
    totalSaved: 30000,
    lastMovements: MOVEMENTS.slice(0, 5),
  }
}

/** GET /api/movements?offset=&limit= */
export function mockMovements(offset = 0, limit = 20): MovementsPageJson {
  const items = MOVEMENTS.slice(offset, offset + limit)
  const nextOffset = offset + items.length < MOVEMENTS.length ? offset + items.length : null
  return { items, nextOffset }
}

/** POST /api/topups — same validations, order and errors as docs/api.md §4.3. */
export function mockTopup(amountCents: number): TopupJson {
  const today = new Date().toDateString()
  if (today !== topupDay) {
    topupDay = today
    toppedUpToday = 0
  }

  if (!Number.isInteger(amountCents)) {
    throw mockError('VALIDATION_ERROR', "L'import ha de ser un enter en cèntims.")
  }
  if (amountCents <= 0) {
    throw mockError('INVALID_AMOUNT', "L'import ha de ser més gran que 0.")
  }
  if (amountCents > MAX_TOPUP) {
    throw mockError('AMOUNT_OVER_LIMIT', "L'import màxim per recàrrega és de 500,00 €.")
  }
  if (toppedUpToday + amountCents > DAILY_TOPUP_LIMIT) {
    const remainingToday = Math.max(0, DAILY_TOPUP_LIMIT - toppedUpToday)
    throw mockError(
      'DAILY_LIMIT_EXCEEDED',
      `Has superat el límit diari de recàrrega. Avui encara pots recarregar ${(remainingToday / 100).toFixed(2).replace('.', ',')} €.`,
      { remainingToday },
    )
  }

  const movement: MovementJson = {
    id: `mov-topup-${++topupCounter}`,
    amount: amountCents,
    concept: 'Recàrrega',
    date: new Date().toISOString(),
    type: 'income',
    icon: 'topup',
  }
  balance += amountCents
  toppedUpToday += amountCents
  MOVEMENTS.unshift(movement)
  return { balance, movement }
}

function mockError(code: ApiError['code'], message: string, details?: ApiError['details']): ApiError {
  return details === undefined ? { code, message } : { code, message, details }
}
