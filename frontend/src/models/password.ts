const MIN_CHARACTERS = 8

// Password rules come from US-01 and docs/api.md §8.4: min 8, one uppercase (accented ones
// count), one digit. The backend owns them; this copy only answers before sending.
// Shared with the new password screen (US-04), so do not repeat it there.
export function isPasswordStrong(password: string): boolean {
  const hasEnoughCharacters = [...password].length >= MIN_CHARACTERS
  const hasUppercase = /\p{Lu}/u.test(password)
  const hasDigit = /[0-9]/.test(password)
  return hasEnoughCharacters && hasUppercase && hasDigit
}
