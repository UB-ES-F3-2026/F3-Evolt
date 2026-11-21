/**
 * `/api/subaccounts` — currency sub-accounts (§12, US-25/US-26). One function per
 * endpoint.
 *
 * The mock speaks app shapes (`SubaccountList` / `Subaccount`) and the API speaks
 * wire shapes (`SubaccountsJson` / `SubaccountJson`), so only the API path maps:
 * running `fromApiSubaccountsList` over a mock response would find no `currency`
 * field and silently drop every row.
 */

import { apiGet, apiPost } from './apiClient'
import { useMocks } from '@/mocks'
import { mockAddSubaccount, mockSubaccounts } from '@/mocks/currencies'
import {
  fromApiSubaccount,
  fromApiSubaccountsList,
  type CurrencyCode,
  type Subaccount,
  type SubaccountJson,
  type SubaccountList,
  type SubaccountsJson,
} from '@/models/currency'

/** GET /api/subaccounts (§12.3): the rows plus the server-computed approximate total. */
export async function getSubaccounts(): Promise<SubaccountList> {
  if (useMocks()) return mockSubaccounts()
  return fromApiSubaccountsList(await apiGet<SubaccountsJson>('/api/subaccounts'))
}

/** POST /api/subaccounts (§12.4): a new currency sub-account, with `balance: 0`. */
export async function addSubaccount(code: CurrencyCode): Promise<Subaccount> {
  return useMocks()
    ? mockAddSubaccount({ currency: code })
    : fromApiSubaccount(await apiPost<SubaccountJson>('/api/subaccounts', { currency: code }))
}
