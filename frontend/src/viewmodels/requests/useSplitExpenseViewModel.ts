import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { isApiError } from '@/models/apiError'
import { messageForCode, toUserMessage } from '@/models/errorMessages'
import { eurosToCents, formatCents } from '@/models/money'
import { MAX_REQUEST_CENTS, MAX_REQUEST_CONCEPT_LENGTH, REQUEST_AMOUNT_OVER_LIMIT_MESSAGE } from '@/models/moneyRequest'
import { equalShares, MAX_SPLIT_PARTICIPANTS, type NewSplitExpense, type SplitExpense } from '@/models/splitExpense'
import type { UserSummary } from '@/models/user'
import { createSplitExpense } from '@/services/requests/splitExpensesService'
import { searchUsers } from '@/services/usersService'
import { usePaymentsViewModel } from '@/viewmodels/payments/usePaymentsViewModel'

// The same pause as «Demanar diners» to one person, so the confirmation can be read (US-30, criterion 6).
const CONFIRMATION_MS = 1500

export type ShareMode = 'equal' | 'custom'

export interface Participant {
  user: UserSummary
  /** What is typed in euros with «Imports personalitzats»; unused with «Parts iguals». */
  typed: string
}

export interface SplitConfirmation {
  title: string
  pending: string
}

export interface SplitExpenseDependencies {
  searchUsers: (q: string) => Promise<UserSummary[]>
  wait: (ms: number) => Promise<void>
  createSplitExpense: (expense: NewSplitExpense) => Promise<SplitExpense>
  goToRequests: () => Promise<unknown>
}

/** Cents as typed in a part: `1500` → `"15,00"`. */
function toTyped(cents: number): string {
  return (cents / 100).toFixed(2).replace('.', ',')
}

/**
 * «Dividir una despesa» in «Demanar diners» (`/requests/new`, US-30): the total, the concept, the participants
 * chosen with the search of US-13 and the part of each, also mine. «Enviar sol·licituds» sends them all at once.
 */
