import { describe, expect, it } from 'vitest'
import { fromApiReceivedMoneyRequest, type ReceivedMoneyRequestJson } from './moneyRequest'

const json: ReceivedMoneyRequestJson = {
  id: 'req-06',
  from: { id: 'usr-03', name: 'Alicia', username: 'aliciaa415' },
  amount: 2500,
  concept: 'El sopar de divendres',
  status: 'pending',
  createdAt: '2026-11-23T19:30:00+01:00',
  expiresAt: '2026-11-30T00:00:00+01:00',
}

describe('fromApiReceivedMoneyRequest', () => {
  it('keeps the fields of the contract, with from instead of to (docs/api.md §15.1)', () => {
    const request = fromApiReceivedMoneyRequest(json)

    expect(request.id).toBe('req-06')
    expect(request.from.username).toBe('aliciaa415')
    expect(request.amount).toBe(2500)
    expect(request.status).toBe('pending')
    expect(request.expiresAt).toBe('2026-11-30T00:00:00+01:00')
  })

  it('shows an unknown status as still pending: the server decides what can be done with it', () => {
    expect(fromApiReceivedMoneyRequest({ ...json, status: 'cancelled' }).status).toBe('pending')
  })
})
