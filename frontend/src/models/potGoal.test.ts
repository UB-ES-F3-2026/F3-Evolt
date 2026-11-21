import { describe, expect, it } from 'vitest'
import type { Pot } from './pot'
import { computePercentage, goalStatusFor, potGoalStatus, potPercentage } from './potGoal'

function potFixture(overrides: Partial<Pot>): Pot {
  return { id: 'pot-01', name: 'Vacances', balance: 15000, target: 100000, color: 'blue', ...overrides }
}

describe('computePercentage', () => {
  it('gives 0% for an empty pot', () => {
    expect(computePercentage(0, 100000)).toBe(0)
  })

  it('gives 15% at 15000 of 100000 cents', () => {
    expect(computePercentage(15000, 100000)).toBe(15)
  })

  it('gives 100% when the balance reaches the target', () => {
    expect(computePercentage(100000, 100000)).toBe(100)
  })

  it('goes above 100% when the balance passes the target', () => {
    expect(computePercentage(115000, 100000)).toBe(115)
  })

  it('rounds half-up (62.5% becomes 63)', () => {
    expect(computePercentage(625, 1000)).toBe(63)
  })
})

describe('goalStatusFor', () => {
  it('is null when there is no goal', () => {
    expect(goalStatusFor(15000, null)).toBeNull()
  })

  it('is null when the target is zero', () => {
    expect(goalStatusFor(15000, 0)).toBeNull()
  })

  it('is achieved at equality with the target', () => {
    expect(goalStatusFor(100000, 100000)).toBe('achieved')
  })

  it('is in progress below the target', () => {
    expect(goalStatusFor(15000, 100000)).toBe('in_progress')
  })
})

describe('potPercentage', () => {
  it('is null when the pot has no goal', () => {
    expect(potPercentage(potFixture({ target: null }))).toBeNull()
  })

  it('is null when the target is zero', () => {
    expect(potPercentage(potFixture({ target: 0 }))).toBeNull()
  })

  it('prefers the percentage computed by the API', () => {
    expect(potPercentage(potFixture({ percentage: 42 }))).toBe(42)
  })

  it('falls back to the local rule when the API field is missing', () => {
    expect(potPercentage(potFixture({}))).toBe(15)
  })
})

describe('potGoalStatus', () => {
  it('is null when the pot has no goal', () => {
    expect(potGoalStatus(potFixture({ target: null }))).toBeNull()
  })

  it('is null when the target is zero', () => {
    expect(potGoalStatus(potFixture({ target: 0 }))).toBeNull()
  })

  it('is achieved when the balance equals the target', () => {
    expect(potGoalStatus(potFixture({ balance: 100000 }))).toBe('achieved')
  })

  it('is in progress below the target', () => {
    expect(potGoalStatus(potFixture({}))).toBe('in_progress')
  })

  it('prefers the status computed by the API', () => {
    expect(potGoalStatus(potFixture({ goalStatus: 'achieved' }))).toBe('achieved')
  })

  it('narrows an unknown API status to in progress', () => {
    expect(potGoalStatus(potFixture({ goalStatus: 'done' }))).toBe('in_progress')
  })
})
