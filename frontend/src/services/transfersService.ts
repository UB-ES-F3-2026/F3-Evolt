/** /api/transfers — sending money to another user (US-14). One function per endpoint. */

import { apiGet, apiPost } from './apiClient'
import { useMocks } from '@/mocks'
import { mockSendTransfer, mockTransferLimit } from '@/mocks/transfers'
import { fromApiTransfer, type Transfer, type TransferJson, type TransferLimit, type TransferRequest } from '@/models/transfer'

/** What can still be sent today (docs/api.md §13.5). */
export async function getTransferLimit(): Promise<TransferLimit> {
  return useMocks() ? mockTransferLimit() : await apiGet<TransferLimit>('/api/transfers/limit')
}

/** Sends the money; the server checks balance and limit again (docs/api.md §13.4). */
export async function sendTransfer(request: TransferRequest): Promise<Transfer> {
  const json = useMocks() ? mockSendTransfer({ ...request }) : await apiPost<TransferJson>('/api/transfers', request)
  return fromApiTransfer(json)
}
