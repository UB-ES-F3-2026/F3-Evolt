/**
 * Split expenses, shaped exactly like docs/api.md §17. Nobody has one in the seed; each one is a group
 * of money requests kept in ./moneyRequests.ts, so they are not listed on their own (§17.6).
 */

import { MAX_REQUEST_CENTS, MAX_REQUEST_CONCEPT_LENGTH, type MoneyRequestJson } from '@/models/moneyRequest'
import { MAX_SPLIT_PARTICIPANTS, type SplitExpenseJson } from '@/models/splitExpense'
import { mockError } from './index'
import { toContractDate } from './madridTime'
import { mockAddSplitRequests } from './moneyRequests'
import { mockCurrentUser, onMockUserChange } from './mockUser'
import { mockUser, mockUserIdByEmail } from './users'

let nextNumber = 1
onMockUserChange(() => {
  nextNumber = 1
})

interface SplitBody {
  concept?: unknown
  total?: unknown
  myShare?: unknown
  parts?: unknown
}

interface Part {
  toUserId: string
  amount: number
}

/**
 * POST /api/split-expenses — validations in the order of §17.2: body format → RECIPIENT_NOT_FOUND →
 * SELF_REQUEST → INVALID_AMOUNT → AMOUNT_OVER_LIMIT → INVALID_CONCEPT → INVALID_SHARE → SHARES_DO_NOT_MATCH.
 * All or nothing: on an error no request is created.
 */
export function mockCreateSplitExpense(body: SplitBody, currentEmail: string | null = mockCurrentUser()): SplitExpenseJson {
  const { concept, total, myShare } = body
  const parts = validParts(body.parts)
  if (typeof concept !== 'string' || !isInteger(total) || !isInteger(myShare) || parts === null) {
    throw mockError('VALIDATION_ERROR', 'Les dades de la petició no són vàlides.')
  }
  parts.forEach((part) => mockUser(part.toUserId))
  if (parts.some((part) => part.toUserId === mockUserIdByEmail(currentEmail))) {
    throw mockError('SELF_REQUEST', 'No et pots demanar diners a tu mateix.')
  }
  if (total <= 0) throw mockError('INVALID_AMOUNT', "L'import ha de ser més gran que 0.")
  if (total > MAX_REQUEST_CENTS) throw mockError('AMOUNT_OVER_LIMIT', "L'import màxim és d'1.000.000,00 €.")
  const cleaned = concept.trim()
  if (cleaned === '' || cleaned.length > MAX_REQUEST_CONCEPT_LENGTH) {
    throw mockError('INVALID_CONCEPT', 'El concepte ha de tenir entre 1 i 140 caràcters.')
  }
  if (myShare <= 0 || parts.some((part) => part.amount <= 0)) {
    throw mockError('INVALID_SHARE', 'Cada part ha de ser més gran que 0.')
  }
  if (myShare + parts.reduce((sum, part) => sum + part.amount, 0) !== total) {
    throw mockError('SHARES_DO_NOT_MATCH', 'La suma de les parts ha de ser igual al total.')
  }

  const id = `split-${String(nextNumber++).padStart(2, '0')}`
  const now = new Date()
  const requests = mockAddSplitRequests(id, cleaned, parts, now)
  return toJson(id, cleaned, total, myShare, now, requests)
}

/** 1 to 9 parts `{ toUserId, amount }`, no participant twice; null when the list is not that. */
function validParts(value: unknown): Part[] | null {
  if (!Array.isArray(value) || value.length === 0 || value.length > MAX_SPLIT_PARTICIPANTS) return null
  const parts: Part[] = []
  for (const item of value as unknown[]) {
    if (typeof item !== 'object' || item === null) return null
    const { toUserId, amount } = item as Record<string, unknown>
    if (typeof toUserId !== 'string' || !isInteger(amount)) return null
    if (parts.some((part) => part.toUserId === toUserId)) return null
    parts.push({ toUserId, amount })
  }
  return parts
}

function isInteger(value: unknown): value is number {
  return typeof value === 'number' && Number.isInteger(value)
}

// Just created, every part is pending: nobody has paid yet (§17.2).
function toJson(
  id: string,
  concept: string,
  total: number,
  myShare: number,
  createdAt: Date,
  requests: MoneyRequestJson[],
): SplitExpenseJson {
  return {
    id,
    concept,
    total,
    myShare,
    createdAt: toContractDate(createdAt),
    status: 'pending',
    people: requests.length + 1,
    paidCount: 0,
    pendingAmount: requests.reduce((sum, request) => sum + request.amount, 0),
    parts: requests.map((request) => ({ requestId: request.id, to: request.to, amount: request.amount, status: request.status })),
  }
}
