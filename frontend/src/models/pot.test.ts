import { describe, expect, it } from 'vitest'
import { DEFAULT_POT_COLOR, fromApiPot, fromApiPots } from './pot'

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
})

describe('fromApiPots', () => {
  it('turns a missing list into an empty one', () => {
    expect(fromApiPots(undefined)).toEqual([])
  })
})
