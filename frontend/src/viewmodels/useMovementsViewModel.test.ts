import { flushPromises } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { NO_FILTERS, type Movement, type MovementFilters, type MovementsPage } from '@/models/movement'
import { DATE_RANGE_MESSAGE, SEARCH_DELAY_MS, useMovementsViewModel } from './useMovementsViewModel'

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

// A backend with `total` movements, filtered by type and concept and served in pages
// like docs/api.md §4.2 and §10.2.
function fakeBackend(total: number) {
  const all = Array.from({ length: total }, (_, i) => movement(i + 1))
  return vi.fn(async (offset: number, limit: number, filters: MovementFilters = NO_FILTERS): Promise<MovementsPage> => {
    const matching = all.filter(
      (item) =>
        (filters.type === 'all' || item.type === filters.type) &&
        item.concept.toLowerCase().includes(filters.search.toLowerCase()),
    )
    const items = matching.slice(offset, offset + limit)
    return { items, nextOffset: offset + items.length < matching.length ? offset + items.length : null }
  })
}

// A page that arrives only when the test says so, to put answers out of order.
function deferredPage() {
  let resolve: (page: MovementsPage) => void = () => {}
  const promise = new Promise<MovementsPage>((done) => (resolve = done))
  return { promise, resolve }
}

const networkError = { code: 'NETWORK_ERROR', message: 'x' }

describe('useMovementsViewModel', () => {
  it('loads the first 20 movements and knows there are more', async () => {
    const fetchPage = fakeBackend(30)
    const viewModel = useMovementsViewModel(fetchPage)

    await viewModel.loadFirstPage()

    expect(fetchPage).toHaveBeenCalledWith(0, 20, NO_FILTERS)
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

    expect(fetchPage).toHaveBeenLastCalledWith(20, 20, NO_FILTERS)
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
    expect(fetchPage).toHaveBeenLastCalledWith(20, 20, NO_FILTERS)
    expect(viewModel.items.value).toHaveLength(30)
    expect(viewModel.error.value).toBeNull()
  })
})

