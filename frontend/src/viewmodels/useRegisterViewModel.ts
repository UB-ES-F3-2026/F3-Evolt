import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { isApiError } from '@/models/apiError'
import type { RegisterJson, RegisterRequest } from '@/models/auth'
import { toUserMessage } from '@/models/errorMessages'
import { register } from '@/services/authService'
import { usePasswordFields } from './usePasswordFields'

export interface RegisterDependencies {
  register: (request: RegisterRequest) => Promise<RegisterJson>
  goToVerification: (identifier: string) => Promise<unknown>
}

/** Register screen (US-01): the form, its checks, and creating the pending account. */
export function useRegisterViewModel(dependencies: RegisterDependencies = defaultDependencies()) {
  const identifier = ref('')
  const acceptedTerms = ref(false)
  const isSubmitting = ref(false)
  const submitError = ref<string | null>(null)
  const isAlreadyRegistered = ref(false)
  const { password, repeatedPassword, passwordError, repeatedPasswordError, arePasswordsValid } =
    usePasswordFields()

  const canSubmit = computed(
    () =>
      identifier.value.trim() !== '' &&
      arePasswordsValid.value &&
      acceptedTerms.value &&
      !isSubmitting.value,
  )

  // New data makes the previous answer from the backend stale.
  watch([identifier, password], () => {
    submitError.value = null
    isAlreadyRegistered.value = false
  })

  async function submit(): Promise<boolean> {
    if (!canSubmit.value) return false
    isSubmitting.value = true
    submitError.value = null
    isAlreadyRegistered.value = false

    try {
      const account = await dependencies.register({
        identifier: identifier.value,
        password: password.value,
        acceptedTerms: acceptedTerms.value,
      })
      await dependencies.goToVerification(account.identifier)
      return true
    } catch (failure) {
      submitError.value = toUserMessage(failure)
      isAlreadyRegistered.value = isApiError(failure) && failure.code === 'ALREADY_REGISTERED'
      return false
    } finally {
      isSubmitting.value = false
    }
  }

  return {
    identifier,
    password,
    repeatedPassword,
    acceptedTerms,
    passwordError,
    repeatedPasswordError,
    submitError,
    isAlreadyRegistered,
    canSubmit,
    isSubmitting,
    submit,
  }
}

function defaultDependencies(): RegisterDependencies {
  const router = useRouter()
  return {
    register,
    // In the history state and not in the URL: an email or phone must not end up in the address bar.
    goToVerification: (identifier) => router.push({ path: '/verify', state: { identifier } }),
  }
}
