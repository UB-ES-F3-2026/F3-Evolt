/**
 * Contract error → user-safe message.
 * The decision always comes from `code` (and `details`), never from `message`
 * (docs/api.md §5).
 */

import { formatCents } from './money'

const MESSAGES = {
  INVALID_AMOUNT: "L'import ha de ser més gran que 0.",
  AMOUNT_OVER_LIMIT: "L'import màxim per recàrrega és de 500,00 €.",
  VALIDATION_ERROR: 'Les dades de la petició no són vàlides.',
  INTERNAL_ERROR: "S'ha produït un error inesperat. Torna-ho a provar més tard.",
  NETWORK_ERROR: 'No hi ha connexió amb el servidor. Torna-ho a provar més tard.',
}

export function toUserMessage(failure) {
  if (failure?.code === 'DAILY_LIMIT_EXCEEDED') {
    const remaining = failure.details?.remainingToday ?? 0
    return `Has superat el límit diari de recàrrega. Avui encara pots recarregar ${formatCents(remaining)}.`
  }
  return MESSAGES[failure?.code] ?? MESSAGES.INTERNAL_ERROR
}
