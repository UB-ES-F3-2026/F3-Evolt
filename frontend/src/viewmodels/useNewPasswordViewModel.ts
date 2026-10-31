import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { isApiError } from '@/models/apiError'
import type { ResetPasswordRequest, StatusJson } from '@/models/auth'
import { messageForCode, toUserMessage } from '@/models/errorMessages'
import { resetPassword } from '@/services/authService'
import { closeSession } from '@/services/session'
import { usePasswordFields } from './usePasswordFields'

export interface NewPasswordDependencies {
  /** The one in the recovery link; null when the link has none. */
  token: string | null
  resetPassword: (request: ResetPasswordRequest) => Promise<StatusJson>
  closeSession: () => void
}

/** "Nova contrasenya" screen (US-04): the new password, with the same checks as the register. */
export function useNewPasswordViewModel(dependencies: NewPasswordDependencies = defaultDependencies()) {
  const { token } = dependencies
  const isSubmitting = ref(false)
  const isChanged = ref(false)
  const submitError = ref<string | null>(null)
  const isLinkExpired = ref(token === null)
  const { password, repeatedPassword, passwordError, repeatedPasswordError, arePasswordsValid } =
    usePasswordFields()

  const linkExpiredMessage = messageForCode('RESET_LINK_EXPIRED')
  const canSubmit = computed(() => arePasswordsValid.value && !isSubmitting.value)

  watch(password, () => {
    submitError.value = null
  })

  async function submit(): Promise<boolean> {
    if (token === null || !canSubmit.value) return false
    isSubmitting.value = true
    submitError.value = null

    try {
      await dependencies.resetPassword({ token, password: password.value })
      // The backend has just closed every session of this person (docs/api.md §8.11), this one too.
      dependencies.closeSession()
      isChanged.value = true
      return true
    } catch (failure) {
      if (isApiError(failure) && failure.code === 'RESET_LINK_EXPIRED') {
        isLinkExpired.value = true
      } else {
        submitError.value = toUserMessage(failure)
      }
      return false
    } finally {
      isSubmitting.value = false
    }
  }

  return {
    password,
    repeatedPassword,
    passwordError,
    repeatedPasswordError,
    submitError,
    isLinkExpired,
    linkExpiredMessage,
    isChanged,
    canSubmit,
    isSubmitting,
    submit,
  }
}

function defaultDependencies(): NewPasswordDependencies {
  const { token } = useRoute().query
  return {
    token: typeof token === 'string' ? token : null,
    resetPassword,
    closeSession,
  }
}
