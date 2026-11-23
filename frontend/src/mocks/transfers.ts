/**
 * Sending money, shaped exactly like docs/api.md §13.4 and §13.5. Only the sender's side
 * lives here: the other users' accounts are not in the mocks.
 */

import { MAX_TRANSFER_CONCEPT_LENGTH, type TransferJson, type TransferLimit } from '@/models/transfer'
import { mockBalance, mockError, recordAccountMovement } from './index'
import { madridDayKey } from './madridTime'
import { mockCurrentUser, onMockUserChange } from './mockUser'
import { mockUser, mockUserIdByEmail } from './users'

/** 1.000,00 € a day (docs/api.md §13.5); the screens read it from `mockTransferLimit`. */
const DAILY_LIMIT = 100000

let sent: { at: number; amount: number }[] = []
onMockUserChange(() => {
  sent = []
})

/** GET /api/transfers/limit — what can still be sent today, never below 0. */
export function mockTransferLimit(now: Date = new Date()): TransferLimit {
  return { dailyLimit: DAILY_LIMIT, remainingToday: Math.max(0, DAILY_LIMIT - sentOn(madridDayKey(now))) }
}

/**
 * POST /api/transfers — validations in the order of §13.4: body format → RECIPIENT_NOT_FOUND →
 * SELF_TRANSFER → INVALID_AMOUNT → INSUFFICIENT_BALANCE → TRANSFER_LIMIT_EXCEEDED. Nothing
 * changes until all of them pass.
 */
export function mockSendTransfer(
  body: { toUserId?: unknown; amount?: unknown; concept?: unknown },
  currentEmail: string | null = mockCurrentUser(),
): TransferJson {
  const { toUserId, amount, concept = null } = body
  if (
    typeof toUserId !== 'string' ||
    typeof amount !== 'number' ||
    !Number.isInteger(amount) ||
    (concept !== null && (typeof concept !== 'string' || concept.trim().length > MAX_TRANSFER_CONCEPT_LENGTH))
  ) {
    throw mockError('VALIDATION_ERROR', 'Les dades de la petició no són vàlides.')
  }
  const recipient = mockUser(toUserId)
  if (toUserId === mockUserIdByEmail(currentEmail)) {
    throw mockError('SELF_TRANSFER', 'No et pots enviar diners a tu mateix.')
  }
  if (amount <= 0) throw mockError('INVALID_AMOUNT', "L'import ha de ser més gran que 0.")
  if (amount > mockBalance()) throw mockError('INSUFFICIENT_BALANCE', 'No tens prou saldo.')
  const now = new Date()
  const { remainingToday } = mockTransferLimit(now)
  if (amount > remainingToday) {
    throw mockError('TRANSFER_LIMIT_EXCEEDED', "Has superat el límit diari d'enviament.", { remainingToday })
  }

  const cleaned = typeof concept === 'string' && concept.trim() !== '' ? concept.trim() : 'Transferència enviada'
  const { balance, movement } = recordAccountMovement(cleaned, 'expense', 'transfer', amount, now)
  sent.push({ at: now.getTime(), amount })
  return { balance, movement, recipient }
}

function sentOn(dayKey: string): number {
  return sent.filter(({ at }) => madridDayKey(new Date(at)) === dayKey).reduce((sum, { amount }) => sum + amount, 0)
}
