/**
 * Who is logged in to the mocks, so each account sees its own data, as with the backend:
 * `demo@evolt.test` the seed, and `buit@evolt.test` or a new account nothing (docs/api.md §8.13).
 * It lives in sessionStorage like the rest of the mock session, so a reload keeps it.
 */

const STORAGE_KEY = 'evolt.mock.user'
const listeners: (() => void)[] = []

export function mockCurrentUser(): string | null {
  // Many unit tests run in Node, with no sessionStorage: there nobody is logged in.
  if (typeof sessionStorage === 'undefined') return null
  return sessionStorage.getItem(STORAGE_KEY)
}

/** The auth mock calls it when a session opens or closes. */
export function setMockCurrentUser(identifier: string | null): void {
  if (identifier === mockCurrentUser()) return
  if (identifier === null) sessionStorage.removeItem(STORAGE_KEY)
  else sessionStorage.setItem(STORAGE_KEY, identifier)
  listeners.forEach((listener) => listener())
}

/** Lets the data mocks start again when another person logs in. */
export function onMockUserChange(listener: () => void): void {
  listeners.push(listener)
}
