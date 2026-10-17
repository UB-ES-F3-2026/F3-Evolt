import { readonly, ref } from 'vue'

const STORAGE_KEY = 'evolt.balanceHidden'

// Module-level, so every screen shares one preference. It is read once, when the
// app starts, and kept in localStorage for the next session (US-07 AC 5).
const isHidden = ref(readStoredPreference())

/** "Hide amounts" preference: when on, every amount on screen is masked. */
export function useBalanceVisibility() {
  function toggle(): void {
    isHidden.value = !isHidden.value
    storePreference(isHidden.value)
  }

  // Read-only, so a view cannot change the value without saving it.
  return { isHidden: readonly(isHidden), toggle }
}

function readStoredPreference(): boolean {
  try {
    return localStorage.getItem(STORAGE_KEY) === 'true'
  } catch {
    // Storage blocked by the browser (private mode, settings): start with amounts visible.
    return false
  }
}

function storePreference(hidden: boolean): void {
  try {
    localStorage.setItem(STORAGE_KEY, String(hidden))
  } catch {
    // Without storage the preference still works until the app is closed.
  }
}
