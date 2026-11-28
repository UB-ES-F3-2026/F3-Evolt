import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { isApiError } from '@/models/apiError'
import {
  currencyByCode,
  isCurrencyCode,
  isMainCurrency,
  type SubaccountList,
} from '@/models/currency'
import { EXCHANGE_INSUFFICIENT_BALANCE_MESSAGE, toUserMessage } from '@/models/errorMessages'
import {
  exchangePreview,
  formatCommissionLabel,
  rateLabelCount,
  rateRoundedMinor,
  type ExchangeDraft,
} from '@/models/exchange'
import { currencySymbol, formatMinor } from '@/models/money'
import { getSubaccounts } from '@/services/subaccountsService'
import {
  postExchange,
  type ExchangeRequestJson,
  type ExchangeResult,
} from '@/services/exchange/exchangeService'

// Long enough to read the confirmation before going back to Home.
export const CONFIRMATION_MS = 1500

export interface ExchangeSummaryDependencies {
  /** What «Canviar» left in `history.state`; null when someone opens the screen directly. */
  draft: ExchangeDraft | null
  getSubaccounts: () => Promise<SubaccountList>
  confirmExchange: (request: ExchangeRequestJson) => Promise<ExchangeResult>
  goHome: () => Promise<unknown>
  goToExchange: () => Promise<unknown>
  pause: (ms: number) => Promise<void>
}

/**
 * «Resum del canvi» screen (US-27): the rate, the commission, the exact amount
 * received, and the one POST that does the exchange.
 *
 * The form on «Canviar» only navigates; the exchange is sent from here, after
 * the person has seen every number (US-27, special cases).
 */
