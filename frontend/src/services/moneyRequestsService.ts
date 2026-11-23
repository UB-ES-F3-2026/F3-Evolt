/** /api/money-requests — the requests the person sent (US-15). One function per endpoint. */

import { apiGet, apiPost } from './apiClient'
import { useMocks } from '@/mocks'
import { mockCancelMoneyRequest, mockCreateMoneyRequest, mockMoneyRequests } from '@/mocks/moneyRequests'
import {
  fromApiMoneyRequest,
  fromApiMoneyRequests,
  type MoneyRequest,
  type MoneyRequestJson,
  type MoneyRequestsJson,
  type NewMoneyRequest,
} from '@/models/moneyRequest'

export async function getMoneyRequests(): Promise<MoneyRequest[]> {
  const json = useMocks() ? mockMoneyRequests() : await apiGet<MoneyRequestsJson>('/api/money-requests')
  return fromApiMoneyRequests(json.items)
}

export async function createMoneyRequest(request: NewMoneyRequest): Promise<MoneyRequest> {
  const json = useMocks()
    ? mockCreateMoneyRequest({ ...request })
    : await apiPost<MoneyRequestJson>('/api/money-requests', request)
  return fromApiMoneyRequest(json)
}

/** Deletes a pending request: there is no «Cancel·lada» (docs/api.md §14.4). */
export async function cancelMoneyRequest(requestId: string): Promise<void> {
  if (useMocks()) mockCancelMoneyRequest(requestId)
  // The cancel has no body (§14.4).
  else await apiPost<{ status: string }>(`/api/money-requests/${encodeURIComponent(requestId)}/cancel`, undefined)
}
