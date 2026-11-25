import { computed, ref, watch } from 'vue'
import { toUserMessage } from '@/models/errorMessages'
import type { UserSummary } from '@/models/user'
import { searchUsers } from '@/services/usersService'

// Waits this long after the last key before asking, so typing a phone is one request, not nine.
const TYPING_PAUSE_MS = 250

export interface PaymentsDependencies {
  searchUsers: (q: string) => Promise<UserSummary[]>
  wait: (ms: number) => Promise<void>
}

/**
 * «Enviar diners» screen (US-13): the search bar and the people to send money to.
 * Results come while typing; an empty bar brings back the initial list.
 */
export function usePaymentsViewModel(dependencies: PaymentsDependencies = defaultDependencies()) {
  const query = ref('')
  const users = ref<UserSummary[]>([])
  const isLoading = ref(true)
  const hasLoaded = ref(false)
  const error = ref<string | null>(null)

  const isSearching = computed(() => query.value.trim() !== '')
  // Only the first answer shows the spinner; later ones keep the list on screen while they arrive.
  const showLoading = computed(() => isLoading.value && !hasLoaded.value)
  // «No hi ha resultats» is only for a search: an empty bar is the initial list (US-13).
  const showNoResults = computed(
    () => hasLoaded.value && !isLoading.value && error.value === null && isSearching.value && users.value.length === 0,
  )

  // Each request gets a number; an answer that is not the latest one is dropped.
  let latestRequest = 0
  let latestKey = 0

  async function search(): Promise<void> {
    const request = ++latestRequest
    isLoading.value = true
    error.value = null
    try {
      const found = await dependencies.searchUsers(query.value)
      if (request !== latestRequest) return
      users.value = found
    } catch (failure) {
      if (request !== latestRequest) return
      users.value = []
      error.value = toUserMessage(failure)
    }
    isLoading.value = false
    hasLoaded.value = true
  }

  watch(query, async () => {
    const key = ++latestKey
    await dependencies.wait(TYPING_PAUSE_MS)
    if (key === latestKey) await search()
  })

  return { query, users, isSearching, showLoading, showNoResults, error, search }
}

function defaultDependencies(): PaymentsDependencies {
  return {
    searchUsers,
    wait: (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  }
}
