import { ref, watch } from 'vue'
import { messageForCode, toUserMessage } from '@/models/errorMessages'
import type { MovementDetail } from '@/models/movement'
import { isValidReportDescription } from '@/models/movementReport'
import { getMovement, reportMovement } from '@/services/movementsService'

/** «Reportar un problema» screen (US-11): the movement already chosen and a box to explain what happens. */
export function useReportProblemViewModel(movementId: string) {
  const movement = ref<MovementDetail | null>(null)
  const isLoading = ref(true)
  const loadError = ref<string | null>(null)

  const description = ref('')
  const error = ref<string | null>(null)
  const isSubmitting = ref(false)
  const isSent = ref(false)

  // A new text makes the previous error stale.
  watch(description, () => {
    error.value = null
  })

  async function load(): Promise<void> {
    isLoading.value = true
    loadError.value = null
    try {
      movement.value = await getMovement(movementId)
    } catch (failure) {
      loadError.value = toUserMessage(failure)
    } finally {
      isLoading.value = false
    }
  }

  async function submit(): Promise<boolean> {
    if (isSubmitting.value) return false
    // The button stays enabled: pressing it with an empty box has to say why nothing is sent.
    if (!isValidReportDescription(description.value)) {
      error.value = messageForCode('INVALID_DESCRIPTION')
      return false
    }
    isSubmitting.value = true
    error.value = null

    try {
      await reportMovement(movementId, description.value)
      isSent.value = true
      return true
    } catch (failure) {
      error.value = toUserMessage(failure)
      return false
    } finally {
      isSubmitting.value = false
    }
  }

  return { movement, isLoading, loadError, description, error, isSubmitting, isSent, load, submit }
}
