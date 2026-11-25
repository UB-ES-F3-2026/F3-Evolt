import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { messageForCode, toUserMessage } from '@/models/errorMessages'
import { isApiError } from '@/models/apiError'
import { eurosToCents } from '@/models/money'
import {
  MAX_REQUEST_CENTS,
  MAX_REQUEST_CONCEPT_LENGTH,
  REQUEST_AMOUNT_OVER_LIMIT_MESSAGE,
  type MoneyRequest,
  type NewMoneyRequest,
} from '@/models/moneyRequest'
import { displayName, type UserSummary } from '@/models/user'
import { createMoneyRequest } from '@/services/requests/moneyRequestsService'
import { searchUsers } from '@/services/usersService'
import { usePaymentsViewModel } from '@/viewmodels/payments/usePaymentsViewModel'

// Long enough to read the confirmation before going to the list (US-15).
const CONFIRMATION_MS = 1500

export interface NewMoneyRequestDependencies {
  searchUsers: (q: string) => Promise<UserSummary[]>
  wait: (ms: number) => Promise<void>
  createMoneyRequest: (request: NewMoneyRequest) => Promise<MoneyRequest>
  goToRequests: () => Promise<unknown>
}

/**
 * «Demanar diners» screen (`/requests/new`, US-15): the recipient chosen with the search of
 * US-13, the amount and the concept. «Enviar sol·licitud» stays disabled until the three
 * are valid; an error from the server keeps everything typed.
 */
export function useNewMoneyRequestViewModel(dependencies: NewMoneyRequestDependencies = defaultDependencies()) {
  // The same search as «Enviar diners» (US-13): it never returns the person asking.
  const search = usePaymentsViewModel({ searchUsers: dependencies.searchUsers, wait: dependencies.wait })

  const recipient = ref<UserSummary | null>(null)
  const amount = ref('')
  const concept = ref('')

  const isSubmitting = ref(false)
  const submitError = ref<string | null>(null)
  const confirmation = ref<string | null>(null)

  const cents = computed(() => eurosToCents(amount.value))
  // Only what the form can tell before sending; an empty amount has no message yet.
  const amountError = computed(() => {
    const typed = amount.value.trim()
    if (typed === '') return null
    if (typed.startsWith('-')) return messageForCode('INVALID_AMOUNT')
    if (cents.value === null) return null
    if (cents.value <= 0) return messageForCode('INVALID_AMOUNT')
    if (cents.value > MAX_REQUEST_CENTS) return REQUEST_AMOUNT_OVER_LIMIT_MESSAGE
    return null
  })
  const isConceptValid = computed(() => {
    const length = concept.value.trim().length
    return length >= 1 && length <= MAX_REQUEST_CONCEPT_LENGTH
  })
  const canSend = computed(
    () =>
      recipient.value !== null &&
      cents.value !== null &&
      cents.value > 0 &&
      amountError.value === null &&
      isConceptValid.value &&
      !isSubmitting.value &&
      confirmation.value === null,
  )

  // A change makes the previous answer from the server stale.
  watch([recipient, amount, concept], () => {
    submitError.value = null
  })

  function choose(user: UserSummary): void {
    recipient.value = user
  }

  async function send(): Promise<boolean> {
    if (!canSend.value || recipient.value === null || cents.value === null) return false
    isSubmitting.value = true
    submitError.value = null
    try {
      const created = await dependencies.createMoneyRequest({
        toUserId: recipient.value.id,
        amount: cents.value,
        concept: concept.value.trim(),
      })
      confirmation.value = `Sol·licitud enviada a ${displayName(created.to)}.`
    } catch (failure) {
      // Recipient, amount and concept stay as they are (US-15).
      submitError.value =
        isApiError(failure) && failure.code === 'AMOUNT_OVER_LIMIT'
          ? REQUEST_AMOUNT_OVER_LIMIT_MESSAGE
          : toUserMessage(failure)
      isSubmitting.value = false
      return false
    }
    await dependencies.wait(CONFIRMATION_MS)
    isSubmitting.value = false
    await dependencies.goToRequests()
    return true
  }

  return {
    ...search,
    recipient,
    amount,
    concept,
    maxConceptLength: MAX_REQUEST_CONCEPT_LENGTH,
    amountError,
    canSend,
    isSubmitting,
    submitError,
    confirmation,
    choose,
    send,
  }
}

function defaultDependencies(): NewMoneyRequestDependencies {
  const router = useRouter()
  return {
    searchUsers,
    wait: (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
    createMoneyRequest,
    // Replace: going back from the list must not reopen a request that was already sent.
    goToRequests: () => router.replace({ name: 'money-requests' }),
  }
}
