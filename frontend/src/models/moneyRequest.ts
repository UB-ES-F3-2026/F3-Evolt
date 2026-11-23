/**
 * Money requests the logged-in person sent (docs/api.md §14).
 *
 * Contract invariants worth remembering:
 * - The frontend never works out the status: it shows the `status` it receives (§14.1).
 * - There is no «Cancel·lada»: cancelling deletes the request (§14.4).
 * - Amounts are integer cents up to 1.000.000,00 €; the concept has 1 to 140 characters.
 */

import { formatCents } from './money'
import { fromApiUser, type UserSummary, type UserSummaryJson } from './user'

export const MONEY_REQUEST_STATUSES = ['pending', 'paid', 'rejected', 'expired'] as const
export type MoneyRequestStatus = (typeof MONEY_REQUEST_STATUSES)[number]

/** The label of each status (US-15). In this sprint only «Pendent» and «Caducada» can happen. */
export const MONEY_REQUEST_STATUS_LABELS: Record<MoneyRequestStatus, string> = {
  pending: 'Pendent',
  paid: 'Pagada',
  rejected: 'Rebutjada',
  expired: 'Caducada',
}

/** Most that can be asked for in one request: 1.000.000,00 € (docs/api.md §14.2). */
export const MAX_REQUEST_CENTS = 100000000
/** Longest concept (docs/api.md §14.2). */
export const MAX_REQUEST_CONCEPT_LENGTH = 140

export interface MoneyRequest {
  id: string
  to: UserSummary
  amount: number
  concept: string
  status: MoneyRequestStatus
  createdAt: string
  expiresAt: string
}

export interface MoneyRequestJson {
  id: string
  to: UserSummaryJson
  amount: number
  concept: string
  status: string
  createdAt: string
  expiresAt: string
}

/** GET /api/money-requests. */
export interface MoneyRequestsJson {
  items: MoneyRequestJson[]
}

/** POST /api/money-requests body. */
export interface NewMoneyRequest {
  toUserId: string
  amount: number
  concept: string
}

function isStatus(value: string): value is MoneyRequestStatus {
  return (MONEY_REQUEST_STATUSES as readonly string[]).includes(value)
}

export function fromApiMoneyRequest(json: MoneyRequestJson): MoneyRequest {
  return {
    id: json.id,
    to: fromApiUser(json.to),
    amount: json.amount,
    concept: json.concept,
    // An unknown status is safest shown as still pending: it can be cancelled and the server decides.
    status: isStatus(json.status) ? json.status : 'pending',
    createdAt: json.createdAt,
    expiresAt: json.expiresAt,
  }
}

export function fromApiMoneyRequests(jsonList: MoneyRequestJson[] | null | undefined): MoneyRequest[] {
  return (jsonList ?? []).map(fromApiMoneyRequest)
}

/** «L'import màxim és d'1.000.000,00 €.», the text of «Demanar diners» for AMOUNT_OVER_LIMIT (§14.7). */
export const REQUEST_AMOUNT_OVER_LIMIT_MESSAGE = `L'import màxim és d'${formatCents(MAX_REQUEST_CENTS)}.`
