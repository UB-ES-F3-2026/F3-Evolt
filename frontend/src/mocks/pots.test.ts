import { describe, expect, it } from 'vitest'
import { mockHome } from './index'
import { mockPots, mockTotalSaved } from './pots'

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
