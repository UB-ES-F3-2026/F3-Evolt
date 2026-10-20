/**
 * Money for display. Amounts travel as integer cents (docs/api.md §1) and
 * become euros only at the presentation edge, through this module.
 * Turning a typed euro amount into cents (T09.4) belongs here too, so every
 * euro ↔ cent conversion lives in one file.
 */

const EUROS = new Intl.NumberFormat('ca-ES', { style: 'currency', currency: 'EUR' })

/** `125050` → `"1.250,50 €"` */
export function formatCents(cents: number): string {
  return EUROS.format(cents / 100)
}

// What a person types: digits, then optionally a comma or a dot and 1 or 2 decimals.
const TYPED_EUROS = /^(\d+)(?:[.,](\d{1,2}))?$/

/** `"12,5"` → `1250`. `null` when the text is not an amount with at most 2 decimals. */
export function eurosToCents(text: string): number | null {
  const match = TYPED_EUROS.exec(text.trim())
  if (match === null) return null
  const [, euros, decimals = ''] = match
  const cents = Number(euros) * 100 + Number(decimals.padEnd(2, '0'))
  return Number.isSafeInteger(cents) ? cents : null
}
