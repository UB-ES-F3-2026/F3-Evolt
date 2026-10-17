/**
 * Dates for display. The API sends ISO 8601 with the Madrid offset
 * (docs/api.md §1), and "today" is the Madrid calendar day, so dates are
 * shown in Madrid time whatever the browser's time zone.
 */

const TIME_ZONE = 'Europe/Madrid'

const DAY = new Intl.DateTimeFormat('ca-ES', { timeZone: TIME_ZONE, day: 'numeric', month: 'short' })
const TIME = new Intl.DateTimeFormat('ca-ES', {
  timeZone: TIME_ZONE,
  hour: '2-digit',
  minute: '2-digit',
  hourCycle: 'h23',
})

/** `"2026-10-11T21:15:00+02:00"` → `"11 d’oct. · 21:15"` */
export function formatDateTime(isoDate: string): string {
  const instant = new Date(isoDate)
  // Intl throws on an invalid date; one bad value must not break a whole list.
  if (Number.isNaN(instant.getTime())) return isoDate
  return `${DAY.format(instant)} · ${TIME.format(instant)}`
}
