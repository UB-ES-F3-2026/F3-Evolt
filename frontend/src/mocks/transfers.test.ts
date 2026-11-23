import { describe, expect, it } from 'vitest'
import { mockBalance, mockHome } from './index'
import { mockSendTransfer, mockTransferLimit } from './transfers'

// Logged in as the user 1 of the seed. The mock keeps its state for the whole file, in order.
const DEMO = 'demo@evolt.test'

describe('mockSendTransfer (docs/api.md §13.4)', () => {
  it.each([
    [{ toUserId: 'usr-02', amount: '20' }, 'VALIDATION_ERROR'],
    [{ toUserId: 'usr-02', amount: 2000, concept: 'x'.repeat(141) }, 'VALIDATION_ERROR'],
    [{ toUserId: 'usr-99', amount: 2000 }, 'RECIPIENT_NOT_FOUND'],
    [{ toUserId: 'usr-01', amount: 2000 }, 'SELF_TRANSFER'],
    [{ toUserId: 'usr-02', amount: 0 }, 'INVALID_AMOUNT'],
    [{ toUserId: 'usr-02', amount: 379522 }, 'INSUFFICIENT_BALANCE'],
    [{ toUserId: 'usr-02', amount: 100001 }, 'TRANSFER_LIMIT_EXCEEDED'],
  ])('EN-19…: rejects %j as %s and changes nothing', (body, code) => {
    const before = mockHome()

    expect(() => mockSendTransfer(body, DEMO)).toThrow(expect.objectContaining({ code }) as Error)

    expect(mockHome()).toEqual(before)
  })

  it('EN-01, EN-02: sends 20,00 €, with the movement first in Inici', () => {
    const result = mockSendTransfer({ toUserId: 'usr-02', amount: 2000, concept: 'El sopar de divendres' }, DEMO)

    expect(result.balance).toBe(377521)
    expect(result.recipient).toEqual({ id: 'usr-02', name: 'Usuari nou', username: 'buit' })
    expect(result.movement).toMatchObject({
      amount: 2000,
      concept: 'El sopar de divendres',
      type: 'expense',
      icon: 'transfer',
    })
    expect(mockHome().lastMovements[0].concept).toBe('El sopar de divendres')
  })

  it('EN-04: without a concept the movement says «Transferència enviada»', () => {
    expect(mockSendTransfer({ toUserId: 'usr-02', amount: 1000, concept: '   ' }, DEMO).movement.concept).toBe(
      'Transferència enviada',
    )
  })

  it('EN-12, EN-14, GET /api/transfers/limit: what was sent today counts for the limit', () => {
    expect(mockTransferLimit()).toEqual({ dailyLimit: 100000, remainingToday: 97000 })
    expect(() => mockSendTransfer({ toUserId: 'usr-02', amount: 97001 }, DEMO)).toThrow(
      expect.objectContaining({ code: 'TRANSFER_LIMIT_EXCEEDED', details: { remainingToday: 97000 } }) as Error,
    )
    expect(mockSendTransfer({ toUserId: 'usr-03', amount: 97000 }, DEMO).balance).toBe(mockBalance())
    expect(mockTransferLimit().remainingToday).toBe(0)
  })
})
