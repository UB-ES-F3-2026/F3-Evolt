import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  currencyByCode,
  formatCurrencyAmount,
  type CurrencyCode,
  type Subaccount,
  type SubaccountList,
} from '@/models/currency'
import { formatDateTime } from '@/models/date'
import { isApiError } from '@/models/apiError'
import { messageForCode, toUserMessage } from '@/models/errorMessages'
import type { MovementsPage } from '@/models/movement'
import { getMovements } from '@/services/movementsService'
import { deleteSubaccount, getSubaccountMovements, getSubaccounts } from '@/services/subaccountsService'
import type { SubaccountMovement } from '@/models/currency'

// Long enough to read the confirmation before going back to Home (as in US-25).
const CONFIRMATION_MS = 1500
// «Últims moviments» of the EUR detail: the same count as Home.
const EURO_LAST_MOVEMENTS = 5

export interface SubaccountDependencies {
  getSubaccounts: () => Promise<SubaccountList>
  getSubaccountMovements: (subaccountId: string) => Promise<SubaccountMovement[]>
  getMovements: (offset: number, limit: number) => Promise<MovementsPage>
  deleteSubaccount: (subaccountId: string) => Promise<void>
  goHome: () => Promise<unknown>
  goToCurrencies: () => Promise<unknown>
  pause: (ms: number) => Promise<void>
}

/** One line of «Últims moviments», already formatted in the account's currency. */
export interface SubaccountHistoryRow {
  id: string
  concept: string
  date: string
  dateText: string
  amountText: string
  isIncome: boolean
}

/** Which of the two windows of «Eliminar subcompte» is open (US-26). */
export type DeleteDialog = 'not-empty' | 'confirm' | null

/**
 * One currency account's screen (US-26): its balance, its last movements and,
 * for a foreign sub-account, «Eliminar subcompte» with its two windows.
 * The EUR account is never deleted: it has no button, and its movements are the
 * ones of `GET /api/movements` (docs/api.md §12.6).
 */
export function useSubaccountViewModel(
  subaccountId: string,
  dependencies: SubaccountDependencies = defaultDependencies(),
) {
  const subaccount = ref<Subaccount | null>(null)
  const history = ref<SubaccountHistoryRow[]>([])
  // Starts true so an empty account never flashes before the first answer.
  const isLoading = ref(true)
  const error = ref<string | null>(null)
  const dialog = ref<DeleteDialog>(null)
  const isDeleting = ref(false)
  const deleteError = ref<string | null>(null)
  const confirmation = ref<string | null>(null)
  // A sub-account that is gone (deleted elsewhere): the screen says so and goes back to /divises.
  const notFound = ref<string | null>(null)

  const code = computed<CurrencyCode | null>(() => subaccount.value?.code ?? null)
  const title = computed(() => {
    if (code.value === null) return 'Divisa'
    return `${code.value} · ${currencyByCode(code.value).name}`
  })
  const balanceText = computed(() =>
    subaccount.value === null ? '' : formatCurrencyAmount(subaccount.value.balance, subaccount.value.code),
  )
  // ELP-02: the EUR detail never offers to delete it.
  const canDelete = computed(() => code.value !== null && code.value !== 'EUR')
  const hasHistory = computed(() => history.value.length > 0)

  async function load(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      // There is no GET /api/subaccounts/{id} (docs/api.md §12): the account comes from the list.
      const accounts = (await dependencies.getSubaccounts()).items
      const found = accounts.find((candidate) => candidate.id === subaccountId) ?? null
      subaccount.value = found
      if (found === null) {
        error.value = messageForCode('SUBACCOUNT_NOT_FOUND')
        return
      }
      history.value = found.code === 'EUR' ? await euroHistory() : await foreignHistory(found)
    } catch (failure) {
      error.value = toUserMessage(failure)
    } finally {
      isLoading.value = false
    }
  }

  async function euroHistory(): Promise<SubaccountHistoryRow[]> {
    const page = await dependencies.getMovements(0, EURO_LAST_MOVEMENTS)
    return page.items.map((movement) => ({
      id: movement.id,
      concept: movement.concept,
      date: movement.date,
      dateText: formatDateTime(movement.date),
      amountText: signed(formatCurrencyAmount(movement.amount, 'EUR'), movement.type === 'income'),
      isIncome: movement.type === 'income',
    }))
  }

  async function foreignHistory(account: Subaccount): Promise<SubaccountHistoryRow[]> {
    const entries = await dependencies.getSubaccountMovements(account.id)
    return entries.map((entry) => ({
      id: entry.id,
      concept: entry.concept,
      date: entry.date,
      dateText: formatDateTime(entry.date),
      amountText: signed(formatCurrencyAmount(entry.amount, account.code), entry.type === 'income'),
      isIncome: entry.type === 'income',
    }))
  }

  /** «Eliminar subcompte»: window 1 with any balance (even 0,01 $), window 2 with exactly 0. */
  function askToDelete(): void {
    if (!canDelete.value || subaccount.value === null || confirmation.value !== null) return
    deleteError.value = null
    dialog.value = subaccount.value.balance === 0 ? 'confirm' : 'not-empty'
  }

  function closeDialog(): void {
    if (isDeleting.value) return
    dialog.value = null
    deleteError.value = null
  }

  async function confirmDelete(): Promise<boolean> {
    // The guard is the whole double-click protection: a second tap never sends.
    if (isDeleting.value || subaccount.value === null || dialog.value !== 'confirm') return false
    isDeleting.value = true
    deleteError.value = null

    try {
      await dependencies.deleteSubaccount(subaccount.value.id)
    } catch (failure) {
      isDeleting.value = false
      return handleDeleteFailure(failure)
    }

    dialog.value = null
    confirmation.value = 'Subcompte eliminat'
    // `isDeleting` stays true until leaving: the screen is already on its way out.
    await dependencies.pause(CONFIRMATION_MS)
    await dependencies.goHome()
    return true
  }

  async function handleDeleteFailure(failure: unknown): Promise<false> {
    // The server is the last word: money arrived meanwhile (an exchange), so window 1.
    if (isApiError(failure) && failure.code === 'SUBACCOUNT_NOT_EMPTY') {
      dialog.value = 'not-empty'
      void load()
      return false
    }
    // Deleted from somewhere else: say it and go back to the list (US-26).
    if (isApiError(failure) && failure.code === 'SUBACCOUNT_NOT_FOUND') {
      dialog.value = null
      notFound.value = messageForCode('SUBACCOUNT_NOT_FOUND')
      await dependencies.pause(CONFIRMATION_MS)
      await dependencies.goToCurrencies()
      return false
    }
    // Anything else keeps window 2 open with the error, to try again or cancel.
    deleteError.value = toUserMessage(failure)
    return false
  }

  return {
    subaccount,
    history,
    title,
    balanceText,
    canDelete,
    hasHistory,
    isLoading,
    error,
    dialog,
    isDeleting,
    deleteError,
    confirmation,
    notFound,
    load,
    askToDelete,
    closeDialog,
    confirmDelete,
  }
}

function signed(amountText: string, isIncome: boolean): string {
  return `${isIncome ? '+' : '−'}${amountText}`
}

function defaultDependencies(): SubaccountDependencies {
  const router = useRouter()
  return {
    getSubaccounts,
    getSubaccountMovements,
    getMovements: (offset, limit) => getMovements(offset, limit),
    deleteSubaccount,
    // US-26: replace, so the browser's Back button does not return to a deleted sub-account.
    goHome: () => router.replace({ name: 'home' }),
    goToCurrencies: () => router.replace({ name: 'currencies' }),
    pause: (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  }
}
