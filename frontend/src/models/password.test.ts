import { describe, expect, it } from 'vitest'
import { isPasswordStrong } from './password'

describe('isPasswordStrong', () => {
  it.each(['Platja2026', 'Àlgebra26', 'ABCDEFG1'])('accepts %j', (password) => {
    expect(isPasswordStrong(password)).toBe(true)
  })

  it.each([
    ['too short', 'curta1A'],
    ['no uppercase', 'platja2026'],
    ['no digit', 'PlatjaNova'],
    ['empty', ''],
  ])('rejects a password with %s', (_reason, password) => {
    expect(isPasswordStrong(password)).toBe(false)
  })
})
