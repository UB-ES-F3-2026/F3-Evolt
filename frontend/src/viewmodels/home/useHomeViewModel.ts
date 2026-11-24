import { computed, ref } from 'vue'
import { toUserMessage } from '@/models/errorMessages'
import type { Movement } from '@/models/movement'
import { getHome } from '@/services/homeService'

/** Home screen (US-07): balance, total saved in pots and the last 5 movements, in cents. */
export function useHomeViewModel() {
  const balance = ref(0)
  const totalSaved = ref(0)
  const lastMovements = ref<Movement[]>([])
  // Starts true so the screen never shows the 0 placeholder before the first answer.
  const isLoading = ref(true)
  const error = ref<string | null>(null)

  const hasMovements = computed(() => lastMovements.value.length > 0)

  async function load(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const home = await getHome()
      balance.value = home.balance
      totalSaved.value = home.totalSaved
      lastMovements.value = home.lastMovements
    } catch (failure) {
      error.value = toUserMessage(failure)
    } finally {
      isLoading.value = false
    }
  }

  return { balance, totalSaved, lastMovements, hasMovements, isLoading, error, load }
}
