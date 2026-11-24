import { computed, ref } from 'vue'
import { isApiError } from '@/models/apiError'
import { toUserMessage } from '@/models/errorMessages'
import type { MoneyRequest } from '@/models/moneyRequest'
import { cancelMoneyRequest, getMoneyRequests } from '@/services/requests/moneyRequestsService'

export interface MoneyRequestsDependencies {
  getMoneyRequests: () => Promise<MoneyRequest[]>
  cancelMoneyRequest: (requestId: string) => Promise<void>
}

/**
 * «Sol·licituds enviades» screen (`/requests`, US-15): the requests the person sent, each with
 * its status, and «Cancel·lar» on the pending ones, which deletes them after the dialog.
 */
export function useMoneyRequestsViewModel(dependencies: MoneyRequestsDependencies = { getMoneyRequests, cancelMoneyRequest }) {
  const requests = ref<MoneyRequest[]>([])
  const isLoading = ref(true)
  const loadError = ref<string | null>(null)

  /** The request whose «Cancel·lar sol·licitud» dialog is open, or null. */
  const requestToCancel = ref<MoneyRequest | null>(null)
  const isCancelling = ref(false)
  /** «Sol·licitud cancel·lada.» at the top after a cancel. */
  const notice = ref<string | null>(null)
  /** An answer of the server to a cancel, in red at the top. */
  const cancelError = ref<string | null>(null)

  const isEmpty = computed(() => !isLoading.value && loadError.value === null && requests.value.length === 0)

  async function load(): Promise<void> {
    isLoading.value = true
    loadError.value = null
    try {
      requests.value = await dependencies.getMoneyRequests()
    } catch (failure) {
      loadError.value = toUserMessage(failure)
    } finally {
      isLoading.value = false
    }
  }

  /** «Cancel·lar» on a pending row: only opens the dialog, nothing is sent yet. */
  function askToCancel(request: MoneyRequest): void {
    notice.value = null
    cancelError.value = null
    requestToCancel.value = request
  }

  /** «Cancel·lar», Esc or a click outside: closes the dialog without any call (US-15). */
  function keepRequest(): void {
    if (!isCancelling.value) requestToCancel.value = null
  }

  async function confirmCancel(): Promise<void> {
    const request = requestToCancel.value
    if (request === null || isCancelling.value) return
    isCancelling.value = true
    try {
      await dependencies.cancelMoneyRequest(request.id)
      // Deleted for good: the row goes and never comes back (§14.4).
      requests.value = requests.value.filter((candidate) => candidate.id !== request.id)
      notice.value = 'Sol·licitud cancel·lada.'
    } catch (failure) {
      cancelError.value = toUserMessage(failure)
      // It expired or is gone in the meantime: the list on screen is stale (US-15).
      if (isApiError(failure) && ['REQUEST_NOT_PENDING', 'REQUEST_NOT_FOUND'].includes(failure.code)) {
        await load()
      }
    } finally {
      isCancelling.value = false
      requestToCancel.value = null
    }
  }

  return {
    requests,
    isLoading,
    loadError,
    isEmpty,
    requestToCancel,
    isCancelling,
    notice,
    cancelError,
    load,
    askToCancel,
    keepRequest,
    confirmCancel,
  }
}
