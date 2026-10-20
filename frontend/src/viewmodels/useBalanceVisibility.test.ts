// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const STORAGE_KEY = 'evolt.balanceHidden'

// The preference is read once, when the module loads (app start), so each test
// loads a fresh copy after preparing localStorage.
async function startApp() {
  vi.resetModules()
  const { useBalanceVisibility } = await import('./useBalanceVisibility')
  return useBalanceVisibility
}

beforeEach(() => {
  localStorage.clear()
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('useBalanceVisibility', () => {
  it('shows the amounts when nothing was saved', async () => {
    const useBalanceVisibility = await startApp()

    expect(useBalanceVisibility().isHidden.value).toBe(false)
  })

  it('saves the choice every time it changes', async () => {
    const { isHidden, toggle } = (await startApp())()

    toggle()
    expect(isHidden.value).toBe(true)
    expect(localStorage.getItem(STORAGE_KEY)).toBe('true')

    toggle()
    expect(isHidden.value).toBe(false)
    expect(localStorage.getItem(STORAGE_KEY)).toBe('false')
  })

  it('keeps the amounts hidden in the next session', async () => {
    ;(await startApp())().toggle()

    const nextSession = await startApp()

    expect(nextSession().isHidden.value).toBe(true)
  })

  it('shares one preference between screens', async () => {
    const useBalanceVisibility = await startApp()
    const home = useBalanceVisibility()
    const movements = useBalanceVisibility()

    home.toggle()

    expect(movements.isHidden.value).toBe(true)
  })

  it('still works for the session when the browser blocks storage', async () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('blocked')
    })
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('blocked')
    })
    const { isHidden, toggle } = (await startApp())()

    expect(isHidden.value).toBe(false)
    toggle()
    expect(isHidden.value).toBe(true)
  })
})
