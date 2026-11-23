import { describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { messageForCode } from '@/models/errorMessages'
import type { UserSummary } from '@/models/user'
import { usePaymentsViewModel, type PaymentsDependencies } from './usePaymentsViewModel'

const alicia: UserSummary = { id: 'usr-03', name: 'Alicia', username: 'aliciaa415' }
const huabin: UserSummary = { id: 'usr-04', name: 'Huabin', username: '123huabin123' }
const initial = [alicia, huabin]

function setUp(overrides: Partial<PaymentsDependencies> = {}) {
  const dependencies = {
    searchUsers: vi.fn((q: string) => Promise.resolve(q.trim() === '' ? initial : q.includes('611') ? [huabin] : [])),
    wait: vi.fn(() => Promise.resolve()),
    ...overrides,
  }
  return { viewModel: usePaymentsViewModel(dependencies), dependencies }
}

/** Types into the bar and lets the pause and the answer go by. */
async function type(viewModel: ReturnType<typeof usePaymentsViewModel>, text: string): Promise<void> {
  viewModel.query.value = text
  await nextTick()
  await vi.waitFor(() => expect(viewModel.showLoading.value).toBe(false))
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('usePaymentsViewModel', () => {
  it('CUP-01: shows the initial list before typing, without «Resultats de la cerca»', async () => {
    const { viewModel, dependencies } = setUp()
    expect(viewModel.showLoading.value).toBe(true)

    await viewModel.search()

    expect(dependencies.searchUsers).toHaveBeenCalledWith('')
    expect(viewModel.users.value).toEqual(initial)
    expect(viewModel.isSearching.value).toBe(false)
    expect(viewModel.showNoResults.value).toBe(false)
  })

  it('CUP-03: results come while typing, after a short pause', async () => {
    const { viewModel, dependencies } = setUp()
    await viewModel.search()

    await type(viewModel, '611 22 33 02')

    expect(dependencies.wait).toHaveBeenCalledWith(250)
    expect(dependencies.searchUsers).toHaveBeenLastCalledWith('611 22 33 02')
    expect(viewModel.users.value).toEqual([huabin])
    expect(viewModel.isSearching.value).toBe(true)
  })

  it('CUP-04: a search without matches shows «No hi ha resultats»', async () => {
    const { viewModel } = setUp()
    await viewModel.search()

    await type(viewModel, '612 34 56 78')

    expect(viewModel.users.value).toEqual([])
    expect(viewModel.showNoResults.value).toBe(true)
  })

  it('CUP-05: clearing the bar brings back the initial list, without «No hi ha resultats»', async () => {
    const { viewModel } = setUp()
    await viewModel.search()
    await type(viewModel, '612 34 56 78')

    await type(viewModel, '')

    expect(viewModel.users.value).toEqual(initial)
    expect(viewModel.showNoResults.value).toBe(false)
  })

  it('drops an answer that arrives after a newer one, so the list matches what is typed', async () => {
    let answerOld: (users: UserSummary[]) => void = () => undefined
    const searchUsers = vi
      .fn<(q: string) => Promise<UserSummary[]>>()
      .mockImplementationOnce(() => new Promise((resolve) => (answerOld = resolve)))
      .mockImplementationOnce(() => Promise.resolve([huabin]))
    const { viewModel } = setUp({ searchUsers })

    const old = viewModel.search()
    await viewModel.search()
    answerOld(initial)
    await old

    expect(viewModel.users.value).toEqual([huabin])
  })

  it('CUP-07: a text of more than 64 characters shows the validation text, and «Reintentar» asks again', async () => {
    const searchUsers = vi.fn(() => Promise.reject({ code: 'VALIDATION_ERROR', message: 'x' }))
    const { viewModel } = setUp({ searchUsers })

    await viewModel.search()

    expect(viewModel.error.value).toBe(messageForCode('VALIDATION_ERROR'))
    expect(viewModel.showNoResults.value).toBe(false)

    await viewModel.search()
    expect(searchUsers).toHaveBeenCalledTimes(2)
  })
})
