import { describe, expect, it } from 'vitest'
import type { MovementJson } from '@/models/movement'
import { madridDaysAgoAt, toContractDate } from './madridTime'
import { filterMovements, foldText } from './movementFilters'
import { DEMO_MOVEMENTS } from './seed'

// The seed of docs/proves-moviments.md: "today" is 3/11/2026, newest first.
const T0 = new Date('2026-11-03T10:00:00+01:00')
const SEED: MovementJson[] = DEMO_MOVEMENTS.map(([daysAgo, hhmm, concept, type, icon, amount, counterparty], i) => ({
  id: `mov-${String(i + 1).padStart(2, '0')}`,
  amount,
  concept,
  date: toContractDate(madridDaysAgoAt(T0, daysAgo, hhmm)),
  type,
  icon,
  counterparty: counterparty ?? null,
  status: 'completed',
  reference: `EVT-${String(i + 1).padStart(6, '0')}`,
})).reverse()

const ids = (list: MovementJson[]) => list.map((movement) => movement.id)

function expectFailure(action: () => unknown, code: string) {
  let failure: unknown
  try {
    action()
  } catch (thrown) {
    failure = thrown
  }
  expect(failure).toMatchObject({ code })
}

describe('filterMovements (docs/api.md §10.2)', () => {
  it('M-01 · finds the 4 «Supermercat» among the expenses, newest first', () => {
    expect(ids(filterMovements(SEED, { type: 'expense', q: 'super' }))).toEqual(['mov-28', 'mov-23', 'mov-13', 'mov-06'])
  })

  it('M-02, M-03 · ignores accents and case', () => {
    expect(ids(filterMovements(SEED, { q: 'recarrega' }))).toEqual(['mov-16', 'mov-07'])
    expect(filterMovements(SEED, { q: 'SUPER' })).toEqual(filterMovements(SEED, { q: 'super' }))
  })

  it('M-04, M-05 · keeps only the chosen type', () => {
    expect(filterMovements(SEED, { type: 'expense' })).toHaveLength(23)
    expect(filterMovements(SEED, { type: 'income' })).toHaveLength(7)
  })

  it('M-06, M-07 · searches the counterparty too, also without accents', () => {
    expect(ids(filterMovements(SEED, { q: 'marta' }))).toEqual(['mov-09'])
    expect(ids(filterMovements(SEED, { q: 'nuria' }))).toEqual(['mov-29'])
  })

  it('M-08, M-09 · includes both ends of the dates', () => {
    expect(ids(filterMovements(SEED, { dateFrom: '2026-11-01', dateTo: '2026-11-02' }))).toEqual([
      'mov-30',
      'mov-29',
      'mov-28',
    ])
    expect(ids(filterMovements(SEED, { dateFrom: '2026-11-01', dateTo: '2026-11-01' }))).toEqual(['mov-29', 'mov-28'])
  })

  it('M-10, M-11 · rejects a start after the end and days that do not exist', () => {
    expectFailure(() => filterMovements(SEED, { dateFrom: '2026-11-02', dateTo: '2026-11-01' }), 'VALIDATION_ERROR')
    expectFailure(() => filterMovements(SEED, { dateFrom: '2026-13-01' }), 'VALIDATION_ERROR')
    expectFailure(() => filterMovements(SEED, { dateFrom: '01/11/2026' }), 'VALIDATION_ERROR')
  })

  it('M-15, M-16 · gives nothing for an unknown text, and everything for only spaces', () => {
    expect(filterMovements(SEED, { q: 'xyz' })).toEqual([])
    expect(filterMovements(SEED, { q: '   ' })).toHaveLength(30)
  })

  it('M-18 · combines dates, type and search', () => {
    expect(ids(filterMovements(SEED, { dateFrom: '2026-10-01', type: 'income', q: 'nomina' }))).toEqual(['mov-17'])
  })
})

describe('foldText', () => {
  it('drops accents and capitals', () => {
    expect(foldText('Núria Soler')).toBe('nuria soler')
    expect(foldText('Recàrrega')).toBe('recarrega')
  })
})
