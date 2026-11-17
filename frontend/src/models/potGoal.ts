/**
 * Goal progress of a pot: percentage and status, as `goalStatus` names it in
 * the contract (docs/api.md §9.1).
 *
 * The backend computes the percentage (issue #150); until those fields exist,
 * the same rule is repeated here locally (round half-up). The API value always
 * wins when present.
 */

import type { Pot } from './pot'

/** State of a pot's goal, as goalStatus names it in the contract (docs/api.md §9.1). */
export type GoalStatus = 'in_progress' | 'achieved'

// TODO(a crear): camps percentage/goalStatus del backend — issue #150

/** Raw calculation (backend rule): round half-up. Exported for the mocks. */
export function computePercentage(balance: number, target: number): number {
  return Math.floor((balance * 100) / target + 0.5)
}

/**
 * Goal state from the balance alone (backend rule): achieved at equality, in
 * progress below. Null when the pot has no goal (target null or <= 0). Shared
 * with the mocks, so the rule is written once.
 */
export function goalStatusFor(balance: number, target: number | null): GoalStatus | null {
  if (target === null || target <= 0) {
    return null
  }
  return balance >= target ? 'achieved' : 'in_progress'
}

/** Percentage to display: API value when present, else local rule. Null when no goal. */
export function potPercentage(pot: Pot): number | null {
  if (pot.target === null || pot.target <= 0) {
    return null
  }
  return pot.percentage ?? computePercentage(pot.balance, pot.target)
}

/** Goal state: API value when present, else balance >= target. Null when no goal. */
export function potGoalStatus(pot: Pot): GoalStatus | null {
  if (pot.target === null || pot.target <= 0) {
    return null
  }
  if (pot.goalStatus !== undefined && pot.goalStatus !== null) {
    return pot.goalStatus === 'achieved' ? 'achieved' : 'in_progress'
  }
  return goalStatusFor(pot.balance, pot.target)
}
