import { beforeEach, describe, expect, it, vi } from 'vitest'
import { messageForCode } from '@/models/errorMessages'
import { formatSignedCents } from '@/models/money'
import type { MovementDetail } from '@/models/movement'
import { saveFile } from '@/services/fileDownload'
import { getMovement } from '@/services/movementsService'
import { makeReceiptPdf } from '@/services/receiptPdf'
import { useBalanceVisibility } from './useBalanceVisibility'
import { useMovementDetailViewModel } from './useMovementDetailViewModel'

vi.mock('@/services/movementsService', () => ({ getMovement: vi.fn() }))
vi.mock('@/services/receiptPdf', () => ({ makeReceiptPdf: vi.fn() }))
vi.mock('@/services/fileDownload', () => ({ saveFile: vi.fn() }))

const bizum: MovementDetail = {
  id: 'mov-29',
  amount: 1000,
  concept: 'Bizum enviat',
  date: '2026-11-01T18:42:00+01:00',
  type: 'expense',
  icon: 'transfer',
  counterparty: 'Núria Soler',
  status: 'completed',
  reference: 'EVT-000029',
}

beforeEach(() => {
  vi.mocked(getMovement).mockReset()
  vi.mocked(makeReceiptPdf).mockReset()
  vi.mocked(saveFile).mockReset()
})

describe('useMovementDetailViewModel', () => {
  it('starts loading, with nothing to show', () => {
    const viewModel = useMovementDetailViewModel('mov-29')

    expect(viewModel.isLoading.value).toBe(true)
    expect(viewModel.rows.value).toEqual([])
  })

  it('shows the date, the status, the counterparty and the reference in rows (DP-01)', async () => {
    vi.mocked(getMovement).mockResolvedValue(bizum)
    const viewModel = useMovementDetailViewModel('mov-29')

    await viewModel.load()

    expect(vi.mocked(getMovement)).toHaveBeenCalledWith('mov-29')
    expect(viewModel.isLoading.value).toBe(false)
    expect(viewModel.isIncome.value).toBe(false)
    expect(viewModel.rows.value).toEqual([
      { label: 'Data i hora', value: '1/11/2026, 18:42' },
      { label: 'Estat', value: 'Completat' },
      { label: 'Contrapart', value: 'Núria Soler' },
      { label: 'Referència', value: 'EVT-000029' },
    ])
  })

  it('shows a pending movement without counterparty with a dash (DP-02)', async () => {
    vi.mocked(getMovement).mockResolvedValue({ ...bizum, status: 'pending', counterparty: null })
    const viewModel = useMovementDetailViewModel('mov-30')

    await viewModel.load()

    expect(viewModel.rows.value).toContainEqual({ label: 'Estat', value: 'Pendent' })
    expect(viewModel.rows.value).toContainEqual({ label: 'Contrapart', value: '—' })
  })

  it('knows an income (DP-03)', async () => {
    vi.mocked(getMovement).mockResolvedValue({ ...bizum, type: 'income' })
    const viewModel = useMovementDetailViewModel('mov-24')

    await viewModel.load()

    expect(viewModel.isIncome.value).toBe(true)
  })

  it('says the movement does not exist, and does not offer to try again', async () => {
    vi.mocked(getMovement).mockRejectedValue({ code: 'MOVEMENT_NOT_FOUND', message: 'x' })
    const viewModel = useMovementDetailViewModel('mov-99')

    await viewModel.load()

    expect(viewModel.error.value).toBe(messageForCode('MOVEMENT_NOT_FOUND'))
    expect(viewModel.canRetry.value).toBe(false)
    expect(viewModel.movement.value).toBeNull()
    expect(viewModel.isLoading.value).toBe(false)
  })

  it('offers to try again after any other failure, and a retry can recover', async () => {
    vi.mocked(getMovement).mockRejectedValueOnce({ code: 'NETWORK_ERROR', message: 'x' })
    const viewModel = useMovementDetailViewModel('mov-29')

    await viewModel.load()

    expect(viewModel.error.value).toBe(messageForCode('NETWORK_ERROR'))
    expect(viewModel.canRetry.value).toBe(true)

    vi.mocked(getMovement).mockResolvedValueOnce(bizum)
    await viewModel.load()

    expect(viewModel.error.value).toBeNull()
    expect(viewModel.movement.value).toEqual(bizum)
  })
})

