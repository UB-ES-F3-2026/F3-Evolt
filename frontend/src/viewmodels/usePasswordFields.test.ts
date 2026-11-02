import { describe, expect, it } from 'vitest'
import { usePasswordFields } from './usePasswordFields'

describe('usePasswordFields', () => {
  it('starts without errors and not valid', () => {
    const fields = usePasswordFields()

    expect(fields.passwordError.value).toBeNull()
    expect(fields.repeatedPasswordError.value).toBeNull()
    expect(fields.arePasswordsValid.value).toBe(false)
  })

  it('explains the policy under a weak password', () => {
    const fields = usePasswordFields()

    fields.password.value = 'platja2026'

    expect(fields.passwordError.value).toBe('La contrasenya ha de tenir 8 caràcters, una majúscula i un número.')
    expect(fields.arePasswordsValid.value).toBe(false)
  })

  it('says when the two passwords differ', () => {
    const fields = usePasswordFields()

    fields.password.value = 'Platja2026'
    fields.repeatedPassword.value = 'Platja2025'

    expect(fields.passwordError.value).toBeNull()
    expect(fields.repeatedPasswordError.value).toBe('Les contrasenyes no coincideixen')
    expect(fields.arePasswordsValid.value).toBe(false)
  })

  it('is valid with a strong password repeated exactly', () => {
    const fields = usePasswordFields()

    fields.password.value = 'Platja2026'
    fields.repeatedPassword.value = 'Platja2026'

    expect(fields.repeatedPasswordError.value).toBeNull()
    expect(fields.arePasswordsValid.value).toBe(true)
  })
})
