/**
 * The only place that talks HTTP. Services import `apiGet` / `apiPost`
 * and never call `fetch` themselves.
 *
 * Failures always reject with the contract's error shape `{ code, message, details? }`
 * (docs/api.md §5) plus a frontend-only `NETWORK_ERROR` when fetch itself fails.
 * A body that is not a contract error (e.g. FastAPI's default `{ detail }`, HTML,
 * empty) becomes `VALIDATION_ERROR` on 422 and `INTERNAL_ERROR` otherwise.
 */

import { isApiError, type ApiError } from '@/models/apiError'

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
    if (isApiError(payload)) throw payload
    throw response.status === 422 ? validationError() : internalError()
  }

  // Every endpoint answers with a JSON body; anything else is a server fault.
  if (payload === null) throw internalError()

  return payload as T
}

// Default texts from docs/api.md §5. The screen text is chosen from `code`.
function validationError(): ApiError {
  return { code: 'VALIDATION_ERROR', message: 'Les dades de la petició no són vàlides.' }
}

function internalError(): ApiError {
  return { code: 'INTERNAL_ERROR', message: "S'ha produït un error inesperat. Torna-ho a provar més tard." }
}

export function apiGet<T>(path: string): Promise<T> {
  return request<T>(path)
}

export function apiPost<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, { method: 'POST', body })
}
