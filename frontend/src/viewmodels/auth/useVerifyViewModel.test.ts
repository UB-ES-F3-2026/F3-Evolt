import { nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'
import { useVerifyViewModel, type VerifyDependencies } from './useVerifyViewModel'

function fakeDependencies(overrides: Partial<VerifyDependencies> = {}) {
  return {
    identifier: 'ana@x.com',
    verify: vi.fn(() => Promise.resolve({ token: 'token-1' })),
    resendCode: vi.fn(() => Promise.resolve({ status: 'ok' as const })),
    saveToken: vi.fn(),
    goHome: vi.fn(() => Promise.resolve()),
    goToRegister: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
}

function failingVerify(code: string) {
  return vi.fn(() => Promise.reject({ code, message: 'x' }))
}

/** Lets the watch fire and the fake answer arrive. */
async function settle() {
  await nextTick()
  await new Promise((resolve) => setTimeout(resolve))
}

describe('useVerifyViewModel', () => {
  it('sends nothing until the sixth digit', async () => {
    const dependencies = fakeDependencies()
    const viewModel = useVerifyViewModel(dependencies)

    viewModel.code.value = '04821'
    await settle()

    expect(dependencies.verify).not.toHaveBeenCalled()
  })

  it('with the right code keeps the token and opens Home', async () => {
    const dependencies = fakeDependencies()
    const viewModel = useVerifyViewModel(dependencies)

    viewModel.code.value = '048213'
    await settle()

    expect(dependencies.verify).toHaveBeenCalledWith({ identifier: 'ana@x.com', code: '048213' })
    expect(dependencies.saveToken).toHaveBeenCalledWith('token-1')
    expect(dependencies.goHome).toHaveBeenCalledTimes(1)
    expect(viewModel.isSubmitting.value).toBe(false)
  })

  it.each(['INVALID_CODE', 'CODE_EXPIRED'])('with %s shows the same text and empties the boxes', async (code) => {
    const dependencies = fakeDependencies({ verify: failingVerify(code) })
    const viewModel = useVerifyViewModel(dependencies)

    viewModel.code.value = '111111'
    await settle()

    expect(viewModel.error.value).toBe('El codi no és correcte o ha caducat.')
    expect(viewModel.code.value).toBe('')
    expect(viewModel.isLocked.value).toBe(false)
    expect(dependencies.goHome).not.toHaveBeenCalled()
  })

  it('keeps the error while the boxes are empty and clears it when typing again', async () => {
    const viewModel = useVerifyViewModel(fakeDependencies({ verify: failingVerify('INVALID_CODE') }))
    viewModel.code.value = '111111'
    await settle()
    expect(viewModel.error.value).not.toBeNull()

    viewModel.code.value = '2'
    await settle()

    expect(viewModel.error.value).toBeNull()
  })

  it('locks the boxes after too many attempts', async () => {
    const dependencies = fakeDependencies({ verify: failingVerify('TOO_MANY_ATTEMPTS') })
    const viewModel = useVerifyViewModel(dependencies)

    viewModel.code.value = '111111'
    await settle()

    expect(viewModel.isLocked.value).toBe(true)
    expect(viewModel.error.value).toBe('Has fet massa intents. Demana un codi nou.')
    expect(await viewModel.submit()).toBe(false)
    expect(dependencies.verify).toHaveBeenCalledTimes(1)
  })

  it('a new code unlocks the boxes and says it was sent', async () => {
    const dependencies = fakeDependencies({ verify: failingVerify('TOO_MANY_ATTEMPTS') })
    const viewModel = useVerifyViewModel(dependencies)
    viewModel.code.value = '111111'
    await settle()

    await viewModel.resend()

    expect(dependencies.resendCode).toHaveBeenCalledWith('ana@x.com')
    expect(viewModel.isLocked.value).toBe(false)
    expect(viewModel.error.value).toBeNull()
    expect(viewModel.notice.value).toBe("T'hem enviat un codi nou.")
  })

  it('keeps the boxes locked when asking for a new code fails', async () => {
    const dependencies = fakeDependencies({
      verify: failingVerify('TOO_MANY_ATTEMPTS'),
      resendCode: vi.fn(() => Promise.reject({ code: 'NETWORK_ERROR', message: 'x' })),
    })
    const viewModel = useVerifyViewModel(dependencies)
    viewModel.code.value = '111111'
    await settle()

    await viewModel.resend()

    expect(viewModel.isLocked.value).toBe(true)
    expect(viewModel.error.value).toMatch(/connexió/)
    expect(viewModel.notice.value).toBeNull()
  })

  it('sends someone without an account back to register', async () => {
    const dependencies = fakeDependencies({ identifier: null })
    const viewModel = useVerifyViewModel(dependencies)

    await viewModel.start()

    expect(dependencies.goToRegister).toHaveBeenCalledTimes(1)
  })

  it('stays on the screen when it knows who is verifying', async () => {
    const dependencies = fakeDependencies()
    const viewModel = useVerifyViewModel(dependencies)

    await viewModel.start()

    expect(dependencies.goToRegister).not.toHaveBeenCalled()
  })
})
