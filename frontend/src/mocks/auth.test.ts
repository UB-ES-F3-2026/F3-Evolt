// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mockOutbox, mockRegister, mockResendCode, mockVerify } from './auth'

const VALID = { identifier: 'ana@x.com', password: 'Platja2026', acceptedTerms: true }
const TEN_MINUTES_MS = 10 * 60 * 1000

function lastCode(to: string): string {
  return mockOutbox(to)[0]?.code ?? ''
}

/** A valid code that is not the right one. */
function wrongCode(to: string): string {
  return lastCode(to) === '000000' ? '111111' : '000000'
}

function expectFailure(action: () => unknown, code: string) {
  expect(action).toThrow(expect.objectContaining({ code }))
}

beforeEach(() => {
  sessionStorage.clear()
  vi.spyOn(console, 'info').mockImplementation(() => undefined)
})

afterEach(() => {
  vi.useRealTimers()
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

describe('mockVerify', () => {
  beforeEach(() => {
    mockRegister(VALID)
  })

  it('activates the account and opens a session with the right code', () => {
    const { token } = mockVerify({ identifier: 'ana@x.com', code: lastCode('ana@x.com') })

    expect(token).not.toBe('')
    expectFailure(() => mockVerify({ identifier: 'ana@x.com', code: '123456' }), 'INVALID_CODE')
  })

  it('still accepts the code one second before the 10 minutes', () => {
    vi.useFakeTimers()
    mockResendCode('ana@x.com')

    vi.advanceTimersByTime(TEN_MINUTES_MS - 1000)

    expect(mockVerify({ identifier: 'ana@x.com', code: lastCode('ana@x.com') }).token).not.toBe('')
  })

  it('rejects the code at exactly 10 minutes', () => {
    vi.useFakeTimers()
    mockResendCode('ana@x.com')

    vi.advanceTimersByTime(TEN_MINUTES_MS)

    expectFailure(() => mockVerify({ identifier: 'ana@x.com', code: lastCode('ana@x.com') }), 'CODE_EXPIRED')
  })

  it('answers VALIDATION_ERROR to a malformed code, without counting it', () => {
    for (let attempt = 0; attempt < 6; attempt += 1) {
      expectFailure(() => mockVerify({ identifier: 'ana@x.com', code: '12a456' }), 'VALIDATION_ERROR')
    }
    expect(mockVerify({ identifier: 'ana@x.com', code: lastCode('ana@x.com') }).token).not.toBe('')
  })

  it('does not reveal an account that does not exist', () => {
    expectFailure(() => mockVerify({ identifier: 'ningu@x.com', code: '123456' }), 'INVALID_CODE')
  })

  it('blocks at the fifth wrong code, even for the right one afterwards', () => {
    const wrong = wrongCode('ana@x.com')
    for (let attempt = 0; attempt < 4; attempt += 1) {
      expectFailure(() => mockVerify({ identifier: 'ana@x.com', code: wrong }), 'INVALID_CODE')
    }
    expectFailure(() => mockVerify({ identifier: 'ana@x.com', code: wrong }), 'TOO_MANY_ATTEMPTS')
    expectFailure(
      () => mockVerify({ identifier: 'ana@x.com', code: lastCode('ana@x.com') }),
      'TOO_MANY_ATTEMPTS',
    )
  })
})

describe('mockResendCode', () => {
  beforeEach(() => {
    mockRegister(VALID)
  })

  it('makes the old code stop working and starts the attempts again', () => {
    const wrong = wrongCode('ana@x.com')
    for (let attempt = 0; attempt < 5; attempt += 1) {
      expect(() => mockVerify({ identifier: 'ana@x.com', code: wrong })).toThrow()
    }

    expect(mockResendCode('ana@x.com')).toEqual({ status: 'ok' })

    expect(mockVerify({ identifier: 'ana@x.com', code: lastCode('ana@x.com') }).token).not.toBe('')
  })

  it('answers the same and sends nothing to a missing or an active account', () => {
    expect(mockResendCode('ningu@x.com')).toEqual({ status: 'ok' })
    expect(mockResendCode('demo@evolt.test')).toEqual({ status: 'ok' })

    expect(mockOutbox('ningu@x.com')).toEqual([])
    expect(mockOutbox('demo@evolt.test')).toEqual([])
  })
})
