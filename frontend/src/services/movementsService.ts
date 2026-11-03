/** GET /api/movements — paginated movement list (US-08) with its filters (US-10). One function per endpoint. */

import { apiGet } from './apiClient'
import { mockMovements, useMocks } from '@/mocks'
import { fromApiMovements, NO_FILTERS, toMovementsQuery } from '@/models/movement'
import type { MovementFilters, MovementsPage, MovementsPageJson } from '@/models/movement'

export async function getMovements(
  offset = 0,
  limit = 20,
  filters: MovementFilters = NO_FILTERS,
): Promise<MovementsPage> {
  const query = toMovementsQuery(filters)
  const json = useMocks()
    ? mockMovements(offset, limit, query)
    : await apiGet<MovementsPageJson>(
        `/api/movements?${new URLSearchParams({ offset: String(offset), limit: String(limit), ...query })}`,
      )
  return {
    items: fromApiMovements(json.items),
    nextOffset: json.nextOffset,
  }
}
