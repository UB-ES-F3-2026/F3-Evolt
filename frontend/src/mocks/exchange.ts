/**
 * In-memory currency exchange, shaped like what POST /api/exchanges answers
 * (§12.7, US-27). The sub-account state lives in ./currencies.ts, the catalogue
 * owner: this file keeps only the exchange — the §12.7 validations, in the
 * contract's order and stopped at the first error, and one all-or-nothing write,
 * so no check can leave half an exchange behind.
 */

import { messageForCode } from '@/models/errorMessages'
import { exchangePreview, type ExchangePreview, type ExchangeResult } from '@/models/exchange'
import { currencyByCode, type Subaccount } from '@/models/currency'
import { mockError, recordAccountMovement } from './index'
import { mockSetSubaccountBalance, mockSubaccounts } from './currencies'

/**
 * POST /api/exchanges (§12.7, US-27). The body arrives untrusted, like a real
 * request, so it is narrowed here instead of being trusted as a typed object.
 *
 * Validations in the contract's order, stopped at the first error:
 *
 * 1. Body format → `VALIDATION_ERROR`: a missing field, a currency that is not a
 *    string, or an `amount` that is not a strict JSON integer. `"1000"` and `10.5`
 *    are refused, never coerced (CV-17).
 * 2. Same currency → `SAME_CURRENCY`. It goes before the amount because CV-18 sends
 *    «EUR → EUR, 0» and the screen must say the pair is wrong, not the amount.
 * 3. Either currency without a sub-account of this user → `SUBACCOUNT_NOT_FOUND`.
 *    Reading the rows covers both cases in one check: a currency the person has not
 *    opened (CV-08) and a code outside the catalogue like `"BTC"`, which is in no
 *    row. It goes before the amount, so an unowned pair never reads
 *    `INVALID_AMOUNT` first.
 * 4. `amount ≤ 0` → `INVALID_AMOUNT`, on an owned pair (CV-09). Same code as the
 *    top-up and the pot contribution.
 * 5. The converted amount must reach one target minor unit → `AMOUNT_TOO_SMALL`.
 * 6. `amount + commission` must fit the source balance → `INSUFFICIENT_BALANCE`.
 *
 * Checks 5 and 6 use the balances before the exchange, like the summary screen does.
 */
export function mockPostExchange(body: {
  fromCurrency?: unknown
  toCurrency?: unknown
  amount?: unknown
}): ExchangeResult {
  const { fromCurrency, toCurrency, amount } = body

  // 1. Body format (§12.7-1, CV-17). `typeof` narrows the three fields; only then can
  //    `Number.isSafeInteger` say whether the amount is a strict JSON integer.
  if (
    typeof fromCurrency !== 'string' ||
    typeof toCurrency !== 'string' ||
    typeof amount !== 'number' ||
    !Number.isSafeInteger(amount)
  ) {
    throw mockError('VALIDATION_ERROR', messageForCode('VALIDATION_ERROR'))
  }
  // 2. Same currency before the amount (§12.7-2, CV-18).
  if (fromCurrency === toCurrency) {
    throw mockError('SAME_CURRENCY', messageForCode('SAME_CURRENCY'))
  }
  // 3. Both currencies are sub-accounts of this user (§12.7-3, CV-08). The state only
  //    ever holds validated codes, so a row is found only for an owned, real currency:
  //    `"BTC"` never reaches the rate table.
  const owned = mockSubaccounts().items
  const fromRow = owned.find((row) => row.code === fromCurrency)
  const toRow = owned.find((row) => row.code === toCurrency)
  if (fromRow === undefined || toRow === undefined) {
    throw mockError('SUBACCOUNT_NOT_FOUND', messageForCode('SUBACCOUNT_NOT_FOUND'))
  }
  // 4. Zero or negative only once the pair is known to be owned (§12.7-4, CV-09).
  if (amount <= 0) {
    throw mockError('INVALID_AMOUNT', messageForCode('INVALID_AMOUNT'))
  }

  // 5–6. The balance is the source row snapshotted above: for EUR it is the live main
  //      balance, exactly what the summary screen previews.
  const preview = exchangePreview(amount, fromRow.code, toRow.code, fromRow.balance)
  if (preview.tooSmall) {
    throw mockError('AMOUNT_TOO_SMALL', messageForCode('AMOUNT_TOO_SMALL'))
  }
  if (preview.insufficient) {
    throw mockError('INSUFFICIENT_BALANCE', messageForCode('INSUFFICIENT_BALANCE'))
  }

  return applyExchange(fromRow, toRow, amount, preview)
}

/**
 * The writes of an exchange, once every check passed (§12.7 response, §12.8
 * movements). Both rows are read before the first write and every write happens in
 * one synchronous block, all or nothing.
 *
 * The source pays the amount plus the commission and the target receives the exact
 * converted amount, so the main account side never moves the raw amount. Euros go
 * through the main account movement (their balance is the sum of the movements); a
 * foreign currency writes its own sub-account row.
 */
function applyExchange(
  fromRow: Subaccount,
  toRow: Subaccount,
  amount: number,
  preview: ExchangePreview,
): ExchangeResult {
  let newFrom: number
  if (fromRow.code === 'EUR') {
    newFrom = recordAccountMovement(
      `Canvi a ${currencyByCode(toRow.code).name}`,
      'expense',
      'transfer',
      preview.totalChargeMinor,
    ).balance
  } else {
    newFrom = fromRow.balance - preview.totalChargeMinor
    mockSetSubaccountBalance(fromRow.code, newFrom)
  }

  let newTo: number
  if (toRow.code === 'EUR') {
    newTo = recordAccountMovement(
      `Canvi de ${currencyByCode(fromRow.code).name}`,
      'income',
      'transfer',
      preview.exactReceivedMinor,
    ).balance
  } else {
    newTo = toRow.balance + preview.exactReceivedMinor
    mockSetSubaccountBalance(toRow.code, newTo)
  }

  // The §12.7 response echoes the figures already applied, so the screen never
  // recomputes what the server decided.
  return {
    from: { ...fromRow, balance: newFrom },
    to: { ...toRow, balance: newTo },
    amount,
    commission: preview.commissionSrcMinor,
    received: preview.exactReceivedMinor,
  }
}
