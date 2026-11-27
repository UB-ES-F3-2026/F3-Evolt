import { describe, expect, it } from 'vitest'
import { mockAccountDetails, mockIbanFor } from './account'

/** The table of docs/api.md §16.2, without spaces. */
const SEED_IBANS = [
  'ES9121000418450200051332',
  'ES2121000418410200051333',
  'ES0221000418440200051334',
  'ES5321000418490200051335',
  'ES1021000418430200051336',
  'ES6121000418480200051337',
  'ES1821000418420200051338',
  'ES6921000418470200051339',
]

/** ISO 13616: the first four characters at the end, letters as numbers, remainder 1 by 97. */
function passesIbanCheck(iban: string): boolean {
  const moved = `${iban.slice(4)}1428${iban.slice(2, 4)}`
  return BigInt(moved) % 97n === 1n
}

describe('mockIbanFor (docs/api.md §16.2)', () => {
  it('gives each seed user the IBAN of the table', () => {
    expect([1, 2, 3, 4, 5, 6, 7, 8].map(mockIbanFor)).toEqual(SEED_IBANS)
  })

  it('IB-03: every IBAN is different and passes the check digits', () => {
    const ibans = Array.from({ length: 200 }, (_, index) => mockIbanFor(index + 1))
    expect(new Set(ibans).size).toBe(200)
    expect(ibans.every(passesIbanCheck)).toBe(true)
  })
})

describe('mockAccountDetails (docs/api.md §16.1)', () => {
  it('IBP-02: the demo user', () => {
    expect(mockAccountDetails('demo@evolt.test')).toEqual({
      iban: 'ES9121000418450200051332',
      bic: 'EVOLESB1XXX',
      holder: 'Usuari demo',
    })
  })

  it('IBP-06: the user 2 has its own IBAN and name', () => {
    expect(mockAccountDetails('buit@evolt.test')).toMatchObject({ iban: 'ES2121000418410200051333', holder: 'Usuari nou' })
  })
})
