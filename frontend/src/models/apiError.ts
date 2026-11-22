/**
 * Contract error type (docs/api.md §5). Services reject with this shape.
 * The frontend decides from `code` (and `details`), never from `message`.
 */

/** Contract codes (docs/api.md §5) plus the frontend-only `NETWORK_ERROR`. */
const API_ERROR_CODES = [
  'INVALID_AMOUNT',
  'AMOUNT_OVER_LIMIT',
  'DAILY_LIMIT_EXCEEDED',
  'INVALID_POT_NAME',
  'INVALID_TARGET',
  'INSUFFICIENT_BALANCE',
  'INSUFFICIENT_POT_BALANCE',
  'POT_NOT_FOUND',
  'MOVEMENT_NOT_FOUND',
  'RECIPIENT_NOT_FOUND',
  'INVALID_DESCRIPTION',
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
  'RESET_LINK_EXPIRED',
  // Multi-currency (US-25 and US-26, docs/api.md §12.10).
  'CURRENCY_EXISTS',
  'CURRENCY_NOT_SUPPORTED',
  'SUBACCOUNT_NOT_FOUND',
  'MAIN_ACCOUNT_NOT_DELETABLE',
  'SUBACCOUNT_NOT_EMPTY',
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
