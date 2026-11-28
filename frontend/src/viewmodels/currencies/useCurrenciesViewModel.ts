import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  CURRENCIES,
  formatCurrencyAmount,
  type CurrencyCode,
  type Subaccount,
  type SubaccountList,
} from '@/models/currency'
import { toUserMessage } from '@/models/errorMessages'
import { getSubaccounts } from '@/services/subaccountsService'

export interface CurrenciesDependencies {
  getSubaccounts: () => Promise<SubaccountList>
  goToAdd: () => unknown
  goChange: () => unknown
  /** US-26: each row opens its account's detail. */
  goToSubaccount: (subaccountId: string) => unknown
}

/** One line of the currencies list: only the sub-accounts the person already owns. */
export interface CurrencyRow {
  /** The account's id (`main` for EUR), for its detail (US-26). */
  id: string
  code: CurrencyCode
  name: string
  symbol: string
  amountText: string
}

/**
 * Currencies screen (US-25): the sub-accounts the person owns, each with its
 * balance, the total in euros, and the way to add or change currencies.
 */
export function useCurrenciesViewModel(dependencies: CurrenciesDependencies = defaultDependencies()) {
  const subaccounts = ref<Subaccount[]>([])
  // Starts true so a zero total never flashes before the first answer.
  const isLoading = ref(true)
  const error = ref<string | null>(null)

  // CURRENCIES order, so EUR is always first and the list never reorders.
  const rows = computed<CurrencyRow[]>(() =>
    CURRENCIES.flatMap((currency) => {
      const subaccount = subaccounts.value.find((owned) => owned.code === currency.code)
      if (subaccount === undefined) return []
      return [
        {
          id: subaccount.id,
          code: currency.code,
          name: currency.name,
          symbol: currency.symbol,
          amountText: formatCurrencyAmount(subaccount.balance, currency.code),
        },
      ]
    }),
  )

  // The server computes the total (§12.3): the screen only displays it, never
  // recomputes it from the rows. `null` until the first answer arrives.
  const totalInEuros = ref<number | null>(null)
  const totalCents = computed(() => totalInEuros.value ?? 0)

  async function load(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const list = await dependencies.getSubaccounts()
      subaccounts.value = list.items
      totalInEuros.value = list.totalInEuros
    } catch (failure) {
      error.value = toUserMessage(failure)
    } finally {
      isLoading.value = false
    }
  }

  return {
    rows,
    totalCents,
    isLoading,
    error,
    load,
    goToAdd: dependencies.goToAdd,
    goChange: dependencies.goChange,
    goToSubaccount: dependencies.goToSubaccount,
  }
}

function defaultDependencies(): CurrenciesDependencies {
  const router = useRouter()
  return {
    getSubaccounts,
    goToAdd: () => router.push({ name: 'add-currency' }),
    // Owned by US-27: the route does not exist yet, so it is pushed by raw path.
    goChange: () => router.push('/canviar'),
    goToSubaccount: (subaccountId) => router.push({ name: 'subaccount', params: { subaccountId } }),
  }
}
