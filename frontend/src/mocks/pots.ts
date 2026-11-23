/**
 * In-memory pots, shaped exactly like docs/api.md §9. The demo user starts with
 * the 3 pots of ./seed.ts and any other account with none, as with the backend.
 *
 * US-20 (issue #150): like the backend, every pot that leaves the mocks carries
 * the goal progress fields `percentage` and `goalStatus` of §11.1.
 */

import {
  DEFAULT_POT_COLOR,
  isPotColor,
  type ContributionJson,
  type GoalStatus,
  type PotColor,
  type PotJson,
  type PotMovementJson,
  type PotMovementsJson,
  type PotsJson,
  type WithdrawalJson,
} from '@/models/pot'
import { mockBalance, mockError, recordAccountMovement } from './index'
import { madridDaysAgoAt, toContractDate } from './madridTime'
import { mockCurrentUser, onMockUserChange } from './mockUser'
import { DEMO_POTS, hasDemoData } from './seed'

interface StoredPotMovement {
  potId: string
  json: PotMovementJson
  /** Instant in ms and creation order, to sort newest first with the P4 tie-break. */
  at: number
  seq: number
}

let pots: PotJson[] = []
let nextNumber = 0
let history: StoredPotMovement[] = []
let nextEntryNumber = 0
startPots()
onMockUserChange(startPots)

/** A pot as the backend sends it since US-20 (issue #150): with its goal progress. */
type PotJsonWithProgress = PotJson & { percentage: number | null; goalStatus: GoalStatus | null }

/**
 * US-20 (issue #150): the mock plays the backend, so the goal progress rule
 * lives here (docs/api.md §11.1). Round half-up, but below the target the
 * number never shows 100 % (79,99 € of 80,00 € → 99); from the target on the
 * real value stands (100 at equality, more above). No goal → both null.
 */
function goalProgressOf(
  balance: number,
  target: number | null,
): { percentage: number | null; goalStatus: GoalStatus | null } {
  if (target === null || target <= 0) {
    return { percentage: null, goalStatus: null }
  }
  // Half-up, never banker's rounding: 62,5 % of 8000 is 63, not 62.
  const rounded = Math.floor((balance * 100) / target + 0.5)
  if (balance >= target) {
    return { percentage: rounded, goalStatus: 'achieved' }
  }
  // Below the target a full bar would say «assolit»: 79,99 € of 80,00 € is 99, not 100.
  return { percentage: Math.min(99, rounded), goalStatus: 'in_progress' }
}

/** A pot as the backend sends it since US-20 (issue #150): with its goal progress. */
function withProgress(pot: PotJson): PotJsonWithProgress {
  return { ...pot, ...goalProgressOf(pot.balance, pot.target) }
}

/** The pots of whoever is logged in: the seed ones for the demo user, none for anyone else. */
function startPots(): void {
  pots = hasDemoData(mockCurrentUser())
    ? DEMO_POTS.map(([name, balance, target, color], index) => ({
        id: potId(index + 1),
        name,
        balance,
        target,
        color,
      }))
    : []
  nextNumber = DEMO_POTS.length + 1
  // Each seed pot starts with one «Saldo inicial» entry for its balance, before today (P32).
  history = pots.map((pot, index) =>
    toStoredEntry(index + 1, pot.id, madridDaysAgoAt(new Date(), 30, '10:00'), 'Saldo inicial', pot.balance),
  )
  nextEntryNumber = history.length + 1
}

/** GET /api/pots — in creation order (P23). Copies, so callers cannot change the state. */
export function mockPots(): PotsJson {
  return { items: pots.map((pot) => withProgress(pot)) }
}

/** `totalSaved` of GET /api/home: the sum of every pot's balance (docs/api.md §4.1). */
export function mockTotalSaved(): number {
  return pots.reduce((sum, pot) => sum + pot.balance, 0)
}

/**
 * POST /api/pots — same validations, order and errors as docs/api.md §9.3 (P26):
 * body format → INVALID_POT_NAME → INVALID_TARGET. An error creates nothing and
 * uses no id.
 */
export function mockCreatePot(body: { name?: unknown; target?: unknown; color?: unknown }): PotJson {
  const { name, target = null, color = null } = body

  if (typeof name !== 'string' || !isTargetFormat(target) || !isColorFormat(color)) {
    throw mockError('VALIDATION_ERROR', 'Les dades de la petició no són vàlides.')
  }
  if (name.trim() === '') {
    throw mockError('INVALID_POT_NAME', 'El nom de la guardiola no pot estar buit.')
  }
  if (target !== null && target <= 0) {
    throw mockError('INVALID_TARGET', "L'objectiu ha de ser més gran que 0.")
  }

  const pot: PotJson = {
    id: potId(nextNumber++),
    name: name.trim(),
    balance: 0,
    target,
    color: color ?? DEFAULT_POT_COLOR,
  }
  pots.push(pot)
  return withProgress(pot)
}

