/**
 * In-memory mock data, shaped exactly like the API responses in docs/api.md.
 * Used when VITE_USE_MOCKS=true so the UI works before the backend exists.
 */

const MOVEMENTS = [
  { id: 'mov-20', amount: 2350, concept: 'Restaurant La Plaça', date: '2026-10-11T21:15:00+02:00', type: 'expense', icon: 'food' },
  { id: 'mov-19', amount: 4590, concept: 'Supermercat', date: '2026-10-10T18:42:00+02:00', type: 'expense', icon: 'shopping' },
  { id: 'mov-18', amount: 1200, concept: 'Bitllet de tren', date: '2026-10-09T08:05:00+02:00', type: 'expense', icon: 'transport' },
  { id: 'mov-17', amount: 180000, concept: "Nòmina d'octubre", date: '2026-10-01T09:00:00+02:00', type: 'income', icon: 'salary' },
  { id: 'mov-16', amount: 5000, concept: 'Transferència rebuda', date: '2026-09-28T13:20:00+02:00', type: 'income', icon: 'transfer' },
  { id: 'mov-02', amount: 3999, concept: 'Botiga de roba', date: '2026-09-03T17:10:00+02:00', type: 'expense', icon: 'shopping' },
  { id: 'mov-01', amount: 100000, concept: 'Ingrés inicial', date: '2026-09-01T10:00:00+02:00', type: 'income', icon: 'other' },
]

export function useMocks() {
  return import.meta.env.VITE_USE_MOCKS === 'true'
}

/** GET /api/home */
export function mockHome() {
  return {
    balance: 125050,
    totalSaved: 30000,
    lastMovements: MOVEMENTS.slice(0, 5),
  }
}

/** GET /api/movements?offset=&limit= */
export function mockMovements(offset = 0, limit = 20) {
  const items = MOVEMENTS.slice(offset, offset + limit)
  const nextOffset = offset + items.length < MOVEMENTS.length ? offset + items.length : null
  return { items, nextOffset }
}

/** POST /api/topups — echoes the requested amount like the real 201 response. */
export function mockTopup(amountCents) {
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