describe('the receipt (DP-04, DP-09, DP-10)', () => {
  const pdf = new Blob(['%PDF-'], { type: 'application/pdf' })

  async function loaded(movement: MovementDetail = bizum) {
    vi.mocked(getMovement).mockResolvedValue(movement)
    const viewModel = useMovementDetailViewModel(movement.id)
    await viewModel.load()
    return viewModel
  }

  it('says exactly what the screen says, and saves the file with the reference in its name', async () => {
    vi.mocked(makeReceiptPdf).mockResolvedValue(pdf)
    const viewModel = await loaded()

    await viewModel.downloadReceipt()

    expect(vi.mocked(makeReceiptPdf)).toHaveBeenCalledWith({
      amount: formatSignedCents(1000, 'negative'),
      isIncome: false,
      concept: 'Bizum enviat',
      rows: viewModel.rows.value,
    })
    expect(vi.mocked(saveFile)).toHaveBeenCalledWith(pdf, 'justificant-EVT-000029.pdf')
    expect(viewModel.isMakingReceipt.value).toBe(false)
    expect(viewModel.receiptError.value).toBeNull()
  })

  it('puts «+» on the amount of an income', async () => {
    vi.mocked(makeReceiptPdf).mockResolvedValue(pdf)
    const viewModel = await loaded({ ...bizum, type: 'income' })

    await viewModel.downloadReceipt()

    expect(vi.mocked(makeReceiptPdf)).toHaveBeenCalledWith(
      expect.objectContaining({ amount: formatSignedCents(1000, 'positive'), isIncome: true }),
    )
  })

  it('keeps the real amount with the amounts hidden on screen', async () => {
    // PO decision: a receipt without the amount is no use, so the eye only masks the screen.
    const { isHidden, toggle } = useBalanceVisibility()
    toggle()
    expect(isHidden.value).toBe(true)
    try {
      vi.mocked(makeReceiptPdf).mockResolvedValue(pdf)
      const viewModel = await loaded()

      await viewModel.downloadReceipt()

      expect(vi.mocked(makeReceiptPdf)).toHaveBeenCalledWith(
        expect.objectContaining({ amount: formatSignedCents(1000, 'negative') }),
      )
    } finally {
      toggle()
    }
  })

  it('does not make two at once', async () => {
    vi.mocked(makeReceiptPdf).mockResolvedValue(pdf)
    const viewModel = await loaded()

    const first = viewModel.downloadReceipt()
    expect(viewModel.isMakingReceipt.value).toBe(true)
    await viewModel.downloadReceipt()
    await first

    expect(vi.mocked(makeReceiptPdf)).toHaveBeenCalledOnce()
  })

  it('says it failed and leaves the detail on screen; another try clears the error', async () => {
    vi.mocked(makeReceiptPdf).mockRejectedValueOnce(new TypeError('Failed to fetch dynamically imported module'))
    const viewModel = await loaded()

    await viewModel.downloadReceipt()

    expect(viewModel.receiptError.value).toBe(
      "No s'ha pogut generar el justificant. Recarrega la pàgina i torna-ho a provar.",
    )
    expect(viewModel.error.value).toBeNull()
    expect(viewModel.movement.value).toEqual(bizum)
    expect(vi.mocked(saveFile)).not.toHaveBeenCalled()

    vi.mocked(makeReceiptPdf).mockResolvedValueOnce(pdf)
    await viewModel.downloadReceipt()

    expect(viewModel.receiptError.value).toBeNull()
  })

  it('does nothing before the movement has loaded', async () => {
    await useMovementDetailViewModel('mov-29').downloadReceipt()

    expect(vi.mocked(makeReceiptPdf)).not.toHaveBeenCalled()
  })
})
