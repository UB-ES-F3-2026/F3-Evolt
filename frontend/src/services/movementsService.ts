/** /api/movements — the list (US-08) with its filters (US-10), the detail and the report (US-11). One function per endpoint. */

import { apiGet, apiPost } from './apiClient'
import { mockMovement, mockMovements, mockReportMovement, useMocks } from '@/mocks'
import { fromApiMovementDetail, fromApiMovements, NO_FILTERS, toMovementsQuery } from '@/models/movement'
import type { MovementDetail, MovementFilters, MovementJson, MovementsPage, MovementsPageJson } from '@/models/movement'
import type { MovementReport } from '@/models/movementReport'

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

export async function getMovement(movementId: string): Promise<MovementDetail> {
  const json = useMocks()
    ? mockMovement(movementId)
    : await apiGet<MovementJson>(`/api/movements/${encodeURIComponent(movementId)}`)
  return fromApiMovementDetail(json)
}

export async function reportMovement(movementId: string, description: string): Promise<MovementReport> {
  return useMocks()
    ? mockReportMovement(movementId, description)
    : apiPost<MovementReport>(`/api/movements/${encodeURIComponent(movementId)}/reports`, { description })
}
