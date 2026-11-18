/** /api/subaccounts and /api/currencies — currency sub-accounts (US-25/US-27). One function per endpoint. */

import { apiGet, apiPost } from './apiClient'
import { useMocks } from '@/mocks'
import { mockAddSubaccount, mockSubaccounts } from '@/mocks/currencies'
import {
  fromApiSubaccount,
  fromApiSubaccounts,
  type CurrencyCode,
  type Subaccount,
  type SubaccountJson,
  type SubaccountsJson,
} from '@/models/currency'

// TODO(a crear): GET /api/currencies — issue #166. Returns the owned sub-accounts
// (code, balance, isMain). Rates are NOT fetched: the rate table is a client constant
// (models/currency.ts). Nothing calls it yet.

// TODO(a crear): GET /api/subaccounts — issue #166
export async function getSubaccounts(): Promise<Subaccount[]> {
  const json = useMocks() ? mockSubaccounts() : await apiGet<SubaccountsJson>('/api/subaccounts')
  return fromApiSubaccounts(json.items)
}

// TODO(a crear): POST /api/subaccounts — issue #166/#167
export async function addSubaccount(code: CurrencyCode): Promise<Subaccount> {
  const json = useMocks()
    ? mockAddSubaccount({ currency: code })
    : await apiPost<SubaccountJson>('/api/subaccounts', { currency: code })
  return fromApiSubaccount(json)
}

// TODO(a crear): POST /api/subaccounts/{id}/topups — issue #166. Future endpoint:
// top up one sub-account (documented; no caller yet).