/** A strict JSON integer, or nothing: `"300"` and `300.5` are format errors (P5). */
function isTargetFormat(value: unknown): value is number | null {
  return value === null || (typeof value === 'number' && Number.isInteger(value))
}

function isColorFormat(value: unknown): value is PotColor | null {
  return value === null || (typeof value === 'string' && isPotColor(value))
}

/** GET /api/pots/{potId}/movements — newest first, created later first on equal dates (P31, P4). */
export function mockPotMovements(potId: string): PotMovementsJson {
  findPot(potId)
  return {
    items: history
      .filter((entry) => entry.potId === potId)
      .sort((a, b) => b.at - a.at || b.seq - a.seq)
      .map(({ json }) => ({ ...json })),
  }
}

/**
 * POST /api/pots/{potId}/contributions — validations in the order of docs/api.md §9.4 (P28):
 * body format → POT_NOT_FOUND → INVALID_AMOUNT → INSUFFICIENT_BALANCE. All or nothing:
 * the four writes (account balance, pot balance, account movement, pot history) only
 * happen once everything is valid.
 */
export function mockContribute(potId: string, body: { amount?: unknown }): ContributionJson {
  const { amount } = body
  if (typeof amount !== 'number' || !Number.isInteger(amount)) {
    throw mockError('VALIDATION_ERROR', 'Les dades de la petició no són vàlides.')
  }
  const pot = findPot(potId)
  if (amount <= 0) {
    throw mockError('INVALID_AMOUNT', "L'import ha de ser més gran que 0.")
  }
  if (amount > mockBalance()) {
    throw mockError('INSUFFICIENT_BALANCE', 'No tens prou saldo.')
  }

  const now = new Date()
  const { balance, movement } = recordAccountMovement(`Aportació a ${pot.name}`, 'expense', 'savings', amount, now)
  pot.balance += amount
  history.push(toStoredEntry(nextEntryNumber++, pot.id, now, 'Aportació', amount))
  // US-20 (issue #150): the contribution answer carries the pot's fresh progress.
  return { balance, pot: withProgress(pot), movement }
}

/**
 * POST /api/pots/{potId}/withdrawals — the inverse of a contribution, with the order of
 * docs/api.md §11.2: body format → POT_NOT_FOUND → INVALID_AMOUNT → INSUFFICIENT_POT_BALANCE.
 * All or nothing, as in §9.4. The account gets «Retirada de <nom>» as income and the pot
 * history «Retirada» as expense.
 */
export function mockWithdraw(potId: string, body: { amount?: unknown }): WithdrawalJson {
  const { amount } = body
  if (typeof amount !== 'number' || !Number.isInteger(amount)) {
    throw mockError('VALIDATION_ERROR', 'Les dades de la petició no són vàlides.')
  }
  const pot = findPot(potId)
  if (amount <= 0) {
    throw mockError('INVALID_AMOUNT', "L'import ha de ser més gran que 0.")
  }
  if (amount > pot.balance) {
    throw mockError('INSUFFICIENT_POT_BALANCE', 'La guardiola no té prou saldo per aquesta retirada.')
  }

  const now = new Date()
  const { balance, movement } = recordAccountMovement(`Retirada de ${pot.name}`, 'income', 'savings', amount, now)
  pot.balance -= amount
  history.push(toStoredEntry(nextEntryNumber++, pot.id, now, 'Retirada', amount, 'expense'))
  return { balance, pot: { ...pot }, movement }
}

/** A pot that does not exist gets the same answer as one of another user (§9.4). */
function findPot(potId: string): PotJson {
  const pot = pots.find((candidate) => candidate.id === potId)
  if (pot === undefined) throw mockError('POT_NOT_FOUND', "No s'ha trobat la guardiola.")
  return pot
}

/** `type` is seen from the pot: money in is income, a withdrawal is expense (§9.5, §11.3). */
function toStoredEntry(
  number: number,
  potId: string,
  at: Date,
  concept: string,
  amount: number,
  type: PotMovementJson['type'] = 'income',
): StoredPotMovement {
  const date = toContractDate(at)
  return {
    potId,
    json: { id: `pmov-${String(number).padStart(2, '0')}`, amount, concept, date, type },
    at: Date.parse(date),
    seq: number,
  }
}

/** Same opaque id format as the backend (P21). */
function potId(number: number): string {
  return `pot-${String(number).padStart(2, '0')}`
}
