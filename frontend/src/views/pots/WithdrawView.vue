<script setup lang="ts">
import { onMounted, useTemplateRef, watch } from 'vue'
import { CircleCheck } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import MoneyAmount from '@/components/MoneyAmount.vue'
import { useBalanceVisibility } from '@/viewmodels/useBalanceVisibility'
import { useWithdrawViewModel } from '@/viewmodels/pots/useWithdrawViewModel'

const props = defineProps<{ potId: string }>()

// The ViewModel checks the amount while it is typed, so `amountError` is already there
// before submitting and the button stays disabled until the amount is valid.
// A server answer (`submitError`) goes under the button and leaves the field as it is (US-19).
const {
  pot,
  balance,
  title,
  isLoading,
  loadError,
  amount,
  amountError,
  submitError,
  canSubmit,
  isSubmitting,
  confirmation,
  load,
  submit,
} = useWithdrawViewModel(props.potId)
const { isHidden } = useBalanceVisibility()

onMounted(load)

// This screen only asks for one number: open the keyboard as soon as the field exists.
const amountInput = useTemplateRef<HTMLInputElement>('amountInput')
watch(amountInput, (input) => input?.focus())
</script>

<template>
  <AppShell :title="title" back>
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

    <form v-else-if="pot" class="card" novalidate @submit.prevent="submit">
      <dl class="balances">
        <div class="balance-row">
          <dt>Saldo de la guardiola</dt>
          <dd><MoneyAmount :cents="pot.balance" :hidden="isHidden" /></dd>
        </div>
      </dl>

      <label class="label" for="withdrawal-amount">Import</label>
      <div class="field" :class="{ invalid: amountError }">
        <input
          id="withdrawal-amount"
          ref="amountInput"
          v-model="amount"
          class="input"
          type="text"
          inputmode="decimal"
          autocomplete="off"
          placeholder="0,00"
          :disabled="isSubmitting"
          :aria-invalid="amountError !== null"
          :aria-describedby="amountError ? 'withdrawal-amount-error' : undefined"
        />
        <span class="currency" aria-hidden="true">€</span>
      </div>
      <p v-if="amountError" id="withdrawal-amount-error" class="error" role="alert">{{ amountError }}</p>

      <button type="submit" class="button" :disabled="!canSubmit">
        {{ isSubmitting ? 'Enviant…' : 'Confirmar' }}
      </button>
      <p v-if="submitError" class="error submit-error" role="alert">{{ submitError }}</p>
      <!-- Nothing is sent: it only opens the «Retirada cancel·lada» notice (REP-12). Replace, so going
           back from that notice does not reopen the form with the amount still typed. -->
      <router-link :to="{ name: 'withdraw-cancelled', params: { potId } }" replace class="cancel">
        Cancel·lar
      </router-link>
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

.submit-error {
  margin: 0.5rem 0 0;
  text-align: center;
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
