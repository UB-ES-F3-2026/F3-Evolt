/** POST /api/topups types (docs/api.md §4.3). Amounts in cents. */

import type { Movement, MovementJson } from './movement'

// The backend enforces it (docs/api.md §1); the frontend repeats it to warn before sending.
export const MAX_TOPUP_CENTS = 50000

export interface TopupJson {
  balance: number
  movement: MovementJson
}

export interface TopupResult {
  balance: number
  movement: Movement
}
