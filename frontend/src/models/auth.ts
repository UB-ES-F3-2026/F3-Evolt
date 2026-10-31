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
