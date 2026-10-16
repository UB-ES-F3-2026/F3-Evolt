/**
 * Dates as the contract wants them (docs/api.md §1): ISO 8601 with the
 * Europe/Madrid offset (+02:00 summer, +01:00 winter), seconds precision.
 * "Today" is the calendar day in Madrid, whatever the browser's time zone.
 * Only the mocks need this; the real dates come from the backend.
 */

const MADRID_PARTS = new Intl.DateTimeFormat('en-GB', {
  timeZone: 'Europe/Madrid',
  hourCycle: 'h23',
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
})

interface WallClock {
  year: number
  month: number
  day: number
  hour: number
  minute: number
  second: number
}

function madridWallClock(instant: Date): WallClock {
  const parts: Record<string, number> = {}
  for (const { type, value } of MADRID_PARTS.formatToParts(instant)) {
    if (type !== 'literal') parts[type] = Number(value)
  }
  return {
    year: parts.year,
    month: parts.month,
    day: parts.day,
    hour: parts.hour,
    minute: parts.minute,
    second: parts.second,
  }
}

/** Madrid offset at `instant`, in minutes east of UTC (+120 or +60). */
function madridOffsetMinutes(instant: Date): number {
  const c = madridWallClock(instant)
  const wallAsUtc = Date.UTC(c.year, c.month - 1, c.day, c.hour, c.minute, c.second)
  const wholeSeconds = Math.floor(instant.getTime() / 1000) * 1000
  return Math.round((wallAsUtc - wholeSeconds) / 60000)
}

const pad = (value: number): string => String(value).padStart(2, '0')

/** `2026-10-15T21:15:00+02:00` */
export function toContractDate(instant: Date): string {
  const c = madridWallClock(instant)
  const offset = madridOffsetMinutes(instant)
  const sign = offset >= 0 ? '+' : '-'
  const abs = Math.abs(offset)
  return (
    `${c.year}-${pad(c.month)}-${pad(c.day)}T${pad(c.hour)}:${pad(c.minute)}:${pad(c.second)}` +
    `${sign}${pad(Math.floor(abs / 60))}:${pad(abs % 60)}`
  )
}

/** Madrid calendar day of `instant`, as `YYYY-MM-DD`. Equal keys = same "today". */
export function madridDayKey(instant: Date): string {
  const c = madridWallClock(instant)
  return `${c.year}-${pad(c.month)}-${pad(c.day)}`
}

/**
 * The instant of (Madrid today − `daysAgo`) at `hhmm` Madrid time, like
 * `_days_ago_at` in seed.py. The offset is the one of that day, so it stays
 * right across a clock change.
 */
export function madridDaysAgoAt(now: Date, daysAgo: number, hhmm: string): Date {
  const today = madridWallClock(now)
  const [hour, minute] = hhmm.split(':').map(Number)
  // Calendar arithmetic on the Madrid date; Date.UTC handles month/year rollover.
  const wallAsUtc = Date.UTC(today.year, today.month - 1, today.day - daysAgo, hour, minute)
  // Guess with the offset at that moment, then correct once if the guess crossed a change.
  const firstGuess = wallAsUtc - madridOffsetMinutes(new Date(wallAsUtc)) * 60000
  return new Date(wallAsUtc - madridOffsetMinutes(new Date(firstGuess)) * 60000)
}
