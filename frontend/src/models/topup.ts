/** POST /api/topups types (docs/api.md §4.3). Amounts in cents. */

import type { Movement, MovementJson } from './movement'

export interface TopupJson {
  balance: number
  movement: MovementJson
}

export interface TopupResult {
  balance: number
  movement: Movement
}
