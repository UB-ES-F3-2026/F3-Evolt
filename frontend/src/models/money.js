/**
 * Money helpers. Amounts are integer cents everywhere (docs/api.md §1);
 * only the View shows euros, using `formatCents`.
 */

/** "12,50" / "12.50" / "12" → 1250. Returns null when the text is not a valid amount. */
export function eurosToCents(text) {
  if (typeof text !== 'string') return null
  const normalized = text.trim().replace(/\./g, '').replace(',', '.')
  if (!/^\d+(\.\d{1,2})?$/.test(normalized)) return null
  const [units, decimals = ''] = normalized.split('.')
  return Number(units) * 100 + Number((decimals + '00').slice(0, 2))
}

/** 1250 → "12,50 €" (ca-ES formatting). */
export function formatCents(cents) {
  return new Intl.NumberFormat('ca-ES', {
    style: 'currency',
    currency: 'EUR',
  }).format(cents / 100)
}
