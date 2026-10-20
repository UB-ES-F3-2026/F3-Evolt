import { computed, ref } from 'vue'
import { toUserMessage } from '@/models/errorMessages'
import type { Movement, MovementsPage } from '@/models/movement'
import { getMovements } from '@/services/movementsService'

// Default page size of the contract (docs/api.md §4.2).
const PAGE_SIZE = 20

type FetchPage = (offset: number, limit: number) => Promise<MovementsPage>

/** Movements screen (US-08): every movement, newest first, one page at a time. */
export function useMovementsViewModel(fetchPage: FetchPage = getMovements) {
  const items = ref<Movement[]>([])
  const isLoading = ref(false)
  const isLoadingMore = ref(false)
  const error = ref<string | null>(null)
  // Where the next page starts; null once the backend says there are no more.
  const nextOffset = ref<number | null>(0)

  const hasMore = computed(() => nextOffset.value !== null)
  const isEmpty = computed(
    () => !isLoading.value && error.value === null && items.value.length === 0 && !hasMore.value,
  )

  async function loadFirstPage(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const page = await fetchPage(0, PAGE_SIZE)
      items.value = page.items
      nextOffset.value = page.nextOffset
    } catch (failure) {
      error.value = toUserMessage(failure)
    } finally {
      isLoading.value = false
    }
  }

  // Ignored while another page is loading, after the last page, or after a failure
  // (then only retry() asks again), so the same page is never loaded twice.
  async function loadMore(): Promise<void> {
    if (isLoading.value || isLoadingMore.value || nextOffset.value === null || error.value) return
    isLoadingMore.value = true
    try {
      const page = await fetchPage(nextOffset.value, PAGE_SIZE)
      items.value = [...items.value, ...page.items]
      nextOffset.value = page.nextOffset
    } catch (failure) {
      error.value = toUserMessage(failure)
    } finally {
      isLoadingMore.value = false
    }
  }

  async function retry(): Promise<void> {
    error.value = null
    await (items.value.length === 0 ? loadFirstPage() : loadMore())
  }

  return { items, isLoading, isLoadingMore, error, hasMore, isEmpty, loadFirstPage, loadMore, retry }
}
