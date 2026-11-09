import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { AMOUNT_FORMAT_MESSAGE, messageForCode, toUserMessage } from '@/models/errorMessages'
import type { Home } from '@/models/home'
import { eurosToCents, formatCents } from '@/models/money'
import type { Contribution, Pot } from '@/models/pot'
import { getHome } from '@/services/homeService'
import { contribute, getPots } from '@/services/potsService'

// Long enough to read the confirmation before going back to the pot.
const CONFIRMATION_MS = 1500

export interface ContributeDependencies {
  getHome: () => Promise<Home>
  getPots: () => Promise<Pot[]>
  contribute: (potId: string, amountCents: number) => Promise<Contribution>
  goToPot: () => Promise<unknown>
  pause: (ms: number) => Promise<void>
}

/** «Aportar a <nom>» screen (US-18): the amount in euros, its checks, and moving it to the pot. */
export function useContributeViewModel(
  potId: string,
  dependencies: ContributeDependencies = defaultDependencies(potId),
) {
  const pot = ref<Pot | null>(null)
  /** Main account balance, in cents: the most that can be moved (US-18, criterion 3). */
  const balance = ref<number | null>(null)
  const isLoading = ref(true)
  const loadError = ref<string | null>(null)

  const amount = ref('')
  const isSubmitting = ref(false)
  const submitError = ref<string | null>(null)
  const confirmation = ref<string | null>(null)

  const title = computed(() => (pot.value === null ? 'Aportar' : `Aportar a ${pot.value.name}`))
  const cents = computed(() => eurosToCents(amount.value))

  // Same rules as the backend (docs/api.md §9.4), checked here only to answer before sending.
  const amountError = computed(() => {
    const typed = amount.value.trim()
    if (typed === '') return null
    // eurosToCents only reads digits, so a minus sign would read as a format error: US-18 asks for this text.
    if (typed.startsWith('-')) return messageForCode('INVALID_AMOUNT')
    if (cents.value === null) return AMOUNT_FORMAT_MESSAGE
    if (cents.value <= 0) return messageForCode('INVALID_AMOUNT')
    if (balance.value !== null && cents.value > balance.value) return messageForCode('INSUFFICIENT_BALANCE')
    return null
  })

  const error = computed(() => submitError.value ?? amountError.value)
  const canSubmit = computed(
    () =>
      pot.value !== null &&
      cents.value !== null &&
      amountError.value === null &&
      !isSubmitting.value,
  )

  // A new amount makes the previous answer from the backend stale.
  watch(amount, () => {
    submitError.value = null
  })

  async function load(): Promise<void> {
    isLoading.value = true
    loadError.value = null
    try {
      const [home, pots] = await Promise.all([dependencies.getHome(), dependencies.getPots()])
      balance.value = home.balance
      pot.value = pots.find((candidate) => candidate.id === potId) ?? null
      if (pot.value === null) loadError.value = messageForCode('POT_NOT_FOUND')
    } catch (failure) {
      loadError.value = toUserMessage(failure)
    } finally {
      isLoading.value = false
    }
  }

  async function submit(): Promise<boolean> {
    if (!canSubmit.value || pot.value === null || cents.value === null) return false
    isSubmitting.value = true
    submitError.value = null

    try {
      const result = await dependencies.contribute(potId, cents.value)
      // The answer has both new balances, so nothing has to be asked again (§9.4).
      balance.value = result.balance
      pot.value = result.pot
      confirmation.value = `Has aportat ${formatCents(result.movement.amount)} a ${result.pot.name}`
    } catch (failure) {
      // Nothing changed on the server, so the balances on screen stay as they were.
      submitError.value = toUserMessage(failure)
      isSubmitting.value = false
      return false
    }

    // The button stays disabled while the confirmation is on screen.
    await dependencies.pause(CONFIRMATION_MS)
    isSubmitting.value = false
    await dependencies.goToPot()
    return true
  }

  return {
    pot,
    balance,
    title,
    isLoading,
    loadError,
    amount,
    error,
    canSubmit,
    isSubmitting,
    confirmation,
    load,
    submit,
  }
}

function defaultDependencies(potId: string): ContributeDependencies {
  const router = useRouter()
  return {
    getHome,
    getPots,
    contribute,
    // Replace: going back from the pot must not reopen a contribution that was already sent.
    goToPot: () => router.replace({ name: 'pot', params: { potId } }),
    pause: (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  }
}
