/** Home screen state and actions (US-07). */

import { ref } from 'vue'
import { getHome } from '@/services/homeService'
import { toUserMessage } from '@/models/apiError'

export function useHomeViewModel() {
  const isLoading = ref(false)
  const error = ref(null)
  const balance = ref(null)
  const totalSaved = ref(null)
  const lastMovements = ref([])

  async function load() {
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

  return { isLoading, error, balance, totalSaved, lastMovements, load }
}
