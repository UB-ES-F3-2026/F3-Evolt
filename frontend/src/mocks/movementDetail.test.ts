import { describe, expect, it } from 'vitest'
import { mockMovement, mockReportMovement, mockTopup } from './index'

// The cases of docs/proves-moviments.md (D-xx and I-xx), against the mock.
describe('mockMovement', () => {
  it('gives a movement with counterparty, like the seed (D-01)', () => {
    expect(mockMovement('mov-29')).toMatchObject({
      concept: 'Bizum enviat',
      status: 'completed',
      counterparty: 'Núria Soler',
      reference: 'EVT-000029',
    })
  })

  it('gives the newest movement of the seed as pending and without counterparty (D-02)', () => {
    expect(mockMovement('mov-30')).toMatchObject({ status: 'pending', counterparty: null })
  })

  it('does not find a movement that does not exist (D-03, D-05)', () => {
    expect(() => mockMovement('mov-99')).toThrow()
    expect(() => mockMovement('abc')).toThrow()
    try {
      mockMovement('mov-99')
    } catch (failure) {
      expect(failure).toMatchObject({ code: 'MOVEMENT_NOT_FOUND' })
    }
  })

  it('gives a new movement as completed, with its own reference (D-07)', () => {
    const { movement } = mockTopup(100)

    expect(mockMovement(movement.id)).toEqual(movement)
    expect(movement).toMatchObject({ status: 'completed', counterparty: null, reference: 'EVT-000031' })
  })
})

describe('mockReportMovement', () => {
  function failureOf(action: () => unknown): unknown {
    try {
      action()
    } catch (failure) {
      return failure
    }
    return null
  }

  it('saves the description without the spaces at the ends, with a new id each time (I-01, I-08, I-09)', () => {
    const first = mockReportMovement('mov-30', '  No el reconec  ')
    const second = mockReportMovement('mov-30', 'Encara no el reconec')

    expect(first).toMatchObject({ id: 'rep-01', movementId: 'mov-30', description: 'No el reconec' })
    expect(second.id).toBe('rep-02')
  })

  it('rejects an empty or a too long description (I-03, I-04)', () => {
    expect(failureOf(() => mockReportMovement('mov-30', '   '))).toMatchObject({ code: 'INVALID_DESCRIPTION' })
    expect(failureOf(() => mockReportMovement('mov-30', 'a'.repeat(501)))).toMatchObject({
      code: 'INVALID_DESCRIPTION',
    })
  })

  it('checks the movement before the description (I-07)', () => {
    expect(failureOf(() => mockReportMovement('mov-99', ''))).toMatchObject({ code: 'MOVEMENT_NOT_FOUND' })
  })
})
