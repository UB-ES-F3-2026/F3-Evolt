import { computed, ref } from 'vue'
import { messageForCode } from '@/models/errorMessages'
import { isPasswordStrong } from '@/models/password'

const PASSWORDS_DIFFER = 'Les contrasenyes no coincideixen'

/** The two password fields and their checks, shared by register (US-01) and new password (US-04). */
export function usePasswordFields() {
  const password = ref('')
  const repeatedPassword = ref('')

  // An empty field shows nothing: nobody has made a mistake yet.
  const passwordError = computed(() =>
    password.value !== '' && !isPasswordStrong(password.value) ? messageForCode('WEAK_PASSWORD') : null,
  )
  const repeatedPasswordError = computed(() =>
    repeatedPassword.value !== '' && repeatedPassword.value !== password.value ? PASSWORDS_DIFFER : null,
  )
  const arePasswordsValid = computed(
    () => isPasswordStrong(password.value) && repeatedPassword.value === password.value,
  )

  return { password, repeatedPassword, passwordError, repeatedPasswordError, arePasswordsValid }
}
