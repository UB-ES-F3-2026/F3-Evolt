/** GET /api/home types (docs/api.md §4.1). Amounts in cents. */

import type { Movement, MovementJson } from './movement'

export interface HomeJson {
  balance: number
  totalSaved: number
  lastMovements: MovementJson[]
}

export interface Home {
  balance: number
  totalSaved: number
  lastMovements: Movement[]
}
