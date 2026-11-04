/**
 * The filters of GET /api/movements as docs/api.md §10.2 defines them, for the mocks:
 * days in Madrid with both ends included, and a search in the concept or the
 * counterparty that ignores case, accents and the spaces at the ends.
 */

import type { MovementJson, MovementsQuery } from '@/models/movement'
import { mockError } from './index'
import { madridDayKey } from './madridTime'

const DAY_FORMAT = /^\d{4}-\d{2}-\d{2}$/

/**
 * The movements that match every filter in `query`, in the same order.
 * A bad day or `dateFrom` after `dateTo` throws `VALIDATION_ERROR`, like the backend.
 */
export function filterMovements(movements: MovementJson[], query: MovementsQuery): MovementJson[] {
  const { dateFrom, dateTo, type } = query
  if (!isValidDay(dateFrom) || !isValidDay(dateTo) || (dateFrom && dateTo && dateFrom > dateTo)) {
    throw mockError('VALIDATION_ERROR', 'Les dades de la petició no són vàlides.')
  }
  const text = foldText(query.q?.trim() ?? '')

  return movements.filter((movement) => {
    const day = madridDayKey(new Date(movement.date))
    if (dateFrom && day < dateFrom) return false
    if (dateTo && day > dateTo) return false
    if (type && movement.type !== type) return false
    if (!text) return true
    return [movement.concept, movement.counterparty ?? ''].some((field) => foldText(field).includes(text))
  })
}

/** `recarrega` finds «Recàrrega» and `SUPER` finds «Supermercat». */
export function foldText(text: string): string {
  return text.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
}

/** A missing day is fine; a present one must be a real `YYYY-MM-DD` (`2026-13-01` is not). */
function isValidDay(day: string | undefined): boolean {
  if (day === undefined) return true
  if (!DAY_FORMAT.test(day)) return false
  const [year, month, date] = day.split('-').map(Number)
  const parsed = new Date(Date.UTC(year, month - 1, date))
  return parsed.getUTCFullYear() === year && parsed.getUTCMonth() === month - 1 && parsed.getUTCDate() === date
}
