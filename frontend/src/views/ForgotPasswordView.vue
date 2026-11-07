<script setup lang="ts">
import AppShell from '@/components/AppShell.vue'
import FormField from '@/components/FormField.vue'
import PrimaryButton from '@/components/PrimaryButton.vue'
import { useForgotPasswordViewModel } from '@/viewmodels/useForgotPasswordViewModel'

const { identifier, error, notice, canSubmit, isSubmitting, submit } = useForgotPasswordViewModel()
</script>

<template>
  <AppShell title="He oblidat la contrasenya">
    <form class="card" novalidate @submit.prevent="submit">
      <FormField
        id="identifier"
        v-model="identifier"
        label="Email o telèfon"
        autocomplete="username"
        :disabled="isSubmitting"
      />

      <p v-if="error" class="message error" role="alert">{{ error }}</p>
      <p v-else-if="notice" class="message" role="status">{{ notice }}</p>

      <PrimaryButton :disabled="!canSubmit">
        {{ isSubmitting ? 'Enviant…' : 'Enviar' }}
      </PrimaryButton>

      <p class="links">
        <router-link :to="{ name: 'login' }">Inicia sessió</router-link>
      </p>
    </form>
  </AppShell>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1.25rem;
}

.message {
  margin: 0 0 1rem;
  font-size: 0.875rem;
}

.error {
  color: var(--color-error);
}

.links {
  margin: 1rem 0 0;
  font-size: 0.875rem;
  text-align: center;
}
</style>
