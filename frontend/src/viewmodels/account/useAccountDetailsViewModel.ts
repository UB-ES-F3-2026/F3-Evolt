import { computed, ref } from 'vue'
import { groupIban, shareText, type AccountDetails } from '@/models/account'
import { toUserMessage } from '@/models/errorMessages'
import { getAccountDetails } from '@/services/account/accountService'

/** How long «IBAN copiat» and «Dades copiades» stay at the bottom (US-12, criterion 4). */
export const NOTICE_MS = 2000

export interface AccountDetailsDependencies {
  getAccountDetails: () => Promise<AccountDetails>
  /** Writes a text to the clipboard. */
  copyText: (text: string) => Promise<void>
  /** Opens the share menu of the phone, or null when the browser has none. */
  shareText: ((text: string) => Promise<void>) | null
  /** Calls `done` after `ms`, so the tests do not wait 2 s. */
  later: (done: () => void, ms: number) => void
}

function browserShare(): AccountDetailsDependencies['shareText'] {
  if (typeof navigator === 'undefined' || typeof navigator.share !== 'function') return null
  return (text) => navigator.share({ text })
}

const browserDependencies: AccountDetailsDependencies = {
  getAccountDetails,
  copyText: (text) => navigator.clipboard.writeText(text),
  shareText: browserShare(),
  later: (done, ms) => {
    setTimeout(done, ms)
  },
}

/** The person closed the share menu without choosing anything: nothing else has to happen. */
function isShareCancelled(failure: unknown): boolean {
  return failure instanceof DOMException && failure.name === 'AbortError'
}

/**
 * «Dades del compte» screen (`/account`, US-12): the IBAN in groups of four, the BIC and the holder.
 * Touching the IBAN copies it without spaces; «Compartir» shares the three of them, or copies them
 * when the browser cannot share.
 */
export function useAccountDetailsViewModel(dependencies: AccountDetailsDependencies = browserDependencies) {
  const details = ref<AccountDetails | null>(null)
  const isLoading = ref(true)
  const loadError = ref<string | null>(null)
  /** «IBAN copiat» or «Dades copiades», at the bottom for 2 s. */
  const notice = ref<string | null>(null)
  // A newer notice must not be cleared by the timer of an older one.
  let noticeNumber = 0

  const groupedIban = computed(() => (details.value === null ? '' : groupIban(details.value.iban)))

  async function load(): Promise<void> {
    isLoading.value = true
    loadError.value = null
    try {
      details.value = await dependencies.getAccountDetails()
    } catch (failure) {
      loadError.value = toUserMessage(failure)
    } finally {
      isLoading.value = false
    }
  }

  function showNotice(text: string): void {
    const number = ++noticeNumber
    notice.value = text
    dependencies.later(() => {
      if (number === noticeNumber) notice.value = null
    }, NOTICE_MS)
  }

  /** Touching the IBAN: it is copied without spaces, as the server sends it (§16.1). */
  async function copyIban(): Promise<void> {
    if (details.value === null) return
    try {
      await dependencies.copyText(details.value.iban)
      showNotice('IBAN copiat')
    } catch {
      // The story gives no text for a clipboard the browser blocks: nothing is shown.
    }
  }

  /** «Compartir»: the share menu of the phone; without one, the same text is copied (US-12, criterion 5). */
  async function share(): Promise<void> {
    if (details.value === null) return
    const text = shareText(details.value)
    if (dependencies.shareText !== null) {
      try {
        await dependencies.shareText(text)
        return
      } catch (failure) {
        if (isShareCancelled(failure)) return
        // Any other refusal is a browser that does not let it share: copy instead.
      }
    }
    try {
      await dependencies.copyText(text)
      showNotice('Dades copiades')
    } catch {
      // As with the IBAN: no text defined for a blocked clipboard.
    }
  }

  return { details, groupedIban, isLoading, loadError, notice, load, copyIban, share }
}
