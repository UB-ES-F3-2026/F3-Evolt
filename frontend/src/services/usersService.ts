/** /api/users — the other users of the app (US-13). One function per endpoint. */

import { apiGet } from './apiClient'
import { useMocks } from '@/mocks'
import { mockSearchUsers, mockUser } from '@/mocks/users'
import { fromApiUser, fromApiUsers, type UserSummary, type UserSummaryJson, type UsersJson } from '@/models/user'

/** The initial list for an empty text, or the users that match it (docs/api.md §13.2). */
export async function searchUsers(q: string): Promise<UserSummary[]> {
  const text = q.trim()
  const path = text === '' ? '/api/users' : `/api/users?q=${encodeURIComponent(text)}`
  const json = useMocks() ? mockSearchUsers(text) : await apiGet<UsersJson>(path)
  return fromApiUsers(json.items)
}

/** One user, to check a recipient again when «Enviar» is reloaded (docs/api.md §13.3). */
export async function getUser(userId: string): Promise<UserSummary> {
  const json = useMocks()
    ? mockUser(userId)
    : await apiGet<UserSummaryJson>(`/api/users/${encodeURIComponent(userId)}`)
  return fromApiUser(json)
}
