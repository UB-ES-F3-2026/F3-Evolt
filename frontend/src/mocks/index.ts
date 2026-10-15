/**
 * In-memory mock data, shaped exactly like the API responses in docs/api.md.
 * On by default so the UI works before the backend exists; only an explicit
 * VITE_USE_MOCKS=false turns them off (so no .env copy is needed to run dev).
 */

import type { HomeJson } from '@/models/home'
import type { MovementJson, MovementsPageJson } from '@/models/movement'
import type { TopupJson } from '@/models/topup'

const MOVEMENTS: MovementJson[] = [
  { id: 'mov-20', amount: 2350, concept: 'Restaurant La Plaça', date: '2026-10-11T21:15:00+02:00', type: 'expense', icon: 'food' },
  { id: 'mov-19', amount: 4590, concept: 'Supermercat', date: '2026-10-10T18:42:00+02:00', type: 'expense', icon: 'shopping' },
  { id: 'mov-18', amount: 1200, concept: 'Bitllet de tren', date: '2026-10-09T08:05:00+02:00', type: 'expense', icon: 'transport' },
  { id: 'mov-17', amount: 180000, concept: "Nòmina d'octubre", date: '2026-10-01T09:00:00+02:00', type: 'income', icon: 'salary' },
  { id: 'mov-16', amount: 5000, concept: 'Transferència rebuda', date: '2026-09-28T13:20:00+02:00', type: 'income', icon: 'transfer' },
  { id: 'mov-02', amount: 3999, concept: 'Botiga de roba', date: '2026-09-03T17:10:00+02:00', type: 'expense', icon: 'shopping' },
  { id: 'mov-01', amount: 100000, concept: 'Ingrés inicial', date: '2026-09-01T10:00:00+02:00', type: 'income', icon: 'other' },
]

export function useMocks(): boolean {
  const value = import.meta.env.VITE_USE_MOCKS
  // Missing (no .env copied) → mocks on, so `npm run dev` works out of the box.
  if (value === undefined || value === '') return true
  return String(value).toLowerCase() !== 'false'
}

/** GET /api/home */
export function mockHome(): HomeJson {
  return {
    balance: 125050,
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

/** POST /api/topups — echoes the requested amount like the real 201 response. */
export function mockTopup(amountCents: number): TopupJson {
  return {
    balance: 125050 + amountCents,
    movement: {
      id: `mov-topup-${amountCents}`,
      amount: amountCents,
      concept: 'Recàrrega',
      date: new Date().toISOString(),
      type: 'income',
      icon: 'topup',
    },
  }
}
