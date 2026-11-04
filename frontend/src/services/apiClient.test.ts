// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { apiGet, apiPost } from './apiClient'
import { closeSession, hasSession, onSessionEnded, saveToken } from './session'

const fetchMock = vi.fn()
const ended = vi.fn()

function answer(status: number, body: unknown) {
  fetchMock.mockResolvedValue(new Response(JSON.stringify(body), { status }))
}

function sentHeaders(): Record<string, string> {
  const init = fetchMock.mock.calls[0]?.[1] as RequestInit
  return init.headers as Record<string, string>
}

beforeEach(() => {
  sessionStorage.clear()
  fetchMock.mockReset()
  ended.mockReset()
  vi.stubGlobal('fetch', fetchMock)
  onSessionEnded(ended)
})

afterEach(() => {
  closeSession()
  vi.unstubAllGlobals()
})

describe('the session token', () => {
  it('goes in the Authorization header', async () => {
    saveToken('token-1')
    answer(200, { ok: true })

    await apiGet('/api/home')

    expect(sentHeaders().Authorization).toBe('Bearer token-1')
  })

  it('is not sent without a session', async () => {
    answer(200, { ok: true })

    await apiPost('/api/auth/login', { identifier: 'a', password: 'b' })

    expect(sentHeaders()).not.toHaveProperty('Authorization')
  })
})

describe('an answer saying the session is gone', () => {
  it('SESSION_EXPIRED ends it as inactivity and still rejects', async () => {
    saveToken('token-1')
    answer(401, { code: 'SESSION_EXPIRED', message: 'x' })

    await expect(apiGet('/api/home')).rejects.toMatchObject({ code: 'SESSION_EXPIRED' })

    expect(hasSession()).toBe(false)
    expect(ended).toHaveBeenCalledWith('inactivity')
  })

  it('UNAUTHENTICATED ends it without talking about inactivity', async () => {
    saveToken('token-1')
    answer(401, { code: 'UNAUTHENTICATED', message: 'x' })

    await expect(apiGet('/api/home')).rejects.toMatchObject({ code: 'UNAUTHENTICATED' })

    expect(hasSession()).toBe(false)
    expect(ended).toHaveBeenCalledWith('unauthenticated')
  })
})

describe('any other failure', () => {
  it('keeps the session', async () => {
    saveToken('token-1')
    answer(422, { code: 'AMOUNT_OVER_LIMIT', message: 'x' })

    await expect(apiPost('/api/topups', { amount: 60000 })).rejects.toMatchObject({ code: 'AMOUNT_OVER_LIMIT' })

    expect(hasSession()).toBe(true)
    expect(ended).not.toHaveBeenCalled()
  })

  it('a wrong login does not end anything', async () => {
    answer(401, { code: 'INVALID_CREDENTIALS', message: 'x' })

    await expect(apiPost('/api/auth/login', {})).rejects.toMatchObject({ code: 'INVALID_CREDENTIALS' })

    expect(ended).not.toHaveBeenCalled()
  })

  it('a body outside the contract becomes INTERNAL_ERROR', async () => {
    answer(401, { detail: 'Unauthorized' })

    await expect(apiGet('/api/home')).rejects.toMatchObject({ code: 'INTERNAL_ERROR' })
  })

  it('no connection becomes NETWORK_ERROR', async () => {
    fetchMock.mockRejectedValue(new TypeError('Failed to fetch'))

    await expect(apiGet('/api/home')).rejects.toMatchObject({ code: 'NETWORK_ERROR' })
  })
})
