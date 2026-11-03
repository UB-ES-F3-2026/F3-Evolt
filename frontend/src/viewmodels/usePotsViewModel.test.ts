import { beforeEach, describe, expect, it, vi } from 'vitest'
import { messageForCode } from '@/models/errorMessages'
import type { Pot } from '@/models/pot'
import { getPots } from '@/services/potsService'
import { usePotsViewModel } from './usePotsViewModel'

vi.mock('@/services/potsService', () => ({ getPots: vi.fn() }))

const pots: Pot[] = [
  { id: 'pot-01', name: 'Vacances', balance: 15000, target: 100000, color: 'blue' },
  { id: 'pot-02', name: 'Emergències', balance: 10000, target: null, color: 'orange' },
]

beforeEach(() => {
  vi.mocked(getPots).mockReset()
})

describe('usePotsViewModel', () => {
  it('starts loading, so the empty state never shows before the first answer', () => {
    const viewModel = usePotsViewModel()

    expect(viewModel.isLoading.value).toBe(true)
    expect(viewModel.isEmpty.value).toBe(false)
    expect(viewModel.error.value).toBeNull()
  })

  it('lists the pots in the order the API sends them', async () => {
    vi.mocked(getPots).mockResolvedValue(pots)
    const viewModel = usePotsViewModel()

    await viewModel.load()

    expect(viewModel.pots.value).toEqual(pots)
    expect(viewModel.isEmpty.value).toBe(false)
    expect(viewModel.isLoading.value).toBe(false)
  })

  it('is empty when the user has no pots (US-17, criterion 2)', async () => {
    vi.mocked(getPots).mockResolvedValue([])
    const viewModel = usePotsViewModel()

    await viewModel.load()

    expect(viewModel.isEmpty.value).toBe(true)
  })

  it('shows the shared message for the error code, and is not empty then', async () => {
    vi.mocked(getPots).mockRejectedValue({ code: 'NETWORK_ERROR', message: 'x' })
    const viewModel = usePotsViewModel()

    await viewModel.load()

    expect(viewModel.error.value).toBe(messageForCode('NETWORK_ERROR'))
    expect(viewModel.isEmpty.value).toBe(false)
    expect(viewModel.isLoading.value).toBe(false)
  })

  it('clears the error when a later load works', async () => {
    vi.mocked(getPots)
      .mockRejectedValueOnce({ code: 'INTERNAL_ERROR', message: 'x' })
      .mockResolvedValueOnce(pots)
    const viewModel = usePotsViewModel()

    await viewModel.load()
    await viewModel.load()

    expect(viewModel.error.value).toBeNull()
    expect(viewModel.pots.value).toHaveLength(2)
  })
})
