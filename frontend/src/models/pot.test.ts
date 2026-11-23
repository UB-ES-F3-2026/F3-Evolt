import { describe, expect, it } from 'vitest'
import { AMOUNT_FORMAT_MESSAGE, messageForCode } from './errorMessages'
import { DEFAULT_POT_COLOR, fromApiPot, fromApiPots, potAmountError } from './pot'

describe('fromApiPot', () => {
  it('keeps the fields of the contract', () => {
    const json = { id: 'pot-01', name: 'Vacances', balance: 15000, target: 100000, color: 'blue' }

    expect(fromApiPot(json)).toEqual(json)
  })

  it('keeps a pot without target as null', () => {
    expect(fromApiPot({ id: 'pot-02', name: 'Fons', balance: 0, target: null, color: 'teal' }).target).toBeNull()
  })

  it('falls back to the default colour when an unknown one arrives', () => {
    const pot = fromApiPot({ id: 'pot-03', name: 'Regal', balance: 5000, target: 8000, color: 'red' })

    expect(pot.color).toBe(DEFAULT_POT_COLOR)
  })
})

describe('fromApiPots', () => {
  it('turns a missing list into an empty one', () => {
    expect(fromApiPots(undefined)).toEqual([])
  })
})

describe('potAmountError', () => {
  it.each([
    ['', null],
    ['  ', null],
    ['30', null],
    ['150,00', null],
    ['0', messageForCode('INVALID_AMOUNT')],
    ['-5', messageForCode('INVALID_AMOUNT')],
    ['abc', AMOUNT_FORMAT_MESSAGE],
    ['150,01', messageForCode('INSUFFICIENT_POT_BALANCE')],
  ])('reads %j with a limit of 150,00 € as %j', (typed, expected) => {
    expect(potAmountError(typed, 15000, 'INSUFFICIENT_POT_BALANCE')).toBe(expected)
  })

  it('does not check the limit while it is unknown', () => {
    expect(potAmountError('999999', null, 'INSUFFICIENT_BALANCE')).toBeNull()
  })
})
