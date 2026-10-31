/** Shapes of the access routes (docs/api.md §8). */

export interface RegisterRequest {
  identifier: string
  password: string
  acceptedTerms: boolean
}

export interface RegisterJson {
  /** Normalized by the backend: the next screen must use this one, not the typed text. */
  identifier: string
  status: 'pending'
}

export interface VerifyRequest {
  identifier: string
  /** A string, so the zeros on the left are not lost. */
  code: string
}

/** Answer of the routes that open a session. The token is opaque: the frontend never reads it. */
export interface SessionJson {
  token: string
}

export interface StatusJson {
  status: 'ok'
}

export interface LoginRequest {
  identifier: string
  password: string
}

export interface ResetPasswordRequest {
  /** The one in the recovery link. */
  token: string
  password: string
}

export const CODE_LENGTH = 6
