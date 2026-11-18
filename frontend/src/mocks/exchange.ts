/**
 * In-memory currency exchange, shaped like what POST /api/exchanges will answer
 * (US-27, issues #166 and #173). The sub-account state lives in ./currencies.ts,
 * the catalogue owner: this file keeps only the exchange — validations in the
 * order of the «Canviar» screen and one all-or-nothing write, so no check can
 * leave half an exchange behind.
 */

import { messageForCode } from '@/models/errorMessages'
import {
  exchangePreview,
  type CurrencyCode,
  type ExchangePreview,
  type ExchangeRequestJson,
  type ExchangeResultJson,
} from '@/models/exchange'
import { currencyByCode, isCurrencyCode } from '@/models/currency'
import { mockError, recordAccountMovement } from './index'
import { mockGetSubaccounts, mockSubaccountBalance, mockSetSubaccountBalance } from './currencies'

/**
 * POST /api/exchanges (US-27, issues #166 and #173) — validations in the order of
 * the «Canviar» screen: body format → SAME_CURRENCY → both currencies are owned
 * sub-accounts (VALIDATION_ERROR) → AMOUNT_TOO_SMALL → INSUFFICIENT_BALANCE.
 * All or nothing: the four writes (both balances and the main account movement)
 * only happen once everything is valid, in one synchronous block, so no check can
 * leave half an exchange behind.
 */
export function mockPostExchange(request: ExchangeRequestJson): ExchangeResultJson {
  const { srcCurrency, tgtCurrency, amountMinor } = request

  if (
    !Number.isInteger(amountMinor) ||
    amountMinor <= 0 ||
    !isCurrencyCode(srcCurrency) ||
    !isCurrencyCode(tgtCurrency)
  ) {
    throw mockError('VALIDATION_ERROR', messageForCode('VALIDATION_ERROR'))
  }
  if (srcCurrency === tgtCurrency) {
    throw mockError('SAME_CURRENCY', messageForCode('SAME_CURRENCY'))
  }
  // A hand-crafted request can name a currency the person has no sub-account for:
  // reject it, or `applyExchange` would open that balance out of nowhere.
  const owned = new Set(mockGetSubaccounts().map((account) => account.code))
  if (!owned.has(srcCurrency) || !owned.has(tgtCurrency)) {
    throw mockError('VALIDATION_ERROR', messageForCode('VALIDATION_ERROR'))
  }

  // Both checks use the balances before the exchange, like the summary screen does.
  const preview = exchangePreview(amountMinor, srcCurrency, tgtCurrency, mockSubaccountBalance(srcCurrency))
  if (preview.tooSmall) {
    throw mockError('AMOUNT_TOO_SMALL', messageForCode('AMOUNT_TOO_SMALL'))
  }
  if (preview.insufficient) {
    throw mockError('INSUFFICIENT_BALANCE', messageForCode('INSUFFICIENT_BALANCE'))
  }

  return applyExchange(srcCurrency, tgtCurrency, preview)
}

/**
 * The writes of an exchange, once every check passed. The source pays the amount
 * plus the commission and the target receives the exact converted amount, so the
 * main account side never moves the raw amount.
 */
function applyExchange(src: CurrencyCode, tgt: CurrencyCode, preview: ExchangePreview): ExchangeResultJson {
  if (src === 'EUR') {
    const { balance } = recordAccountMovement(
      `Canvi a ${currencyByCode(tgt).name}`,
      'expense',
      'transfer',
      preview.totalChargeMinor,
    )
    const tgtBalance = mockSubaccountBalance(tgt) + preview.exactReceivedMinor
    mockSetSubaccountBalance(tgt, tgtBalance)
    return { srcBalanceMinor: balance, tgtBalanceMinor: tgtBalance }
  }

  const srcBalance = mockSubaccountBalance(src) - preview.totalChargeMinor
  mockSetSubaccountBalance(src, srcBalance)
  if (tgt === 'EUR') {
    const { balance } = recordAccountMovement(
      `Canvi de ${currencyByCode(src).name}`,
      'income',
      'transfer',
      preview.exactReceivedMinor,
    )
    return { srcBalanceMinor: srcBalance, tgtBalanceMinor: balance }
  }

  const tgtBalance = mockSubaccountBalance(tgt) + preview.exactReceivedMinor
  mockSetSubaccountBalance(tgt, tgtBalance)
  return { srcBalanceMinor: srcBalance, tgtBalanceMinor: tgtBalance }
}
