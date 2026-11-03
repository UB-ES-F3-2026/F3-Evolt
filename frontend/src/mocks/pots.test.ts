import { describe, expect, it } from 'vitest'
import { mockHome } from './index'
import { mockCreatePot, mockPots, mockTotalSaved } from './pots'

// The mock keeps its state for the whole file, like `npm run dev` keeps it until a reload.
// The tests that create pots are therefore written in order.

describe('pots mock', () => {
  it('starts with the three pots of the seed (docs/api.md §9.8), in creation order', () => {
    expect(mockPots().items).toEqual([
      { id: 'pot-01', name: 'Vacances', balance: 15000, target: 100000, color: 'blue' },
      { id: 'pot-02', name: 'Emergències', balance: 10000, target: null, color: 'orange' },
      { id: 'pot-03', name: "Regal d'aniversari", balance: 5000, target: 8000, color: 'pink' },
    ])
  })

  it('gives the home the sum of the pots as total saved', () => {
    expect(mockTotalSaved()).toBe(30000)
    expect(mockHome().totalSaved).toBe(30000)
  })

  it('returns copies, so a caller cannot change the stored pots', () => {
    mockPots().items[0].balance = 0

    expect(mockPots().items[0].balance).toBe(15000)
  })
})

describe('mockCreatePot (docs/api.md §9.3)', () => {
  it.each([
    [{ name: 123 }, 'VALIDATION_ERROR'],
    [{ name: 'Viatge', target: '300' }, 'VALIDATION_ERROR'],
    [{ name: 'Viatge', target: 300.5 }, 'VALIDATION_ERROR'],
    [{ name: 'Viatge', color: 'red' }, 'VALIDATION_ERROR'],
    [{ name: '' }, 'INVALID_POT_NAME'],
    [{ name: '   ' }, 'INVALID_POT_NAME'],
    [{ name: 'Viatge', target: 0 }, 'INVALID_TARGET'],
    [{ name: 'Viatge', target: -500 }, 'INVALID_TARGET'],
    // The name is checked before the target (P26).
    [{ name: '', target: 0 }, 'INVALID_POT_NAME'],
  ])('rejects %j with %s and creates nothing', (body, code) => {
    expect(() => mockCreatePot(body)).toThrow(expect.objectContaining({ code }) as Error)
    expect(mockPots().items).toHaveLength(3)
  })

  it('creates the pot with balance 0, the trimmed name and the default colour, using the next id', () => {
    const pot = mockCreatePot({ name: '  Viatge  ', target: 30000 })

    // The errors above did not use any id (P-15).
    expect(pot).toEqual({ id: 'pot-04', name: 'Viatge', balance: 0, target: 30000, color: 'purple' })
    expect(mockPots().items.at(-1)).toEqual(pot)
  })

  it('creates a pot without target, with the chosen colour', () => {
    const pot = mockCreatePot({ name: 'Fons', color: 'teal' })

    expect(pot).toMatchObject({ id: 'pot-05', target: null, color: 'teal' })
  })

  it('does not change the total saved: a new pot is empty', () => {
    expect(mockHome().totalSaved).toBe(30000)
  })
})
