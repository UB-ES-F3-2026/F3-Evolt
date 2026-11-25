import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { CURRENCIES, type CurrencyCode, type Subaccount } from '@/models/currency'
import { toUserMessage } from '@/models/errorMessages'
import { addSubaccount, getSubaccounts } from '@/services/subaccountsService'

// Long enough to read the confirmation before going back to Home.
const CONFIRMATION_MS = 1500

export interface AddCurrencyDependencies {
  getSubaccounts: () => Promise<Subaccount[]>
  addSubaccount: (code: CurrencyCode) => Promise<Subaccount>
  goHome: () => Promise<unknown>
  pause: (ms: number) => Promise<void>
}

/** One line of the picker: every currency, whether it is already owned and whether it can be chosen. */
export interface AddCurrencyRow {
  code: CurrencyCode
  name: string
  symbol: string
  owned: boolean
  disabled: boolean
}

/**
 * Add-currency screen (US-25): the five currencies, the ones already owned
 * marked, and creating the sub-account of the chosen one.
 */
export function useAddCurrencyViewModel(dependencies: AddCurrencyDependencies = defaultDependencies()) {
  const subaccounts = ref<Subaccount[]>([])
  // Starts true so "none owned" never flashes before the first answer.
  const isLoading = ref(true)
  const error = ref<string | null>(null)
  const isSubmitting = ref(false)
  const confirmation = ref<string | null>(null)

  function isOwned(code: CurrencyCode): boolean {
    return subaccounts.value.some((subaccount) => subaccount.code === code)
  }

  // Every currency is listed; owned and in-flight ones cannot be chosen again.
  const rows = computed<AddCurrencyRow[]>(() =>
    CURRENCIES.map((currency) => {
      const owned = isOwned(currency.code)
      return {
        code: currency.code,
        name: currency.name,
        symbol: currency.symbol,
        owned,
        disabled: owned || isSubmitting.value || confirmation.value !== null,
      }
    }),
  )

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

  async function add(code: CurrencyCode): Promise<boolean> {
    // The guard is the whole double-click protection: a second tap never sends.
    if (isSubmitting.value || confirmation.value !== null || isOwned(code)) return false

    isSubmitting.value = true
    error.value = null

    try {
      await dependencies.addSubaccount(code)
    } catch (failure) {
      error.value = toUserMessage(failure)
      isSubmitting.value = false
      return false
    }

    // The sub-account exists from here on: a failed reload must never read as a failed add.
    try {
      // Reload instead of pushing the new row: the backend is the source of truth.
      subaccounts.value = await dependencies.getSubaccounts()
    } catch {
      // The picker is already leaving; Home reloads the list when it arrives.
    }
    confirmation.value = `Subcompte en ${code} creat`

    // `isSubmitting` stays true until leaving: the screen is already on its way out.
    await dependencies.pause(CONFIRMATION_MS)
    await dependencies.goHome()
    return true
  }

  return { rows, isLoading, error, isSubmitting, confirmation, load, add }
}

function defaultDependencies(): AddCurrencyDependencies {
  const router = useRouter()
  return {
    getSubaccounts,
    addSubaccount,
    // US-25: replace, so the browser's Back button does not return to the picker;
    // by the named `home` route instead of a raw path.
    goHome: () => router.replace({ name: 'home' }),
    pause: (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  }
}
