import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useGoBack } from './useGoBack'

const router = {
  options: { history: { state: { back: null as string | null } } },
  back: vi.fn(),
  push: vi.fn(),
}

vi.mock('vue-router', () => ({ useRouter: () => router }))

beforeEach(() => {
  router.options.history.state.back = null
  router.back.mockReset()
  router.push.mockReset()
})

describe('useGoBack', () => {
  it('returns to the screen it came from', () => {
    router.options.history.state.back = '/'

    useGoBack({ name: 'movements' })()

    expect(router.back).toHaveBeenCalledOnce()
    expect(router.push).not.toHaveBeenCalled()
  })

  it('goes to the fallback when the screen was opened directly', () => {
    useGoBack({ name: 'movements' })()

    expect(router.push).toHaveBeenCalledWith({ name: 'movements' })
    expect(router.back).not.toHaveBeenCalled()
  })
})
