import { computed, ref } from 'vue'
import { messageForCode, toUserMessage } from '@/models/errorMessages'
import type { Movement } from '@/models/movement'
import { potMovementAsMovement, type Pot } from '@/models/pot'
import { getPotMovements, getPots } from '@/services/potsService'

/** One pot's screen (US-18): its balance, its history and the way to «Aportar». */
export function usePotViewModel(potId: string) {
  const pot = ref<Pot | null>(null)
  const history = ref<Movement[]>([])
  // Starts true so the screen never shows an empty pot before the first answer.
  const isLoading = ref(true)
  const error = ref<string | null>(null)

  const title = computed(() => pot.value?.name ?? 'Guardiola')
  const hasHistory = computed(() => history.value.length > 0)

  async function load(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      // There is no GET /api/pots/{potId} (docs/api.md §9): the pot comes from the list.
      const [pots, entries] = await Promise.all([getPots(), getPotMovements(potId)])
      pot.value = pots.find((candidate) => candidate.id === potId) ?? null
      history.value = entries.map(potMovementAsMovement)
      if (pot.value === null) error.value = messageForCode('POT_NOT_FOUND')
    } catch (failure) {
      error.value = toUserMessage(failure)
    } finally {
      isLoading.value = false
    }
  }

  return { pot, history, title, hasHistory, isLoading, error, load }
}
