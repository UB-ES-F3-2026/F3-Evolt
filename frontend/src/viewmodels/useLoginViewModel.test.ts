import { nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'
import { useLoginViewModel, type LoginDependencies } from './useLoginViewModel'

function fakeDependencies(overrides: Partial<LoginDependencies> = {}) {
  return {
    sessionExpired: false,
    login: vi.fn(() => Promise.resolve({ token: 'token-1' })),
    resendCode: vi.fn(() => Promise.resolve({ status: 'ok' as const })),
    saveToken: vi.fn(),
    goHome: vi.fn(() => Promise.resolve()),
    goToVerification: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
}

function filledViewModel(dependencies: LoginDependencies) {
  const viewModel = useLoginViewModel(dependencies)
  viewModel.identifier.value = 'demo@evolt.test'
  viewModel.password.value = 'Evolt2026'
  return viewModel
}

function failingLogin(code: string) {
  return vi.fn(() => Promise.reject({ code, message: 'x' }))
}

describe('useLoginViewModel', () => {
  it('needs both fields before sending', () => {
    const viewModel = useLoginViewModel(fakeDependencies())
    expect(viewModel.canSubmit.value).toBe(false)

    viewModel.identifier.value = 'demo@evolt.test'
    expect(viewModel.canSubmit.value).toBe(false)

    viewModel.password.value = 'Evolt2026'
    expect(viewModel.canSubmit.value).toBe(true)
  })

  it('keeps the token and opens Home with the right data', async () => {
    const dependencies = fakeDependencies()
    const viewModel = filledViewModel(dependencies)

    expect(await viewModel.submit()).toBe(true)

    expect(dependencies.login).toHaveBeenCalledWith({ identifier: 'demo@evolt.test', password: 'Evolt2026' })
    expect(dependencies.saveToken).toHaveBeenCalledWith('token-1')
    expect(dependencies.goHome).toHaveBeenCalledTimes(1)
  })

  it('stays disabled while sending, so a double click sends once', async () => {
    const dependencies = fakeDependencies()
    const viewModel = filledViewModel(dependencies)

    const first = viewModel.submit()
    expect(viewModel.canSubmit.value).toBe(false)
    expect(await viewModel.submit()).toBe(false)
    await first

    expect(dependencies.login).toHaveBeenCalledTimes(1)
    expect(viewModel.isSubmitting.value).toBe(false)
  })

  it.each([
    ['INVALID_CREDENTIALS', "L'email, el telèfon o la contrasenya no són correctes."],
    ['ACCOUNT_LOCKED', 'Compte bloquejat durant 15 minuts.'],
  ])('with %s shows its text and stays on the screen', async (code, text) => {
    const dependencies = fakeDependencies({ login: failingLogin(code) })
    const viewModel = filledViewModel(dependencies)

    expect(await viewModel.submit()).toBe(false)

    expect(viewModel.error.value).toBe(text)
    expect(dependencies.saveToken).not.toHaveBeenCalled()
    expect(dependencies.goHome).not.toHaveBeenCalled()
  })

  it('sends a pending account to verify, with a new code', async () => {
    const dependencies = fakeDependencies({ login: failingLogin('ACCOUNT_NOT_VERIFIED') })
    const viewModel = filledViewModel(dependencies)

    expect(await viewModel.submit()).toBe(false)

    expect(dependencies.resendCode).toHaveBeenCalledWith('demo@evolt.test')
    expect(dependencies.goToVerification).toHaveBeenCalledWith('demo@evolt.test')
    expect(viewModel.error.value).toBeNull()
  })

  it('goes to verify even if asking for the new code fails', async () => {
    const dependencies = fakeDependencies({
      login: failingLogin('ACCOUNT_NOT_VERIFIED'),
      resendCode: vi.fn(() => Promise.reject({ code: 'NETWORK_ERROR', message: 'x' })),
    })

    await filledViewModel(dependencies).submit()

    expect(dependencies.goToVerification).toHaveBeenCalledTimes(1)
  })

  it('explains that the session closed by inactivity', () => {
    const viewModel = useLoginViewModel(fakeDependencies({ sessionExpired: true }))

    expect(viewModel.notice.value).toBe("La sessió s'ha tancat per inactivitat.")
  })

  it('says nothing about inactivity on a normal visit', () => {
    expect(useLoginViewModel(fakeDependencies()).notice.value).toBeNull()
  })

  it('clears the error and the notice when typing again', async () => {
    const viewModel = filledViewModel(
      fakeDependencies({ sessionExpired: true, login: failingLogin('INVALID_CREDENTIALS') }),
    )
    await viewModel.submit()
    expect(viewModel.error.value).not.toBeNull()

    viewModel.password.value = 'Altra2026'
    await nextTick()

    expect(viewModel.error.value).toBeNull()
    expect(viewModel.notice.value).toBeNull()
  })
})
