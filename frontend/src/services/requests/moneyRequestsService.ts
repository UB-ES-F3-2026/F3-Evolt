/** /api/money-requests — the requests the person sent (US-15) and received (US-16). One function per endpoint. */

import { apiGet, apiPost } from '@/services/apiClient'
import { useMocks } from '@/mocks'
import {
  mockCancelMoneyRequest,
  mockCreateMoneyRequest,
  mockMoneyRequests,
  mockReceivedMoneyRequests,
} from '@/mocks/moneyRequests'
import {
  fromApiMoneyRequest,
  fromApiMoneyRequests,
  fromApiReceivedMoneyRequests,
  type MoneyRequest,
  type MoneyRequestJson,
  type MoneyRequestsJson,
  type NewMoneyRequest,
  type ReceivedMoneyRequest,
  type ReceivedMoneyRequestsJson,
} from '@/models/moneyRequest'

export async function getMoneyRequests(): Promise<MoneyRequest[]> {
  const json = useMocks() ? mockMoneyRequests() : await apiGet<MoneyRequestsJson>('/api/money-requests')
  return fromApiMoneyRequests(json.items)
}

/** The requests someone sent to the person, in every status, newest first (docs/api.md §15.2). */
export async function getReceivedMoneyRequests(): Promise<ReceivedMoneyRequest[]> {
  const json = useMocks()
    ? mockReceivedMoneyRequests()
    : await apiGet<ReceivedMoneyRequestsJson>('/api/money-requests/received')
  return fromApiReceivedMoneyRequests(json.items)
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
