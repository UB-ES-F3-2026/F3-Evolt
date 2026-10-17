import { describe, expect, it, vi } from 'vitest'
import type { Movement, MovementsPage } from '@/models/movement'
import { useMovementsViewModel } from './useMovementsViewModel'

function movement(n: number): Movement {
  return {
    id: `mov-${n}`,
    amount: 100 * n,
    concept: `Moviment ${n}`,
    date: '2026-10-11T21:15:00+02:00',
    type: n % 2 ? 'expense' : 'income',
    icon: 'other',
  }
}

// A backend with `total` movements, served in pages like docs/api.md §4.2.
function fakeBackend(total: number) {
  const all = Array.from({ length: total }, (_, i) => movement(i + 1))
  return vi.fn(async (offset: number, limit: number): Promise<MovementsPage> => {
    const items = all.slice(offset, offset + limit)
    return { items, nextOffset: offset + items.length < total ? offset + items.length : null }
  })
}

const networkError = { code: 'NETWORK_ERROR', message: 'x' }

describe('useMovementsViewModel', () => {
  it('loads the first 20 movements and knows there are more', async () => {
    const fetchPage = fakeBackend(30)
    const viewModel = useMovementsViewModel(fetchPage)

    await viewModel.loadFirstPage()

    expect(fetchPage).toHaveBeenCalledWith(0, 20)
    expect(viewModel.items.value).toHaveLength(20)
    expect(viewModel.items.value[0].id).toBe('mov-1')
    expect(viewModel.hasMore.value).toBe(true)
    expect(viewModel.isLoading.value).toBe(false)
  })

  it('adds the next page at the end, in order', async () => {
    const fetchPage = fakeBackend(30)
    const viewModel = useMovementsViewModel(fetchPage)
    await viewModel.loadFirstPage()

    await viewModel.loadMore()

    expect(fetchPage).toHaveBeenLastCalledWith(20, 20)
    expect(viewModel.items.value.map((item) => item.id)).toEqual(
      Array.from({ length: 30 }, (_, i) => `mov-${i + 1}`),
    )
    expect(viewModel.hasMore.value).toBe(false)
  })

  it('stops asking at the end of the list', async () => {
    const fetchPage = fakeBackend(5)
    const viewModel = useMovementsViewModel(fetchPage)
    await viewModel.loadFirstPage()

    await viewModel.loadMore()

    expect(viewModel.hasMore.value).toBe(false)
    expect(fetchPage).toHaveBeenCalledTimes(1)
  })

  it('never loads the same page twice when asked twice at once', async () => {
    const fetchPage = fakeBackend(60)
    const viewModel = useMovementsViewModel(fetchPage)
    await viewModel.loadFirstPage()

    await Promise.all([viewModel.loadMore(), viewModel.loadMore()])

    expect(fetchPage).toHaveBeenCalledTimes(2)
    expect(new Set(viewModel.items.value.map((item) => item.id)).size).toBe(40)
  })

  it('does not load more while the first page is still loading', async () => {
    const fetchPage = fakeBackend(30)
    const viewModel = useMovementsViewModel(fetchPage)

    const first = viewModel.loadFirstPage()
    await viewModel.loadMore()
    await first

    expect(fetchPage).toHaveBeenCalledTimes(1)
  })

  it('is empty only for a user with no movements', async () => {
    const viewModel = useMovementsViewModel(fakeBackend(0))
    expect(viewModel.isEmpty.value).toBe(false)

    await viewModel.loadFirstPage()

    expect(viewModel.items.value).toEqual([])
    expect(viewModel.isEmpty.value).toBe(true)
  })

  it('shows an error if the first page fails, and retry loads it again', async () => {
    const working = fakeBackend(30)
    const fetchPage = vi.fn().mockRejectedValueOnce(networkError).mockImplementation(working)
    const viewModel = useMovementsViewModel(fetchPage)

    await viewModel.loadFirstPage()
    expect(viewModel.error.value).toMatch(/connexió/)
    expect(viewModel.isEmpty.value).toBe(false)

    await viewModel.retry()
    expect(viewModel.error.value).toBeNull()
    expect(viewModel.items.value).toHaveLength(20)
  })

  it('keeps what was loaded when the next page fails, and retry continues from there', async () => {
    const working = fakeBackend(30)
    const fetchPage = vi.fn(working)
    const viewModel = useMovementsViewModel(fetchPage)
    await viewModel.loadFirstPage()
    fetchPage.mockRejectedValueOnce(networkError)

    await viewModel.loadMore()
    expect(viewModel.items.value).toHaveLength(20)
    expect(viewModel.error.value).toMatch(/connexió/)

    await viewModel.loadMore()
    expect(fetchPage).toHaveBeenCalledTimes(2)

    await viewModel.retry()
    expect(fetchPage).toHaveBeenLastCalledWith(20, 20)
    expect(viewModel.items.value).toHaveLength(30)
    expect(viewModel.error.value).toBeNull()
  })
})
