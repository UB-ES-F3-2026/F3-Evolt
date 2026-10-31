import { nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'
import { useRegisterViewModel, type RegisterDependencies } from './useRegisterViewModel'

function fakeDependencies(overrides: Partial<RegisterDependencies> = {}) {
  return {
    register: vi.fn(() => Promise.resolve({ identifier: 'ana@x.com', status: 'pending' as const })),
    goToVerification: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
}

function filledViewModel(dependencies: RegisterDependencies) {
  const viewModel = useRegisterViewModel(dependencies)
  viewModel.identifier.value = 'Ana@X.com'
  viewModel.password.value = 'Platja2026'
  viewModel.repeatedPassword.value = 'Platja2026'
  viewModel.acceptedTerms.value = true
  return viewModel
}

describe('useRegisterViewModel', () => {
  it('starts empty: no errors and the button disabled', () => {
    const viewModel = useRegisterViewModel(fakeDependencies())

    expect(viewModel.passwordError.value).toBeNull()
    expect(viewModel.repeatedPasswordError.value).toBeNull()
    expect(viewModel.submitError.value).toBeNull()
    expect(viewModel.canSubmit.value).toBe(false)
  })

  it('can be sent once everything is right', () => {
    expect(filledViewModel(fakeDependencies()).canSubmit.value).toBe(true)
  })

  it('stays disabled until the terms are accepted', () => {
    const viewModel = filledViewModel(fakeDependencies())

    viewModel.acceptedTerms.value = false

    expect(viewModel.canSubmit.value).toBe(false)
  })

  it('stays disabled with a weak password, and says why', () => {
    const viewModel = filledViewModel(fakeDependencies())

    viewModel.password.value = 'platja2026'
    viewModel.repeatedPassword.value = 'platja2026'

    expect(viewModel.passwordError.value).toMatch(/8 caràcters, una majúscula i un número/)
    expect(viewModel.canSubmit.value).toBe(false)
  })

  it('stays disabled when the passwords differ, and says why', () => {
    const viewModel = filledViewModel(fakeDependencies())

    viewModel.repeatedPassword.value = 'Platja2025'

    expect(viewModel.repeatedPasswordError.value).toBe('Les contrasenyes no coincideixen')
    expect(viewModel.canSubmit.value).toBe(false)
  })

  it('stays disabled without an email or phone', () => {
    const viewModel = filledViewModel(fakeDependencies())

    viewModel.identifier.value = '   '

    expect(viewModel.canSubmit.value).toBe(false)
  })

  it('sends the form and goes on with the identifier the backend normalized', async () => {
    const dependencies = fakeDependencies()
    const viewModel = filledViewModel(dependencies)

    expect(await viewModel.submit()).toBe(true)

    expect(dependencies.register).toHaveBeenCalledWith({
      identifier: 'Ana@X.com',
      password: 'Platja2026',
      acceptedTerms: true,
    })
    expect(dependencies.goToVerification).toHaveBeenCalledWith('ana@x.com')
    expect(viewModel.isSubmitting.value).toBe(false)
  })

  it('stays disabled while sending, so a double click sends once', async () => {
    const dependencies = fakeDependencies()
    const viewModel = filledViewModel(dependencies)

    const first = viewModel.submit()
    expect(viewModel.canSubmit.value).toBe(false)
    const second = await viewModel.submit()
    await first

    expect(second).toBe(false)
    expect(dependencies.register).toHaveBeenCalledTimes(1)
  })

  it('offers to log in when the account already exists', async () => {
    const failure = { code: 'ALREADY_REGISTERED', message: 'x' }
    const dependencies = fakeDependencies({ register: vi.fn(() => Promise.reject(failure)) })
    const viewModel = filledViewModel(dependencies)

    expect(await viewModel.submit()).toBe(false)

    expect(viewModel.submitError.value).toBe('Aquest email o telèfon ja té un compte.')
    expect(viewModel.isAlreadyRegistered.value).toBe(true)
    expect(dependencies.goToVerification).not.toHaveBeenCalled()
  })

  it('does not offer to log in for any other failure', async () => {
    const failure = { code: 'NETWORK_ERROR', message: 'x' }
    const viewModel = filledViewModel(fakeDependencies({ register: vi.fn(() => Promise.reject(failure)) }))

    await viewModel.submit()

    expect(viewModel.submitError.value).toMatch(/connexió/)
    expect(viewModel.isAlreadyRegistered.value).toBe(false)
  })

  it('clears the backend answer when the identifier changes', async () => {
    const failure = { code: 'ALREADY_REGISTERED', message: 'x' }
    const viewModel = filledViewModel(fakeDependencies({ register: vi.fn(() => Promise.reject(failure)) }))
    await viewModel.submit()

    viewModel.identifier.value = 'altra@x.com'
    await nextTick()

    expect(viewModel.submitError.value).toBeNull()
    expect(viewModel.isAlreadyRegistered.value).toBe(false)
  })
})
