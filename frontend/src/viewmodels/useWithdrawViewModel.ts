import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { messageForCode, toUserMessage } from '@/models/errorMessages'
import { eurosToCents, formatCents } from '@/models/money'
import { potAmountError, type Pot, type Withdrawal } from '@/models/pot'
import { getPots, withdraw } from '@/services/potsService'

// Long enough to read the confirmation before going back to the pot.
const CONFIRMATION_MS = 1500

export interface WithdrawDependencies {
  getPots: () => Promise<Pot[]>
  withdraw: (potId: string, amountCents: number) => Promise<Withdrawal>
  goToPot: () => Promise<unknown>
  pause: (ms: number) => Promise<void>
}

/** «Retirar de <nom>» screen (US-19): the amount in euros, its checks, and moving it back to the main account. */
export function useWithdrawViewModel(potId: string, dependencies: WithdrawDependencies = defaultDependencies(potId)) {
  const pot = ref<Pot | null>(null)
  /** Main account balance after the withdrawal, in cents: only the answer brings it (docs/api.md §11.2). */
  const balance = ref<number | null>(null)
  const isLoading = ref(true)
  const loadError = ref<string | null>(null)

  const amount = ref('')
  const isSubmitting = ref(false)
  const submitError = ref<string | null>(null)
  const confirmation = ref<string | null>(null)

  const title = computed(() => (pot.value === null ? 'Retirar' : `Retirar de ${pot.value.name}`))
  const cents = computed(() => eurosToCents(amount.value))
  // The pot balance is the most that can come out; taking exactly all of it is allowed (US-19).
  // Shown under the field, which turns red; a server answer goes under the button instead (REP-03, REP-08).
  const amountError = computed(() =>
    potAmountError(amount.value, pot.value?.balance ?? null, 'INSUFFICIENT_POT_BALANCE'),
  )

  const canSubmit = computed(
    () => pot.value !== null && cents.value !== null && amountError.value === null && !isSubmitting.value,
  )

  // A new amount makes the previous answer from the backend stale.
  watch(amount, () => {
    submitError.value = null
  })

  async function load(): Promise<void> {
    isLoading.value = true
    loadError.value = null
    try {
      // There is no GET /api/pots/{potId} (docs/api.md §9): the pot comes from the list.
      const pots = await dependencies.getPots()
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
      const result = await dependencies.withdraw(potId, cents.value)
      // The answer has both new balances, so nothing has to be asked again (§11.2).
      balance.value = result.balance
      pot.value = result.pot
      confirmation.value = `Has retirat ${formatCents(result.movement.amount)} de ${result.pot.name}`
    } catch (failure) {
      // Nothing changed on the server, so the amount stays typed and the balances as they were.
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
    amountError,
    submitError,
    canSubmit,
    isSubmitting,
    confirmation,
    load,
    submit,
  }
}

function defaultDependencies(potId: string): WithdrawDependencies {
  const router = useRouter()
  return {
    getPots,
    withdraw,
    // Replace: going back from the pot must not reopen a withdrawal that was already sent.
    goToPot: () => router.replace({ name: 'pot', params: { potId } }),
    pause: (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  }
}
