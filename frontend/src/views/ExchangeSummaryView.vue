<script setup lang="ts">
import { onMounted } from 'vue'
import { CircleCheck } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import { useExchangeSummaryViewModel } from '@/viewmodels/useExchangeSummaryViewModel'

const {
  draft,
  isLoading,
  loadError,
  originLine,
  rateLabel,
  rateValue,
  commissionText,
  chargeNote,
  exactLine,
  insufficient,
  insufficientMessage,
  balanceNotLoaded,
  isConfirming,
  confirmed,
  submitError,
  newBalanceRows,
  start,
  confirm,
} = useExchangeSummaryViewModel()

// «Canviar» only navigated: this screen fetches the origin balance before offering to send.
onMounted(start)
</script>

<template>
  <AppShell title="Resum del canvi" back>
    <section v-if="confirmed" class="card success" role="status">
      <CircleCheck class="success-icon" :size="40" />
      <p class="success-text">Canvi fet</p>
      <p class="returning">Tornant a Inici…</p>
      <ul class="balances">
        <li v-for="row in newBalanceRows" :key="row.label" class="balance-row">
          <span class="balance-label">{{ row.label }}</span>
          <span class="balance-value">{{ row.value }}</span>
        </li>
      </ul>
    </section>

    <LoadingIndicator v-else-if="draft !== null && isLoading" />

    <section v-else-if="draft !== null && loadError" class="card">
      <ErrorState :message="loadError" retryable @retry="start" />
    </section>

    <template v-else-if="draft !== null">
      <section class="card">
        <ol class="summary" role="list">
          <li class="origin">{{ originLine }}</li>
          <li class="row">
            <span class="row-label">{{ rateLabel }}</span>
            <span class="row-value">{{ rateValue }}</span>
          </li>
          <li class="row commission-row">
            <span class="row-value commission">{{ commissionText }}</span>
          </li>
          <li class="note">{{ chargeNote }}</li>
          <li class="divider" aria-hidden="true"></li>
          <li class="total">{{ exactLine }}</li>
        </ol>
      </section>

      <button
        type="button"
        class="button"
        :disabled="isConfirming || insufficient || balanceNotLoaded"
        @click="confirm()"
      >
        Confirmar canvi
      </button>

      <p v-if="insufficient" class="error" role="alert">{{ insufficientMessage }}</p>
      <p v-if="submitError" class="error" role="alert">{{ submitError }}</p>
    </template>
  </AppShell>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1.25rem;
  margin-bottom: 1rem;
}

.summary {
  margin: 0;
  padding: 0;
  list-style: none;
}

.origin {
  margin-bottom: 1rem;
  font-size: 1.25rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.375rem 0;
}

.row-label {
  font-size: 0.9375rem;
}

.row-value {
  font-size: 0.9375rem;
  font-variant-numeric: tabular-nums;
}

.commission-row {
  justify-content: flex-end;
}

.commission {
  color: var(--color-expense);
}

.note {
  margin: 0.375rem 0 0;
  font-size: 0.9375rem;
  line-height: 1.4;
}

.divider {
  height: 1px;
  margin: 0.75rem 0;
  background: var(--color-border);
}

.total {
  font-size: 1.5rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
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
  margin: 0.75rem 0 0;
  color: var(--color-expense);
  font-size: 0.9375rem;
  font-weight: 600;
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
  font-size: 1.375rem;
  font-weight: 600;
}

.returning {
  margin: 0;
  color: var(--color-muted);
  font-size: 0.875rem;
}

.balances {
  width: 100%;
  margin: 0.5rem 0 0;
  padding: 0;
  list-style: none;
}

.balance-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.3125rem 0;
  font-size: 1rem;
  font-variant-numeric: tabular-nums;
}

.balance-value {
  font-weight: 600;
}
</style>
