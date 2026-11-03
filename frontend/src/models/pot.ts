/**
 * Pot (guardiola) type and mapper: API JSON (docs/api.md §9.1) → app object.
 *
 * Contract invariants worth remembering:
 * - `balance` and `target` are integer cents; `target` is null when the pot has none.
 * - `color` is a closed list; an unknown value falls back to the default one.
 */

export const POT_COLORS = ['purple', 'blue', 'teal', 'orange', 'pink', 'yellow'] as const

export type PotColor = (typeof POT_COLORS)[number]

/** The colour of a pot created without choosing one (docs/api.md §9.3). */
export const DEFAULT_POT_COLOR: PotColor = 'purple'

export interface Pot {
  id: string
  name: string
  balance: number
  target: number | null
  color: PotColor
}

/** A pot as the API sends it, before `color` is checked. */
export interface PotJson {
  id: string
  name: string
  balance: number
  target: number | null
  color: string
}

/** GET /api/pots (docs/api.md §9.2). */
export interface PotsJson {
  items: PotJson[]
}

export function isPotColor(value: string): value is PotColor {
  return (POT_COLORS as readonly string[]).includes(value)
}

export function fromApiPot(json: PotJson): Pot {
  return {
    id: json.id,
    name: json.name,
    balance: json.balance,
    target: json.target ?? null,
    color: isPotColor(json.color) ? json.color : DEFAULT_POT_COLOR,
  }
}

export function fromApiPots(jsonList: PotJson[] | null | undefined): Pot[] {
  return (jsonList ?? []).map(fromApiPot)
}
