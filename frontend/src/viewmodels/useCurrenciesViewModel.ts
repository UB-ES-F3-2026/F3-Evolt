import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  CURRENCIES,
  formatCurrencyAmount,
  totalInEurosMinor,
  type CurrencyCode,
  type Subaccount,
} from '@/models/currency'
import { toUserMessage } from '@/models/errorMessages'
import { getSubaccounts } from '@/services/subaccountsService'

export interface CurrenciesDependencies {
  getSubaccounts: () => Promise<Subaccount[]>
  goToAdd: () => unknown
  goChange: () => unknown
}

/** One line of the currencies list: only the sub-accounts the person already owns. */
export interface CurrencyRow {
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
          code: currency.code,
          name: currency.name,
          symbol: currency.symbol,
          amountText: formatCurrencyAmount(subaccount.balance, currency.code),
        },
      ]
    }),
  )

  // Each row is converted to euros on its own and then summed (see the model).
  const totalCents = computed(() => totalInEurosMinor(subaccounts.value))

  async function load(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      subaccounts.value = await dependencies.getSubaccounts()
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
  }
}

function defaultDependencies(): CurrenciesDependencies {
  const router = useRouter()
  return {
    getSubaccounts,
    goToAdd: () => router.push({ name: 'add-currency' }),
    // Owned by US-27: the route does not exist yet, so it is pushed by raw path.
    goChange: () => router.push('/canviar'),
  }
}
