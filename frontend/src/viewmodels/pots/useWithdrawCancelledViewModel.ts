import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { messageForCode, toUserMessage } from '@/models/errorMessages'
import type { Home } from '@/models/home'
import type { Pot } from '@/models/pot'
import { getHome } from '@/services/homeService'
import { getPots } from '@/services/pots/potsService'

// The same pause as after a withdrawal, so both notices last the same (US-19, REP-12).
const NOTICE_MS = 1500

export interface WithdrawCancelledDependencies {
  getHome: () => Promise<Home>
  getPots: () => Promise<Pot[]>
  goToPot: () => Promise<unknown>
  pause: (ms: number) => Promise<void>
}

/**
 * «Retirada cancel·lada» notice (US-19, REP-12): nothing was withdrawn, so it shows both
 * balances unchanged and goes back to the pot by itself after 1,5 s, or earlier with
 * «Tornar a la guardiola». It never shows the amount that was typed.
 */
export function useWithdrawCancelledViewModel(
  potId: string,
  dependencies: WithdrawCancelledDependencies = defaultDependencies(potId),
) {
  const pot = ref<Pot | null>(null)
  const balance = ref<number | null>(null)
  const isLoading = ref(true)
  const error = ref<string | null>(null)
  // Leaving once is enough: the button and the timer must not both navigate.
  let hasLeft = false

  async function load(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const [home, pots] = await Promise.all([dependencies.getHome(), dependencies.getPots()])
      balance.value = home.balance
      pot.value = pots.find((candidate) => candidate.id === potId) ?? null
      if (pot.value === null) error.value = messageForCode('POT_NOT_FOUND')
    } catch (failure) {
      error.value = toUserMessage(failure)
    } finally {
      isLoading.value = false
    }
  }

  async function backToPot(): Promise<void> {
    if (hasLeft) return
    hasLeft = true
    await dependencies.goToPot()
  }

  /** Waits the notice time and goes back, unless the person already left. */
  async function returnAutomatically(): Promise<void> {
    await dependencies.pause(NOTICE_MS)
    await backToPot()
  }

  /** The screen is gone (another link was used): the timer must not navigate anymore. */
  function stop(): void {
    hasLeft = true
  }

  return { pot, balance, isLoading, error, load, backToPot, returnAutomatically, stop }
}

function defaultDependencies(potId: string): WithdrawCancelledDependencies {
  const router = useRouter()
  return {
    getHome,
    getPots,
    // Replace, as after a withdrawal: going back from the pot must not show this notice again.
    goToPot: () => router.replace({ name: 'pot', params: { potId } }),
    pause: (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  }
}
