import { describe, expect, it } from 'vitest'
import { mockHome, mockMovements } from './index'
import { mockContribute, mockCreatePot, mockPotMovements, mockPots, mockTotalSaved } from './pots'

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

describe('mockPotMovements (docs/api.md §9.5)', () => {
  it('starts each seed pot with one «Saldo inicial» entry for its balance', () => {
    expect(mockPotMovements('pot-02').items).toEqual([
      expect.objectContaining({ id: 'pmov-02', amount: 10000, concept: 'Saldo inicial', type: 'income' }),
    ])
  })

  it('answers POT_NOT_FOUND for a pot that does not exist', () => {
    expect(() => mockPotMovements('pot-99')).toThrow(expect.objectContaining({ code: 'POT_NOT_FOUND' }) as Error)
  })
})

describe('mockContribute (docs/api.md §9.4)', () => {
  it.each([
    ['pot-01', { amount: '30' }, 'VALIDATION_ERROR'],
    ['pot-01', { amount: 30.5 }, 'VALIDATION_ERROR'],
    ['pot-01', {}, 'VALIDATION_ERROR'],
    ['pot-99', { amount: 3000 }, 'POT_NOT_FOUND'],
    // The pot is checked before the amount (P28).
    ['pot-99', { amount: 0 }, 'POT_NOT_FOUND'],
    ['pot-01', { amount: 0 }, 'INVALID_AMOUNT'],
    ['pot-01', { amount: -100 }, 'INVALID_AMOUNT'],
    ['pot-01', { amount: 379522 }, 'INSUFFICIENT_BALANCE'],
  ])('rejects %s with %j as %s and changes nothing (A-07…A-13)', (potId, body, code) => {
    const before = { home: mockHome(), pots: mockPots(), history: mockPotMovements('pot-01') }

    expect(() => mockContribute(potId, body)).toThrow(expect.objectContaining({ code }) as Error)

    expect(mockHome()).toEqual(before.home)
    expect(mockPots()).toEqual(before.pots)
    expect(mockPotMovements('pot-01')).toEqual(before.history)
  })

  it('moves the money from the account to the pot, with the movement «Aportació a Vacances» (A-01)', () => {
    const result = mockContribute('pot-01', { amount: 3000 })

    expect(result.balance).toBe(376521)
    expect(result.pot).toMatchObject({ id: 'pot-01', name: 'Vacances', balance: 18000 })
    expect(result.movement).toMatchObject({
      amount: 3000,
      concept: 'Aportació a Vacances',
      type: 'expense',
      icon: 'savings',
    })
  })

  it('keeps balance + total saved the same, and shows the movement first in home and in the list (A-02, A-03)', () => {
    const home = mockHome()

    expect(home.balance).toBe(376521)
    expect(home.totalSaved).toBe(33000)
    expect(home.balance + home.totalSaved).toBe(379521 + 30000)
    expect(home.lastMovements[0].concept).toBe('Aportació a Vacances')
    expect(mockMovements(0, 1).items[0].concept).toBe('Aportació a Vacances')
  })

  it('adds «Aportació» to the top of the pot history; the history adds up to the pot balance (A-04)', () => {
    const items = mockPotMovements('pot-01').items

    expect(items.map((entry) => [entry.concept, entry.amount, entry.type])).toEqual([
      ['Aportació', 3000, 'income'],
      ['Saldo inicial', 15000, 'income'],
    ])
    expect(items.reduce((sum, entry) => sum + entry.amount, 0)).toBe(18000)
  })

  it('allows moving exactly the whole main balance (A-06)', () => {
    const result = mockContribute('pot-02', { amount: mockHome().balance })

    expect(result.balance).toBe(0)
  })
})
