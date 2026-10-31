/** /api/auth/* — access routes (docs/api.md §8). One function per endpoint. */

import { apiPost } from './apiClient'
import { useMocks } from '@/mocks'
import { mockLogin, mockLogout, mockRegister, mockResendCode, mockVerify } from '@/mocks/auth'
import type {
  LoginRequest,
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

export async function login(request: LoginRequest): Promise<SessionJson> {
  return useMocks() ? mockLogin(request) : apiPost<SessionJson>('/api/auth/login', request)
}

export async function logout(): Promise<StatusJson> {
  return useMocks() ? mockLogout() : apiPost<StatusJson>('/api/auth/logout', undefined)
}
