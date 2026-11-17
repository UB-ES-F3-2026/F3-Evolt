/** Currency exchange (US-27): the owned sub-accounts and one exchange. One function per endpoint. */

import { apiGet, apiPost } from './apiClient'
import { useMocks } from '@/mocks'
import { mockGetSubaccounts, mockPostExchange } from '@/mocks/exchange'
import type { ExchangeRequestJson, ExchangeResultJson, SubaccountJson } from '@/models/exchange'

// The contract types belong to `models/` (AGENTS.md §3); re-exported so the
// ViewModels keep importing them from the service they call.
export type { ExchangeRequestJson, ExchangeResultJson, SubaccountJson }

/**
 * TODO(a crear): GET /api/currencies — issue #166. Returns the owned sub-accounts
 * (code, balance, isMain). Rates are NOT fetched: the rate table is local (US-25).
 */
export async function getSubaccounts(): Promise<SubaccountJson[]> {
  return useMocks() ? mockGetSubaccounts() : await apiGet<SubaccountJson[]>('/api/currencies')
}

/**
 * TODO(a crear): POST /api/exchanges — issue #166. The backend exchange is one atomic
 * transaction (both balances + both movements, all or nothing) — issue #173.
 * When #166 lands, the response must also echo the applied `rateBps` and `commission`,
 * so the summary shows the server's figures instead of recomputing them client-side.
 */
export async function postExchange(request: ExchangeRequestJson): Promise<ExchangeResultJson> {
  return useMocks()
    ? mockPostExchange(request)
    : await apiPost<ExchangeResultJson>('/api/exchanges', request)
}
