import { computed, ref } from 'vue'
import { toUserMessage } from '@/models/errorMessages'
import type { ReceivedMoneyRequest } from '@/models/moneyRequest'
import { getReceivedMoneyRequests } from '@/services/requests/moneyRequestsService'

export interface ReceivedMoneyRequestsDependencies {
  getReceivedMoneyRequests: () => Promise<ReceivedMoneyRequest[]>
}

/**
 * «Sol·licituds rebudes» screen (`/requests/received`, US-16): the requests someone sent to the
 * person, newest first, each with its status. «Pagar» (US-39) and «Rebutjar» (US-40) come later.
 */
export function useReceivedMoneyRequestsViewModel(
  dependencies: ReceivedMoneyRequestsDependencies = { getReceivedMoneyRequests },
) {
  const requests = ref<ReceivedMoneyRequest[]>([])
  const isLoading = ref(true)
  const loadError = ref<string | null>(null)

  const isEmpty = computed(() => !isLoading.value && loadError.value === null && requests.value.length === 0)

  async function load(): Promise<void> {
    isLoading.value = true
    loadError.value = null
    try {
      // The server already sorts them and works out «Caducada» (docs/api.md §15.2).
      requests.value = await dependencies.getReceivedMoneyRequests()
    } catch (failure) {
      loadError.value = toUserMessage(failure)
    } finally {
      isLoading.value = false
    }
  }

  return { requests, isLoading, loadError, isEmpty, load }
}
