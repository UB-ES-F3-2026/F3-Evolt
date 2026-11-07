<script setup lang="ts">
import AppShell from '@/components/AppShell.vue'
import FormField from '@/components/FormField.vue'
import PrimaryButton from '@/components/PrimaryButton.vue'
import { useLoginViewModel } from '@/viewmodels/useLoginViewModel'

const { identifier, password, error, notice, canSubmit, isSubmitting, submit } = useLoginViewModel()
</script>

<template>
  <AppShell title="Inicia sessió">
    <form class="card" novalidate @submit.prevent="submit">
      <p v-if="notice" class="notice" role="status">{{ notice }}</p>

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
        autocomplete="current-password"
        :disabled="isSubmitting"
      />

      <p v-if="error" class="error" role="alert">{{ error }}</p>

      <PrimaryButton :disabled="!canSubmit">
        {{ isSubmitting ? 'Entrant…' : 'Entrar' }}
      </PrimaryButton>

      <p class="links">
        <router-link to="/forgot-password">He oblidat la contrasenya</router-link>
        <router-link :to="{ name: 'register' }">Crear compte</router-link>
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

.notice {
  margin: 0 0 1rem;
  padding: 0.75rem;
  border-radius: var(--radius);
  background: var(--color-bg);
  font-size: 0.875rem;
}

.error {
  margin: 0 0 1rem;
  font-size: 0.875rem;
  color: var(--color-error);
}

.links {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin: 1rem 0 0;
  font-size: 0.875rem;
}
</style>
