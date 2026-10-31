import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { isApiError } from '@/models/apiError'
import type { LoginRequest, SessionJson, StatusJson } from '@/models/auth'
import { messageForCode, toUserMessage } from '@/models/errorMessages'
import { login, resendCode } from '@/services/authService'
import { saveToken } from '@/services/session'

export interface LoginDependencies {
  /** The app came here because the session closed by itself. */
  sessionExpired: boolean
  login: (request: LoginRequest) => Promise<SessionJson>
  resendCode: (identifier: string) => Promise<StatusJson>
  saveToken: (token: string) => void
  goHome: () => Promise<unknown>
  goToVerification: (identifier: string) => Promise<unknown>
}

/** Login screen (US-03): the form, opening the session, and where each answer leads. */
export function useLoginViewModel(dependencies: LoginDependencies = defaultDependencies()) {
  const identifier = ref('')
  const password = ref('')
  const isSubmitting = ref(false)
  const error = ref<string | null>(null)
  const notice = ref(dependencies.sessionExpired ? messageForCode('SESSION_EXPIRED') : null)

  const canSubmit = computed(
    () => identifier.value.trim() !== '' && password.value !== '' && !isSubmitting.value,
  )

  // New data makes the previous answer stale, and the person has already read the notice.
  watch([identifier, password], () => {
    error.value = null
    notice.value = null
  })

  async function submit(): Promise<boolean> {
    if (!canSubmit.value) return false
    isSubmitting.value = true
    error.value = null
    notice.value = null

    try {
      const session = await dependencies.login({ identifier: identifier.value, password: password.value })
      dependencies.saveToken(session.token)
      await dependencies.goHome()
      return true
    } catch (failure) {
      if (isApiError(failure) && failure.code === 'ACCOUNT_NOT_VERIFIED') {
        await sendToVerification()
      } else {
        error.value = toUserMessage(failure)
      }
      return false
    } finally {
      isSubmitting.value = false
    }
  }

  // The first code may have expired long ago, so a new one goes out (docs/api.md §8.8).
  // If that fails, the next screen still has "Envia'm un codi nou".
  async function sendToVerification(): Promise<void> {
    await dependencies.resendCode(identifier.value).catch(() => undefined)
    await dependencies.goToVerification(identifier.value)
  }

  return { identifier, password, error, notice, canSubmit, isSubmitting, submit }
}

function defaultDependencies(): LoginDependencies {
  const router = useRouter()
  const route = useRoute()
  return {
    sessionExpired: route.query.expired === '1',
    login,
    resendCode,
    saveToken,
    goHome: () => router.replace({ name: 'home' }),
    goToVerification: (identifier) => router.push({ name: 'verify', state: { identifier } }),
  }
}
