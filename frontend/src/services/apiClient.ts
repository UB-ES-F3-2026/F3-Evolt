/**
 * The only place that talks HTTP. Services import `apiGet` / `apiPost`
 * and never call `fetch` themselves.
 *
 * Failures reject with the contract's error shape `{ code, message, details? }`
 * (docs/api.md §5) plus a frontend-only `NETWORK_ERROR` when fetch itself fails.
 */

import type { ApiError } from '@/models/apiError'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const USER_ID = import.meta.env.VITE_DEMO_USER ?? '1'

interface RequestOptions {
  method?: 'GET' | 'POST'
  body?: unknown
}

async function request<T>(path: string, { method = 'GET', body }: RequestOptions = {}): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': USER_ID,
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    const networkError: ApiError = { code: 'NETWORK_ERROR', message: 'No hi ha connexió amb el servidor.' }
    throw networkError
  }

  const payload: unknown = await response.json().catch(() => null)

  if (!response.ok) {
    const emptyError: ApiError = { code: 'INTERNAL_ERROR', message: 'Resposta del servidor sense cos.' }
    throw payload ?? emptyError
  }

  return payload as T
}

export function apiGet<T>(path: string): Promise<T> {
  return request<T>(path)
}

export function apiPost<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, { method: 'POST', body })
}