export function useExchangeSummaryViewModel(
  dependencies: ExchangeSummaryDependencies = defaultDependencies(),
) {
  // A draft whose origin and target are the same subaccount is not a draft (SAME_CURRENCY):
  // treat it like a missing one, or a crafted state would print the same row twice.
  const { draft: rawDraft } = dependencies
  const draft: ExchangeDraft | null =
    rawDraft !== null && rawDraft.srcCurrency !== rawDraft.tgtCurrency ? rawDraft : null

  // Starts true so the card never shows a rate computed against an unknown balance.
  const isLoading = ref(true)
  const loadError = ref<string | null>(null)
  /** Origin balance in source minor units: the most that can be charged (US-27). */
  const originBalance = ref<number | null>(null)

  const isConfirming = ref(false)
  const confirmed = ref(false)
  const submitError = ref<string | null>(null)
  const newBalances = ref<ExchangeResult | null>(null)

  const preview = computed(() => {
    if (draft === null) return null
    return exchangePreview(
      draft.amountMinor,
      draft.srcCurrency,
      draft.tgtCurrency,
      originBalance.value ?? 0,
    )
  })

  const originLine = computed(() => {
    if (draft === null) return ''
    return `${formatMinor(draft.amountMinor, draft.srcCurrency)} → ${draft.tgtCurrency}`
  })

  // Quoted per 100 yen when the origin is JPY: the 2-decimal rate is per 100 minor units.
  const rateLabel = computed(() => {
    if (draft === null) return ''
    return `${rateLabelCount(draft.srcCurrency)} ${currencySymbol(draft.srcCurrency)} =`
  })

  const rateValue = computed(() => {
    if (draft === null) return ''
    return formatMinor(rateRoundedMinor(draft.srcCurrency, draft.tgtCurrency), draft.tgtCurrency)
  })

  const commissionText = computed(() => {
    if (draft === null || preview.value === null) return ''
    return formatCommissionLabel(preview.value.commissionSrcMinor, draft.srcCurrency)
  })

  const chargeNote = computed(() => {
    if (draft === null || preview.value === null) return ''
    return `Se't descomptaran ${formatMinor(preview.value.totalChargeMinor, draft.srcCurrency)} del subcompte d'origen`
  })

  const exactLine = computed(() => {
    if (draft === null || preview.value === null) return ''
    return `Rebràs exactament ${formatMinor(preview.value.exactReceivedMinor, draft.tgtCurrency)}`
  })

  // No balance, no verdict: until it loads, the button stays disabled anyway.
  const insufficient = computed(
    () => originBalance.value !== null && preview.value?.insufficient === true,
  )

  const balanceNotLoaded = computed(
    () => isLoading.value || loadError.value !== null || originBalance.value === null,
  )

  /** Both balances after the exchange, ready to print (US-27 «Canvi fet» mockup). */
  const newBalanceRows = computed(() => {
    if (draft === null || newBalances.value === null) return []
    const { srcCurrency: src, tgtCurrency: tgt } = draft
    // §12.7 echoes both accounts already updated: print the server's balances, not a recomputation.
    const { from, to } = newBalances.value
    return [
      {
        label: isMainCurrency(src) ? 'Compte en euros' : `${src} · ${currencyByCode(src).name}`,
        value: formatMinor(from.balance, src),
      },
      {
        label: isMainCurrency(tgt) ? 'Compte en euros' : `${tgt} · ${currencyByCode(tgt).name}`,
        value: formatMinor(to.balance, tgt),
      },
    ]
  })

  async function start(): Promise<void> {
    if (draft === null) {
      await dependencies.goToExchange()
      return
    }

    isLoading.value = true
    loadError.value = null
    try {
      const subaccounts = (await dependencies.getSubaccounts()).items
      // Fetched fresh: the server balance decides, whatever «Canviar» showed.
      originBalance.value =
        subaccounts.find((subaccount) => subaccount.code === draft.srcCurrency)?.balance ?? 0
    } catch (failure) {
      loadError.value = toUserMessage(failure)
    } finally {
      isLoading.value = false
    }
  }

  async function confirm(): Promise<void> {
    if (draft === null || isConfirming.value || confirmed.value) return
    if (insufficient.value || balanceNotLoaded.value) return

    isConfirming.value = true
    submitError.value = null

    try {
      newBalances.value = await dependencies.confirmExchange({
        fromCurrency: draft.srcCurrency,
        toCurrency: draft.tgtCurrency,
        amount: draft.amountMinor,
      })
      confirmed.value = true
      // The tick and the new balances stay on screen while the ViewModel waits.
      await dependencies.pause(CONFIRMATION_MS)
      await dependencies.goHome()
    } catch (failure) {
      submitError.value =
        isApiError(failure) && failure.code === 'INSUFFICIENT_BALANCE'
          ? EXCHANGE_INSUFFICIENT_BALANCE_MESSAGE
          : toUserMessage(failure)
    } finally {
      // Only reaches the screen when the exchange failed: success has navigated away.
      isConfirming.value = false
    }
  }

  return {
    draft,
    isLoading,
    loadError,
    originLine,
    rateLabel,
    rateValue,
    commissionText,
    chargeNote,
    exactLine,
    insufficient,
    insufficientMessage: EXCHANGE_INSUFFICIENT_BALANCE_MESSAGE,
    balanceNotLoaded,
    isConfirming,
    confirmed,
    submitError,
    newBalances,
    newBalanceRows,
    start,
    confirm,
  }
}

function defaultDependencies(): ExchangeSummaryDependencies {
  const router = useRouter()
  const state = window.history.state as {
    srcCurrency?: unknown
    tgtCurrency?: unknown
    amountMinor?: unknown
  } | null
  const { srcCurrency, tgtCurrency, amountMinor } = state ?? {}

  // `history.state` is untyped data from another screen, so it is checked before use.
  let draft: ExchangeDraft | null = null
  if (
    isCurrencyCode(srcCurrency) &&
    isCurrencyCode(tgtCurrency) &&
    typeof amountMinor === 'number' &&
    Number.isInteger(amountMinor) &&
    amountMinor > 0
  ) {
    draft = { srcCurrency, tgtCurrency, amountMinor }
  }

  return {
    draft,
    getSubaccounts,
    confirmExchange: postExchange,
    // Replace: going back from Home must not reopen a summary that was already sent.
    goHome: () => router.replace({ name: 'home' }),
    goToExchange: () => router.replace({ name: 'exchange' }),
    pause: (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  }
}
