/**
 * In-memory pots, shaped exactly like docs/api.md §9. The demo user starts with
 * the 3 pots of ./seed.ts and the empty user with none, as with the backend.
 */

import {
  DEFAULT_POT_COLOR,
  isPotColor,
  type ContributionJson,
  type PotColor,
  type PotJson,
  type PotMovementJson,
  type PotMovementsJson,
  type PotsJson,
} from '@/models/pot'
import { mockBalance, mockError, recordAccountMovement } from './index'
import { madridDaysAgoAt, toContractDate } from './madridTime'
import { DEMO_POTS, IS_EMPTY_USER } from './seed'

interface StoredPotMovement {
  potId: string
  json: PotMovementJson
  /** Instant in ms and creation order, to sort newest first with the P4 tie-break. */
  at: number
  seq: number
}

const pots: PotJson[] = IS_EMPTY_USER
  ? []
  : DEMO_POTS.map(([name, balance, target, color], index) => ({
      id: potId(index + 1),
      name,
      balance,
      target,
      color,
    }))

let nextNumber = DEMO_POTS.length + 1

// Each seed pot starts with one «Saldo inicial» entry for its balance, before today (P32).
const history: StoredPotMovement[] = pots.map((pot, index) =>
  toStoredEntry(index + 1, pot.id, madridDaysAgoAt(new Date(), 30, '10:00'), 'Saldo inicial', pot.balance),
)
let nextEntryNumber = history.length + 1

/** GET /api/pots — in creation order (P23). Copies, so callers cannot change the state. */
export function mockPots(): PotsJson {
  return { items: pots.map((pot) => ({ ...pot })) }
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
  return { ...pot }
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
    throw mockError('INSUFFICIENT_BALANCE', 'No tens prou saldo per fer aquesta aportació.')
  }

  const now = new Date()
  const { balance, movement } = recordAccountMovement(`Aportació a ${pot.name}`, 'expense', 'savings', amount, now)
  pot.balance += amount
  history.push(toStoredEntry(nextEntryNumber++, pot.id, now, 'Aportació', amount))
  return { balance, pot: { ...pot }, movement }
}

/** A pot that does not exist gets the same answer as one of another user (§9.4). */
function findPot(potId: string): PotJson {
  const pot = pots.find((candidate) => candidate.id === potId)
  if (pot === undefined) throw mockError('POT_NOT_FOUND', "No s'ha trobat la guardiola.")
  return pot
}

function toStoredEntry(number: number, potId: string, at: Date, concept: string, amount: number): StoredPotMovement {
  const date = toContractDate(at)
  return {
    potId,
    // Every entry brings money into the pot, so it is income seen from the pot (§9.5).
    json: { id: `pmov-${String(number).padStart(2, '0')}`, amount, concept, date, type: 'income' },
    at: Date.parse(date),
    seq: number,
  }
}

/** Same opaque id format as the backend (P21). */
function potId(number: number): string {
  return `pot-${String(number).padStart(2, '0')}`
}
