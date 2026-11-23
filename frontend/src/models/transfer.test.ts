import { describe, expect, it } from 'vitest'
import { cleanConcept, pressAmountKey, transferAmountError, transferLimitMessage } from './transfer'

const limit = { dailyLimit: 100000, remainingToday: 98000 }

describe('transferAmountError (US-14)', () => {
  it.each([
    [null, null],
    [0, null],
    [2000, null],
    [98000, null],
    [98001, 'limit'],
    [379522, 'No tens prou saldo.'],
  ])('reads %j cents with 3.795,21 € and 980,00 € left as %j', (cents, expected) => {
    const message = transferAmountError(cents, 379521, limit)
    expect(message).toBe(expected === 'limit' ? transferLimitMessage(100000) : expected)
  })

  it('says the limit read from the API, exactly as US-14 writes it', () => {
    expect(transferLimitMessage(100000)).toMatch(/^Has superat el límit diari de 1\.000,00\s€\.$/)
  })
})

describe('pressAmountKey (keypad of US-14-import-teclat)', () => {
  it.each([
    ['', '2', '2'],
    ['2', '0', '20'],
    ['20', ',', '20,'],
    ['20,', '5', '20,5'],
    ['20,5', '0', '20,50'],
    ['20,50', '1', '20,50'],
    ['20,5', ',', '20,5'],
    ['', ',', '0,'],
    ['0', '5', '5'],
    ['20', '⌫', '2'],
    ['', '⌫', ''],
    ['1234567', '8', '1234567'],
  ])('%j + %j → %j', (amount, key, expected) => {
    expect(pressAmountKey(amount, key)).toBe(expected)
  })
})

describe('cleanConcept', () => {
  it('keeps a concept without the spaces at the ends, and makes a blank one null (EN-04)', () => {
    expect(cleanConcept('  El sopar  ')).toBe('El sopar')
    expect(cleanConcept('   ')).toBeNull()
  })
})
