import { computed, ref, watch } from 'vue'
import { toUserMessage } from '@/models/errorMessages'
import {
  hasFilters,
  MOVEMENT_TYPE_FILTER_LABELS,
  type Movement,
  type MovementFilters,
  type MovementsPage,
  type MovementTypeFilter,
} from '@/models/movement'
import { getMovements } from '@/services/movementsService'

// Default page size of the contract (docs/api.md §4.2).
const PAGE_SIZE = 20
// The search waits this long after the last key, so it does not ask once per letter.
export const SEARCH_DELAY_MS = 300

export const DATE_RANGE_MESSAGE = "La data d'inici no pot ser posterior a la data final."

type FetchPage = (offset: number, limit: number, filters: MovementFilters) => Promise<MovementsPage>

/**
 * Movements screen (US-08): every movement, newest first, one page at a time.
 * US-10 adds the dates, the type and the search; each change starts again from the first page.
 */
export function useMovementsViewModel(fetchPage: FetchPage = getMovements) {
  const items = ref<Movement[]>([])
  const isLoading = ref(false)
  const isLoadingMore = ref(false)
  const error = ref<string | null>(null)
  // Where the next page starts; null once the backend says there are no more.
  const nextOffset = ref<number | null>(0)

  // What the filter controls hold. The search reaches the list SEARCH_DELAY_MS later.
  const search = ref('')
  const dateFrom = ref('')
  const dateTo = ref('')
  const type = ref<MovementTypeFilter>('all')
  const areFiltersOpen = ref(false)
  const appliedSearch = ref('')

  const typeOptions = (Object.keys(MOVEMENT_TYPE_FILTER_LABELS) as MovementTypeFilter[]).map((value) => ({
    value,
    label: MOVEMENT_TYPE_FILTER_LABELS[value],
  }))

  /** The filters the list on screen follows. */
  const filters = computed<MovementFilters>(() => ({
    dateFrom: dateFrom.value,
    dateTo: dateTo.value,
    type: type.value,
    search: appliedSearch.value,
  }))

  // The backend would answer VALIDATION_ERROR (docs/api.md §10.2), so the list is not asked.
  const dateError = computed(() =>
    dateFrom.value && dateTo.value && dateFrom.value > dateTo.value ? DATE_RANGE_MESSAGE : null,
  )
  // Counts the search being typed too, so «Esborrar filtres» shows from the first letter.
  const canClearFilters = computed(() => hasFilters({ ...filters.value, search: search.value }))

  const hasMore = computed(() => nextOffset.value !== null)
  const isListEmpty = computed(
    () => !isLoading.value && error.value === null && items.value.length === 0 && !hasMore.value,
  )
  /** The user has no movements at all. */
  const isEmpty = computed(() => isListEmpty.value && !hasFilters(filters.value))
  /** There are movements, but none matches the filters (US-10, criterion 5). */
  const hasNoResults = computed(() => isListEmpty.value && hasFilters(filters.value))

  // Each first page opens a new generation. An answer from an older one is dropped, so a
  // slow search or a page asked before a filter changed never mixes into the new list.
  let generation = 0

  async function loadFirstPage(): Promise<void> {
    if (dateError.value) return
    const current = ++generation
    isLoading.value = true
    isLoadingMore.value = false
    error.value = null
    items.value = []
    nextOffset.value = 0
    try {
      const page = await fetchPage(0, PAGE_SIZE, filters.value)
      if (current !== generation) return
      items.value = page.items
      nextOffset.value = page.nextOffset
    } catch (failure) {
      if (current === generation) error.value = toUserMessage(failure)
    } finally {
      if (current === generation) isLoading.value = false
    }
  }

  // Ignored while another page is loading, after the last page, or after a failure
  // (then only retry() asks again), so the same page is never loaded twice.
  async function loadMore(): Promise<void> {
    if (isLoading.value || isLoadingMore.value || nextOffset.value === null || error.value) return
    const current = generation
    isLoadingMore.value = true
    try {
      const page = await fetchPage(nextOffset.value, PAGE_SIZE, filters.value)
      if (current !== generation) return
      items.value = [...items.value, ...page.items]
      nextOffset.value = page.nextOffset
    } catch (failure) {
      if (current === generation) error.value = toUserMessage(failure)
    } finally {
      if (current === generation) isLoadingMore.value = false
    }
  }

  async function retry(): Promise<void> {
    error.value = null
    await (items.value.length === 0 ? loadFirstPage() : loadMore())
  }

  function toggleFilters(): void {
    areFiltersOpen.value = !areFiltersOpen.value
  }

  let searchTimer: ReturnType<typeof setTimeout> | undefined

  /** Back to the full list, with a single request. */
  function clearFilters(): void {
    clearTimeout(searchTimer)
    search.value = ''
    appliedSearch.value = ''
    dateFrom.value = ''
    dateTo.value = ''
    type.value = 'all'
  }

  watch(search, (text) => {
    clearTimeout(searchTimer)
    searchTimer = setTimeout(() => {
      appliedSearch.value = text.trim()
    }, SEARCH_DELAY_MS)
  })

  // Changes made together (like clearFilters) arrive here once, so they ask once.
  watch([dateFrom, dateTo, type, appliedSearch], () => loadFirstPage())

  return {
    items,
    isLoading,
    isLoadingMore,
    error,
    hasMore,
    isEmpty,
    hasNoResults,
    search,
    dateFrom,
    dateTo,
    type,
    typeOptions,
    dateError,
    areFiltersOpen,
    canClearFilters,
    loadFirstPage,
    loadMore,
    retry,
    toggleFilters,
    clearFilters,
  }
}
