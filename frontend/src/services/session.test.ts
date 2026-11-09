// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  closeSession,
  endSession,
  getToken,
  hasSession,
  onSessionEnded,
  saveToken,
  touchSession,
} from './session'

const FIVE_MINUTES_MS = 5 * 60 * 1000
const ended = vi.fn()

beforeEach(() => {
  vi.useFakeTimers()
  sessionStorage.clear()
  ended.mockReset()
  onSessionEnded(ended)
})

afterEach(() => {
  closeSession()
  vi.useRealTimers()
})

describe('session token', () => {
  it('has no session at the start', () => {
    expect(getToken()).toBeNull()
    expect(hasSession()).toBe(false)
  })

  it('keeps the token until the session is closed', () => {
    saveToken('token-1')
    expect(getToken()).toBe('token-1')
    expect(hasSession()).toBe(true)

    closeSession()
    expect(getToken()).toBeNull()
    expect(hasSession()).toBe(false)
  })
})

describe('inactivity', () => {
  it('ends the session after 5 minutes without activity', () => {
    saveToken('token-1')

    vi.advanceTimersByTime(FIVE_MINUTES_MS - 1000)
    expect(ended).not.toHaveBeenCalled()

    vi.advanceTimersByTime(1000)
    expect(ended).toHaveBeenCalledWith('inactivity')
    expect(hasSession()).toBe(false)
  })

  it('starts counting again with each activity', () => {
    saveToken('token-1')

    vi.advanceTimersByTime(FIVE_MINUTES_MS - 1000)
    touchSession()
    vi.advanceTimersByTime(FIVE_MINUTES_MS - 1000)

    expect(ended).not.toHaveBeenCalled()
    expect(hasSession()).toBe(true)
  })

  it('does not end anything without a session', () => {
    touchSession()

    vi.advanceTimersByTime(FIVE_MINUTES_MS)

    expect(ended).not.toHaveBeenCalled()
  })

  it('does not fire after the person has logged out', () => {
    saveToken('token-1')
    closeSession()

    vi.advanceTimersByTime(FIVE_MINUTES_MS)

    expect(ended).not.toHaveBeenCalled()
  })
})

describe('endSession', () => {
  it('clears the token and tells why', () => {
    saveToken('token-1')

    endSession('unauthenticated')

    expect(hasSession()).toBe(false)
    expect(ended).toHaveBeenCalledWith('unauthenticated')
  })
})
