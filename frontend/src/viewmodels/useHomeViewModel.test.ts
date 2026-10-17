import { beforeEach, describe, expect, it, vi } from 'vitest'
import { messageForCode } from '@/models/errorMessages'
import type { Home } from '@/models/home'
import { getHome } from '@/services/homeService'
import { useHomeViewModel } from './useHomeViewModel'

vi.mock('@/services/homeService', () => ({ getHome: vi.fn() }))

const home: Home = {
  balance: 125050,
  totalSaved: 30000,
  lastMovements: [
    {
      id: 'mov-20',
      amount: 2350,
      concept: 'Restaurant La Plaça',
      date: '2026-10-11T21:15:00+02:00',
      type: 'expense',
      icon: 'food',
    },
  ],
}

beforeEach(() => {
  vi.mocked(getHome).mockReset()
})

describe('useHomeViewModel', () => {
  it('fills balance, total saved and the last movements', async () => {
    vi.mocked(getHome).mockResolvedValue(home)
    const viewModel = useHomeViewModel()

    await viewModel.load()

    expect(viewModel.balance.value).toBe(125050)
    expect(viewModel.totalSaved.value).toBe(30000)
    expect(viewModel.lastMovements.value).toEqual(home.lastMovements)
    expect(viewModel.hasMovements.value).toBe(true)
    expect(viewModel.isLoading.value).toBe(false)
    expect(viewModel.error.value).toBeNull()
  })

  it('is loading only while the request is pending', async () => {
    let resolveHome!: (value: Home) => void
    vi.mocked(getHome).mockReturnValue(new Promise((resolve) => (resolveHome = resolve)))
    const viewModel = useHomeViewModel()

    const loading = viewModel.load()
    expect(viewModel.isLoading.value).toBe(true)

    resolveHome(home)
    await loading
    expect(viewModel.isLoading.value).toBe(false)
  })

  it('shows the shared message for the error code when the summary cannot be loaded', async () => {
    vi.mocked(getHome).mockRejectedValue({ code: 'NETWORK_ERROR', message: 'x' })
    const viewModel = useHomeViewModel()

    await viewModel.load()

    expect(viewModel.error.value).toBe(messageForCode('NETWORK_ERROR'))
    expect(viewModel.isLoading.value).toBe(false)
  })

  it('clears the error when a later load works', async () => {
    vi.mocked(getHome).mockRejectedValueOnce({ code: 'INTERNAL_ERROR', message: 'x' }).mockResolvedValueOnce(home)
    const viewModel = useHomeViewModel()

    await viewModel.load()
    await viewModel.load()

    expect(viewModel.error.value).toBeNull()
    expect(viewModel.balance.value).toBe(125050)
  })

  it('knows when there are no movements', async () => {
    vi.mocked(getHome).mockResolvedValue({ balance: 0, totalSaved: 0, lastMovements: [] })
    const viewModel = useHomeViewModel()

    await viewModel.load()

    expect(viewModel.hasMovements.value).toBe(false)
  })
})
