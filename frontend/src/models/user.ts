/**
 * Another user of the app, as search and transfers show them (docs/api.md §13.1).
 *
 * Contract invariants worth remembering:
 * - It never carries money, email, phone or account state: only who the person is.
 * - `name` is null when the person never gave one; the screen then shows the @username.
 * - `username` comes without the `@`; the screen adds it.
 */

export interface UserSummary {
  id: string
  name: string | null
  username: string
}

export type UserSummaryJson = UserSummary

/** GET /api/users (docs/api.md §13.2). */
export interface UsersJson {
  items: UserSummaryJson[]
}

/** Longest search text the API accepts; longer is VALIDATION_ERROR (docs/api.md §13.2). */
export const MAX_USER_SEARCH_LENGTH = 64

export function fromApiUser(json: UserSummaryJson): UserSummary {
  return { id: json.id, name: json.name ?? null, username: json.username }
}

export function fromApiUsers(jsonList: UserSummaryJson[] | null | undefined): UserSummary[] {
  return (jsonList ?? []).map(fromApiUser)
}

export function atUsername(user: UserSummary): string {
  return `@${user.username}`
}

/** The name a person is shown with: their name, or their @username if they have none (US-13). */
export function displayName(user: UserSummary): string {
  return user.name ?? atUsername(user)
}

/** Up to two letters for the round avatar: «Usuari nou» → «UN», «Alicia» → «AL», «@buit» → «BU». */
export function initials(user: UserSummary): string {
  const words = (user.name ?? user.username).trim().split(/\s+/).filter(Boolean)
  const letters = words.length > 1 ? words[0][0] + words[1][0] : (words[0] ?? '').slice(0, 2)
  return letters.toUpperCase()
}
