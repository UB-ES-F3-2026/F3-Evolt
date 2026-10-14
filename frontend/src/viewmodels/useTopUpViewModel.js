/** Top-up screen state and actions (US-09). */

import { computed, ref } from 'vue'
import { createTopup } from '@/services/topupService'
import { eurosToCents } from '@/models/money'
import { toUserMessage } from '@/models/apiError'

export function useTopUpViewModel() {
  const amount = ref('')
  const isSubmitting = ref(false)
  const error = ref(null)
  const successMessage = ref(null)
  const newBalance = ref(null)

  const canSubmit = computed(
    () => eurosToCents(amount.value) !== null && !isSubmitting.value,
  )

  async function submit() {
    error.value = null
    successMessage.value = null

    const cents = eurosToCents(amount.value)
    if (cents === null || cents <= 0) {
      error.value = "Introdueix un import vàlid"
      return false
    }

    isSubmitting.value = true
    try {
      const result = await createTopup(cents)
      newBalance.value = result.balance
      successMessage.value = 'Recàrrega feta correctament'
      amount.value = ''
      return true
    } catch (failure) {
      error.value = toUserMessage(failure)
      return false
    } finally {
      isSubmitting.value = false
    }
  }

  return { amount, isSubmitting, error, successMessage, newBalance, canSubmit, submit }
}
