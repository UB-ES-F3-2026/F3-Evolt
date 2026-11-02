/**
 * The Catalan text a person sees for each error code (docs/api.md §5).
 * Every ViewModel goes through this module, so a code always reads the same.
 * The backend's `message` is never shown: the text comes from `code` and `details`.
 */

import { isApiError, type ApiError, type ApiErrorCode } from './apiError'
import { formatCents } from './money'
import { MAX_TOPUP_CENTS } from './topup'

const MESSAGES: Record<ApiErrorCode, string> = {
  INVALID_AMOUNT: "L'import ha de ser més gran que 0.",
  AMOUNT_OVER_LIMIT: `L'import màxim per recàrrega és de ${formatCents(MAX_TOPUP_CENTS)}.`,
  DAILY_LIMIT_EXCEEDED: 'Has superat el límit diari de recàrrega.',
  VALIDATION_ERROR: 'Les dades no són vàlides. Revisa-les i torna-ho a provar.',
  INTERNAL_ERROR: "S'ha produït un error inesperat. Torna-ho a provar més tard.",
  NETWORK_ERROR: 'No hi ha connexió amb el servidor. Torna-ho a provar.',
  WEAK_PASSWORD: 'La contrasenya ha de tenir 8 caràcters, una majúscula i un número.',
  ALREADY_REGISTERED: 'Aquest email o telèfon ja té un compte.',
}

export function messageForCode(code: ApiErrorCode, details?: ApiError['details']): string {
  const remainingToday = details?.remainingToday
  if (code === 'DAILY_LIMIT_EXCEEDED' && remainingToday !== undefined) {
    return `${MESSAGES.DAILY_LIMIT_EXCEEDED} Avui encara pots recarregar ${formatCents(remainingToday)}.`
  }
  return MESSAGES[code]
}

/** For anything a service rejected with; unknown failures read as an unexpected error. */
export function toUserMessage(failure: unknown): string {
  return isApiError(failure) ? messageForCode(failure.code, failure.details) : MESSAGES.INTERNAL_ERROR
}
