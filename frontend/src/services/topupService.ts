/** POST /api/topups — test top-up (US-09). One function per endpoint. */

import { apiPost } from './apiClient'
import { mockTopup, useMocks } from '@/mocks'
import { fromApiMovement } from '@/models/movement'
import type { TopupJson, TopupResult } from '@/models/topup'

export async function createTopup(amountCents: number): Promise<TopupResult> {
  const json = useMocks()
    ? mockTopup(amountCents)
    : await apiPost<TopupJson>('/api/topups', { amount: amountCents })
  return {
    balance: json.balance,
    movement: fromApiMovement(json.movement),
  }
}
