/**
 * In-memory currency sub-accounts, shaped like what GET /api/currencies will
 * answer (US-27, issue #166). Only the balances that are NOT the main account
 * live here: the EUR account IS the main account of ./index.ts and is always
 * read live with `mockBalance()`, so the money a person owns has one source of
 * truth. The demo user starts with 317,55 $ and any other account with only its
 * EUR account, as with the backend.
 */

import { messageForCode } from '@/models/errorMessages'
import {
  CURRENCIES,
  exchangePreview,
  isCurrencyCode,
  type CurrencyCode,
  type ExchangePreview,
  type ExchangeRequestJson,
  type ExchangeResultJson,
  type SubaccountJson,
} from '@/models/exchange'
import { mockBalance, mockError, recordAccountMovement } from './index'
import { mockCurrentUser, onMockUserChange } from './mockUser'
import { hasDemoData } from './seed'

/** Minor units of every sub-account that is not EUR; a missing code has no sub-account. */
let balances: Partial<Record<CurrencyCode, number>> = {}
startExchange()
onMockUserChange(startExchange)

/** The sub-accounts of whoever is logged in: EUR + 317,55 $ for the demo user, only EUR for anyone else. */
function startExchange(): void {
  balances = hasDemoData(mockCurrentUser()) ? { USD: 31755 } : {}
}

/** GET /api/currencies (issue #166) — the owned sub-accounts, the main one first. */
export function mockGetSubaccounts(): SubaccountJson[] {
  return [
    { code: 'EUR', balanceMinor: mockBalance(), isMain: true },
    ...subaccountCodes().map((code) => ({ code, balanceMinor: balances[code] ?? 0, isMain: false })),
  ]
}

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
  const preview = exchangePreview(amountMinor, srcCurrency, tgtCurrency, subaccountBalance(srcCurrency))
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
      `Canvi a ${CURRENCIES[tgt].name}`,
      'expense',
      'transfer',
      preview.totalChargeMinor,
    )
    const tgtBalance = subaccountBalance(tgt) + preview.exactReceivedMinor
    balances[tgt] = tgtBalance
    return { srcBalanceMinor: balance, tgtBalanceMinor: tgtBalance }
  }

  const srcBalance = subaccountBalance(src) - preview.totalChargeMinor
  balances[src] = srcBalance
  if (tgt === 'EUR') {
    const { balance } = recordAccountMovement(
      `Canvi de ${CURRENCIES[src].name}`,
      'income',
      'transfer',
      preview.exactReceivedMinor,
    )
    return { srcBalanceMinor: srcBalance, tgtBalanceMinor: balance }
  }

  const tgtBalance = subaccountBalance(tgt) + preview.exactReceivedMinor
  balances[tgt] = tgtBalance
  return { srcBalanceMinor: srcBalance, tgtBalanceMinor: tgtBalance }
}

/** Live balance of a sub-account: the main account for EUR, the stored one for the rest. */
function subaccountBalance(code: CurrencyCode): number {
  return code === 'EUR' ? mockBalance() : (balances[code] ?? 0)
}

function subaccountCodes(): CurrencyCode[] {
  return Object.keys(balances) as CurrencyCode[]
}
