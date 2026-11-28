import { describe, expect, it } from 'vitest'
import { mockCancelMoneyRequest, mockMoneyRequests } from './moneyRequests'
import { mockCreateSplitExpense } from './splitExpenses'

// Logged in as the user 1 of the seed. The mocks keep their state for the whole file: tests in order.
const DEMO = 'demo@evolt.test'
// The expense of docs/proves-despeses.md (D0): Izan, Alicia and Martí, 15,00 € each and 15,00 € for me.
const D0 = {
  concept: "Sopar d'aniversari",
  total: 6000,
  myShare: 1500,
  parts: [
    { toUserId: 'usr-05', amount: 1500 },
    { toUserId: 'usr-03', amount: 1500 },
    { toUserId: 'usr-08', amount: 1500 },
  ],
}

describe('mockCreateSplitExpense (docs/api.md §17.2)', () => {
  it.each([
    [{ ...D0, total: '6000' }, 'VALIDATION_ERROR'],
    [{ ...D0, parts: [] }, 'VALIDATION_ERROR'],
    [{ ...D0, parts: [D0.parts[0], D0.parts[0]] }, 'VALIDATION_ERROR'],
    [{ ...D0, parts: [{ toUserId: 'usr-99', amount: 4500 }] }, 'RECIPIENT_NOT_FOUND'],
    // The participants are checked before the amount (DD-15).
    [{ ...D0, total: 0, parts: [{ toUserId: 'usr-01', amount: 4500 }] }, 'SELF_REQUEST'],
    [{ ...D0, total: 0 }, 'INVALID_AMOUNT'],
    [{ ...D0, total: 100000001 }, 'AMOUNT_OVER_LIMIT'],
    [{ ...D0, concept: '   ' }, 'INVALID_CONCEPT'],
    [{ ...D0, myShare: 0, total: 4500 }, 'INVALID_SHARE'],
    [{ ...D0, parts: [D0.parts[0], D0.parts[1], { toUserId: 'usr-08', amount: 1000 }] }, 'SHARES_DO_NOT_MATCH'],
  ])('DD-07…DD-16: rejects %j as %s and creates no request', (body, code) => {
    const before = mockMoneyRequests()

    expect(() => mockCreateSplitExpense(body, DEMO)).toThrow(expect.objectContaining({ code }) as Error)

    expect(mockMoneyRequests()).toEqual(before)
  })

  it('DD-01: creates the expense with its three pending parts, in the order they were added', () => {
    const created = mockCreateSplitExpense(D0, DEMO)

    expect(created).toMatchObject({
      id: 'split-01',
      concept: "Sopar d'aniversari",
      total: 6000,
      myShare: 1500,
      status: 'pending',
      people: 4,
      paidCount: 0,
      pendingAmount: 4500,
    })
    expect(created.parts.map(({ to, amount, status }) => [to.name, amount, status])).toEqual([
      ['Izan', 1500, 'pending'],
      ['Alicia', 1500, 'pending'],
      ['Martí', 1500, 'pending'],
    ])
  })

  it('DD-05: its requests are not listed on their own, and cannot be cancelled (P104, P105)', () => {
    const { parts } = mockCreateSplitExpense({ ...D0, concept: 'Cinema' }, DEMO)
    const listed = mockMoneyRequests().items.map((request) => request.id)

    expect(parts.some((part) => listed.includes(part.requestId))).toBe(false)
    expect(() => mockCancelMoneyRequest(parts[0].requestId)).toThrow(
      expect.objectContaining({ code: 'REQUEST_NOT_FOUND' }) as Error,
    )
  })
})
