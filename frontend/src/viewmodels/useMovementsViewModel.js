/** Movements screen state and actions (US-08), prepared for infinite scroll. */

import { computed, ref } from 'vue'
import { getMovements } from '@/services/movementsService'
import { toUserMessage } from '@/models/apiError'

const PAGE_SIZE = 20

export function useMovementsViewModel() {
  const isLoading = ref(false)
  const error = ref(null)
  const items = ref([])
  const nextOffset = ref(null)

  const isEmpty = computed(() => !isLoading.value && items.value.length === 0)
  const hasMore = computed(() => nextOffset.value !== null)

  async function load() {
    isLoading.value = true
    error.value = null
    try {
      const page = await getMovements(0, PAGE_SIZE)
      items.value = page.items
      nextOffset.value = page.nextOffset
    } catch (failure) {
      error.value = toUserMessage(failure)
    } finally {
      isLoading.value = false
    }
  }

  async function loadMore() {
    if (isLoading.value || nextOffset.value === null) return
    isLoading.value = true
    error.value = null
    try {
      const page = await getMovements(nextOffset.value, PAGE_SIZE)
      items.value = items.value.concat(page.items)
      nextOffset.value = page.nextOffset
    } catch (failure) {
      error.value = toUserMessage(failure)
    } finally {
      isLoading.value = false
    }
  }

  return { isLoading, error, items, isEmpty, hasMore, load, loadMore }
}
