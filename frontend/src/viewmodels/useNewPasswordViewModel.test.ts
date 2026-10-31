import { nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'
import { useNewPasswordViewModel, type NewPasswordDependencies } from './useNewPasswordViewModel'

function fakeDependencies(overrides: Partial<NewPasswordDependencies> = {}) {
  return {
    token: 'token-1',
    resetPassword: vi.fn(() => Promise.resolve({ status: 'ok' as const })),
    closeSession: vi.fn(),
    ...overrides,
  }
}

function filledViewModel(dependencies: NewPasswordDependencies) {
  const viewModel = useNewPasswordViewModel(dependencies)
  viewModel.password.value = 'NovaClau2026'
  viewModel.repeatedPassword.value = 'NovaClau2026'
  return viewModel
}

function failingReset(code: string) {
  return vi.fn(() => Promise.reject({ code, message: 'x' }))
}

describe('useNewPasswordViewModel', () => {
  it('applies the same checks as the register', () => {
    const viewModel = useNewPasswordViewModel(fakeDependencies())

    viewModel.password.value = 'novaclau'

    expect(viewModel.passwordError.value).toBe('La contrasenya ha de tenir 8 caràcters, una majúscula i un número.')
    expect(viewModel.canSubmit.value).toBe(false)
  })

  it('changes the password with the token of the link and closes the local session', async () => {
    const dependencies = fakeDependencies()
    const viewModel = filledViewModel(dependencies)

    expect(await viewModel.submit()).toBe(true)

    expect(dependencies.resetPassword).toHaveBeenCalledWith({ token: 'token-1', password: 'NovaClau2026' })
    expect(dependencies.closeSession).toHaveBeenCalledTimes(1)
    expect(viewModel.isChanged.value).toBe(true)
    expect(viewModel.isSubmitting.value).toBe(false)
  })

  it('says the link expired and offers a new one', async () => {
    const dependencies = fakeDependencies({ resetPassword: failingReset('RESET_LINK_EXPIRED') })
    const viewModel = filledViewModel(dependencies)

    expect(await viewModel.submit()).toBe(false)

    expect(viewModel.isLinkExpired.value).toBe(true)
    expect(viewModel.linkExpiredMessage).toBe('Aquest enllaç ha caducat.')
    expect(viewModel.isChanged.value).toBe(false)
    expect(dependencies.closeSession).not.toHaveBeenCalled()
  })

  it('treats a link without a token as expired, and sends nothing', async () => {
    const dependencies = fakeDependencies({ token: null })
    const viewModel = filledViewModel(dependencies)

    expect(viewModel.isLinkExpired.value).toBe(true)
    expect(await viewModel.submit()).toBe(false)
    expect(dependencies.resetPassword).not.toHaveBeenCalled()
  })

  it('lets the person try again with the same link after a weak password', async () => {
    const dependencies = fakeDependencies({ resetPassword: failingReset('WEAK_PASSWORD') })
    const viewModel = filledViewModel(dependencies)

    await viewModel.submit()

    expect(viewModel.submitError.value).toMatch(/8 caràcters/)
    expect(viewModel.isLinkExpired.value).toBe(false)
    expect(viewModel.canSubmit.value).toBe(true)
  })

  it('clears the backend answer when the password changes', async () => {
    const viewModel = filledViewModel(fakeDependencies({ resetPassword: failingReset('NETWORK_ERROR') }))
    await viewModel.submit()
    expect(viewModel.submitError.value).toMatch(/connexió/)

    viewModel.password.value = 'AltraClau2026'
    await nextTick()

    expect(viewModel.submitError.value).toBeNull()
  })
})
