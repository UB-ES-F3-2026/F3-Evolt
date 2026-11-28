/**
 * Money requests, shaped exactly like docs/api.md §14. The demo user starts with the two
 * requests of the seed (§14.8): one expired to Huabin and one pending to Alicia.
 */

import {
  MAX_REQUEST_CENTS,
  MAX_REQUEST_CONCEPT_LENGTH,
  type MoneyRequestJson,
  type MoneyRequestsJson,
} from '@/models/moneyRequest'
import { mockError } from './index'
import { madridDaysAgoAt, toContractDate } from './madridTime'
import { mockCurrentUser, onMockUserChange } from './mockUser'
import { mockUser, mockUserIdByEmail } from './users'
import { hasDemoData } from './seed'

interface StoredRequest {
  id: string
  toUserId: string
  amount: number
  concept: string
  /** Instant in ms and creation order, to sort newest first with the P4 tie-break. */
  at: number
  seq: number
  /** The split expense it belongs to (§17.6): such requests only show inside it. */
  splitId: string | null
}

let requests: StoredRequest[] = []
let nextNumber = 1
startRequests()
onMockUserChange(startRequests)

/** The seed of §14.8 for the demo user; nobody else has any. */
function startRequests(now: Date = new Date()): void {
  requests = hasDemoData(mockCurrentUser())
    ? [
        stored(1, 'usr-04', 4200, 'Pizza del diumenge', madridDaysAgoAt(now, 9, '21:15')),
        stored(2, 'usr-03', 2500, 'El sopar de divendres', madridDaysAgoAt(now, 1, '19:30')),
      ]
    : []
  nextNumber = 3
}

/** GET /api/money-requests — newest first; the status is worked out now (§14.5). */
export function mockMoneyRequests(now: Date = new Date()): MoneyRequestsJson {
  // The parts of a split expense are not listed on their own (§17.6, P104).
  const single = requests.filter((request) => request.splitId === null)
  return { items: single.sort((a, b) => b.at - a.at || b.seq - a.seq).map((request) => toJson(request, now)) }
}

/**
 * The requests of a split expense, one per participant, as POST /api/split-expenses creates them (§17.2):
 * the same concept and date for all. The caller has already checked the body, so nothing here fails.
 */
export function mockAddSplitRequests(
  splitId: string,
  concept: string,
  parts: { toUserId: string; amount: number }[],
  at: Date,
): MoneyRequestJson[] {
  const created = parts.map((part) => ({ ...stored(nextNumber++, part.toUserId, part.amount, concept, at), splitId }))
  requests.push(...created)
  return created.map((request) => toJson(request, at))
}

/**
 * POST /api/money-requests — validations in the order of §14.2: body format → RECIPIENT_NOT_FOUND →
 * SELF_REQUEST → INVALID_AMOUNT → AMOUNT_OVER_LIMIT → INVALID_CONCEPT. Nothing is saved on an error.
 */
export function mockCreateMoneyRequest(
  body: { toUserId?: unknown; amount?: unknown; concept?: unknown },
  currentEmail: string | null = mockCurrentUser(),
): MoneyRequestJson {
  const { toUserId, amount, concept } = body
  if (typeof toUserId !== 'string' || typeof amount !== 'number' || !Number.isInteger(amount) || typeof concept !== 'string') {
    throw mockError('VALIDATION_ERROR', 'Les dades de la petició no són vàlides.')
  }
  mockUser(toUserId)
  if (toUserId === mockUserIdByEmail(currentEmail)) {
    throw mockError('SELF_REQUEST', 'No et pots demanar diners a tu mateix.')
  }
  if (amount <= 0) throw mockError('INVALID_AMOUNT', "L'import ha de ser més gran que 0.")
  if (amount > MAX_REQUEST_CENTS) throw mockError('AMOUNT_OVER_LIMIT', "L'import màxim és d'1.000.000,00 €.")
  const cleaned = concept.trim()
  if (cleaned === '' || cleaned.length > MAX_REQUEST_CONCEPT_LENGTH) {
    throw mockError('INVALID_CONCEPT', 'El concepte ha de tenir entre 1 i 140 caràcters.')
  }

  const now = new Date()
  const request = stored(nextNumber++, toUserId, amount, cleaned, now)
  requests.push(request)
  return toJson(request, now)
}

/**
 * POST /api/money-requests/{requestId}/cancel — deletes a pending request (§14.4).
 * REQUEST_NOT_FOUND when it is not there; REQUEST_NOT_PENDING when it already expired.
 */
export function mockCancelMoneyRequest(requestId: string, now: Date = new Date()): { status: 'ok' } {
  // A part of a split expense cannot be cancelled: it reads as not there (§17.6, P105).
  const request = requests.find((candidate) => candidate.id === requestId && candidate.splitId === null)
  if (request === undefined) throw mockError('REQUEST_NOT_FOUND', 'Aquesta sol·licitud ja no existeix.')
  if (toJson(request, now).status !== 'pending') {
    throw mockError('REQUEST_NOT_PENDING', 'Només es poden cancel·lar les sol·licituds pendents.')
  }
  requests = requests.filter((candidate) => candidate !== request)
  return { status: 'ok' }
}

function stored(number: number, toUserId: string, amount: number, concept: string, at: Date): StoredRequest {
  return {
    id: `req-${String(number).padStart(2, '0')}`,
    toUserId,
    amount,
    concept,
    at: at.getTime(),
    seq: number,
    splitId: null,
  }
}

/** 00:00 Madrid of the seventh day after the day it was created: from then it reads «Caducada» (§14.5). */
function expiresAt(createdAt: Date): Date {
  return madridDaysAgoAt(createdAt, -7, '00:00')
}

function toJson(request: StoredRequest, now: Date): MoneyRequestJson {
  const created = new Date(request.at)
  const expires = expiresAt(created)
  return {
    id: request.id,
    to: mockUser(request.toUserId),
    amount: request.amount,
    concept: request.concept,
    status: now.getTime() >= expires.getTime() ? 'expired' : 'pending',
    createdAt: toContractDate(created),
    expiresAt: toContractDate(expires),
  }
}
