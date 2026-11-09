import { nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'
import { useForgotPasswordViewModel } from './useForgotPasswordViewModel'

const LINK_SENT = "Si l'email és correcte, rebràs un enllaç per canviar la contrasenya"

function fakeDependencies() {
  return { forgotPassword: vi.fn(() => Promise.resolve({ status: 'ok' as const })) }
}

describe('useForgotPasswordViewModel', () => {
  it('needs something typed before sending', () => {
    const viewModel = useForgotPasswordViewModel(fakeDependencies())
    expect(viewModel.canSubmit.value).toBe(false)

    viewModel.identifier.value = 'demo@evolt.test'
    expect(viewModel.canSubmit.value).toBe(true)
  })

  it('asks for the link and shows the agreed text', async () => {
    const dependencies = fakeDependencies()
    const viewModel = useForgotPasswordViewModel(dependencies)
    viewModel.identifier.value = 'demo@evolt.test'

    expect(await viewModel.submit()).toBe(true)

    expect(dependencies.forgotPassword).toHaveBeenCalledWith('demo@evolt.test')
    expect(viewModel.notice.value).toBe(LINK_SENT)
    expect(viewModel.isSubmitting.value).toBe(false)
  })

  it('shows a failure instead of pretending the link was sent', async () => {
    const failure = { code: 'NETWORK_ERROR', message: 'x' }
    const viewModel = useForgotPasswordViewModel({ forgotPassword: vi.fn(() => Promise.reject(failure)) })
    viewModel.identifier.value = 'demo@evolt.test'

    expect(await viewModel.submit()).toBe(false)

    expect(viewModel.error.value).toMatch(/connexió/)
    expect(viewModel.notice.value).toBeNull()
  })

  it('clears the previous answer when typing again', async () => {
    const viewModel = useForgotPasswordViewModel(fakeDependencies())
    viewModel.identifier.value = 'demo@evolt.test'
    await viewModel.submit()

    viewModel.identifier.value = 'ningu@x.com'
    await nextTick()

    expect(viewModel.notice.value).toBeNull()
  })
})
