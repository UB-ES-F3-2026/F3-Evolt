import { describe, expect, it } from 'vitest'
import { equalShares, fromApiSplitExpense, type SplitExpenseJson } from './splitExpense'

describe('equalShares (docs/api.md §17.2)', () => {
  it('DDP-03: 60,00 € among 3 participants and me → 15,00 € each', () => {
    expect(equalShares(6000, 3)).toEqual({ each: 1500, mine: 1500 })
  })

  it('DDP-03: 100,00 € among 2 participants and me → 33,33 € each, and the cents left over are mine', () => {
    expect(equalShares(10000, 2)).toEqual({ each: 3333, mine: 3334 })
  })

  it('a total too small for everyone leaves the participants at 0', () => {
    expect(equalShares(2, 3)).toEqual({ each: 0, mine: 2 })
  })
})

describe('fromApiSplitExpense', () => {
  const json: SplitExpenseJson = {
    id: 'split-01',
    concept: "Sopar d'aniversari",
    total: 6000,
    myShare: 1500,
    createdAt: '2026-11-15T21:15:00+01:00',
    status: 'pending',
    people: 4,
    paidCount: 0,
    pendingAmount: 4500,
    parts: [{ requestId: 'req-07', to: { id: 'usr-05', name: 'Izan', username: 'izanfarreny47' }, amount: 1500, status: 'pending' }],
  }

  it('keeps the fields of §17.1', () => {
    expect(fromApiSplitExpense(json)).toEqual({
      ...json,
      parts: [{ requestId: 'req-07', to: { id: 'usr-05', name: 'Izan', username: 'izanfarreny47' }, amount: 1500, status: 'pending' }],
    })
  })

  it('reads an unknown status as pending, for the expense and for a part', () => {
    const read = fromApiSplitExpense({ ...json, status: 'archived', parts: [{ ...json.parts[0], status: 'lost' }] })
    expect(read.status).toBe('pending')
    expect(read.parts[0].status).toBe('pending')
  })
})
