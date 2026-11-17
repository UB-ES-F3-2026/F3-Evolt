/** /api/subaccounts — currency sub-accounts (US-25). One function per endpoint. */

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
