/** /api/account — the details of the person's account (US-12). One function per endpoint. */

import { apiGet } from '@/services/apiClient'
import { useMocks } from '@/mocks'
import { mockAccountDetails } from '@/mocks/account'
import { fromApiAccountDetails, type AccountDetails, type AccountDetailsJson } from '@/models/account'

export async function getAccountDetails(): Promise<AccountDetails> {
  const json = useMocks() ? mockAccountDetails() : await apiGet<AccountDetailsJson>('/api/account')
  return fromApiAccountDetails(json)
}
