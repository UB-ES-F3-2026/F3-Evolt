import { beforeEach, describe, expect, it, vi } from 'vitest'
import { messageForCode } from '@/models/errorMessages'
import type { Pot, PotMovement } from '@/models/pot'
import { getPotMovements, getPots } from '@/services/potsService'
import { usePotViewModel } from './usePotViewModel'

vi.mock('@/services/potsService', () => ({ getPots: vi.fn(), getPotMovements: vi.fn() }))

const vacances: Pot = { id: 'pot-01', name: 'Vacances', balance: 18000, target: 100000, color: 'blue' }
const entries: PotMovement[] = [
  { id: 'pmov-04', amount: 3000, concept: 'Aportació', date: '2026-11-03T10:00:00+01:00', type: 'income' },
  { id: 'pmov-01', amount: 15000, concept: 'Saldo inicial', date: '2026-10-04T10:00:00+02:00', type: 'income' },
]

beforeEach(() => {
  vi.mocked(getPots).mockReset()
  vi.mocked(getPotMovements).mockReset()
})

describe('usePotViewModel', () => {
  it('starts loading, with the generic title', () => {
    const viewModel = usePotViewModel('pot-01')

    expect(viewModel.isLoading.value).toBe(true)
    expect(viewModel.title.value).toBe('Guardiola')
  })

  it('shows the pot and its history, newest first, drawn as income with the pot icon', async () => {
    vi.mocked(getPots).mockResolvedValue([vacances])
    vi.mocked(getPotMovements).mockResolvedValue(entries)
    const viewModel = usePotViewModel('pot-01')

    await viewModel.load()

    expect(vi.mocked(getPotMovements)).toHaveBeenCalledWith('pot-01')
    expect(viewModel.pot.value).toEqual(vacances)
    expect(viewModel.title.value).toBe('Vacances')
    expect(viewModel.history.value.map((entry) => [entry.concept, entry.type, entry.icon])).toEqual([
      ['Aportació', 'income', 'savings'],
      ['Saldo inicial', 'income', 'savings'],
    ])
    expect(viewModel.hasHistory.value).toBe(true)
    expect(viewModel.error.value).toBeNull()
  })

  it('knows when a pot has no history yet', async () => {
    vi.mocked(getPots).mockResolvedValue([{ ...vacances, balance: 0 }])
    vi.mocked(getPotMovements).mockResolvedValue([])
    const viewModel = usePotViewModel('pot-01')

    await viewModel.load()

    expect(viewModel.hasHistory.value).toBe(false)
  })

  it('says the pot does not exist when the backend answers POT_NOT_FOUND', async () => {
    vi.mocked(getPots).mockResolvedValue([vacances])
    vi.mocked(getPotMovements).mockRejectedValue({ code: 'POT_NOT_FOUND', message: 'x' })
    const viewModel = usePotViewModel('pot-99')

    await viewModel.load()

    expect(viewModel.error.value).toBe(messageForCode('POT_NOT_FOUND'))
    expect(viewModel.isLoading.value).toBe(false)
  })

  it('says the pot does not exist when it is not in the list', async () => {
    vi.mocked(getPots).mockResolvedValue([])
    vi.mocked(getPotMovements).mockResolvedValue([])
    const viewModel = usePotViewModel('pot-01')

    await viewModel.load()

    expect(viewModel.pot.value).toBeNull()
    expect(viewModel.error.value).toBe(messageForCode('POT_NOT_FOUND'))
  })
})
