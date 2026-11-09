import { computed, ref } from 'vue'
import { toUserMessage } from '@/models/errorMessages'
import type { Pot } from '@/models/pot'
import { getPots } from '@/services/potsService'

/** Pots screen (US-17): the user's pots with their balance, or the empty state. */
export function usePotsViewModel() {
  const pots = ref<Pot[]>([])
  // Starts true so the empty state never flashes before the first answer.
  const isLoading = ref(true)
  const error = ref<string | null>(null)

  const isEmpty = computed(() => !isLoading.value && error.value === null && pots.value.length === 0)

  async function load(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      pots.value = await getPots()
    } catch (failure) {
      error.value = toUserMessage(failure)
    } finally {
      isLoading.value = false
    }
  }

  return { pots, isLoading, error, isEmpty, load }
}
