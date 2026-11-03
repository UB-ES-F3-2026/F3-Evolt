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
  /** Who pays or gets paid (docs/api.md §10.1). Optional until the backend sends it (T10.2). */
  counterparty?: string | null
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

/** «Tots» in the filters: no `type` sent, so every movement comes back. */
export type MovementTypeFilter = MovementType | 'all'

export const MOVEMENT_TYPE_FILTER_LABELS: Record<MovementTypeFilter, string> = {
  all: 'Tots',
  income: 'Ingressos',
  expense: 'Despeses',
}

/**
 * The filters of «Moviments» (US-10). An empty string means «not chosen», which is
 * what an empty date picker or search box gives. Days are `YYYY-MM-DD`.
 */
export interface MovementFilters {
  dateFrom: string
  dateTo: string
  type: MovementTypeFilter
  search: string
}

export const NO_FILTERS: Readonly<MovementFilters> = { dateFrom: '', dateTo: '', type: 'all', search: '' }

/** Query parameters of GET /api/movements (docs/api.md §10.2). */
export interface MovementsQuery {
  dateFrom?: string
  dateTo?: string
  type?: MovementType
  q?: string
}

/** Only the filters in use are sent; a search of only spaces does not filter (§10.2). */
export function toMovementsQuery(filters: MovementFilters): MovementsQuery {
  const query: MovementsQuery = {}
  if (filters.dateFrom) query.dateFrom = filters.dateFrom
  if (filters.dateTo) query.dateTo = filters.dateTo
  if (filters.type !== 'all') query.type = filters.type
  const text = filters.search.trim()
  if (text) query.q = text
  return query
}

export function hasFilters(filters: MovementFilters): boolean {
  return Object.keys(toMovementsQuery(filters)).length > 0
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
