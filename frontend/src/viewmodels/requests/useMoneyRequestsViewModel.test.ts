import { describe, expect, it, vi } from 'vitest'
import { messageForCode } from '@/models/errorMessages'
import type { MoneyRequest } from '@/models/moneyRequest'
import { useMoneyRequestsViewModel, type MoneyRequestsDependencies } from './useMoneyRequestsViewModel'

const pending: MoneyRequest = {
  id: 'req-02',
  to: { id: 'usr-03', name: 'Alicia', username: 'aliciaa415' },
  amount: 2500,
  concept: 'El sopar de divendres',
  status: 'pending',
  createdAt: '2026-11-22T19:30:00+01:00',
  expiresAt: '2026-11-29T00:00:00+01:00',
}
const expired: MoneyRequest = {
  ...pending,
  id: 'req-01',
  to: { id: 'usr-04', name: 'Huabin', username: '123huabin123' },
  amount: 4200,
  concept: 'Pizza del diumenge',
  status: 'expired',
}

function setUp(overrides: Partial<MoneyRequestsDependencies> = {}) {
  const dependencies = {
    getMoneyRequests: vi.fn(() => Promise.resolve([pending, expired])),
    cancelMoneyRequest: vi.fn((_id: string) => Promise.resolve()),
    ...overrides,
  }
  return { viewModel: useMoneyRequestsViewModel(dependencies), dependencies }
}

describe('useMoneyRequestsViewModel', () => {
  it('SOP-01: lists the sent requests with their status', async () => {
    const { viewModel } = setUp()

    await viewModel.load()

    expect(viewModel.requests.value).toEqual([pending, expired])
    expect(viewModel.isEmpty.value).toBe(false)
  })

  it('SOP-02: with no request the screen is empty', async () => {
    const { viewModel } = setUp({ getMoneyRequests: vi.fn(() => Promise.resolve([])) })

    await viewModel.load()

    expect(viewModel.isEmpty.value).toBe(true)
  })

  it('SOP-07, SOP-08: «Cancel·lar» opens the dialog, and closing it sends nothing', async () => {
    const { viewModel, dependencies } = setUp()
    await viewModel.load()

    viewModel.askToCancel(pending)
    expect(viewModel.requestToCancel.value).toEqual(pending)
    viewModel.keepRequest()

    expect(viewModel.requestToCancel.value).toBeNull()
    expect(dependencies.cancelMoneyRequest).not.toHaveBeenCalled()
    expect(viewModel.requests.value).toHaveLength(2)
  })

  it('SOP-09: «Confirmar» deletes it, says «Sol·licitud cancel·lada.» and removes the row', async () => {
    const { viewModel, dependencies } = setUp()
    await viewModel.load()
    viewModel.askToCancel(pending)

    await viewModel.confirmCancel()

    expect(dependencies.cancelMoneyRequest).toHaveBeenCalledWith('req-02')
    expect(viewModel.notice.value).toBe('Sol·licitud cancel·lada.')
    expect(viewModel.requests.value).toEqual([expired])
    expect(viewModel.requestToCancel.value).toBeNull()
  })

  it.each(['REQUEST_NOT_PENDING', 'REQUEST_NOT_FOUND'] as const)(
    'SOP-10: %s shows its text and reads the list again',
    async (code) => {
      const { viewModel, dependencies } = setUp({
        cancelMoneyRequest: vi.fn(() => Promise.reject({ code, message: 'x' })),
      })
      await viewModel.load()
      viewModel.askToCancel(pending)

      await viewModel.confirmCancel()

      expect(viewModel.cancelError.value).toBe(messageForCode(code))
      expect(viewModel.notice.value).toBeNull()
      expect(dependencies.getMoneyRequests).toHaveBeenCalledTimes(2)
    },
  )
})
