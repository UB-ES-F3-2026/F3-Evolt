import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { messageForCode, toUserMessage } from '@/models/errorMessages'
import { eurosToCents, formatCents } from '@/models/money'
import { MAX_TOPUP_CENTS, type TopupResult } from '@/models/topup'
import { createTopup } from '@/services/topupService'

const FORMAT_ERROR = 'Escriu un import en euros, amb 2 decimals com a màxim.'

// Long enough to read the confirmation before going back to Home.
const CONFIRMATION_MS = 1500

export interface TopUpDependencies {
  createTopup: (amountCents: number) => Promise<TopupResult>
  goHome: () => Promise<unknown>
  pause: (ms: number) => Promise<void>
}

/** Top-up screen (US-09): the amount typed in euros, its checks, and sending it. */
export function useTopUpViewModel(dependencies: TopUpDependencies = defaultDependencies()) {
  const amount = ref('')
  const isSubmitting = ref(false)
  const confirmation = ref<string | null>(null)
  const submitError = ref<string | null>(null)

  const cents = computed(() => eurosToCents(amount.value))

  // Same limits as the backend, checked here only to answer before sending.
  const amountError = computed(() => {
    if (amount.value.trim() === '') return null
    if (cents.value === null) return FORMAT_ERROR
    if (cents.value <= 0) return messageForCode('INVALID_AMOUNT')
    if (cents.value > MAX_TOPUP_CENTS) return messageForCode('AMOUNT_OVER_LIMIT')
    return null
  })

  const error = computed(() => submitError.value ?? amountError.value)
  const canSubmit = computed(
    () => cents.value !== null && amountError.value === null && !isSubmitting.value,
  )

  // A new amount makes the previous answer from the backend stale.
  watch(amount, () => {
    submitError.value = null
  })

  async function submit(): Promise<boolean> {
    if (!canSubmit.value || cents.value === null) return false
    isSubmitting.value = true
    submitError.value = null

    try {
      const result = await dependencies.createTopup(cents.value)
      confirmation.value = `Recàrrega feta: +${formatCents(result.movement.amount)}`
    } catch (failure) {
      submitError.value = toUserMessage(failure)
      isSubmitting.value = false
      return false
    }

    // The button stays disabled while the confirmation is on screen.
    await dependencies.pause(CONFIRMATION_MS)
    isSubmitting.value = false
    await dependencies.goHome()
    return true
  }

  // For the help text under the field, so the view never types the limit itself.
  const maxAmountCents = MAX_TOPUP_CENTS

  return { amount, error, canSubmit, isSubmitting, confirmation, maxAmountCents, submit }
}

function defaultDependencies(): TopUpDependencies {
  const router = useRouter()
  return {
    createTopup,
    goHome: () => router.push({ name: 'home' }),
    pause: (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  }
}
