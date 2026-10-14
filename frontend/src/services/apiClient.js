/**
 * The only place that talks HTTP. Services import `apiGet` / `apiPost`
 * and never call `fetch` themselves.
 *
 * Failures reject with the contract's error shape `{ code, message, details? }`
 * (docs/api.md §5) plus a frontend-only `NETWORK_ERROR` when fetch itself fails.
 */

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const USER_ID = import.meta.env.VITE_DEMO_USER ?? '1'

async function request(path, { method = 'GET', body } = {}) {
  let response
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
    throw { code: 'NETWORK_ERROR', message: 'No hi ha connexió amb el servidor.' }
  }

  const payload = await response.json().catch(() => null)

  if (!response.ok) {
    throw payload ?? { code: 'INTERNAL_ERROR', message: 'Resposta del servidor sense cos.' }
  }

  return payload
}

export function apiGet(path) {
  return request(path)
}

export function apiPost(path, body) {
  return request(path, { method: 'POST', body })
}
