import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { isApiError } from '@/models/apiError'
import { CODE_LENGTH, type SessionJson, type StatusJson, type VerifyRequest } from '@/models/auth'
import { toUserMessage } from '@/models/errorMessages'
import { resendCode, verify } from '@/services/authService'
import { saveToken } from '@/services/session'

const NEW_CODE_SENT = "T'hem enviat un codi nou."

export interface VerifyDependencies {
  /** Who is verifying; null when someone opens the screen directly. */
  identifier: string | null
  verify: (request: VerifyRequest) => Promise<SessionJson>
  resendCode: (identifier: string) => Promise<StatusJson>
  saveToken: (token: string) => void
  goHome: () => Promise<unknown>
  goToRegister: () => Promise<unknown>
}

/** Verification screen (US-02): the 6 digits, sending them, and asking for a new code. */
export function useVerifyViewModel(dependencies: VerifyDependencies = defaultDependencies()) {
  const { identifier } = dependencies
  const code = ref('')
  const error = ref<string | null>(null)
  const notice = ref<string | null>(null)
  const isLocked = ref(false)
  const isSubmitting = ref(false)
  const isResending = ref(false)

  // There is no button in US-02: the last digit sends the code.
  watch(code, (typed) => {
    if (typed === '') return
    error.value = null
    notice.value = null
    if (typed.length === CODE_LENGTH) void submit()
  })

  async function start(): Promise<void> {
    if (identifier === null) await dependencies.goToRegister()
  }

  async function submit(): Promise<boolean> {
    if (identifier === null || code.value.length !== CODE_LENGTH) return false
    if (isLocked.value || isSubmitting.value) return false
    isSubmitting.value = true

    try {
      const session = await dependencies.verify({ identifier, code: code.value })
      dependencies.saveToken(session.token)
      await dependencies.goHome()
      return true
    } catch (failure) {
      error.value = toUserMessage(failure)
      isLocked.value = isApiError(failure) && failure.code === 'TOO_MANY_ATTEMPTS'
      // Empty boxes to type again; the watch above keeps the error until then.
      code.value = ''
      return false
    } finally {
      isSubmitting.value = false
    }
  }

  async function resend(): Promise<void> {
    if (identifier === null || isResending.value) return
    isResending.value = true
    notice.value = null

    try {
      await dependencies.resendCode(identifier)
      code.value = ''
      error.value = null
      isLocked.value = false
      notice.value = NEW_CODE_SENT
    } catch (failure) {
      error.value = toUserMessage(failure)
    } finally {
      isResending.value = false
    }
  }

  return {
    identifier,
    code,
    codeLength: CODE_LENGTH,
    error,
    notice,
    isLocked,
    isSubmitting,
    isResending,
    start,
    submit,
    resend,
  }
}

function defaultDependencies(): VerifyDependencies {
  const router = useRouter()
  const saved: unknown = window.history.state?.identifier
  return {
    identifier: typeof saved === 'string' ? saved : null,
    verify,
    resendCode,
    saveToken,
    goHome: () => router.replace({ name: 'home' }),
    goToRegister: () => router.replace({ name: 'register' }),
  }
}
