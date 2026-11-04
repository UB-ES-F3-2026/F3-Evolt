<script setup lang="ts">
import { CircleCheck } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import FormField from '@/components/FormField.vue'
import PrimaryButton from '@/components/PrimaryButton.vue'
import { useNewPasswordViewModel } from '@/viewmodels/useNewPasswordViewModel'

const {
  password,
  repeatedPassword,
  passwordError,
  repeatedPasswordError,
  submitError,
  isLinkExpired,
  linkExpiredMessage,
  isChanged,
  canSubmit,
  isSubmitting,
  submit,
} = useNewPasswordViewModel()
</script>

<template>
  <AppShell title="Nova contrasenya">
    <section v-if="isChanged" class="card result" role="status">
      <CircleCheck class="success-icon" :size="40" />
      <p class="result-text">Contrasenya canviada</p>
      <router-link :to="{ name: 'login' }">Inicia sessió</router-link>
    </section>

    <section v-else-if="isLinkExpired" class="card result">
      <p class="result-text" role="alert">{{ linkExpiredMessage }}</p>
      <router-link :to="{ name: 'forgot-password' }" class="ask-again">Demanar-ne un de nou</router-link>
    </section>

    <form v-else class="card" novalidate @submit.prevent="submit">
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

      <p v-if="submitError" class="error" role="alert">{{ submitError }}</p>

      <PrimaryButton :disabled="!canSubmit">
        {{ isSubmitting ? 'Canviant…' : 'Canviar la contrasenya' }}
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

.result {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem 1.25rem;
  text-align: center;
}

.result-text {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.success-icon {
  color: var(--color-income);
}

.ask-again {
  padding: 0.625rem 1rem;
  border-radius: var(--radius);
  background: var(--color-primary);
  color: var(--color-surface);
  font-weight: 600;
}

.error {
  margin: 0 0 1rem;
  font-size: 0.875rem;
  color: var(--color-error);
}
</style>
