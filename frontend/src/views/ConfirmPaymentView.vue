<script setup lang="ts">
import { onMounted } from 'vue'
import { Check } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import MoneyAmount from '@/components/MoneyAmount.vue'
import UserRow from '@/components/UserRow.vue'
import { useBalanceVisibility } from '@/viewmodels/useBalanceVisibility'
import { useConfirmPaymentViewModel } from '@/viewmodels/useConfirmPaymentViewModel'

const props = defineProps<{ to?: string; amount?: string; concept?: string }>()

const {
  recipient,
  amount,
  concept,
  balance,
  isLoading,
  loadError,
  isRecipientMissing,
  isSubmitting,
  submitError,
  confirmation,
  canConfirm,
  load,
  confirm,
} = useConfirmPaymentViewModel({ to: props.to, amount: props.amount, concept: props.concept })
const { isHidden } = useBalanceVisibility()

onMounted(load)
</script>

<template>
  <AppShell title="Confirmar" back>
    <LoadingIndicator v-if="isLoading" />

    <section v-else-if="loadError" class="card">
      <ErrorState :message="loadError" :retryable="!isRecipientMissing" @retry="load" />
      <router-link v-if="isRecipientMissing" :to="{ name: 'payments' }" class="choose-again">
        Torna a triar el destinatari
      </router-link>
    </section>

    <!-- The success is a state of this screen, not a route, with no button (mockup US-14-exit-tic-verd). -->
    <section v-else-if="confirmation" class="card success" role="status">
      <span class="tick"><Check :size="40" /></span>
      <p class="success-text">{{ confirmation }}</p>
      <p v-if="balance !== null" class="success-balance">
        Saldo disponible: <MoneyAmount :cents="balance" :hidden="isHidden" />
      </p>
    </section>

    <template v-else-if="recipient">
      <section class="card">
        <dl class="summary">
          <div class="row">
            <dt>Destinatari</dt>
            <dd>
              <ul class="recipient"><UserRow :user="recipient" /></ul>
            </dd>
          </div>
          <div class="row">
            <dt>Import</dt>
            <dd class="amount"><MoneyAmount :cents="amount" /></dd>
          </div>
          <div v-if="concept" class="row">
            <dt>Concepte</dt>
            <dd class="strong">{{ concept }}</dd>
          </div>
          <div v-if="balance !== null" class="row">
            <dt>Saldo disponible</dt>
            <dd class="strong"><MoneyAmount :cents="balance" :hidden="isHidden" /></dd>
          </div>
        </dl>
      </section>

      <button type="button" class="button" :disabled="!canConfirm" @click="confirm">
        {{ isSubmitting ? 'Enviant…' : 'Confirmar enviament' }}
      </button>
      <p v-if="submitError" class="error" role="alert">{{ submitError }}</p>
      <router-link v-if="isRecipientMissing" :to="{ name: 'payments' }" class="choose-again">
        Torna a triar el destinatari
      </router-link>
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

.summary {
  margin: 0;
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 0;
}

.row + .row {
  border-top: 1px solid var(--color-border);
}

.row dt {
  color: var(--color-muted);
}

.row dd {
  margin: 0;
  min-width: 0;
  text-align: right;
}

.recipient {
  margin: 0;
  padding: 0;
}

.amount {
  font-size: 2rem;
  font-weight: 700;
}

.strong {
  font-weight: 600;
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

.error {
  margin: 0.5rem 0 0;
  text-align: center;
  font-size: 0.875rem;
  color: var(--color-error);
}

.choose-again {
  display: block;
  margin: 0.75rem auto 1rem;
  text-align: center;
  font-weight: 600;
}

.success {
  align-items: center;
  gap: 0.75rem;
  padding: 3rem 1.25rem;
  text-align: center;
}

.tick {
  display: grid;
  place-items: center;
  width: 4.5rem;
  height: 4.5rem;
  border-radius: 50%;
  background: var(--color-income);
  color: var(--color-surface);
}

.success-text {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
}

.success-balance {
  margin: 0;
  color: var(--color-muted);
}
</style>
