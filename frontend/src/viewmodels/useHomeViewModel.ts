import { computed, ref } from 'vue'
import type { Movement } from '@/models/movement'
import { getHome } from '@/services/homeService'

// Network down or server error: the user can only retry, so one message covers both.
const LOAD_ERROR = "No s'ha pogut carregar el saldo. Torna-ho a provar."

/** Home screen (US-07): balance, total saved in pots and the last 5 movements, in cents. */
export function useHomeViewModel() {
  const balance = ref(0)
  const totalSaved = ref(0)
  const lastMovements = ref<Movement[]>([])
  const isLoading = ref(false)
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
    } catch {
      error.value = LOAD_ERROR
    } finally {
      isLoading.value = false
    }
  }

  return { balance, totalSaved, lastMovements, hasMovements, isLoading, error, load }
}
