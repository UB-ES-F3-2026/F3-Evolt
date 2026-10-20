/** GET /api/home — home summary (US-07). One function per endpoint. */

import { apiGet } from './apiClient'
import { mockHome, useMocks } from '@/mocks'
import { fromApiMovements } from '@/models/movement'
import type { Home, HomeJson } from '@/models/home'

export async function getHome(): Promise<Home> {
  const json = useMocks() ? mockHome() : await apiGet<HomeJson>('/api/home')
  return {
    balance: json.balance,
    totalSaved: json.totalSaved,
    lastMovements: fromApiMovements(json.lastMovements),
  }
}
