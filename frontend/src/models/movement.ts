/**
 * Movement type and mapper: API JSON (docs/api.md §3) → app object.
 *
 * Contract invariants worth remembering:
 * - `amount` is always a positive integer in cents; direction comes from `type`.
 * - `icon` is a closed list; unknown values fall back to `other`.
 */

const ICONS = ['topup', 'salary', 'transfer', 'shopping', 'food', 'transport', 'other'] as const
const TYPES = ['income', 'expense'] as const

export type MovementIcon = (typeof ICONS)[number]
export type MovementType = (typeof TYPES)[number]

export interface Movement {
  id: string
  amount: number
  concept: string
  date: string
  type: MovementType
  icon: MovementIcon
}

/** A movement as the API sends it, before `type` and `icon` are checked. */
export interface MovementJson {
  id: string
  amount: number
  concept: string
  date: string
  type: string
  icon: string
}

/** GET /api/movements page (docs/api.md §4.2). */
export interface MovementsPageJson {
  items: MovementJson[]
  nextOffset: number | null
}

export interface MovementsPage {
  items: Movement[]
  nextOffset: number | null
}

function isOneOf<T extends string>(list: readonly T[], value: string): value is T {
  return (list as readonly string[]).includes(value)
}

export function fromApiMovement(json: MovementJson): Movement {
  return {
    id: json.id,
    amount: json.amount,
    concept: json.concept,
    date: json.date,
    type: isOneOf(TYPES, json.type) ? json.type : 'expense',
    icon: isOneOf(ICONS, json.icon) ? json.icon : 'other',
  }
}

export function fromApiMovements(jsonList: MovementJson[] | null | undefined): Movement[] {
  return (jsonList ?? []).map(fromApiMovement)
}
