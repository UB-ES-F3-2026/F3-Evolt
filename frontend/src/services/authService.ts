/** /api/auth/* — access routes (docs/api.md §8). One function per endpoint. */

import { apiPost } from './apiClient'
import { useMocks } from '@/mocks'
import { mockRegister, mockResendCode, mockVerify } from '@/mocks/auth'
import type {
  RegisterJson,
  RegisterRequest,
  SessionJson,
  StatusJson,
  VerifyRequest,
} from '@/models/auth'

export async function register(request: RegisterRequest): Promise<RegisterJson> {
  return useMocks() ? mockRegister(request) : apiPost<RegisterJson>('/api/auth/register', request)
}

export async function verify(request: VerifyRequest): Promise<SessionJson> {
  return useMocks() ? mockVerify(request) : apiPost<SessionJson>('/api/auth/verify', request)
}

export async function resendCode(identifier: string): Promise<StatusJson> {
  return useMocks()
    ? mockResendCode(identifier)
    : apiPost<StatusJson>('/api/auth/resend-code', { identifier })
}
