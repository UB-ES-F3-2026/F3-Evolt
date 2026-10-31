/** /api/auth/* — access routes (docs/api.md §8). One function per endpoint. */

import { apiPost } from './apiClient'
import { useMocks } from '@/mocks'
import { mockRegister } from '@/mocks/auth'
import type { RegisterJson, RegisterRequest } from '@/models/auth'

export async function register(request: RegisterRequest): Promise<RegisterJson> {
  return useMocks() ? mockRegister(request) : apiPost<RegisterJson>('/api/auth/register', request)
}
