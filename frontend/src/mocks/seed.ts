/**
 * Mock copy of backend/app/data/seed.py (T07.3). Keep both files in sync, so
 * the app looks the same with mocks on and with the real backend.
 *
 * - Demo user (1): 30 movements and 3 pots. The balance is the signed sum of
 *   the movements, as in the seed.
 * - Empty user (2): no movements, no pots, balance 0.
 */

import type { MovementIcon, MovementType } from '@/models/movement'

/** `X-User-Id` value of the user with an empty account (docs/api.md §2). */
export const EMPTY_USER_ID = '2'

/** [days ago, "HH:MM" in Madrid, concept, type, icon, amount in cents] */
export type SeedMovement = readonly [number, string, string, MovementType, MovementIcon, number]

// Oldest to newest, like `_USER1_MOVEMENTS`: the position gives id and creation order.
// Times avoid 02:00–03:00, which is ambiguous on the day the clocks change.
export const DEMO_MOVEMENTS: readonly SeedMovement[] = [
  [40, '10:00', 'Ingrés inicial', 'income', 'other', 100000],
  [38, '17:10', 'Botiga de roba', 'expense', 'shopping', 3999],
  [36, '09:00', 'Nòmina', 'income', 'salary', 180000],
  [35, '08:05', 'Abonament de transport', 'expense', 'transport', 2220],
  [34, '13:30', 'Menú del dia', 'expense', 'food', 1350],
  [32, '18:42', 'Supermercat', 'expense', 'shopping', 5230],
  [30, '20:15', 'Recàrrega', 'income', 'topup', 20000],
  [29, '21:00', 'Restaurant La Plaça', 'expense', 'food', 3480],
  [27, '13:20', 'Transferència rebuda', 'income', 'transfer', 5000],
  [26, '11:00', 'Lloguer', 'expense', 'transfer', 65000],
  [24, '19:05', 'Farmàcia', 'expense', 'other', 1475],
  [22, '08:30', 'Bitllet de tren', 'expense', 'transport', 1200],
  [21, '18:10', 'Supermercat', 'expense', 'shopping', 4590],
  [19, '14:00', 'Cafeteria', 'expense', 'food', 420],
  [17, '12:45', 'Llibreria', 'expense', 'shopping', 2495],
  [15, '10:30', 'Recàrrega', 'income', 'topup', 15000],
  [13, '09:00', 'Nòmina', 'income', 'salary', 180000],
  [12, '16:20', 'Transferència enviada', 'expense', 'transfer', 2500],
  [11, '21:30', 'Sopar amb amics', 'expense', 'food', 2750],
  [10, '08:10', 'Taxi', 'expense', 'transport', 1890],
  [9, '18:00', 'Gimnàs', 'expense', 'other', 3990],
  [8, '13:15', 'Menú del dia', 'expense', 'food', 1350],
  [7, '17:40', 'Supermercat', 'expense', 'shopping', 6120],
  [6, '11:00', 'Bizum rebut', 'income', 'transfer', 1500],
  [5, '20:30', 'Cinema', 'expense', 'other', 950],
  [4, '08:05', 'Bitllet de tren', 'expense', 'transport', 1200],
  [3, '19:25', 'Fruiteria', 'expense', 'food', 1830],
  // Same date on purpose, to test the tie-break (P4): "Bizum enviat" goes first.
  [2, '18:42', 'Supermercat', 'expense', 'shopping', 4590],
  [2, '18:42', 'Bizum enviat', 'expense', 'transfer', 1000],
  [1, '21:15', 'Restaurant La Plaça', 'expense', 'food', 2350],
]

/** Sum of the demo user's pots: Vacances 15000 + Emergències 10000 + Regal d'aniversari 5000. */
export const DEMO_TOTAL_SAVED = 30000
