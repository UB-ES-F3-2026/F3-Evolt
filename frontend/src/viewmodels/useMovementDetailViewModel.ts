import { computed, ref } from 'vue'
import { formatFullDateTime } from '@/models/date'
import { toUserMessage } from '@/models/errorMessages'
import { MOVEMENT_STATUS_LABELS, type MovementDetail } from '@/models/movement'
import { getMovement } from '@/services/movementsService'

const NO_COUNTERPARTY = '—'

/** «Detall del moviment» screen (US-11): the amount on top and the rest of the data in rows. */
export function useMovementDetailViewModel(movementId: string) {
  const movement = ref<MovementDetail | null>(null)
  // Starts true so the screen never shows an empty detail before the first answer.
  const isLoading = ref(true)
  const error = ref<string | null>(null)

  const isIncome = computed(() => movement.value?.type === 'income')
  const rows = computed(() => {
    if (movement.value === null) return []
    const { date, status, counterparty, reference } = movement.value
    return [
      { label: 'Data i hora', value: formatFullDateTime(date) },
      { label: 'Estat', value: MOVEMENT_STATUS_LABELS[status] },
      { label: 'Contrapart', value: counterparty ?? NO_COUNTERPARTY },
      { label: 'Referència', value: reference },
    ]
  })

  async function load(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      movement.value = await getMovement(movementId)
    } catch (failure) {
      error.value = toUserMessage(failure)
    } finally {
      isLoading.value = false
    }
  }

  return { movement, rows, isIncome, isLoading, error, load }
}
