/**
 * Contract error type (docs/api.md §5). Services reject with this shape.
 * The frontend decides from `code` (and `details`), never from `message`.
 */

/** Contract codes (docs/api.md §5) plus the frontend-only `NETWORK_ERROR`. */
export type ApiErrorCode =
  | 'INVALID_AMOUNT'
  | 'AMOUNT_OVER_LIMIT'
  | 'DAILY_LIMIT_EXCEEDED'
  | 'VALIDATION_ERROR'
  | 'INTERNAL_ERROR'
  | 'NETWORK_ERROR'

export interface ApiError {
  code: ApiErrorCode
  message: string
  details?: { remainingToday?: number }
}