describe('useMovementsViewModel filters (US-10)', () => {
  beforeEach(() => {
    // Only the timers: flushPromises still needs the real setImmediate.
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] })
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  async function typeAndWait(viewModel: ReturnType<typeof useMovementsViewModel>, text: string) {
    viewModel.search.value = text
    await flushPromises()
    vi.advanceTimersByTime(SEARCH_DELAY_MS)
    await flushPromises()
  }

  it('sends the chosen dates and type, starting again from the first page', async () => {
    const fetchPage = fakeBackend(30)
    const viewModel = useMovementsViewModel(fetchPage)
    await viewModel.loadFirstPage()

    viewModel.dateFrom.value = '2026-11-01'
    viewModel.dateTo.value = '2026-11-02'
    viewModel.type.value = 'expense'
    await flushPromises()

    // The three changes ask once, not three times.
    expect(fetchPage).toHaveBeenCalledTimes(2)
    expect(fetchPage).toHaveBeenLastCalledWith(0, 20, {
      dateFrom: '2026-11-01',
      dateTo: '2026-11-02',
      type: 'expense',
      search: '',
    })
    expect(viewModel.items.value.every((item) => item.type === 'expense')).toBe(true)
  })

  it('waits until the typing stops before searching, and searches once', async () => {
    const fetchPage = fakeBackend(30)
    const viewModel = useMovementsViewModel(fetchPage)
    await viewModel.loadFirstPage()

    for (const text of ['M', 'Mo', 'Moviment 1']) {
      viewModel.search.value = text
      await flushPromises()
      vi.advanceTimersByTime(SEARCH_DELAY_MS - 1)
    }
    expect(fetchPage).toHaveBeenCalledTimes(1)

    vi.advanceTimersByTime(1)
    await flushPromises()

    expect(fetchPage).toHaveBeenCalledTimes(2)
    expect(fetchPage).toHaveBeenLastCalledWith(0, 20, { ...NO_FILTERS, search: 'Moviment 1' })
    // «Moviment 1» and «Moviment 10» to «Moviment 19».
    expect(viewModel.items.value).toHaveLength(11)
  })

  it('does not search again for spaces at the ends', async () => {
    const fetchPage = fakeBackend(30)
    const viewModel = useMovementsViewModel(fetchPage)
    await viewModel.loadFirstPage()

    await typeAndWait(viewModel, '   ')

    expect(fetchPage).toHaveBeenCalledTimes(1)
  })

  it('keeps only the answer of the last request when an older one arrives late', async () => {
    const slow = deferredPage()
    const fetchPage = vi.fn(fakeBackend(30)).mockReturnValueOnce(slow.promise)
    const viewModel = useMovementsViewModel(fetchPage)

    const first = viewModel.loadFirstPage()
    viewModel.type.value = 'income'
    await flushPromises()
    slow.resolve({ items: [movement(1)], nextOffset: 1 })
    await first

    expect(viewModel.items.value).toHaveLength(15)
    expect(viewModel.items.value.every((item) => item.type === 'income')).toBe(true)
    expect(viewModel.isLoading.value).toBe(false)
  })

  it('never adds a page asked before a filter changed, so nothing is repeated', async () => {
    const fetchPage = vi.fn(fakeBackend(60))
    const viewModel = useMovementsViewModel(fetchPage)
    await viewModel.loadFirstPage()
    const late = deferredPage()
    fetchPage.mockReturnValueOnce(late.promise)

    const more = viewModel.loadMore()
    viewModel.type.value = 'expense'
    await flushPromises()
    late.resolve({ items: [movement(21), movement(22)], nextOffset: 22 })
    await more

    const ids = viewModel.items.value.map((item) => item.id)
    expect(ids).toHaveLength(20)
    expect(new Set(ids).size).toBe(20)
    expect(viewModel.items.value.every((item) => item.type === 'expense')).toBe(true)
    expect(viewModel.isLoadingMore.value).toBe(false)
  })

  it('says «No hi ha resultats» when nothing matches, not that there are no movements', async () => {
    const viewModel = useMovementsViewModel(fakeBackend(30))
    await viewModel.loadFirstPage()

    await typeAndWait(viewModel, 'xyz')

    expect(viewModel.items.value).toEqual([])
    expect(viewModel.hasNoResults.value).toBe(true)
    expect(viewModel.isEmpty.value).toBe(false)
  })

  it('clears every filter with one request and shows the full list again', async () => {
    const fetchPage = fakeBackend(30)
    const viewModel = useMovementsViewModel(fetchPage)
    await viewModel.loadFirstPage()
    expect(viewModel.canClearFilters.value).toBe(false)

    viewModel.type.value = 'expense'
    viewModel.dateFrom.value = '2026-10-01'
    await typeAndWait(viewModel, 'xyz')
    expect(viewModel.canClearFilters.value).toBe(true)
    const callsBefore = fetchPage.mock.calls.length

    viewModel.clearFilters()
    await flushPromises()
    vi.advanceTimersByTime(SEARCH_DELAY_MS)
    await flushPromises()

    expect(fetchPage).toHaveBeenCalledTimes(callsBefore + 1)
    expect(fetchPage).toHaveBeenLastCalledWith(0, 20, NO_FILTERS)
    expect(viewModel.items.value).toHaveLength(20)
    expect(viewModel.hasNoResults.value).toBe(false)
    expect(viewModel.canClearFilters.value).toBe(false)
  })

  it('offers to clear the search while it is still being typed', () => {
    const viewModel = useMovementsViewModel(fakeBackend(30))

    viewModel.search.value = 'Mov'

    expect(viewModel.canClearFilters.value).toBe(true)
  })

  it('does not ask the backend when the start date is after the end date', async () => {
    const fetchPage = fakeBackend(30)
    const viewModel = useMovementsViewModel(fetchPage)
    await viewModel.loadFirstPage()

    viewModel.dateFrom.value = '2026-11-02'
    viewModel.dateTo.value = '2026-11-01'
    await flushPromises()

    expect(viewModel.dateError.value).toBe(DATE_RANGE_MESSAGE)
    expect(fetchPage).toHaveBeenCalledTimes(1)

    viewModel.dateTo.value = '2026-11-03'
    await flushPromises()

    expect(viewModel.dateError.value).toBeNull()
    expect(fetchPage).toHaveBeenCalledTimes(2)
  })

  it('does not ask for the next page while the dates are the wrong way round', async () => {
    const fetchPage = fakeBackend(30)
    const viewModel = useMovementsViewModel(fetchPage)
    await viewModel.loadFirstPage()

    viewModel.dateFrom.value = '2026-11-02'
    viewModel.dateTo.value = '2026-11-01'
    await flushPromises()
    await viewModel.loadMore()

    expect(fetchPage).toHaveBeenCalledTimes(1)
    expect(viewModel.items.value).toHaveLength(20)
    expect(viewModel.error.value).toBeNull()
  })

  it('opens and closes the filters', () => {
    const viewModel = useMovementsViewModel(fakeBackend(0))
    expect(viewModel.areFiltersOpen.value).toBe(false)

    viewModel.toggleFilters()
    expect(viewModel.areFiltersOpen.value).toBe(true)

    viewModel.toggleFilters()
    expect(viewModel.areFiltersOpen.value).toBe(false)
  })

  it('names the type options in order: Tots, Ingressos, Despeses', () => {
    const viewModel = useMovementsViewModel(fakeBackend(0))

    expect(viewModel.typeOptions.map((option) => option.label)).toEqual(['Tots', 'Ingressos', 'Despeses'])
  })
})
