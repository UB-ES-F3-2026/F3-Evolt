import { describe, expect, it, vi } from 'vitest'
import { messageForCode } from '@/models/errorMessages'
import type { ReceivedMoneyRequest } from '@/models/moneyRequest'
import {
  useReceivedMoneyRequestsViewModel,
  type ReceivedMoneyRequestsDependencies,
} from './useReceivedMoneyRequestsViewModel'

const pending: ReceivedMoneyRequest = {
  id: 'req-06',
  from: { id: 'usr-03', name: 'Alicia', username: 'aliciaa415' },
  amount: 2500,
  concept: 'El sopar de divendres',
  status: 'pending',
  createdAt: '2026-11-23T19:30:00+01:00',
  expiresAt: '2026-11-30T00:00:00+01:00',
}
const paid: ReceivedMoneyRequest = {
  ...pending,
  id: 'req-05',
  from: { id: 'usr-07', name: 'Junhao', username: 'junhaozhang' },
  amount: 1200,
  concept: 'Cafès de la setmana',
  status: 'paid',
}

function setUp(overrides: Partial<ReceivedMoneyRequestsDependencies> = {}) {
  const dependencies = {
    getReceivedMoneyRequests: vi.fn(() => Promise.resolve([pending, paid])),
    ...overrides,
  }
  return { viewModel: useReceivedMoneyRequestsViewModel(dependencies), dependencies }
}

describe('useReceivedMoneyRequestsViewModel', () => {
  it('starts loading, with nothing to show yet', () => {
    const { viewModel } = setUp()

    expect(viewModel.isLoading.value).toBe(true)
    expect(viewModel.isEmpty.value).toBe(false)
  })

  it('SRP-02, SRP-03: lists the received requests in the order and with the status the server sends', async () => {
    const { viewModel } = setUp()

    await viewModel.load()

    expect(viewModel.requests.value).toEqual([pending, paid])
    expect(viewModel.isLoading.value).toBe(false)
    expect(viewModel.isEmpty.value).toBe(false)
  })

  it('SRP-05: with no received request the screen is empty', async () => {
    const { viewModel } = setUp({ getReceivedMoneyRequests: vi.fn(() => Promise.resolve([])) })

    await viewModel.load()

    expect(viewModel.isEmpty.value).toBe(true)
    expect(viewModel.loadError.value).toBeNull()
  })

  it('SRP-06: an error shows the generic text, not the empty state', async () => {
    const { viewModel } = setUp({
      getReceivedMoneyRequests: vi.fn(() => Promise.reject({ code: 'INTERNAL_ERROR', message: 'x' })),
    })

    await viewModel.load()

    expect(viewModel.loadError.value).toBe(messageForCode('INTERNAL_ERROR'))
    expect(viewModel.loadError.value).toBe("S'ha produït un error inesperat. Torna-ho a provar més tard.")
    expect(viewModel.isEmpty.value).toBe(false)
  })

  it('SRP-06: «Reintentar» loads the list again and clears the error', async () => {
    const getReceivedMoneyRequests = vi
      .fn<() => Promise<ReceivedMoneyRequest[]>>()
      .mockRejectedValueOnce({ code: 'INTERNAL_ERROR', message: 'x' })
      .mockResolvedValueOnce([pending])
    const { viewModel } = setUp({ getReceivedMoneyRequests })
    await viewModel.load()

    await viewModel.load()

    expect(viewModel.loadError.value).toBeNull()
    expect(viewModel.requests.value).toEqual([pending])
    expect(getReceivedMoneyRequests).toHaveBeenCalledTimes(2)
  })
})
