/** /api/pots — the user's pots (US-17). One function per endpoint. */

import { apiGet } from './apiClient'
import { useMocks } from '@/mocks'
import { mockPots } from '@/mocks/pots'
import { fromApiPots, type Pot, type PotsJson } from '@/models/pot'

export async function getPots(): Promise<Pot[]> {
  const json = useMocks() ? mockPots() : await apiGet<PotsJson>('/api/pots')
  return fromApiPots(json.items)
}
