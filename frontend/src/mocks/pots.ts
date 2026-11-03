/**
 * In-memory pots, shaped exactly like docs/api.md §9. The demo user starts with
 * the 3 pots of ./seed.ts and the empty user with none, as with the backend.
 */

import { DEFAULT_POT_COLOR, isPotColor, type PotColor, type PotJson, type PotsJson } from '@/models/pot'
import { mockError } from './index'
import { DEMO_POTS, IS_EMPTY_USER } from './seed'

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

/** Same opaque id format as the backend (P21). */
function potId(number: number): string {
  return `pot-${String(number).padStart(2, '0')}`
}
