// @vitest-environment jsdom
import { beforeEach, describe, expect, it } from 'vitest'
import { clearToken, getToken, hasSession, saveToken } from './session'

beforeEach(() => {
  sessionStorage.clear()
})

describe('session token', () => {
  it('has no session at the start', () => {
    expect(getToken()).toBeNull()
    expect(hasSession()).toBe(false)
  })

  it('keeps the token until it is cleared', () => {
    saveToken('token-1')
    expect(getToken()).toBe('token-1')
    expect(hasSession()).toBe(true)

    clearToken()
    expect(getToken()).toBeNull()
    expect(hasSession()).toBe(false)
  })
})
