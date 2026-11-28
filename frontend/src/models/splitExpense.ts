/**
 * Split expenses (docs/api.md §17): one money request per participant, with a common concept (US-30).
 *
 * Contract invariants worth remembering:
 * - The screen works out the parts, also with «Parts iguals», and sends them all (§17.2).
 * - My part (`myShare`) makes no request; it still has to be more than 0 (P101).
 * - The frontend never works out `status`, `paidCount` or `pendingAmount`: it shows what it gets (§17.1).
 */

import { MONEY_REQUEST_STATUSES, type MoneyRequestStatus } from './moneyRequest'
import { fromApiUser, type UserSummary, type UserSummaryJson } from './user'

/** At most 9 participants besides me: 10 people (US-30, §17.2). */
export const MAX_SPLIT_PARTICIPANTS = 9

export const SPLIT_EXPENSE_STATUSES = ['pending', 'completed', 'closed'] as const
export type SplitExpenseStatus = (typeof SPLIT_EXPENSE_STATUSES)[number]

export interface SplitPart {
  requestId: string
  to: UserSummary
  amount: number
  status: MoneyRequestStatus
}

export interface SplitExpense {
  id: string
  concept: string
  total: number
  myShare: number
  createdAt: string
  status: SplitExpenseStatus
  people: number
  paidCount: number
  pendingAmount: number
  parts: SplitPart[]
}

export interface SplitPartJson {
  requestId: string
  to: UserSummaryJson
  amount: number
  status: string
}

export interface SplitExpenseJson {
  id: string
  concept: string
  total: number
  myShare: number
  createdAt: string
  status: string
  people: number
  paidCount: number
  pendingAmount: number
  parts: SplitPartJson[]
}

/** POST /api/split-expenses body (§17.2). Amounts in cents. */
export interface NewSplitExpense {
  concept: string
  total: number
  myShare: number
  parts: { toUserId: string; amount: number }[]
}

/**
 * «Parts iguals» (§17.2): each participant gets the total divided by everyone, rounded down,
 * and the cents left over are mine. 6000 among 3 and me → 1500 each; 10000 among 2 and me → 3333 and 3334 for me.
 */
export function equalShares(total: number, participants: number): { each: number; mine: number } {
  const each = Math.floor(total / (participants + 1))
  return { each, mine: total - each * participants }
}

function isOneOf<T extends string>(values: readonly T[], value: string): value is T {
  return (values as readonly string[]).includes(value)
}

// An unknown status is safest shown as still pending, as with a single request.
function toPartStatus(value: string): MoneyRequestStatus {
  return isOneOf(MONEY_REQUEST_STATUSES, value) ? value : 'pending'
}

function toSplitStatus(value: string): SplitExpenseStatus {
  return isOneOf(SPLIT_EXPENSE_STATUSES, value) ? value : 'pending'
}

export function fromApiSplitExpense(json: SplitExpenseJson): SplitExpense {
  return {
    id: json.id,
    concept: json.concept,
    total: json.total,
    myShare: json.myShare,
    createdAt: json.createdAt,
    status: toSplitStatus(json.status),
    people: json.people,
    paidCount: json.paidCount,
    pendingAmount: json.pendingAmount,
    parts: json.parts.map((part) => ({
      requestId: part.requestId,
      to: fromApiUser(part.to),
      amount: part.amount,
      status: toPartStatus(part.status),
    })),
  }
}
