<script setup lang="ts">
import { onMounted, useTemplateRef } from 'vue'
import { CircleCheck } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import MoneyAmount from '@/components/MoneyAmount.vue'
import { useTopUpViewModel } from '@/viewmodels/useTopUpViewModel'

// The ViewModel checks the amount while it is typed, so `error` is already there
// before submitting and the button stays disabled until the amount is valid.
const { amount, error, canSubmit, isSubmitting, confirmation, maxAmountCents, submit } =
  useTopUpViewModel()

// This screen only asks for one number: open the keyboard straight away.
const amountInput = useTemplateRef<HTMLInputElement>('amountInput')
onMounted(() => amountInput.value?.focus())
</script>

<template>
  <AppShell title="Afegir diners" back>
    <section v-if="confirmation" class="card success" role="status">
      <CircleCheck class="success-icon" :size="40" />
      <p class="success-text">{{ confirmation }}</p>
    </section>

    <form v-else class="card" novalidate @submit.prevent="submit">
      <label class="label" for="amount">Import</label>
      <div class="field" :class="{ invalid: error }">
        <input
          id="amount"
          ref="amountInput"
          v-model="amount"
          class="input"
          type="text"
          inputmode="decimal"
          autocomplete="off"
          placeholder="0,00"
          :disabled="isSubmitting"
          :aria-invalid="error !== null"
          :aria-describedby="error ? 'amount-error' : 'amount-help'"
        />
        <span class="currency" aria-hidden="true">€</span>
      </div>

      <p v-if="error" id="amount-error" class="error" role="alert">{{ error }}</p>
      <p v-else id="amount-help" class="help">
        Màxim <MoneyAmount :cents="maxAmountCents" /> per recàrrega
      </p>

      <button type="submit" class="button" :disabled="!canSubmit">
        {{ isSubmitting ? 'Enviant…' : 'Confirmar' }}
      </button>
      <p class="note">Recàrrega de prova: no cal cap targeta i s'aprova a l'instant.</p>
    </form>
  </AppShell>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1.25rem;
}

.label {
  display: block;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.field {
  display: flex;
  align-items: center;
  margin: 0.5rem 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
}

.field:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px var(--color-primary);
}

.field.invalid {
  border-color: var(--color-error);
}

.field.invalid:focus-within {
  box-shadow: 0 0 0 1px var(--color-error);
}

.input {
  flex: 1;
  min-width: 0;
  padding: 0.75rem;
  border: none;
  border-radius: var(--radius);
  background: transparent;
  color: var(--color-text);
  font: inherit;
  font-size: 1.5rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.input:focus {
  outline: none;
}

.currency {
  padding-right: 0.75rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-muted);
}

.help,
.error {
  margin: 0 0 1rem;
  font-size: 0.875rem;
}

.help {
  color: var(--color-muted);
}

.error {
  color: var(--color-error);
}

.button {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: var(--radius);
  background: var(--color-primary);
  color: var(--color-surface);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.note {
  margin: 0.75rem 0 0;
  color: var(--color-muted);
  font-size: 0.8125rem;
  text-align: center;
}

.success {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem 1.25rem;
  text-align: center;
}

.success-icon {
  color: var(--color-income);
}

.success-text {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
}
</style>
