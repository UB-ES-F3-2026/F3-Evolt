import { computed, ref } from 'vue'
import { isApiError } from '@/models/apiError'
import { formatFullDateTime } from '@/models/date'
import { toUserMessage } from '@/models/errorMessages'
import { formatSignedCents } from '@/models/money'
import { MOVEMENT_STATUS_LABELS, type MovementDetail } from '@/models/movement'
import { receiptFileName } from '@/models/receipt'
import { saveFile } from '@/services/fileDownload'
import { getMovement } from '@/services/movementsService'
import { makeReceiptPdf } from '@/services/receiptPdf'

const NO_COUNTERPARTY = '—'
// The browser remembers a failed load of jsPDF or the font: trying again only works after a reload.
const RECEIPT_ERROR = "No s'ha pogut generar el justificant. Recarrega la pàgina i torna-ho a provar."

/** «Detall del moviment» screen (US-11): the amount on top, the rest of the data in rows and the receipt. */
export function useMovementDetailViewModel(movementId: string) {
  const movement = ref<MovementDetail | null>(null)
  // Starts true so the screen never shows an empty detail before the first answer.
  const isLoading = ref(true)
  const error = ref<string | null>(null)
  const canRetry = ref(true)
  const isMakingReceipt = ref(false)
  const receiptError = ref<string | null>(null)

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
      // A movement that does not exist will not appear on a second try.
      canRetry.value = !(isApiError(failure) && failure.code === 'MOVEMENT_NOT_FOUND')
    } finally {
      isLoading.value = false
    }
  }

  async function downloadReceipt(): Promise<void> {
    if (movement.value === null || isMakingReceipt.value) return
    const { amount, concept, reference } = movement.value
    isMakingReceipt.value = true
    receiptError.value = null
    try {
      const pdf = await makeReceiptPdf({
        amount: formatSignedCents(amount, isIncome.value ? 'positive' : 'negative'),
        isIncome: isIncome.value,
        concept,
        rows: rows.value,
      })
      saveFile(pdf, receiptFileName(reference))
    } catch {
      receiptError.value = RECEIPT_ERROR
    } finally {
      isMakingReceipt.value = false
    }
  }

  return {
    movement,
    rows,
    isIncome,
    isLoading,
    error,
    canRetry,
    isMakingReceipt,
    receiptError,
    load,
    downloadReceipt,
  }
}
