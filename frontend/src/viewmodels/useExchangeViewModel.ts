import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  estimateMinor,
  exchangePreview,
  parseKeypadAmount,
  type CurrencyCode,
  type ExchangeDraft,
} from '@/models/exchange'
import {
  EXCHANGE_INSUFFICIENT_BALANCE_MESSAGE,
  messageForCode,
  toUserMessage,
} from '@/models/errorMessages'
import {
  isMainCurrency,
  toSubaccountOption,
  type Subaccount,
  type SubaccountOption,
} from '@/models/currency'
import { currencyDecimals, formatMinor } from '@/models/money'
import { getSubaccounts } from '@/services/subaccountsService'

// Screen copy for the keypad: the shared AMOUNT_FORMAT_MESSAGE says «en euros»,
// which is wrong once the origin is USD, GBP, CHF or JPY.
const AMOUNT_FORMAT_TWO_DECIMALS = 'Escriu un import vàlid, amb 2 decimals com a màxim.'
const AMOUNT_FORMAT_WHOLE_UNITS = 'Escriu un import vàlid.'

export interface ExchangeDependencies {
  getSubaccounts: () => Promise<Subaccount[]>
  goToSummary: (draft: ExchangeDraft) => Promise<unknown>
  goToCurrencies: () => Promise<unknown>
}

/**
 * «Canviar» screen (US-27): the two subaccounts of the change, the amount typed
 * on the keypad and what the person would receive. «Continuar» only opens the
 * summary with the draft; no exchange is sent from here.
 */
export function useExchangeViewModel(dependencies: ExchangeDependencies = defaultDependencies()) {
  // Starts true so the pickers never render an empty list before the first answer.
  const isLoading = ref(true)
  const loadError = ref<string | null>(null)
  const subaccounts = ref<Subaccount[]>([])
  const srcCurrency = ref<CurrencyCode>('EUR')
  const tgtCurrency = ref<CurrencyCode>('EUR')
  const amount = ref('')

  const isLoaded = computed(() => !isLoading.value && loadError.value === null)

  // The service sends id, code and balance; the option adds the name and the main flag.
  const options = computed<SubaccountOption[]>(() => subaccounts.value.map(toSubaccountOption))

  // With fewer than two subaccounts there is nothing to exchange between (US-27).
  const needsTwoSubaccounts = computed(() => isLoaded.value && subaccounts.value.length < 2)

  const decimals = computed<0 | 2>(() => (currencyDecimals(srcCurrency.value) === 0 ? 0 : 2))

  const amountMinor = computed(() => parseKeypadAmount(amount.value, decimals.value))

  const srcBalance = computed(
    () => subaccounts.value.find((account) => account.code === srcCurrency.value)?.balance ?? null,
  )

  // Same verdict the summary judges: null until the amount parses and the balance is known.
  const preview = computed(() => {
    if (amountMinor.value === null || srcBalance.value === null) return null
    return exchangePreview(amountMinor.value, srcCurrency.value, tgtCurrency.value, srcBalance.value)
  })

  const amountError = computed<string | null>(() => {
    if (amount.value === '') return null
    const parsed = amountMinor.value
    if (parsed === null) {
      return decimals.value === 0 ? AMOUNT_FORMAT_WHOLE_UNITS : AMOUNT_FORMAT_TWO_DECIMALS
    }
    if (parsed <= 0) return messageForCode('INVALID_AMOUNT')
    if (srcBalance.value === null) return null

    if (preview.value?.tooSmall) return messageForCode('AMOUNT_TOO_SMALL')
    // Its own text on purpose: the INSUFFICIENT_BALANCE message speaks of a pot contribution.
    if (preview.value?.insufficient) return EXCHANGE_INSUFFICIENT_BALANCE_MESSAGE
    return null
  })

  // No balance, no verdict: mirrors the summary's rule so the view can place the
  // «No tens prou saldo» message under «Continuar» (US-27 «Saldo insuficient»).
  const insufficient = computed(
    () => srcBalance.value !== null && preview.value?.insufficient === true,
  )

  // The mockup keeps the approximation on screen while the amount is too small.
  const estimateText = computed<string | null>(() => {
    const parsed = amountMinor.value
    if (parsed === null) return null
    return `Rebràs aproximadament ${formatMinor(estimateMinor(parsed, srcCurrency.value, tgtCurrency.value), tgtCurrency.value)}`
  })

  const canContinue = computed(
    () =>
      isLoaded.value &&
      !needsTwoSubaccounts.value &&
      amount.value !== '' &&
      amountMinor.value !== null &&
      amountError.value === null,
  )

  // The target picker disables the origin, but the origin changing must never
  // leave both selectors on the same subaccount.
  watch(srcCurrency, () => {
    if (tgtCurrency.value !== srcCurrency.value) return
    const other = subaccounts.value.find((account) => account.code !== srcCurrency.value)
    if (other !== undefined) tgtCurrency.value = other.code
  })

  async function load(): Promise<void> {
    isLoading.value = true
    loadError.value = null
    try {
      applyInitialSelection(await dependencies.getSubaccounts())
    } catch (failure) {
      loadError.value = toUserMessage(failure)
    } finally {
      isLoading.value = false
    }
  }

  function applyInitialSelection(accounts: Subaccount[]): void {
    subaccounts.value = accounts
    const origin = accounts.find((account) => isMainCurrency(account.code)) ?? accounts[0]
    if (origin === undefined) return
    srcCurrency.value = origin.code
    const target = accounts.find((account) => account.code !== origin.code)
    tgtCurrency.value = target?.code ?? origin.code
  }

  function retry(): Promise<void> {
    return load()
  }

  const goToCurrencies = dependencies.goToCurrencies

  async function proceed(): Promise<void> {
    if (!canContinue.value || amountMinor.value === null) return
    await dependencies.goToSummary({
      srcCurrency: srcCurrency.value,
      tgtCurrency: tgtCurrency.value,
      amountMinor: amountMinor.value,
    })
  }

  return {
    isLoading,
    loadError,
    retry,
    subaccounts,
    options,
    needsTwoSubaccounts,
    srcCurrency,
    tgtCurrency,
    amount,
    decimals,
    amountError,
    insufficient,
    estimateText,
    canContinue,
    load,
    proceed,
    goToCurrencies,
  }
}

function defaultDependencies(): ExchangeDependencies {
  const router = useRouter()
  return {
    getSubaccounts,
    // The summary reads the draft from `history.state`, like the verification code (US-03).
    goToSummary: (draft) =>
      router.push({
        name: 'exchange-summary',
        state: {
          srcCurrency: draft.srcCurrency,
          tgtCurrency: draft.tgtCurrency,
          amountMinor: draft.amountMinor,
        },
      }),
    goToCurrencies: () =>
      // /divises is registered by T25.3 (route NAME differs across branches) — match by
      // path and fall back to Inici until it lands.
      router.getRoutes().some((route) => route.path === '/divises')
        ? router.push('/divises')
        : router.push({ name: 'home' }),
  }
}
