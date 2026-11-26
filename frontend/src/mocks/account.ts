/**
 * The account details, shaped exactly like docs/api.md §16.1. The IBAN follows the rule of §16.2,
 * so each seed user gets the IBAN of the table there (the demo user, `ES91 2100 0418 4502 0005 1332`).
 */

import type { AccountDetailsJson } from '@/models/account'
import { displayName } from '@/models/user'
import { mockCurrentUser } from './mockUser'
import { mockUser, mockUserIdByEmail } from './users'

const BANK_CODE = '2100'
const BRANCH_CODE = '0418'
const ACCOUNT_NUMBER_BASE = 200051331
const BIC = 'EVOLESB1XXX'
/** Weights of the national control digits (CCC), left to right (§16.2). */
const CCC_WEIGHTS = [1, 2, 4, 8, 5, 10, 9, 7, 3, 6]
/** «ES» as digits for the IBAN check: E = 14, S = 28. */
const SPAIN_DIGITS = '1428'
/** Accounts made in the mocks are not in the seed table; they get the next number. */
const FIRST_NEW_ACCOUNT = 9

/** One control digit of the CCC: 11 minus the remainder by 11, with 11 → 0 and 10 → 1. */
function cccDigit(digits: string): number {
  const sum = [...digits].reduce((total, digit, index) => total + Number(digit) * CCC_WEIGHTS[index], 0)
  const rest = 11 - (sum % 11)
  return rest === 11 ? 0 : rest === 10 ? 1 : rest
}

/** The IBAN of the user with internal number `n`, without spaces (§16.2). BigInt: the number has 26 digits. */
export function mockIbanFor(n: number): string {
  const accountNumber = String(ACCOUNT_NUMBER_BASE + n).padStart(10, '0')
  const control = `${cccDigit(`00${BANK_CODE}${BRANCH_CODE}`)}${cccDigit(accountNumber)}`
  const bban = `${BANK_CODE}${BRANCH_CODE}${control}${accountNumber}`
  const check = 98n - (BigInt(`${bban}${SPAIN_DIGITS}00`) % 97n)
  return `ES${String(check).padStart(2, '0')}${bban}`
}

/** GET /api/account for whoever is logged in to the mocks (§16.1). */
export function mockAccountDetails(currentEmail: string | null = mockCurrentUser()): AccountDetailsJson {
  // Nobody logged in (unit tests, first load) reads as the demo user, like the rest of the mocks.
  const userId = currentEmail === null ? 'usr-01' : mockUserIdByEmail(currentEmail)
  if (userId === null) {
    return { iban: mockIbanFor(FIRST_NEW_ACCOUNT), bic: BIC, holder: currentEmail ?? '' }
  }
  return { iban: mockIbanFor(Number(userId.slice(4))), bic: BIC, holder: displayName(mockUser(userId)) }
}
