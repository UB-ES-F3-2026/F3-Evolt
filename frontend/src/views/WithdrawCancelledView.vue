<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted } from 'vue'
import AppShell from '@/components/AppShell.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import MoneyAmount from '@/components/MoneyAmount.vue'
import { useBalanceVisibility } from '@/viewmodels/useBalanceVisibility'
import { useWithdrawCancelledViewModel } from '@/viewmodels/useWithdrawCancelledViewModel'

const props = defineProps<{ potId: string }>()

const { pot, balance, isLoading, error, load, backToPot, returnAutomatically, stop } =
  useWithdrawCancelledViewModel(props.potId)
const { isHidden } = useBalanceVisibility()

// The same header as «Retirar de <nom>», where the person came from (US-19).
const title = computed(() => (pot.value === null ? 'Retirar' : `Retirar de ${pot.value.name}`))

onMounted(() => {
  void load()
  void returnAutomatically()
})
// Leaving through «← Inici» must not be followed by the automatic return.
onBeforeUnmount(stop)
</script>

<template>
  <AppShell :title="title" back>
    <LoadingIndicator v-if="isLoading" />

    <section v-else-if="error" class="card">
      <ErrorState :message="error" @retry="load" />
    </section>

    <!-- No green tick and no amount: nothing happened, and the amount must not be suggested again (REP-12). -->
    <section v-else-if="pot && balance !== null" class="card notice" role="status">
      <h2 class="notice-title">Retirada cancel·lada</h2>
      <p class="notice-text">No s'ha retirat res i cap dels dos saldos canvia.</p>
      <p class="notice-balances">
        Saldo disponible: <MoneyAmount :cents="balance" :hidden="isHidden" /> ·
        {{ pot.name }}: <MoneyAmount :cents="pot.balance" :hidden="isHidden" />
      </p>
      <button type="button" class="button" @click="backToPot">Tornar a la guardiola</button>
    </section>
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

.notice {
  align-items: center;
  gap: 0.75rem;
  padding: 2rem 1.25rem;
  text-align: center;
}

.notice-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.notice-text {
  margin: 0;
}

.notice-balances {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.button {
  align-self: stretch;
  margin-top: 0.5rem;
  padding: 0.75rem;
  border: none;
  border-radius: var(--radius);
  background: var(--color-primary);
  color: var(--color-surface);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}
</style>
