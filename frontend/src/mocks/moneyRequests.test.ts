import { describe, expect, it } from 'vitest'
import { mockCancelMoneyRequest, mockCreateMoneyRequest, mockMoneyRequests } from './moneyRequests'

// Logged in as the user 1 of the seed. The mock keeps its state for the whole file: tests in order.
const DEMO = 'demo@evolt.test'

describe('mockMoneyRequests seed (docs/api.md §14.8)', () => {
  it('SOP-01: starts with the pending one to Alicia and the expired one to Huabin, newest first', () => {
    expect(mockMoneyRequests().items.map(({ id, to, amount, status }) => [id, to.name, amount, status])).toEqual([
      ['req-02', 'Alicia', 2500, 'pending'],
      ['req-01', 'Huabin', 4200, 'expired'],
    ])
  })

  it('SO-18: the expired one cannot be cancelled and stays in the list', () => {
    expect(() => mockCancelMoneyRequest('req-01')).toThrow(
      expect.objectContaining({ code: 'REQUEST_NOT_PENDING' }) as Error,
    )
    expect(mockMoneyRequests().items.map((request) => request.id)).toContain('req-01')
  })
})

describe('mockCreateMoneyRequest (docs/api.md §14.2)', () => {
  it.each([
    [{ toUserId: 'usr-03', amount: '2500', concept: 'x' }, 'VALIDATION_ERROR'],
    [{ toUserId: 'usr-03', amount: 2500 }, 'VALIDATION_ERROR'],
    [{ toUserId: 'usr-99', amount: 2500, concept: 'x' }, 'RECIPIENT_NOT_FOUND'],
    [{ toUserId: 'usr-01', amount: 2500, concept: 'x' }, 'SELF_REQUEST'],
    // The recipient is checked before the amount (SO-13).
    [{ toUserId: 'usr-01', amount: 0, concept: 'x' }, 'SELF_REQUEST'],
    [{ toUserId: 'usr-03', amount: 0, concept: 'x' }, 'INVALID_AMOUNT'],
    [{ toUserId: 'usr-03', amount: 100000001, concept: 'x' }, 'AMOUNT_OVER_LIMIT'],
    [{ toUserId: 'usr-03', amount: 2500, concept: '   ' }, 'INVALID_CONCEPT'],
    [{ toUserId: 'usr-03', amount: 2500, concept: 'x'.repeat(141) }, 'INVALID_CONCEPT'],
  ])('SO-07…SO-13: rejects %j as %s and saves nothing', (body, code) => {
    const before = mockMoneyRequests()

    expect(() => mockCreateMoneyRequest(body, DEMO)).toThrow(expect.objectContaining({ code }) as Error)

    expect(mockMoneyRequests()).toEqual(before)
  })

  it('SO-01, SO-11: creates a pending request, with the concept without the spaces at the ends', () => {
    const created = mockCreateMoneyRequest({ toUserId: 'usr-03', amount: 2500, concept: '  El sopar  ' }, DEMO)

    expect(created).toMatchObject({
      to: { id: 'usr-03', name: 'Alicia', username: 'aliciaa415' },
      amount: 2500,
      concept: 'El sopar',
      status: 'pending',
    })
    expect(Date.parse(created.expiresAt)).toBeGreaterThan(Date.parse(created.createdAt))
  })

  it('SO-02: lists the newest first', () => {
    mockCreateMoneyRequest({ toUserId: 'usr-04', amount: 100, concept: 'Cafè' }, DEMO)

    expect(mockMoneyRequests().items.map((request) => request.id)).toEqual(['req-04', 'req-03', 'req-02', 'req-01'])
  })
})

describe('mockCancelMoneyRequest (docs/api.md §14.4)', () => {
  it('SO-16, SO-17: deletes a pending request for good; cancelling it again is REQUEST_NOT_FOUND', () => {
    const id = mockMoneyRequests().items[0].id

    expect(mockCancelMoneyRequest(id)).toEqual({ status: 'ok' })
    expect(mockMoneyRequests().items.map((request) => request.id)).not.toContain(id)
    expect(() => mockCancelMoneyRequest(id)).toThrow(expect.objectContaining({ code: 'REQUEST_NOT_FOUND' }) as Error)
  })

  it('SO-14, SO-21: from 00:00 of its seventh day it reads «expired» and cannot be cancelled', () => {
    const request = mockMoneyRequests().items[0]
    const atExpiry = new Date(request.expiresAt)

    expect(mockMoneyRequests(atExpiry).items[0].status).toBe('expired')
    expect(mockMoneyRequests(new Date(atExpiry.getTime() - 1)).items[0].status).toBe('pending')
    expect(() => mockCancelMoneyRequest(request.id, atExpiry)).toThrow(
      expect.objectContaining({ code: 'REQUEST_NOT_PENDING' }) as Error,
    )
  })

  it('SO-20: an id that is not there is REQUEST_NOT_FOUND', () => {
    expect(() => mockCancelMoneyRequest('req-99')).toThrow(expect.objectContaining({ code: 'REQUEST_NOT_FOUND' }) as Error)
  })
})
