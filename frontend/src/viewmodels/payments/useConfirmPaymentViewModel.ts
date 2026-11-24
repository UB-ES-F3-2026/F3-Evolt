import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { isApiError } from '@/models/apiError'
import { messageForCode, toUserMessage } from '@/models/errorMessages'
import type { Home } from '@/models/home'
import { formatCents } from '@/models/money'
import { transferLimitMessage, type Transfer, type TransferLimit, type TransferRequest } from '@/models/transfer'
import { displayName, type UserSummary } from '@/models/user'
import { getHome } from '@/services/homeService'
import { getTransferLimit, sendTransfer } from '@/services/payments/transfersService'
import { getUser } from '@/services/usersService'

// Long enough to read the confirmation before going back to Inici (US-14).
const CONFIRMATION_MS = 1500

export interface ConfirmPaymentDependencies {
  getUser: (userId: string) => Promise<UserSummary>
  getHome: () => Promise<Home>
  getTransferLimit: () => Promise<TransferLimit>
  sendTransfer: (request: TransferRequest) => Promise<Transfer>
  goHome: () => Promise<unknown>
  pause: (ms: number) => Promise<void>
}

/** What «Enviar» put in the URL: `?to=<id>&amount=<cents>&concept=<text>`. */
export interface ConfirmPaymentQuery {
  to?: string
  amount?: string
  concept?: string
}

/**
 * «Confirmar» screen (`/pagaments/confirmar`, US-14): the summary, «Confirmar enviament»
 * and the green tick as a state of this same screen. The server checks balance and limit
 * again; if they changed, the same message as in «Enviar» shows and nothing is sent.
 */
export function useConfirmPaymentViewModel(
  query: ConfirmPaymentQuery,
  dependencies: ConfirmPaymentDependencies = defaultDependencies(),
) {
  const amount = Number(query.amount)
  const concept = query.concept?.trim() ? query.concept.trim() : null
  const isDraftValid = query.to !== undefined && query.to !== '' && Number.isSafeInteger(amount) && amount > 0

  const recipient = ref<UserSummary | null>(null)
  const balance = ref<number | null>(null)
  const limit = ref<TransferLimit | null>(null)
  const isLoading = ref(true)
  const loadError = ref<string | null>(null)
  /** The recipient is not a user (anymore): the screen offers to choose another. */
  const isRecipientMissing = ref(false)

  const isSubmitting = ref(false)
  const submitError = ref<string | null>(null)
  const confirmation = ref<string | null>(null)

  const canConfirm = computed(() => recipient.value !== null && !isSubmitting.value && confirmation.value === null)

  async function load(): Promise<void> {
    isLoading.value = true
    loadError.value = null
    isRecipientMissing.value = false
    try {
      // A URL typed by hand without a valid amount or recipient cannot be confirmed.
      if (!isDraftValid || query.to === undefined) {
        loadError.value = messageForCode('VALIDATION_ERROR')
        isRecipientMissing.value = true
        return
      }
      const [user, home, todayLimit] = await Promise.all([
        dependencies.getUser(query.to),
        dependencies.getHome(),
        dependencies.getTransferLimit(),
      ])
      recipient.value = user
      balance.value = home.balance
      limit.value = todayLimit
    } catch (failure) {
      loadError.value = toUserMessage(failure)
      isRecipientMissing.value = isApiError(failure) && failure.code === 'RECIPIENT_NOT_FOUND'
    } finally {
      isLoading.value = false
    }
  }

  async function confirm(): Promise<boolean> {
    if (!canConfirm.value || recipient.value === null) return false
    isSubmitting.value = true
    submitError.value = null

    try {
      const result = await dependencies.sendTransfer({ toUserId: recipient.value.id, amount, concept })
      // The answer has the new balance, so nothing has to be asked again (§13.4).
      balance.value = result.balance
      confirmation.value = `Has enviat ${formatCents(result.movement.amount)} a ${displayName(result.recipient)}`
    } catch (failure) {
      submitError.value = failureMessage(failure)
      isRecipientMissing.value = isApiError(failure) && failure.code === 'RECIPIENT_NOT_FOUND'
      isSubmitting.value = false
      return false
    }

    await dependencies.pause(CONFIRMATION_MS)
    isSubmitting.value = false
    await dependencies.goHome()
    return true
  }

  /** The limit reads as in «Enviar» («Has superat el límit diari de 1.000,00 €.», US-14). */
  function failureMessage(failure: unknown): string {
    if (isApiError(failure) && failure.code === 'TRANSFER_LIMIT_EXCEEDED' && limit.value !== null) {
      return transferLimitMessage(limit.value.dailyLimit)
    }
    return toUserMessage(failure)
  }

  return {
    recipient,
    amount,
    concept,
    balance,
    isLoading,
    loadError,
    isRecipientMissing,
    isSubmitting,
    submitError,
    confirmation,
    canConfirm,
    load,
    confirm,
  }
}

function defaultDependencies(): ConfirmPaymentDependencies {
  const router = useRouter()
  return {
    getUser,
    getHome,
    getTransferLimit,
    sendTransfer,
    // Replace: going back from Inici must not reopen a transfer that was already sent.
    goHome: () => router.replace({ name: 'home' }),
    pause: (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  }
}
