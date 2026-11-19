/**
 * Pot (guardiola) type and mapper: API JSON (docs/api.md §9.1) → app object.
 *
 * Contract invariants worth remembering:
 * - `balance` and `target` are integer cents; `target` is null when the pot has none.
 * - `color` is a closed list; an unknown value falls back to the default one.
 */

import type { ApiErrorCode } from './apiError'
import { AMOUNT_FORMAT_MESSAGE, messageForCode } from './errorMessages'
import { eurosToCents } from './money'
import { fromApiMovement, type Movement, type MovementJson, type MovementType } from './movement'

export const POT_COLORS = ['purple', 'blue', 'teal', 'orange', 'pink', 'yellow'] as const

export type PotColor = (typeof POT_COLORS)[number]

/** The colour of a pot created without choosing one (docs/api.md §9.3). */
export const DEFAULT_POT_COLOR: PotColor = 'purple'

/** How each colour is named to the person (screen readers and the colour picker). */
export const POT_COLOR_LABELS: Record<PotColor, string> = {
  purple: 'Lila',
  blue: 'Blau',
  teal: 'Turquesa',
  orange: 'Taronja',
  pink: 'Rosa',
  yellow: 'Groc',
}

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

/** POST /api/pots body (docs/api.md §9.3). `target` in cents, null for a pot without one. */
export interface CreatePotRequest {
  name: string
  target: number | null
  color: PotColor
}

/**
 * One entry of a pot's history (docs/api.md §9.5). `type` is seen from the pot:
 * a contribution brings money in, so it is `income` here and `expense` in the main account.
 */
export interface PotMovement {
  id: string
  amount: number
  concept: string
  date: string
  type: MovementType
}

export interface PotMovementJson {
  id: string
  amount: number
  concept: string
  date: string
  type: string
}

/** GET /api/pots/{potId}/movements (docs/api.md §9.5). */
export interface PotMovementsJson {
  items: PotMovementJson[]
}

/** POST /api/pots/{potId}/contributions answer (docs/api.md §9.4): both new balances and the new movement. */
export interface ContributionJson {
  balance: number
  pot: PotJson
  movement: MovementJson
}

export interface Contribution {
  balance: number
  pot: Pot
  movement: Movement
}

/** POST /api/pots/{potId}/withdrawals answer (docs/api.md §11.2): the same shape as a contribution. */
export type WithdrawalJson = ContributionJson
export type Withdrawal = Contribution

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

export function fromApiPotMovements(jsonList: PotMovementJson[] | null | undefined): PotMovement[] {
  return (jsonList ?? []).map((json) => ({
    id: json.id,
    amount: json.amount,
    concept: json.concept,
    date: json.date,
    type: json.type === 'expense' ? 'expense' : 'income',
  }))
}

export function fromApiContribution(json: ContributionJson): Contribution {
  return { balance: json.balance, pot: fromApiPot(json.pot), movement: fromApiMovement(json.movement) }
}

export const fromApiWithdrawal: (json: WithdrawalJson) => Withdrawal = fromApiContribution

/**
 * Why an amount typed in euros cannot move between the account and a pot, or null if it can.
 * The backend owns these rules (docs/api.md §9.4 and §11.2); the screens repeat them only to
 * answer before sending. `limit` is the most that can move (the main balance to contribute,
 * the pot balance to withdraw), null while it is unknown; going over it reads as `overLimit`.
 * An empty field is not an error yet: the button just stays disabled.
 */
export function potAmountError(typed: string, limit: number | null, overLimit: ApiErrorCode): string | null {
  const text = typed.trim()
  if (text === '') return null
  // eurosToCents only reads digits, so a minus sign would read as a format error: US-18 asks for this text.
  if (text.startsWith('-')) return messageForCode('INVALID_AMOUNT')
  const cents = eurosToCents(text)
  if (cents === null) return AMOUNT_FORMAT_MESSAGE
  if (cents <= 0) return messageForCode('INVALID_AMOUNT')
  if (limit !== null && cents > limit) return messageForCode(overLimit)
  return null
}

/** A history entry drawn with the same row as the account movements, with the pot icon. */
export function potMovementAsMovement(entry: PotMovement): Movement {
  return { ...entry, icon: 'savings' }
}
