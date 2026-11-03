/** /api/pots — the user's pots (US-17). One function per endpoint. */

import { apiGet, apiPost } from './apiClient'
import { useMocks } from '@/mocks'
import { mockCreatePot, mockPots } from '@/mocks/pots'
import { fromApiPot, fromApiPots, type CreatePotRequest, type Pot, type PotJson, type PotsJson } from '@/models/pot'

export async function getPots(): Promise<Pot[]> {
  const json = useMocks() ? mockPots() : await apiGet<PotsJson>('/api/pots')
  return fromApiPots(json.items)
}

export async function createPot(request: CreatePotRequest): Promise<Pot> {
  const json = useMocks() ? mockCreatePot(request) : await apiPost<PotJson>('/api/pots', request)
  return fromApiPot(json)
}
