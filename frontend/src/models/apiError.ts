/**
 * Contract error type (docs/api.md §5). Services reject with this shape.
 * The frontend decides from `code` (and `details`), never from `message`.
 */

/** Contract codes (docs/api.md §5) plus the frontend-only `NETWORK_ERROR`. */
const API_ERROR_CODES = [
  'INVALID_AMOUNT',
  'AMOUNT_OVER_LIMIT',
  'DAILY_LIMIT_EXCEEDED',
  'VALIDATION_ERROR',
  'INTERNAL_ERROR',
  'NETWORK_ERROR',
  'WEAK_PASSWORD',
  'ALREADY_REGISTERED',
  'INVALID_CODE',
  'CODE_EXPIRED',
  'TOO_MANY_ATTEMPTS',
  'INVALID_CREDENTIALS',
  'ACCOUNT_LOCKED',
  'ACCOUNT_NOT_VERIFIED',
  'UNAUTHENTICATED',
  'SESSION_EXPIRED',
] as const

export type ApiErrorCode = (typeof API_ERROR_CODES)[number]

export interface ApiError {
  code: ApiErrorCode
  message: string
  details?: { remainingToday?: number; lockedUntil?: string }
}

/** True when `value` already has the contract error shape with a known `code`. */
export function isApiError(value: unknown): value is ApiError {
  if (typeof value !== 'object' || value === null) return false
  const { code, message } = value as Record<string, unknown>
  return (
    typeof code === 'string' &&
    (API_ERROR_CODES as readonly string[]).includes(code) &&
    typeof message === 'string'
  )
}
