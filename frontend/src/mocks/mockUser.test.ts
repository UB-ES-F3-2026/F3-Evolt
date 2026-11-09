// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mockLogin, mockLogout, mockOutbox, mockRegister, mockVerify } from './auth'
import { mockHome, mockMovements } from './index'
import { mockPots } from './pots'

// The fictitious seed accounts of docs/api.md §8.13.
const DEMO = { identifier: 'demo@evolt.test', password: 'Evolt2026' }
const EMPTY = { identifier: 'buit@evolt.test', password: 'Evolt2026' }

beforeEach(() => {
  vi.spyOn(console, 'info').mockImplementation(() => undefined)
})

afterEach(() => {
  mockLogout()
  sessionStorage.clear()
})

describe('each mock account sees its own data', () => {
  it('the demo user sees the seed', () => {
    mockLogin(DEMO)

    expect(mockHome().lastMovements).toHaveLength(5)
    expect(mockPots().items).toHaveLength(3)
  })

  it('the empty user sees no movements, no pots and a balance of 0', () => {
    mockLogin(EMPTY)

    expect(mockHome()).toEqual({ balance: 0, totalSaved: 0, lastMovements: [] })
    expect(mockMovements().items).toEqual([])
    expect(mockPots().items).toEqual([])
  })

  it('a new account starts empty, as with the backend', () => {
    mockRegister({ identifier: 'ana@x.com', password: 'Platja2026', acceptedTerms: true })
    mockVerify({ identifier: 'ana@x.com', code: mockOutbox('ana@x.com')[0]?.code ?? '' })

    expect(mockHome()).toEqual({ balance: 0, totalSaved: 0, lastMovements: [] })
  })

  it('changes the data when another person logs in, without a reload', () => {
    mockLogin(DEMO)
    expect(mockPots().items).toHaveLength(3)

    mockLogout()
    mockLogin(EMPTY)

    expect(mockPots().items).toEqual([])
  })
})
