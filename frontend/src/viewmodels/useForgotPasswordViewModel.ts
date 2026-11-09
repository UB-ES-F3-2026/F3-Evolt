import { computed, ref, watch } from 'vue'
import type { StatusJson } from '@/models/auth'
import { toUserMessage } from '@/models/errorMessages'
import { forgotPassword } from '@/services/authService'

// The same text whether the account exists or not (US-04), so nobody can find out which emails have one.
const LINK_SENT = "Si l'email és correcte, rebràs un enllaç per canviar la contrasenya"

export interface ForgotPasswordDependencies {
  forgotPassword: (identifier: string) => Promise<StatusJson>
}

/** "He oblidat la contrasenya" screen (US-04): asking for the recovery link. */
export function useForgotPasswordViewModel(
  dependencies: ForgotPasswordDependencies = { forgotPassword },
) {
  const identifier = ref('')
  const isSubmitting = ref(false)
  const error = ref<string | null>(null)
  const notice = ref<string | null>(null)

  const canSubmit = computed(() => identifier.value.trim() !== '' && !isSubmitting.value)

  watch(identifier, () => {
    error.value = null
    notice.value = null
  })

  async function submit(): Promise<boolean> {
    if (!canSubmit.value) return false
    isSubmitting.value = true
    error.value = null
    notice.value = null

    try {
      await dependencies.forgotPassword(identifier.value)
      notice.value = LINK_SENT
      return true
    } catch (failure) {
      error.value = toUserMessage(failure)
      return false
    } finally {
      isSubmitting.value = false
    }
  }

  return { identifier, error, notice, canSubmit, isSubmitting, submit }
}
