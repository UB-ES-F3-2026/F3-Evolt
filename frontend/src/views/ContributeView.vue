<script setup lang="ts">
import { onMounted, useTemplateRef, watch } from 'vue'
import { CircleCheck } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import MoneyAmount from '@/components/MoneyAmount.vue'
import { useBalanceVisibility } from '@/viewmodels/useBalanceVisibility'
import { useContributeViewModel } from '@/viewmodels/useContributeViewModel'

const props = defineProps<{ potId: string }>()

// The ViewModel checks the amount while it is typed, so `error` is already there
// before submitting and the button stays disabled until the amount is valid.
const {
  pot,
  balance,
  title,
  isLoading,
  loadError,
  amount,
  error,
  canSubmit,
  isSubmitting,
  confirmation,
  load,
  submit,
} = useContributeViewModel(props.potId)
const { isHidden } = useBalanceVisibility()

onMounted(load)

// This screen only asks for one number: open the keyboard as soon as the field exists.
const amountInput = useTemplateRef<HTMLInputElement>('amountInput')
watch(amountInput, (input) => input?.focus())
</script>

<template>
  <AppShell :title="title">
    <LoadingIndicator v-if="isLoading" />

    <section v-else-if="loadError" class="card">
      <ErrorState :message="loadError" @retry="load" />
    </section>

    <section v-else-if="confirmation" class="card success" role="status">
      <CircleCheck class="success-icon" :size="40" />
      <p class="success-text">{{ confirmation }}</p>
      <p v-if="pot && balance !== null" class="success-balances">
        Saldo disponible: <MoneyAmount :cents="balance" :hidden="isHidden" /> ·
        {{ pot.name }}: <MoneyAmount :cents="pot.balance" :hidden="isHidden" />
      </p>
    </section>

    <form v-else-if="pot && balance !== null" class="card" novalidate @submit.prevent="submit">
      <dl class="balances">
        <div class="balance-row">
          <dt>Saldo disponible</dt>
          <dd><MoneyAmount :cents="balance" :hidden="isHidden" /></dd>
        </div>
        <div class="balance-row">
          <dt>{{ pot.name }}</dt>
          <dd><MoneyAmount :cents="pot.balance" :hidden="isHidden" /></dd>
        </div>
      </dl>

      <label class="label" for="contribution-amount">Import</label>
      <div class="field" :class="{ invalid: error }">
        <input
          id="contribution-amount"
          ref="amountInput"
          v-model="amount"
          class="input"
          type="text"
          inputmode="decimal"
          autocomplete="off"
          placeholder="0,00"
          :disabled="isSubmitting"
          :aria-invalid="error !== null"
          :aria-describedby="error ? 'contribution-error' : undefined"
        />
        <span class="currency" aria-hidden="true">€</span>
      </div>
      <p v-if="error" id="contribution-error" class="error" role="alert">{{ error }}</p>

      <button type="submit" class="button" :disabled="!canSubmit">
        {{ isSubmitting ? 'Enviant…' : 'Confirmar' }}
      </button>
      <router-link :to="{ name: 'pot', params: { potId } }" class="cancel">Cancel·lar</router-link>
    </form>
  </AppShell>
</template>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1.25rem;
}

.balances {
  margin: 0 0 1.25rem;
}

.balance-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.375rem 0;
}

.balance-row dt {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--color-muted);
}

.balance-row dd {
  margin: 0;
  font-weight: 600;
}

.label {
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.field {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
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

/* An error replaces the field's bottom space, so the form does not jump. */
.error {
  margin: -0.75rem 0 1rem;
  font-size: 0.875rem;
  color: var(--color-error);
}

.button {
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

.cancel {
  margin-top: 0.75rem;
  font-size: 0.875rem;
  text-align: center;
}

.success {
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

.success-balances {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-muted);
}
</style>
