import { flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { messageForCode } from '@/models/errorMessages'
import type { MovementDetail } from '@/models/movement'
import { MAX_REPORT_LENGTH, type MovementReport } from '@/models/movementReport'
import { getMovement, reportMovement } from '@/services/movementsService'
import { useReportProblemViewModel } from './useReportProblemViewModel'

vi.mock('@/services/movementsService', () => ({ getMovement: vi.fn(), reportMovement: vi.fn() }))

const restaurant: MovementDetail = {
  id: 'mov-30',
  amount: 2350,
  concept: 'Restaurant La Plaça',
  date: '2026-11-02T21:15:00+01:00',
  type: 'expense',
  icon: 'food',
  counterparty: null,
  status: 'pending',
  reference: 'EVT-000030',
}
const report: MovementReport = {
  id: 'rep-01',
  movementId: 'mov-30',
  description: 'No el reconec',
  createdAt: '2026-11-03T10:00:00+01:00',
}

beforeEach(() => {
  vi.mocked(getMovement).mockReset()
  vi.mocked(reportMovement).mockReset()
})

describe('useReportProblemViewModel', () => {
  it('loads the movement, so the form already says which one it is (DP-05)', async () => {
    vi.mocked(getMovement).mockResolvedValue(restaurant)
    const viewModel = useReportProblemViewModel('mov-30')
    expect(viewModel.isLoading.value).toBe(true)

    await viewModel.load()

    expect(vi.mocked(getMovement)).toHaveBeenCalledWith('mov-30')
    expect(viewModel.movement.value).toEqual(restaurant)
    expect(viewModel.isLoading.value).toBe(false)
  })

  it('says the movement does not exist', async () => {
    vi.mocked(getMovement).mockRejectedValue({ code: 'MOVEMENT_NOT_FOUND', message: 'x' })
    const viewModel = useReportProblemViewModel('mov-99')

    await viewModel.load()

    expect(viewModel.loadError.value).toBe(messageForCode('MOVEMENT_NOT_FOUND'))
  })

  it.each([
    ['empty', ''],
    ['only spaces', '   '],
    ['too long', 'a'.repeat(MAX_REPORT_LENGTH + 1)],
  ])('does not send a description that is %s, and says why (DP-06)', async (_case, text) => {
    const viewModel = useReportProblemViewModel('mov-30')
    viewModel.description.value = text
    // On the screen the text arrives before the button is pressed.
    await flushPromises()

    expect(await viewModel.submit()).toBe(false)

    expect(vi.mocked(reportMovement)).not.toHaveBeenCalled()
    expect(viewModel.error.value).toBe(messageForCode('INVALID_DESCRIPTION'))
    expect(viewModel.isSent.value).toBe(false)
  })

  it('clears the error when the text changes', async () => {
    const viewModel = useReportProblemViewModel('mov-30')
    await viewModel.submit()

    viewModel.description.value = 'No el reconec'
    await flushPromises()

    expect(viewModel.error.value).toBeNull()
  })

  it('sends the description and confirms it (DP-07)', async () => {
    vi.mocked(reportMovement).mockResolvedValue(report)
    const viewModel = useReportProblemViewModel('mov-30')
    viewModel.description.value = 'No el reconec'

    expect(await viewModel.submit()).toBe(true)

    expect(vi.mocked(reportMovement)).toHaveBeenCalledWith('mov-30', 'No el reconec')
    expect(viewModel.isSent.value).toBe(true)
    expect(viewModel.isSubmitting.value).toBe(false)
  })

  it('keeps the text and says why when the backend rejects it', async () => {
    vi.mocked(reportMovement).mockRejectedValue({ code: 'NETWORK_ERROR', message: 'x' })
    const viewModel = useReportProblemViewModel('mov-30')
    viewModel.description.value = 'No el reconec'

    expect(await viewModel.submit()).toBe(false)

    expect(viewModel.error.value).toBe(messageForCode('NETWORK_ERROR'))
    expect(viewModel.description.value).toBe('No el reconec')
    expect(viewModel.isSent.value).toBe(false)
  })

  it('sends once when the button is pressed twice', async () => {
    vi.mocked(reportMovement).mockResolvedValue(report)
    const viewModel = useReportProblemViewModel('mov-30')
    viewModel.description.value = 'No el reconec'

    await Promise.all([viewModel.submit(), viewModel.submit()])

    expect(vi.mocked(reportMovement)).toHaveBeenCalledTimes(1)
  })
})
