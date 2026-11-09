/**
 * Where the session token lives, and how a session ends (docs/api.md §8.2).
 * sessionStorage: it survives a reload, and closing the tab leaves no session behind,
 * which suits a bank app better than localStorage.
 */

const TOKEN_KEY = 'evolt.session.token'
const INACTIVITY_MS = 5 * 60 * 1000

export type SessionEndReason = 'inactivity' | 'unauthenticated'

let inactivityTimer: ReturnType<typeof setTimeout> | null = null
let sessionEndedListener: ((reason: SessionEndReason) => void) | null = null

export function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY)
}

export function saveToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token)
  touchSession()
}

export function hasSession(): boolean {
  return getToken() !== null
}

/**
 * The backend only answers SESSION_EXPIRED when a request arrives, so with nobody
 * touching the app it would never say anything. US-03 wants the app back at the login
 * after 5 minutes doing nothing, so this timer mirrors the backend's. The backend still decides.
 */
export function touchSession(): void {
  stopInactivityTimer()
  if (!hasSession()) return
  inactivityTimer = setTimeout(() => endSession('inactivity'), INACTIVITY_MS)
}

/** The person left: no one needs to be told. */
export function closeSession(): void {
  stopInactivityTimer()
  sessionStorage.removeItem(TOKEN_KEY)
}

/** The session was lost without asking for it. */
export function endSession(reason: SessionEndReason): void {
  closeSession()
  sessionEndedListener?.(reason)
}

/** The router listens here, so that this layer does not need to know about screens. */
export function onSessionEnded(listener: (reason: SessionEndReason) => void): void {
  sessionEndedListener = listener
}

function stopInactivityTimer(): void {
  if (inactivityTimer !== null) clearTimeout(inactivityTimer)
  inactivityTimer = null
}
