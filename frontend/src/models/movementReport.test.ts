import { describe, expect, it } from 'vitest'
import { isValidReportDescription, MAX_REPORT_LENGTH } from './movementReport'

describe('isValidReportDescription', () => {
  it('asks for some text', () => {
    expect(isValidReportDescription('')).toBe(false)
    expect(isValidReportDescription('   ')).toBe(false)
    expect(isValidReportDescription('No reconec aquest pagament')).toBe(true)
  })

  it('allows 500 characters and not one more', () => {
    expect(isValidReportDescription('a'.repeat(MAX_REPORT_LENGTH))).toBe(true)
    expect(isValidReportDescription('a'.repeat(MAX_REPORT_LENGTH + 1))).toBe(false)
  })

  it('does not count the spaces at the ends', () => {
    expect(isValidReportDescription(`  ${'a'.repeat(MAX_REPORT_LENGTH)}  `)).toBe(true)
  })
})
