<script setup lang="ts">
import AppShell from '@/components/AppShell.vue'
import FormField from '@/components/FormField.vue'
import PrimaryButton from '@/components/PrimaryButton.vue'
import { useRegisterViewModel } from '@/viewmodels/useRegisterViewModel'

const {
  identifier,
  password,
  repeatedPassword,
  acceptedTerms,
  passwordError,
  repeatedPasswordError,
  submitError,
  isAlreadyRegistered,
  canSubmit,
  isSubmitting,
  submit,
} = useRegisterViewModel()
</script>

<template>
  <AppShell title="Crear compte">
    <form class="card" novalidate @submit.prevent="submit">
      <FormField
        id="identifier"
        v-model="identifier"
        label="Email o telèfon"
        autocomplete="username"
        :disabled="isSubmitting"
      />
      <FormField
        id="password"
        v-model="password"
        label="Contrasenya"
        type="password"
        autocomplete="new-password"
        :error="passwordError"
        :disabled="isSubmitting"
      />
      <FormField
        id="repeated-password"
        v-model="repeatedPassword"
        label="Repeteix la contrasenya"
        type="password"
        autocomplete="new-password"
        :error="repeatedPasswordError"
        :disabled="isSubmitting"
      />

      <label class="terms">
        <input v-model="acceptedTerms" type="checkbox" :disabled="isSubmitting" />
        Accepto els termes i la política de privacitat
      </label>

      <p v-if="submitError" class="error" role="alert">
        {{ submitError }}
        <router-link v-if="isAlreadyRegistered" to="/login">Inicia sessió</router-link>
      </p>

      <PrimaryButton :disabled="!canSubmit">
        {{ isSubmitting ? 'Creant…' : 'Crear compte' }}
      </PrimaryButton>
    </form>
  </AppShell>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1.25rem;
}

.terms {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.error {
  margin: 0 0 1rem;
  font-size: 0.875rem;
  color: var(--color-error);
}
</style>
