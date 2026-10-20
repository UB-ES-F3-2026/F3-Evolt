/** GET /api/movements — paginated movement list (US-08). One function per endpoint. */

import { apiGet } from './apiClient'
import { mockMovements, useMocks } from '@/mocks'
import { fromApiMovements } from '@/models/movement'
import type { MovementsPage, MovementsPageJson } from '@/models/movement'

export async function getMovements(offset = 0, limit = 20): Promise<MovementsPage> {
  const json = useMocks()
    ? mockMovements(offset, limit)
    : await apiGet<MovementsPageJson>(`/api/movements?offset=${offset}&limit=${limit}`)
  return {
    items: fromApiMovements(json.items),
    nextOffset: json.nextOffset,
  }
}
