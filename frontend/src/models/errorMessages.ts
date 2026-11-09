/**
 * The Catalan text a person sees for each error code (docs/api.md §5).
 * Every ViewModel goes through this module, so a code always reads the same.
 * The backend's `message` is never shown: the text comes from `code` and `details`.
 */

import { isApiError, type ApiError, type ApiErrorCode } from './apiError'
import { formatCents } from './money'
import { MAX_REPORT_LENGTH } from './movementReport'
import { MAX_TOPUP_CENTS } from './topup'

const MESSAGES: Record<ApiErrorCode, string> = {
  INVALID_AMOUNT: "L'import ha de ser més gran que 0.",
  AMOUNT_OVER_LIMIT: `L'import màxim per recàrrega és de ${formatCents(MAX_TOPUP_CENTS)}.`,
  DAILY_LIMIT_EXCEEDED: 'Has superat el límit diari de recàrrega.',
  INVALID_POT_NAME: 'El nom de la guardiola no pot estar buit.',
  INVALID_TARGET: "L'objectiu ha de ser més gran que 0.",
  INSUFFICIENT_BALANCE: 'No tens prou saldo per fer aquesta aportació.',
  POT_NOT_FOUND: "No s'ha trobat la guardiola.",
  MOVEMENT_NOT_FOUND: "No s'ha trobat el moviment.",
  INVALID_DESCRIPTION: `Explica què passa amb el moviment (com a màxim ${MAX_REPORT_LENGTH} caràcters).`,
  VALIDATION_ERROR: 'Les dades no són vàlides. Revisa-les i torna-ho a provar.',
  INTERNAL_ERROR: "S'ha produït un error inesperat. Torna-ho a provar més tard.",
  NETWORK_ERROR: 'No hi ha connexió amb el servidor. Torna-ho a provar.',
  WEAK_PASSWORD: 'La contrasenya ha de tenir 8 caràcters, una majúscula i un número.',
  ALREADY_REGISTERED: 'Aquest email o telèfon ja té un compte.',
  INVALID_CODE: 'El codi no és correcte o ha caducat.',
  CODE_EXPIRED: 'El codi no és correcte o ha caducat.',
  TOO_MANY_ATTEMPTS: 'Has fet massa intents. Demana un codi nou.',
  // Generic on purpose (US-03): it must not say whether the account exists.
  INVALID_CREDENTIALS: "L'email, el telèfon o la contrasenya no són correctes.",
  ACCOUNT_LOCKED: 'Compte bloquejat durant 15 minuts.',
  ACCOUNT_NOT_VERIFIED: "Has de verificar el compte abans d'iniciar sessió.",
  UNAUTHENTICATED: 'Cal iniciar sessió.',
  SESSION_EXPIRED: "La sessió s'ha tancat per inactivitat.",
  RESET_LINK_EXPIRED: 'Aquest enllaç ha caducat.',
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

/** An amount typed in euros that is not a number with at most 2 decimals (top-up, pot target). */
export const AMOUNT_FORMAT_MESSAGE = 'Escriu un import en euros, amb 2 decimals com a màxim.'