export function useSplitExpenseViewModel(dependencies: SplitExpenseDependencies = defaultDependencies()) {
  // The search of US-13 never returns the person asking, so I cannot add myself.
  const search = usePaymentsViewModel({ searchUsers: dependencies.searchUsers, wait: dependencies.wait })

  const total = ref('')
  const concept = ref('')
  const participants = ref<Participant[]>([])
  const shareMode = ref<ShareMode>('equal')
  /** My part as typed with «Imports personalitzats». */
  const myTyped = ref('')

  const isSubmitting = ref(false)
  const submitError = ref<string | null>(null)
  const confirmation = ref<SplitConfirmation | null>(null)

  const totalCents = computed(() => eurosToCents(total.value))
  const isTotalValid = computed(
    () => totalCents.value !== null && totalCents.value > 0 && totalCents.value <= MAX_REQUEST_CENTS,
  )
  // Only what the form can tell before sending; an empty total has no message yet.
  const totalError = computed(() => {
    const typed = total.value.trim()
    if (typed === '') return null
    if (typed.startsWith('-')) return messageForCode('INVALID_AMOUNT')
    if (totalCents.value === null) return null
    if (totalCents.value <= 0) return messageForCode('INVALID_AMOUNT')
    if (totalCents.value > MAX_REQUEST_CENTS) return REQUEST_AMOUNT_OVER_LIMIT_MESSAGE
    return null
  })
  const isConceptValid = computed(() => {
    const length = concept.value.trim().length
    return length >= 1 && length <= MAX_REQUEST_CONCEPT_LENGTH
  })

  const isFull = computed(() => participants.value.length >= MAX_SPLIT_PARTICIPANTS)
  const hasNoParticipants = computed(() => participants.value.length === 0)

  /** The part of each participant, in order, and mine, in cents; null where it cannot be read yet. */
  const shares = computed<{ parts: (number | null)[]; mine: number | null }>(() => {
    if (shareMode.value === 'custom') {
      return { parts: participants.value.map((one) => eurosToCents(one.typed)), mine: eurosToCents(myTyped.value) }
    }
    if (!isTotalValid.value || totalCents.value === null || hasNoParticipants.value) {
      return { parts: participants.value.map(() => null), mine: null }
    }
    const { each, mine } = equalShares(totalCents.value, participants.value.length)
    return { parts: participants.value.map(() => each), mine }
  })

  const sharesError = computed(() => {
    if (hasNoParticipants.value) return null
    const all = [...shares.value.parts, shares.value.mine]
    if (all.some((cents) => cents === 0)) return messageForCode('INVALID_SHARE')
    if (!isTotalValid.value || all.some((cents) => cents === null)) return null
    const sum = all.reduce<number>((total, cents) => total + (cents ?? 0), 0)
    return sum === totalCents.value ? null : messageForCode('SHARES_DO_NOT_MATCH')
  })

  const canSend = computed(
    () =>
      isTotalValid.value &&
      isConceptValid.value &&
      !hasNoParticipants.value &&
      [...shares.value.parts, shares.value.mine].every((cents) => cents !== null && cents > 0) &&
      sharesError.value === null &&
      !isSubmitting.value &&
      confirmation.value === null,
  )

  // A change makes the previous answer from the server stale.
  watch([total, concept, participants, shareMode, myTyped], () => {
    submitError.value = null
  }, { deep: true })

  function isChosen(user: UserSummary): boolean {
    return participants.value.some((one) => one.user.id === user.id)
  }

  /** A person from the search; one who is already there, or a tenth, is not added. */
  function add(user: UserSummary): void {
    if (isChosen(user) || isFull.value) return
    participants.value.push({ user, typed: '' })
    search.query.value = ''
  }

  function remove(userId: string): void {
    participants.value = participants.value.filter((one) => one.user.id !== userId)
  }

  /**
   * «Parts iguals» works the parts out again and drops what was typed (US-30). «Imports personalitzats»
   * starts from the equal parts, so only the ones that differ have to be typed.
   */
  function setShareMode(mode: ShareMode): void {
    if (mode === shareMode.value) return
    if (mode === 'custom') {
      participants.value.forEach((one, index) => {
        const cents = shares.value.parts[index]
        one.typed = cents === null ? '' : toTyped(cents)
      })
      myTyped.value = shares.value.mine === null ? '' : toTyped(shares.value.mine)
    } else {
      participants.value.forEach((one) => {
        one.typed = ''
      })
      myTyped.value = ''
    }
    shareMode.value = mode
  }

  async function send(): Promise<boolean> {
    const mine = shares.value.mine
    if (!canSend.value || totalCents.value === null || mine === null) return false
    isSubmitting.value = true
    submitError.value = null
    try {
      const created = await dependencies.createSplitExpense({
        concept: concept.value.trim(),
        total: totalCents.value,
        myShare: mine,
        parts: participants.value.map((one, index) => ({ toUserId: one.user.id, amount: shares.value.parts[index] ?? 0 })),
      })
      const count = created.parts.length
      confirmation.value = {
        title: `Has enviat ${count} ${count === 1 ? 'sol·licitud' : 'sol·licituds'}`,
        pending: `Pendent de cobrar: ${formatCents(created.pendingAmount)}`,
      }
    } catch (failure) {
      // Nothing was sent and everything typed stays as it is (US-30, criteria 8 and 10).
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
    total,
    concept,
    maxConceptLength: MAX_REQUEST_CONCEPT_LENGTH,
    maxParticipants: MAX_SPLIT_PARTICIPANTS,
    participants,
    shareMode,
    myTyped,
    totalError,
    shares,
    sharesError,
    isFull,
    hasNoParticipants,
    canSend,
    isSubmitting,
    submitError,
    confirmation,
    isChosen,
    add,
    remove,
    setShareMode,
    send,
  }
}

function defaultDependencies(): SplitExpenseDependencies {
  const router = useRouter()
  return {
    searchUsers,
    wait: (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
    createSplitExpense,
    // Replace: going back from the list must not reopen an expense that was already sent.
    goToRequests: () => router.replace({ name: 'money-requests' }),
  }
}
