/**
 * In-memory pots, shaped exactly like docs/api.md §9. The demo user starts with
 * the 3 pots of ./seed.ts and the empty user with none, as with the backend.
 */

import type { PotJson, PotsJson } from '@/models/pot'
import { DEMO_POTS, IS_EMPTY_USER } from './seed'

const pots: PotJson[] = IS_EMPTY_USER
  ? []
  : DEMO_POTS.map(([name, balance, target, color], index) => ({
      id: potId(index + 1),
      name,
      balance,
      target,
      color,
    }))

/** GET /api/pots — in creation order (P23). Copies, so callers cannot change the state. */
export function mockPots(): PotsJson {
  return { items: pots.map((pot) => ({ ...pot })) }
}

/** `totalSaved` of GET /api/home: the sum of every pot's balance (docs/api.md §4.1). */
export function mockTotalSaved(): number {
  return pots.reduce((sum, pot) => sum + pot.balance, 0)
}

/** Same opaque id format as the backend (P21). */
function potId(number: number): string {
  return `pot-${String(number).padStart(2, '0')}`
}
