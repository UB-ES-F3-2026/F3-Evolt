import { computed, ref, toValue, type MaybeRefOrGetter } from 'vue'
import { useRouter } from 'vue-router'
import { isApiError } from '@/models/apiError'
import { messageForCode, toUserMessage } from '@/models/errorMessages'
import type { Home } from '@/models/home'
import { eurosToCents, formatCents } from '@/models/money'
import {
  cleanConcept,
  MAX_TRANSFER_CONCEPT_LENGTH,
  pressAmountKey,
  transferAmountError,
  type TransferLimit,
} from '@/models/transfer'
import type { UserSummary } from '@/models/user'
import { getHome } from '@/services/homeService'
import { getTransferLimit } from '@/services/transfersService'
import { getUser } from '@/services/usersService'

/** What «Continuar» hands to «Confirmar», through the URL so a reload keeps it. */
export interface PaymentDraft {
  to: string
  amount: number
  concept: string | null
}

export interface SendPaymentDependencies {
  getUser: (userId: string) => Promise<UserSummary>
  getHome: () => Promise<Home>
  getTransferLimit: () => Promise<TransferLimit>
  goToConfirm: (draft: PaymentDraft) => Promise<unknown>
}

/**
 * «Enviar» screen (`/pagaments/enviar?to=<id>`, US-13 and US-14): who gets the money,
 * the amount typed on the keypad and an optional concept. «Continuar» stays disabled while
 * the amount is empty or zero, above the balance or above what is left of today's limit.
 */
export function useSendPaymentViewModel(
  /** The `?to=` of the URL, read on every `load`, so a new recipient in the same screen is asked again (#212). */
  toUserId: MaybeRefOrGetter<string | undefined>,
  dependencies: SendPaymentDependencies = defaultDependencies(),
) {
  const recipient = ref<UserSummary | null>(null)
  const balance = ref<number | null>(null)
  const limit = ref<TransferLimit | null>(null)
  const isLoading = ref(true)
  const error = ref<string | null>(null)
  /** The recipient is not a user: trying again cannot fix it, so the screen offers to choose another. */
  const isRecipientMissing = ref(false)

  const amount = ref('')
  const concept = ref('')

  const cents = computed(() => eurosToCents(amount.value.endsWith(',') ? amount.value.slice(0, -1) : amount.value))
  /** The amount as the mockup shows it while typing: «4.000,00 €», «0,00 €» when empty. */
  const amountText = computed(() => formatCents(cents.value ?? 0))
  const amountError = computed(() =>
    balance.value === null || limit.value === null ? null : transferAmountError(cents.value, balance.value, limit.value),
  )
  const canContinue = computed(
    () => recipient.value !== null && cents.value !== null && cents.value > 0 && amountError.value === null,
  )

  async function load(): Promise<void> {
    isLoading.value = true
    error.value = null
    isRecipientMissing.value = false
    recipient.value = null
    const userId = toValue(toUserId)
    try {
      // Without `to` there is nobody to send to: the same answer as an id that is not a user.
      if (userId === undefined || userId === '') {
        error.value = messageForCode('RECIPIENT_NOT_FOUND')
        isRecipientMissing.value = true
        return
      }
      // Balance and limit are asked on opening, so the screen can answer before sending (US-14).
      const [user, home, todayLimit] = await Promise.all([
        dependencies.getUser(userId),
        dependencies.getHome(),
        dependencies.getTransferLimit(),
      ])
      recipient.value = user
      balance.value = home.balance
      limit.value = todayLimit
    } catch (failure) {
      error.value = toUserMessage(failure)
      isRecipientMissing.value = isApiError(failure) && failure.code === 'RECIPIENT_NOT_FOUND'
    } finally {
      isLoading.value = false
    }
  }

  /** One key of the numeric keypad: a digit, «,» or «⌫». */
  function pressKey(key: string): void {
    amount.value = pressAmountKey(amount.value, key)
  }

  async function continueToConfirm(): Promise<boolean> {
    if (!canContinue.value || recipient.value === null || cents.value === null) return false
    await dependencies.goToConfirm({
      to: recipient.value.id,
      amount: cents.value,
      concept: cleanConcept(concept.value),
    })
    return true
  }

  return {
    recipient,
    balance,
    isLoading,
    error,
    isRecipientMissing,
    amount,
    amountText,
    concept,
    maxConceptLength: MAX_TRANSFER_CONCEPT_LENGTH,
    amountError,
    canContinue,
    load,
    pressKey,
    continueToConfirm,
  }
}

function defaultDependencies(): SendPaymentDependencies {
  const router = useRouter()
  return {
    getUser,
    getHome,
    getTransferLimit,
    goToConfirm: ({ to, amount, concept }) =>
      router.push({
        name: 'confirm-payment',
        query: concept === null ? { to, amount: String(amount) } : { to, amount: String(amount), concept },
      }),
  }
}
