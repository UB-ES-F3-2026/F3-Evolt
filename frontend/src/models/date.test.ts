import { describe, expect, it } from 'vitest'
import { formatFullDateTime } from './date'

describe('formatFullDateTime', () => {
  it('shows the day with the year and the time', () => {
    expect(formatFullDateTime('2026-11-01T18:42:00+01:00')).toBe('1/11/2026, 18:42')
  })

  it('uses Madrid time whatever the offset of the date', () => {
    expect(formatFullDateTime('2026-11-01T23:30:00Z')).toBe('2/11/2026, 00:30')
  })

  it('leaves an invalid date as it comes', () => {
    expect(formatFullDateTime('not-a-date')).toBe('not-a-date')
  })
})
