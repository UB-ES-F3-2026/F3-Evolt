import { describe, expect, it } from 'vitest'
import { fromApiMovementDetail, hasFilters, NO_FILTERS, toMovementsQuery, type MovementJson } from './movement'

const BIZUM: MovementJson = {
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

describe('fromApiMovementDetail', () => {
  it('keeps the fields of the detail (docs/api.md §10.1)', () => {
    expect(fromApiMovementDetail(BIZUM)).toEqual(BIZUM)
  })

  it('keeps a movement without counterparty', () => {
    expect(fromApiMovementDetail({ ...BIZUM, counterparty: null }).counterparty).toBeNull()
  })

  it('reads an unknown status as pending, never as done', () => {
    expect(fromApiMovementDetail({ ...BIZUM, status: 'lost' }).status).toBe('pending')
  })
})

describe('toMovementsQuery', () => {
  it('sends nothing when no filter is chosen («Tots» included)', () => {
    expect(toMovementsQuery(NO_FILTERS)).toEqual({})
    expect(hasFilters(NO_FILTERS)).toBe(false)
  })

  it('sends every filter in use, with the names of docs/api.md §10.2', () => {
    const query = toMovementsQuery({ dateFrom: '2026-10-01', dateTo: '2026-11-02', type: 'income', search: 'nomina' })

    expect(query).toEqual({ dateFrom: '2026-10-01', dateTo: '2026-11-02', type: 'income', q: 'nomina' })
  })

  it('sends the search without the spaces at the ends, and not at all if it is only spaces', () => {
    expect(toMovementsQuery({ ...NO_FILTERS, search: '  super ' })).toEqual({ q: 'super' })
    expect(toMovementsQuery({ ...NO_FILTERS, search: '   ' })).toEqual({})
    expect(hasFilters({ ...NO_FILTERS, search: '   ' })).toBe(false)
  })

  it('counts a single date as a filter', () => {
    expect(hasFilters({ ...NO_FILTERS, dateTo: '2026-11-01' })).toBe(true)
  })
})
