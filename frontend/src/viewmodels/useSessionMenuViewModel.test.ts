import { describe, expect, it, vi } from 'vitest'
import { useSessionMenuViewModel, type SessionMenuDependencies } from './useSessionMenuViewModel'

function fakeDependencies(overrides: Partial<SessionMenuDependencies> = {}) {
  return {
    hasSession: vi.fn(() => true),
    logout: vi.fn(() => Promise.resolve({ status: 'ok' as const })),
    closeSession: vi.fn(),
    goToLogin: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
}

describe('useSessionMenuViewModel', () => {
  it('knows whether there is a session', () => {
    expect(useSessionMenuViewModel(fakeDependencies()).isLoggedIn).toBe(true)
    expect(useSessionMenuViewModel(fakeDependencies({ hasSession: () => false })).isLoggedIn).toBe(false)
  })

  it('tells the backend first, because the request needs the token', async () => {
    const order: string[] = []
    const dependencies = fakeDependencies({
      logout: vi.fn(() => {
        order.push('logout')
        return Promise.resolve({ status: 'ok' as const })
      }),
      closeSession: vi.fn(() => order.push('close')),
      goToLogin: vi.fn(() => {
        order.push('login')
        return Promise.resolve()
      }),
    })

    await useSessionMenuViewModel(dependencies).logOut()

    expect(order).toEqual(['logout', 'close', 'login'])
  })

  it('leaves even if the request fails', async () => {
    const dependencies = fakeDependencies({
      logout: vi.fn(() => Promise.reject({ code: 'NETWORK_ERROR', message: 'x' })),
    })

    await useSessionMenuViewModel(dependencies).logOut()

    expect(dependencies.closeSession).toHaveBeenCalledTimes(1)
    expect(dependencies.goToLogin).toHaveBeenCalledTimes(1)
  })
})
