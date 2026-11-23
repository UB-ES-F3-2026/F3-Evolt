import { ref } from 'vue'
import { isApiError } from '@/models/apiError'
import { messageForCode, toUserMessage } from '@/models/errorMessages'
import type { UserSummary } from '@/models/user'
import { getUser } from '@/services/usersService'

export interface SendPaymentDependencies {
  getUser: (userId: string) => Promise<UserSummary>
}

/**
 * «Enviar» screen (`/pagaments/enviar?to=<id>`). For US-13 it shows who the money goes to,
 * checked again with the API, so reloading the page keeps the recipient. The amount and
 * the concept come with US-14 (T14.3).
 */
export function useSendPaymentViewModel(
  toUserId: string | undefined,
  dependencies: SendPaymentDependencies = { getUser },
) {
  const recipient = ref<UserSummary | null>(null)
  const isLoading = ref(true)
  const error = ref<string | null>(null)
  /** The recipient is not a user: trying again cannot fix it, so the screen offers to choose another. */
  const isRecipientMissing = ref(false)

  async function load(): Promise<void> {
    isLoading.value = true
    error.value = null
    isRecipientMissing.value = false
    try {
      // Without `to` there is nobody to send to: the same answer as an id that is not a user.
      if (toUserId === undefined || toUserId === '') {
        error.value = messageForCode('RECIPIENT_NOT_FOUND')
        isRecipientMissing.value = true
        return
      }
      recipient.value = await dependencies.getUser(toUserId)
    } catch (failure) {
      error.value = toUserMessage(failure)
      isRecipientMissing.value = isApiError(failure) && failure.code === 'RECIPIENT_NOT_FOUND'
    } finally {
      isLoading.value = false
    }
  }

  return { recipient, isLoading, error, isRecipientMissing, load }
}
