/**
 * Where the session token lives (docs/api.md §8.2).
 * sessionStorage: it survives a reload, and closing the tab leaves no session behind,
 * which suits a bank app better than localStorage.
 */

const TOKEN_KEY = 'evolt.session.token'

export function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY)
}

export function saveToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  sessionStorage.removeItem(TOKEN_KEY)
}

export function hasSession(): boolean {
  return getToken() !== null
}
