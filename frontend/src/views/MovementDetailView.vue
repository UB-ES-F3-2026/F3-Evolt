<script setup lang="ts">
import { onMounted } from 'vue'
import AppShell from '@/components/AppShell.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import MoneyAmount from '@/components/MoneyAmount.vue'
import { useBalanceVisibility } from '@/viewmodels/useBalanceVisibility'
import { useMovementDetailViewModel } from '@/viewmodels/useMovementDetailViewModel'

const props = defineProps<{ movementId: string }>()

const { movement, rows, isIncome, isLoading, error, load } = useMovementDetailViewModel(props.movementId)
const { isHidden } = useBalanceVisibility()

onMounted(load)
</script>

<template>
  <AppShell title="Detall del moviment">
    <router-link :to="{ name: 'movements' }" class="back-link">← Moviments</router-link>

    <LoadingIndicator v-if="isLoading" />

    <section v-else-if="error" class="card">
      <ErrorState :message="error" @retry="load" />
    </section>

    <template v-else-if="movement">
      <section class="card summary">
        <MoneyAmount
          class="amount"
          :class="isIncome ? 'income' : 'expense'"
          :cents="movement.amount"
          :sign="isIncome ? 'positive' : 'negative'"
          :hidden="isHidden"
        />
        <p class="concept">{{ movement.concept }}</p>
      </section>

      <section class="card">
        <dl class="rows">
          <div v-for="row in rows" :key="row.label" class="row">
            <dt>{{ row.label }}</dt>
            <dd>{{ row.value }}</dd>
          </div>
        </dl>
      </section>

      <router-link :to="{ name: 'report-movement', params: { movementId } }" class="report-link">
        Reportar un problema
      </router-link>
    </template>
  </AppShell>
</template>

<style scoped>
.back-link {
  display: inline-block;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
}

.summary {
  text-align: center;
}

.amount {
  display: block;
  font-size: 2rem;
  font-weight: 700;
}

.income {
  color: var(--color-income);
}

.expense {
  color: var(--color-expense);
}

.concept {
  margin: 0.25rem 0 0;
  color: var(--color-muted);
  overflow-wrap: anywhere;
}

.rows {
  margin: 0;
}

.row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.5rem 0;
}

.row dt {
  flex: none;
  color: var(--color-muted);
}

.row dd {
  margin: 0;
  font-weight: 600;
  text-align: right;
  overflow-wrap: anywhere;
}

.report-link {
  display: block;
  padding: 0.5rem;
  font-size: 0.875rem;
  text-align: center;
}
</style>
