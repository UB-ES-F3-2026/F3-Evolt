import { beforeEach, describe, expect, it, vi } from 'vitest'
import { messageForCode } from '@/models/errorMessages'
import type { MovementDetail } from '@/models/movement'
import { getMovement } from '@/services/movementsService'
import { useMovementDetailViewModel } from './useMovementDetailViewModel'

vi.mock('@/services/movementsService', () => ({ getMovement: vi.fn() }))

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

  it('says the movement does not exist, and a retry can recover', async () => {
    vi.mocked(getMovement).mockRejectedValueOnce({ code: 'MOVEMENT_NOT_FOUND', message: 'x' })
    const viewModel = useMovementDetailViewModel('mov-99')

    await viewModel.load()

    expect(viewModel.error.value).toBe(messageForCode('MOVEMENT_NOT_FOUND'))
    expect(viewModel.movement.value).toBeNull()
    expect(viewModel.isLoading.value).toBe(false)

    vi.mocked(getMovement).mockResolvedValueOnce(bizum)
    await viewModel.load()

    expect(viewModel.error.value).toBeNull()
    expect(viewModel.movement.value).toEqual(bizum)
  })
})
