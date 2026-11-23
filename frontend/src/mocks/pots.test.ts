import { describe, expect, it } from 'vitest'
import { mockHome, mockMovements } from './index'
import { mockContribute, mockCreatePot, mockPotMovements, mockPots, mockTotalSaved, mockWithdraw } from './pots'

// The mock keeps its state for the whole file, like `npm run dev` keeps it until a reload.
// The tests that create pots are therefore written in order.

describe('pots mock', () => {
  it('starts with the three pots of the seed (docs/api.md §9.8), in creation order', () => {
    expect(mockPots().items).toEqual([
      // US-20 (issue #150): the backend adds the goal progress to every pot.
      { id: 'pot-01', name: 'Vacances', balance: 15000, target: 100000, color: 'blue', percentage: 15, goalStatus: 'in_progress' },
      { id: 'pot-02', name: 'Emergències', balance: 10000, target: null, color: 'orange', percentage: null, goalStatus: null },
      { id: 'pot-03', name: "Regal d'aniversari", balance: 5000, target: 8000, color: 'pink', percentage: 63, goalStatus: 'in_progress' },
    ])
  })

  it('computes the goal progress of every pot, rounded half-up, and null without a goal (US-20, issue #150)', () => {
    const [vacances, emergencies, regal] = mockPots().items

    expect(vacances).toMatchObject({ percentage: 15, goalStatus: 'in_progress' })
    // 5000 of 8000 is 62.5%, which rounds half-up to 63.
    expect(regal).toMatchObject({ percentage: 63, goalStatus: 'in_progress' })
    expect(emergencies).toMatchObject({ percentage: null, goalStatus: null })
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
    expect(pot).toEqual({
      id: 'pot-04',
      name: 'Viatge',
      balance: 0,
      target: 30000,
      color: 'purple',
      percentage: 0,
      goalStatus: 'in_progress',
    })
    expect(mockPots().items.at(-1)).toEqual(pot)
  })

  it('creates a pot without target, with the chosen colour', () => {
    const pot = mockCreatePot({ name: 'Fons', color: 'teal' })

    expect(pot).toMatchObject({ id: 'pot-05', target: null, color: 'teal', percentage: null, goalStatus: null })
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
    // US-20 (issue #150): the contribution answer carries the pot's fresh progress.
    expect(result.pot).toMatchObject({
      id: 'pot-01',
      name: 'Vacances',
      balance: 18000,
      percentage: 18,
      goalStatus: 'in_progress',
    })
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

  it('answers achieved with 100% once the contribution reaches the target (US-20, issue #150)', () => {
    const result = mockContribute('pot-03', { amount: 3000 })

    expect(result.pot).toMatchObject({ id: 'pot-03', balance: 8000, percentage: 100, goalStatus: 'achieved' })
  })

  it('caps below the target at 99 %: 7999 of 8000 is 99 and in_progress (docs/api.md §11.1, US-20)', () => {
    const pot = mockCreatePot({ name: 'Just sota', target: 8000 })
    const result = mockContribute(pot.id, { amount: 7999 })

    // 7999 of 8000 is 99.98 %, but a bar that says 100 % would also say the goal is reached.
    expect(result.pot).toMatchObject({ balance: 7999, percentage: 99, goalStatus: 'in_progress' })
  })

  it('keeps the real value above the target: 125 and achieved (docs/api.md §11.1, US-20)', () => {
    const pot = mockCreatePot({ name: 'De sobres', target: 8000 })
    const result = mockContribute(pot.id, { amount: 10000 })

    expect(result.pot).toMatchObject({ balance: 10000, percentage: 125, goalStatus: 'achieved' })
  })

  it('allows moving exactly the whole main balance (A-06)', () => {
    const result = mockContribute('pot-02', { amount: mockHome().balance })

    expect(result.balance).toBe(0)
  })
})

// After the contributions above: Vacances (pot-01) holds 18000 and the main account 0.
describe('mockWithdraw (docs/api.md §11.2)', () => {
  it.each([
    ['pot-01', { amount: '30' }, 'VALIDATION_ERROR'],
    ['pot-01', { amount: 30.5 }, 'VALIDATION_ERROR'],
    ['pot-01', {}, 'VALIDATION_ERROR'],
    ['pot-99', { amount: 3000 }, 'POT_NOT_FOUND'],
    // The pot is checked before the amount.
    ['pot-99', { amount: 0 }, 'POT_NOT_FOUND'],
    ['pot-01', { amount: 0 }, 'INVALID_AMOUNT'],
    ['pot-01', { amount: -100 }, 'INVALID_AMOUNT'],
    ['pot-01', { amount: 18001 }, 'INSUFFICIENT_POT_BALANCE'],
  ])('RE-07, RE-09, RE-10, RE-11, RE-13: rejects %s with %j as %s and changes nothing', (potId, body, code) => {
    const before = { home: mockHome(), pots: mockPots(), history: mockPotMovements('pot-01') }

    expect(() => mockWithdraw(potId, body)).toThrow(expect.objectContaining({ code }) as Error)

    expect(mockHome()).toEqual(before.home)
    expect(mockPots()).toEqual(before.pots)
    expect(mockPotMovements('pot-01')).toEqual(before.history)
  })

  it('RE-01, RE-02, RE-03: moves the money from the pot to the account, with the movement «Retirada de Vacances»', () => {
    const before = mockHome()

    const result = mockWithdraw('pot-01', { amount: 3000 })

    expect(result.balance).toBe(before.balance + 3000)
    expect(result.pot).toMatchObject({ id: 'pot-01', name: 'Vacances', balance: 15000 })
    expect(result.movement).toMatchObject({
      amount: 3000,
      concept: 'Retirada de Vacances',
      type: 'income',
      icon: 'savings',
    })
    const after = mockHome()
    expect(after.balance + after.totalSaved).toBe(before.balance + before.totalSaved)
    expect(after.lastMovements[0].concept).toBe('Retirada de Vacances')
  })

  it('RE-04: adds «Retirada» as expense to the top of the pot history', () => {
    const items = mockPotMovements('pot-01').items

    expect(items[0]).toMatchObject({ concept: 'Retirada', amount: 3000, type: 'expense' })
  })

  it('RE-06, RE-08: allows taking exactly the whole pot balance, leaving it at 0', () => {
    const result = mockWithdraw('pot-03', { amount: 5000 })

    expect(result.pot.balance).toBe(0)
    expect(() => mockWithdraw('pot-03', { amount: 1 })).toThrow(
      expect.objectContaining({ code: 'INSUFFICIENT_POT_BALANCE' }) as Error,
    )
  })
})
