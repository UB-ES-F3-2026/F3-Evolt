// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mockOutbox, mockRegister } from './auth'

const VALID = { identifier: 'ana@x.com', password: 'Platja2026', acceptedTerms: true }

beforeEach(() => {
  sessionStorage.clear()
  vi.spyOn(console, 'info').mockImplementation(() => undefined)
})

describe('mockRegister', () => {
  it('creates a pending account with the normalized identifier and leaves a code', () => {
    expect(mockRegister({ ...VALID, identifier: ' Ana@X.com ' })).toEqual({
      identifier: 'ana@x.com',
      status: 'pending',
    })
    expect(mockOutbox('ana@x.com')[0]?.code).toMatch(/^\d{6}$/)
  })

  it('normalizes a phone number', () => {
    expect(mockRegister({ ...VALID, identifier: '612 34 56 78' }).identifier).toBe('+34612345678')
  })

  it.each([
    ['unaccepted terms', { ...VALID, acceptedTerms: false }],
    ['a broken email', { ...VALID, identifier: 'ana@' }],
    ['a broken phone', { ...VALID, identifier: '12ab' }],
    ['a password over 72 bytes', { ...VALID, password: `Aa1${'x'.repeat(70)}` }],
  ])('answers VALIDATION_ERROR to %s', (_reason, request) => {
    expect(() => mockRegister(request)).toThrow(expect.objectContaining({ code: 'VALIDATION_ERROR' }))
  })

  it('checks the format before the password policy', () => {
    const request = { ...VALID, password: 'WEAK', acceptedTerms: false }
    expect(() => mockRegister(request)).toThrow(expect.objectContaining({ code: 'VALIDATION_ERROR' }))
  })

  it('checks the password policy before the duplicate', () => {
    const request = { ...VALID, identifier: 'demo@evolt.test', password: 'curta' }
    expect(() => mockRegister(request)).toThrow(expect.objectContaining({ code: 'WEAK_PASSWORD' }))
  })

  it.each(['demo@evolt.test', 'ANA@x.com'])('rejects the duplicate %s', (identifier) => {
    mockRegister(VALID)
    expect(() => mockRegister({ ...VALID, identifier })).toThrow(
      expect.objectContaining({ code: 'ALREADY_REGISTERED' }),
    )
  })
})
