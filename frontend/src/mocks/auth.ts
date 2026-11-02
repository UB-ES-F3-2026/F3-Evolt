/**
 * Mock of the access routes: same answers and same errors as docs/api.md §8.
 * No email or SMS exists here either, so what the backend would leave in its
 * simulated outbox (§8.12) is printed in the browser console.
 * The state stays in sessionStorage because opening a recovery link reloads the page.
 */

import type { ApiErrorCode } from '@/models/apiError'
import type {
  RegisterJson,
  RegisterRequest,
  SessionJson,
  StatusJson,
  VerifyRequest,
} from '@/models/auth'
import { messageForCode } from '@/models/errorMessages'
import { isPasswordStrong } from '@/models/password'
import { mockError } from './index'

const STORAGE_KEY = 'evolt.mock.auth'
const MAX_PASSWORD_BYTES = 72
const CODE_LIFETIME_MS = 10 * 60 * 1000
const MAX_CODE_ATTEMPTS = 5

interface MockUser {
  identifier: string
  password: string
  status: 'pending' | 'active'
}

interface MockCode {
  identifier: string
  code: string
  createdAt: number
  failedAttempts: number
}

interface MockMessage {
  to: string
  type: 'verification_code'
  code: string
}

interface MockState {
  users: MockUser[]
  codes: MockCode[]
  outbox: MockMessage[]
}

/** POST /api/auth/register — validations in the order of docs/api.md §8.5. */
export function mockRegister({ identifier, password, acceptedTerms }: RegisterRequest): RegisterJson {
  const normalized = normalizeIdentifier(identifier)
  const isTooLong = new TextEncoder().encode(password).length > MAX_PASSWORD_BYTES
  if (normalized === null || acceptedTerms !== true || isTooLong) throw failure('VALIDATION_ERROR')
  if (!isPasswordStrong(password)) throw failure('WEAK_PASSWORD')

  const state = loadState()
  if (state.users.some((user) => user.identifier === normalized)) throw failure('ALREADY_REGISTERED')

  state.users.push({ identifier: normalized, password, status: 'pending' })
  sendNewCode(state, normalized)
  saveState(state)
  return { identifier: normalized, status: 'pending' }
}

/** POST /api/auth/verify — validations in the order of docs/api.md §8.6. */
export function mockVerify({ identifier, code }: VerifyRequest): SessionJson {
  if (!/^\d{6}$/.test(code)) throw failure('VALIDATION_ERROR')

  const state = loadState()
  const normalized = normalizeIdentifier(identifier)
  const user = state.users.find((one) => one.identifier === normalized && one.status === 'pending')
  const current = state.codes.find((one) => one.identifier === normalized)
  if (user === undefined || current === undefined) throw failure('INVALID_CODE')

  if (current.failedAttempts >= MAX_CODE_ATTEMPTS) throw failure('TOO_MANY_ATTEMPTS')
  if (Date.now() - current.createdAt >= CODE_LIFETIME_MS) throw failure('CODE_EXPIRED')
  if (code !== current.code) {
    current.failedAttempts += 1
    saveState(state)
    throw failure(current.failedAttempts >= MAX_CODE_ATTEMPTS ? 'TOO_MANY_ATTEMPTS' : 'INVALID_CODE')
  }

  user.status = 'active'
  state.codes = state.codes.filter((one) => one !== current)
  saveState(state)
  return { token: newToken() }
}

/** POST /api/auth/resend-code — same answer whether the account exists or not (§8.7). */
export function mockResendCode(identifier: string): StatusJson {
  const normalized = normalizeIdentifier(identifier)
  if (normalized === null) throw failure('VALIDATION_ERROR')

  const state = loadState()
  if (state.users.some((user) => user.identifier === normalized && user.status === 'pending')) {
    sendNewCode(state, normalized)
    saveState(state)
  }
  return { status: 'ok' }
}

/** GET /api/dev/outbox?to= — newest first. */
export function mockOutbox(to: string): MockMessage[] {
  const normalized = normalizeIdentifier(to)
  return loadState()
    .outbox.filter((message) => message.to === normalized)
    .reverse()
}

/** docs/api.md §8.3: lower-case email; phone without separators and with its prefix. */
function normalizeIdentifier(raw: string): string | null {
  const text = raw.trim()
  return text.includes('@') ? normalizeEmail(text) : normalizePhone(text)
}

function normalizeEmail(text: string): string | null {
  const email = text.toLowerCase()
  return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) ? email : null
}

function normalizePhone(text: string): string | null {
  let phone = text.replace(/[\s\-.()]/g, '')
  if (phone.startsWith('00')) phone = `+${phone.slice(2)}`
  if (/^\d{9}$/.test(phone)) phone = `+34${phone}`
  return /^\+[1-9]\d{7,14}$/.test(phone) ? phone : null
}

function sendNewCode(state: MockState, identifier: string): void {
  const code = String(Math.floor(Math.random() * 1_000_000)).padStart(6, '0')
  state.codes = state.codes.filter((current) => current.identifier !== identifier)
  state.codes.push({ identifier, code, createdAt: Date.now(), failedAttempts: 0 })
  state.outbox.push({ to: identifier, type: 'verification_code', code })
  console.info(`[mock] Codi de verificació per a ${identifier}: ${code}`)
}

function newToken(): string {
  return `mock-token-${Date.now()}`
}

function failure(code: ApiErrorCode) {
  return mockError(code, messageForCode(code))
}

function loadState(): MockState {
  const saved = sessionStorage.getItem(STORAGE_KEY)
  return saved === null ? initialState() : (JSON.parse(saved) as MockState)
}

function saveState(state: MockState): void {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

/** The fictitious accounts of the backend seed (docs/api.md §8.13). */
function initialState(): MockState {
  return {
    users: [
      { identifier: 'demo@evolt.test', password: 'Evolt2026', status: 'active' },
      { identifier: 'buit@evolt.test', password: 'Evolt2026', status: 'active' },
    ],
    codes: [],
    outbox: [],
  }
}
