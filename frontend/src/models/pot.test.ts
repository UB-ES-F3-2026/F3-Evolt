import { describe, expect, it } from 'vitest'
import { DEFAULT_POT_COLOR, fromApiPot, fromApiPots, type PotJson } from './pot'

describe('fromApiPot', () => {
  it('keeps the fields of the contract', () => {
    const json = { id: 'pot-01', name: 'Vacances', balance: 15000, target: 100000, color: 'blue' }

    expect(fromApiPot(json)).toEqual(json)
  })

  it('keeps a pot without target as null', () => {
    expect(fromApiPot({ id: 'pot-02', name: 'Fons', balance: 0, target: null, color: 'teal' }).target).toBeNull()
  })

  it('falls back to the default colour when an unknown one arrives', () => {
    const pot = fromApiPot({ id: 'pot-03', name: 'Regal', balance: 5000, target: 8000, color: 'red' })

    expect(pot.color).toBe(DEFAULT_POT_COLOR)
  })

  it('keeps the goal progress fields of US-20 when the API sends them', () => {
    const pot = fromApiPot({
      id: 'pot-04',
      name: 'Vacances',
      balance: 42000,
      target: 100000,
      color: 'blue',
      percentage: 42,
      goalStatus: 'achieved',
    })

    expect(pot.percentage).toBe(42)
    expect(pot.goalStatus).toBe('achieved')
  })

  it('leaves the goal progress fields absent when the API does not send them', () => {
    const pot = fromApiPot({ id: 'pot-05', name: 'Fons', balance: 0, target: null, color: 'teal' })

    expect(pot.percentage).toBeUndefined()
    expect(pot.goalStatus).toBeUndefined()
  })

  it('falls back to null when an unknown goalStatus arrives', () => {
    // What a bad server would send: the cast is the test input, not a way around the check.
    const answer = {
      id: 'pot-06',
      name: 'Fons',
      balance: 0,
      target: 8000,
      color: 'teal',
      percentage: 0,
      goalStatus: 'done',
    } as unknown as PotJson

    expect(fromApiPot(answer).goalStatus).toBeNull()
  })

  it('keeps null and the two valid goalStatus values of the contract', () => {
    const potWith = (goalStatus: PotJson['goalStatus']): PotJson => ({
      id: 'pot-07',
      name: 'Fons',
      balance: 0,
      target: 8000,
      color: 'teal',
      percentage: 0,
      goalStatus,
    })

    expect(fromApiPot(potWith(null)).goalStatus).toBeNull()
    expect(fromApiPot(potWith('in_progress')).goalStatus).toBe('in_progress')
    expect(fromApiPot(potWith('achieved')).goalStatus).toBe('achieved')
  })
})

describe('fromApiPots', () => {
  it('turns a missing list into an empty one', () => {
    expect(fromApiPots(undefined)).toEqual([])
  })
})
