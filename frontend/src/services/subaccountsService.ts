/** /api/subaccounts — currency sub-accounts (US-25 and US-26). One function per endpoint. */

import { apiGet, apiPost } from './apiClient'
import { useMocks } from '@/mocks'
import {
  mockAddSubaccount,
  mockDeleteSubaccount,
  mockSubaccountMovements,
  mockSubaccounts,
} from '@/mocks/currencies'
import {
  fromApiSubaccount,
  fromApiSubaccountsList,
  type CurrencyCode,
  type DeleteSubaccountJson,
  type Subaccount,
  type SubaccountJson,
  type SubaccountList,
  type SubaccountMovement,
  type SubaccountMovementsJson,
  type SubaccountsJson,
} from '@/models/currency'

/**
 * GET /api/subaccounts (US-25, docs/api.md §12.3): the rows plus the server-computed
 * total in euro cents, which is passed through untouched and never recomputed here.
 */
export async function getSubaccounts(): Promise<SubaccountList> {
  const json = useMocks() ? mockSubaccounts() : await apiGet<SubaccountsJson>('/api/subaccounts')
  return fromApiSubaccountsList(json)
}

export async function addSubaccount(code: CurrencyCode): Promise<Subaccount> {
  const json = useMocks()
    ? mockAddSubaccount({ currency: code })
    : await apiPost<SubaccountJson>('/api/subaccounts', { currency: code })
  return fromApiSubaccount(json)
}

/** POST /api/subaccounts/{subaccountId}/delete (US-26, docs/api.md §12.5). POST, not DELETE: the apiClient and CORS only allow GET and POST. */
export async function deleteSubaccount(subaccountId: string): Promise<void> {
  if (useMocks()) {
    mockDeleteSubaccount(subaccountId)
    return
  }
  await apiPost<DeleteSubaccountJson>(`/api/subaccounts/${encodeURIComponent(subaccountId)}/delete`, {})
}

/** GET /api/subaccounts/{subaccountId}/movements (US-26, docs/api.md §12.6): newest first. */
export async function getSubaccountMovements(subaccountId: string): Promise<SubaccountMovement[]> {
  const json = useMocks()
    ? mockSubaccountMovements(subaccountId)
    : await apiGet<SubaccountMovementsJson>(`/api/subaccounts/${encodeURIComponent(subaccountId)}/movements`)
  return json.items
}
