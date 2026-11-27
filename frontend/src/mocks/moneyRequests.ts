/**
 * Money requests, shaped exactly like docs/api.md §14 and §15. The demo user starts with the two
 * requests of the seed it sent (§14.8): one expired to Huabin and one pending to Alicia; and the four
 * it received (§15.8), one in each status. A new request is `req-07`, as in the backend.
 */

import {
  MAX_REQUEST_CENTS,
  MAX_REQUEST_CONCEPT_LENGTH,
  type MoneyRequestJson,
  type MoneyRequestsJson,
  type MoneyRequestStatus,
  type ReceivedMoneyRequestJson,
  type ReceivedMoneyRequestsJson,
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
}

/** A request someone sent to the logged-in person. `paid` and `rejected` are saved; `expired` never is (§15.5). */
interface StoredReceivedRequest {
  id: string
  fromUserId: string
  amount: number
  concept: string
  savedStatus: Exclude<MoneyRequestStatus, 'expired'>
  at: number
  seq: number
}

let requests: StoredRequest[] = []
let receivedRequests: StoredReceivedRequest[] = []
let nextNumber = 1
startRequests()
onMockUserChange(startRequests)

/** The seed of §14.8 and §15.8 for the demo user; nobody else has any. */
function startRequests(now: Date = new Date()): void {
  const demo = hasDemoData(mockCurrentUser())
  requests = demo
    ? [
        stored(1, 'usr-04', 4200, 'Pizza del diumenge', madridDaysAgoAt(now, 9, '21:15')),
        stored(2, 'usr-03', 2500, 'El sopar de divendres', madridDaysAgoAt(now, 1, '19:30')),
      ]
    : []
  // The paid one has no movement, so the demo balance does not change (P92).
  receivedRequests = demo
    ? [
        storedReceived(3, 'usr-06', 4200, 'Entrades del concert', 'pending', madridDaysAgoAt(now, 11, '21:15')),
        storedReceived(4, 'usr-05', 1800, "Taxi de l'aeroport", 'rejected', madridDaysAgoAt(now, 5, '08:10')),
        storedReceived(5, 'usr-07', 1200, 'Cafès de la setmana', 'paid', madridDaysAgoAt(now, 4, '10:05')),
        storedReceived(6, 'usr-03', 2500, 'El sopar de divendres', 'pending', madridDaysAgoAt(now, 2, '19:30')),
      ]
    : []
  // The ids are shared by sent and received requests, as in the backend: the next one is req-07.
  nextNumber = 7
}

/** GET /api/money-requests — newest first; the status is worked out now (§14.5). */
export function mockMoneyRequests(now: Date = new Date()): MoneyRequestsJson {
  return { items: [...requests].sort((a, b) => b.at - a.at || b.seq - a.seq).map((request) => toJson(request, now)) }
}

/** GET /api/money-requests/received — every status, newest first; `expired` is worked out now (§15.2). */
export function mockReceivedMoneyRequests(now: Date = new Date()): ReceivedMoneyRequestsJson {
  return {
    items: [...receivedRequests].sort((a, b) => b.at - a.at || b.seq - a.seq).map((request) => toReceivedJson(request, now)),
  }
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
  const request = requests.find((candidate) => candidate.id === requestId)
  if (request === undefined) throw mockError('REQUEST_NOT_FOUND', 'Aquesta sol·licitud ja no existeix.')
  if (toJson(request, now).status !== 'pending') {
    throw mockError('REQUEST_NOT_PENDING', 'Només es poden cancel·lar les sol·licituds pendents.')
  }
  requests = requests.filter((candidate) => candidate !== request)
  return { status: 'ok' }
}

function requestId(number: number): string {
  return `req-${String(number).padStart(2, '0')}`
}

function stored(number: number, toUserId: string, amount: number, concept: string, at: Date): StoredRequest {
  return { id: requestId(number), toUserId, amount, concept, at: at.getTime(), seq: number }
}

function storedReceived(
  number: number,
  fromUserId: string,
  amount: number,
  concept: string,
  savedStatus: StoredReceivedRequest['savedStatus'],
  at: Date,
): StoredReceivedRequest {
  return { id: requestId(number), fromUserId, amount, concept, savedStatus, at: at.getTime(), seq: number }
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

function toReceivedJson(request: StoredReceivedRequest, now: Date): ReceivedMoneyRequestJson {
  const created = new Date(request.at)
  const expires = expiresAt(created)
  // Only a pending one expires; a paid or rejected one never does (§15.5).
  const expired = request.savedStatus === 'pending' && now.getTime() >= expires.getTime()
  return {
    id: request.id,
    from: mockUser(request.fromUserId),
    amount: request.amount,
    concept: request.concept,
    status: expired ? 'expired' : request.savedStatus,
    createdAt: toContractDate(created),
    expiresAt: toContractDate(expires),
  }
}
