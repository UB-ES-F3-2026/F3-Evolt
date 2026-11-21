/**
 * Currency exchange (US-27): one exchange. One function per endpoint.
 *
 * The mock returns app shapes (`ExchangeResult`) and the API answers the §12.7 wire
 * body (`ExchangeResultJson`), so only the API path maps its two accounts.
 */

import { apiPost } from './apiClient'
import { useMocks } from '@/mocks'
import { mockPostExchange } from '@/mocks/exchange'
import { fromApiSubaccount } from '@/models/currency'
import type { ExchangeRequestJson, ExchangeResult, ExchangeResultJson } from '@/models/exchange'

// The contract types belong to `models/` (AGENTS.md §3); re-exported so the
// ViewModels keep importing them from the service they call.
export type { ExchangeRequestJson, ExchangeResult }

/**
 * POST /api/exchanges (§12.7). The response carries the server's figures — both
 * accounts with their new balance, the commission and what the target received — so
 * the success screen shows the confirmed values instead of recomputing them. The
 * applied rates are not echoed: they are the fixed client table of §12.1.
 */
export async function postExchange(request: ExchangeRequestJson): Promise<ExchangeResult> {
  if (useMocks()) return mockPostExchange(request)
  const json = await apiPost<ExchangeResultJson>('/api/exchanges', request)
  return {
    from: fromApiSubaccount(json.from),
    to: fromApiSubaccount(json.to),
    amount: json.amount,
    commission: json.commission,
    received: json.received,
  }
}
