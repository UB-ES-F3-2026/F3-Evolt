/**
 * Sending money to another user (docs/api.md §13.4 and §13.5).
 *
 * Contract invariants worth remembering:
 * - Amounts are integer cents; the concept is optional and at most 140 characters.
 * - The daily limit comes from `GET /api/transfers/limit`: the frontend never writes it down.
 * - The server checks balance and limit again when sending, whatever the screen showed.
 */

import { messageForCode } from './errorMessages'
import { formatCents } from './money'
import { fromApiMovement, type Movement, type MovementJson } from './movement'
import { fromApiUser, type UserSummary, type UserSummaryJson } from './user'

/** Longest concept the API accepts (docs/api.md §13.4). */
export const MAX_TRANSFER_CONCEPT_LENGTH = 140

/** POST /api/transfers body. `concept` is null when the person wrote none. */
export interface TransferRequest {
  toUserId: string
  amount: number
  concept: string | null
}

/** POST /api/transfers answer: the sender's new balance, their movement and who got the money. */
export interface TransferJson {
  balance: number
  movement: MovementJson
  recipient: UserSummaryJson
}

export interface Transfer {
  balance: number
  movement: Movement
  recipient: UserSummary
}

/** GET /api/transfers/limit: the daily limit and what can still be sent today, in cents. */
export interface TransferLimit {
  dailyLimit: number
  remainingToday: number
}

export function fromApiTransfer(json: TransferJson): Transfer {
  return { balance: json.balance, movement: fromApiMovement(json.movement), recipient: fromApiUser(json.recipient) }
}

/** An empty or blank concept is the same as none (docs/api.md §13.4). */
export function cleanConcept(concept: string): string | null {
  const trimmed = concept.trim()
  return trimmed === '' ? null : trimmed
}

/** «Has superat el límit diari de 1.000,00 €.», exactly as US-14 writes it. */
export function transferLimitMessage(dailyLimit: number): string {
  return `Has superat el límit diari de ${formatCents(dailyLimit)}.`
}

/**
 * Why an amount cannot be sent yet, or null: more than the balance, or more than what is
 * left of today's limit (US-14). An empty or zero amount has no message: «Continuar» just
 * stays disabled. The server checks both again when sending.
 */
export function transferAmountError(cents: number | null, balance: number, limit: TransferLimit): string | null {
  if (cents === null || cents <= 0) return null
  if (cents > balance) return messageForCode('INSUFFICIENT_BALANCE')
  if (cents > limit.remainingToday) return transferLimitMessage(limit.dailyLimit)
  return null
}

// What the keypad lets the amount become: digits, at most one comma and 2 decimals.
const MAX_WHOLE_DIGITS = 7
const KEYPAD_AMOUNT = new RegExp(`^(0|[1-9]\\d{0,${MAX_WHOLE_DIGITS - 1}})(,\\d{0,2})?$`)

/**
 * The amount after one key of the numeric keypad: a digit, «,» or «⌫» (backspace).
 * A key that would make a wrong amount (a second comma, a third decimal) is ignored.
 */
export function pressAmountKey(amount: string, key: string): string {
  if (key === '⌫') return amount.slice(0, -1)
  if (key === ',' && amount === '') return '0,'
  const next = amount === '0' && /\d/.test(key) ? key : amount + key
  return KEYPAD_AMOUNT.test(next) ? next : amount
}
