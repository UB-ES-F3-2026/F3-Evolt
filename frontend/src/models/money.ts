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
