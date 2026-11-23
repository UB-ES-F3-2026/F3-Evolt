/**
 * The other users of the app, shaped exactly like docs/api.md §13. The eight users and
 * their phones are the seed of §13.9; the logged-in one never appears in a search.
 */

import { MAX_USER_SEARCH_LENGTH, type UserSummaryJson, type UsersJson } from '@/models/user'
import { mockError } from './index'
import { mockCurrentUser } from './mockUser'

interface SeedUser extends UserSummaryJson {
  email: string
  /** The 9 national digits (+34 is dropped), the part a phone search compares. */
  phone: string
}

/** docs/api.md §13.9: the two old users and one per team member, with their GitHub alias. */
const SEED_USERS: SeedUser[] = [
  { id: 'usr-01', name: 'Usuari demo', username: 'demo', email: 'demo@evolt.test', phone: '611223307' },
  { id: 'usr-02', name: 'Usuari nou', username: 'buit', email: 'buit@evolt.test', phone: '611223308' },
  { id: 'usr-03', name: 'Alicia', username: 'aliciaa415', email: 'alicia@evolt.test', phone: '611223301' },
  { id: 'usr-04', name: 'Huabin', username: '123huabin123', email: 'huabin@evolt.test', phone: '611223302' },
  { id: 'usr-05', name: 'Izan', username: 'izanfarreny47', email: 'izan@evolt.test', phone: '611223303' },
  { id: 'usr-06', name: 'Jiajun', username: 'yayuuun', email: 'jiajun@evolt.test', phone: '611223304' },
  { id: 'usr-07', name: 'Junhao', username: 'junhaozhang', email: 'junhao@evolt.test', phone: '611223305' },
  { id: 'usr-08', name: 'Martí', username: 'sudo-itramplay', email: 'marti@evolt.test', phone: '611223306' },
]

/** At most this many users in any answer (US-14: «màxim 10 resultats»). */
const MAX_RESULTS = 10

/**
 * GET /api/users — the initial list without `q`, or the users that match it by one of the
 * four ways of §13.2. Never the logged-in user; sorted by visible name; at most 10.
 */
export function mockSearchUsers(q = '', currentEmail: string | null = mockCurrentUser()): UsersJson {
  const text = q.trim()
  if (text.length > MAX_USER_SEARCH_LENGTH) {
    throw mockError('VALIDATION_ERROR', 'Les dades de la petició no són vàlides.')
  }
  const others = SEED_USERS.filter((user) => user.email !== currentEmail)
  const found = text === '' ? others : others.filter((user) => matches(user, text))
  return { items: found.sort(byVisibleName).slice(0, MAX_RESULTS).map(toSummary) }
}

/** GET /api/users/{userId} — 404 RECIPIENT_NOT_FOUND for an id that is not a user (§13.3). */
export function mockUser(userId: string): UserSummaryJson {
  const user = SEED_USERS.find((candidate) => candidate.id === userId)
  if (user === undefined) throw mockError('RECIPIENT_NOT_FOUND', 'No hem trobat aquest destinatari.')
  return toSummary(user)
}

/** The API id of whoever is logged in, to tell a transfer to oneself apart (§13.4). */
export function mockUserIdByEmail(email: string | null): string | null {
  return SEED_USERS.find((user) => user.email === email)?.id ?? null
}

function matches(user: SeedUser, text: string): boolean {
  const username = text.startsWith('@') ? text.slice(1) : text
  return (
    // A bare "@" has no handle, so it matches nobody (docs/api.md §13.2).
    (username !== '' && fold(user.username).includes(fold(username))) ||
    fold(user.name ?? '').includes(fold(text)) ||
    // Only the whole email, so a search cannot be used to guess emails.
    user.email === text.toLowerCase() ||
    matchesPhone(user, text)
  )
}

/** Only phone characters and at least 9 digits; the last 9 must be the user's (§13.2). */
function matchesPhone(user: SeedUser, text: string): boolean {
  if (!/^[\d\s+\-.()]+$/.test(text)) return false
  const digits = text.replace(/\D/g, '')
  return digits.length >= 9 && digits.slice(-9) === user.phone
}

/** Lower case and without accents: «MARTÍ» and «marti» are the same text. */
function fold(text: string): string {
  return text.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()
}

function byVisibleName(a: SeedUser, b: SeedUser): number {
  const nameA = fold(a.name ?? a.username)
  const nameB = fold(b.name ?? b.username)
  if (nameA !== nameB) return nameA < nameB ? -1 : 1
  return a.id < b.id ? -1 : 1
}

function toSummary({ id, name, username }: SeedUser): UserSummaryJson {
  return { id, name, username }
}
