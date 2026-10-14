/** GET /api/home — home summary (US-07). One function per endpoint. */

import { apiGet } from './apiClient'
import { mockHome, useMocks } from '@/mocks'
import { fromApiMovements } from '@/models/movement'

export async function getHome() {
  const json = useMocks() ? mockHome() : await apiGet('/api/home')
  return {
    balance: json.balance,
    totalSaved: json.totalSaved,
    lastMovements: fromApiMovements(json.lastMovements),
  }
}
