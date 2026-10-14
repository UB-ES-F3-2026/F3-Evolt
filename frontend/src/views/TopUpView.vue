<script setup>
import AppShell from '@/components/AppShell.vue'
import { formatCents } from '@/models/money'
import { useTopUpViewModel } from '@/viewmodels/useTopUpViewModel'

const { amount, isSubmitting, error, successMessage, newBalance, canSubmit, submit } =
  useTopUpViewModel()
</script>

<template>
  <AppShell title="Recàrrega" back>
    <section class="card">
      <form @submit.prevent="submit">
        <label class="label" for="amount">Import (€)</label>
        <input
          id="amount"
          v-model="amount"
          class="input"
          type="text"
          inputmode="decimal"
          placeholder="0,00"
          :disabled="isSubmitting"
        />
        <button class="button" type="submit" :disabled="!canSubmit">
          {{ isSubmitting ? 'Recarregant…' : 'Recarregar' }}
        </button>
      </form>

      <p v-if="error" class="feedback error" role="alert">{{ error }}</p>
      <p v-if="successMessage" class="feedback success">
        {{ successMessage }} · Saldo actual: {{ formatCents(newBalance ?? 0) }}
      </p>
    </section>
  </AppShell>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
}

.label {
  display: block;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.input {
  width: 100%;
  margin: 0.5rem 0;
  padding: 0.625rem 0.75rem;
  border: 1px solid #e6ebf4;
  border-radius: var(--radius);
  font-size: 1rem;
}

.button {
  width: 100%;
  padding: 0.625rem;
  border: none;
  border-radius: var(--radius);
  background: var(--color-primary);
  color: #ffffff;
  font-size: 1rem;
  cursor: pointer;
}

.button:disabled {
  opacity: 0.6;
  cursor: default;
}

.feedback {
  margin: 0.75rem 0 0;
  font-size: 0.875rem;
}

.error {
  color: var(--color-expense);
}

.success {
  color: var(--color-income);
}
</style>
