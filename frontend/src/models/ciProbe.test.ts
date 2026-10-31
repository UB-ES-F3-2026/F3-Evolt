import { describe, expect, it } from 'vitest'

// Throwaway probe for #89: this test MUST fail so the CI pipeline goes red.
describe('CI red probe', () => {
  it('is intentionally broken', () => {
    expect(1).toBe(2)
  })
})
