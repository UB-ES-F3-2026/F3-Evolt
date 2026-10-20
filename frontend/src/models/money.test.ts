import { describe, expect, it } from 'vitest'
import { eurosToCents, formatCents } from './money'

describe('eurosToCents', () => {
  it.each([
    ['12', 1200],
    ['12,5', 1250],
    ['12.50', 1250],
    [' 7 ', 700],
    ['0', 0],
    ['0,01', 1],
    ['500', 50000],
    ['500,01', 50001],
  ])('reads %j as %i cents', (text, cents) => {
    expect(eurosToCents(text)).toBe(cents)
  })

  it.each(['', 'abc', '12,345', '-5', '12,', ',5', '1.000,00', '1e3', '99999999999999999'])(
    'rejects %j',
    (text) => {
      expect(eurosToCents(text)).toBeNull()
    },
  )
})

describe('formatCents', () => {
  it('shows cents as euros in Catalan format', () => {
    expect(formatCents(125050)).toMatch(/^1\.250,50\s€$/)
  })
})
