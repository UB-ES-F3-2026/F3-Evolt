<script setup lang="ts">
import { onMounted, watch } from 'vue'
import AppShell from '@/components/AppShell.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import UserRow from '@/components/UserRow.vue'
import { useSendPaymentViewModel } from '@/viewmodels/payments/useSendPaymentViewModel'

const props = defineProps<{ to?: string }>()

const {
  recipient,
  isLoading,
  error,
  isRecipientMissing,
  amountText,
  concept,
  maxConceptLength,
  amountError,
  canContinue,
  load,
  pressKey,
  continueToConfirm,
} = useSendPaymentViewModel(() => props.to)

// The keypad of the mockup (US-14-import-teclat): digits, the decimal comma and backspace.
const KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', ',', '0', '⌫']

// The recipient, the balance and the limit are asked on every visit, so a reload keeps them.
onMounted(load)
// Another `?to=` while this screen is open (the same view is reused): ask the new recipient (#212).
watch(
  () => props.to,
  () => load(),
)
</script>

<template>
  <AppShell title="Enviar" back>
    <LoadingIndicator v-if="isLoading" />

    <section v-else-if="error" class="card">
      <ErrorState :message="error" :retryable="!isRecipientMissing" @retry="load" />
      <router-link v-if="isRecipientMissing" :to="{ name: 'payments' }" class="choose-again">
        Torna a triar el destinatari
      </router-link>
    </section>

    <template v-else-if="recipient">
      <section class="card">
        <ul class="recipient">
          <UserRow :user="recipient" />
        </ul>
      </section>

      <section class="card amount-card">
        <h2 class="label">Import</h2>
        <p class="amount" aria-live="polite">{{ amountText }}</p>
        <p v-if="amountError" class="error" role="alert">{{ amountError }}</p>
      </section>

      <div class="keypad">
        <button
          v-for="key in KEYS"
          :key="key"
          type="button"
          class="key"
          :aria-label="key === '⌫' ? 'Esborrar' : undefined"
          @click="pressKey(key)"
        >
          {{ key }}
        </button>
      </div>

      <label class="label concept-label" for="payment-concept">Concepte</label>
      <input
        id="payment-concept"
        v-model="concept"
        class="concept"
        type="text"
        autocomplete="off"
        :maxlength="maxConceptLength"
      />

      <button type="button" class="button" :disabled="!canContinue" @click="continueToConfirm">Continuar</button>
    </template>
  </AppShell>
</template>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  margin-bottom: 0.75rem;
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 0.5rem 1.25rem;
}

.recipient {
  margin: 0;
  padding: 0;
}

.amount-card {
  padding: 1rem 1.25rem;
}

.label {
  margin: 0 0 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-muted);
}

.amount {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.error {
  margin: 0.5rem 0 0;
  font-weight: 600;
  color: var(--color-error);
}

.keypad {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.key {
  padding: 0.875rem 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
  font-size: 1.25rem;
  font-weight: 700;
  cursor: pointer;
}

.concept-label {
  display: block;
}

.concept {
  display: block;
  box-sizing: border-box;
  width: 100%;
  margin-bottom: 1rem;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
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
  background: var(--color-border);
  color: var(--color-muted);
  cursor: not-allowed;
}

.choose-again {
  margin: 0 auto 1rem;
  font-weight: 600;
}
</style>
