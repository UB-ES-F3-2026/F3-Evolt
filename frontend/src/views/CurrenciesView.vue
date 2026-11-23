<script setup lang="ts">
import { onMounted } from 'vue'
import { Plus } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import CurrencyRow from '@/components/CurrencyRow.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import MoneyAmount from '@/components/MoneyAmount.vue'
import { useBalanceVisibility } from '@/viewmodels/useBalanceVisibility'
import { useCurrenciesViewModel } from '@/viewmodels/useCurrenciesViewModel'

const { rows, totalCents, isLoading, error, load, goToAdd, goChange, goToSubaccount } = useCurrenciesViewModel()
const { isHidden } = useBalanceVisibility()

// Every visit reloads, so a currency added on the picker shows up when coming back.
onMounted(load)
</script>

<template>
  <AppShell title="Divises" back>
    <LoadingIndicator v-if="isLoading" />

    <section v-else-if="error" class="card">
      <ErrorState :message="error" @retry="load" />
    </section>

    <template v-else>
      <section class="card">
        <div class="section-header">
          <h2 class="label">Divises</h2>
        </div>
        <ul class="rows">
          <CurrencyRow
            v-for="row in rows"
            :key="row.code"
            :code="row.code"
            :name="row.name"
            :symbol="row.symbol"
            :amount-text="row.amountText"
            :hidden="isHidden"
            selectable
            @select="goToSubaccount(row.id)"
          />
        </ul>
        <p class="total-line">
          Total ≈ <strong><MoneyAmount :cents="totalCents" :hidden="isHidden" /></strong>
        </p>
      </section>

      <div class="actions">
        <button type="button" class="create" @click="goToAdd">
          <Plus :size="18" />
          Afegir divisa
        </button>
        <!-- The /canviar route belongs to US-27; navigate by raw path without creating it. -->
        <button type="button" class="secondary" @click="goChange">Canviar</button>
      </div>
    </template>
  </AppShell>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.label {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.rows {
  list-style: none;
  padding: 0;
  margin: 0;
}

.total-line {
  border-top: 1px solid var(--color-border);
  padding-top: 0.75rem;
  margin: 0.75rem 0 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.create,
.secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.625rem 1rem;
  border-radius: var(--radius);
  font-weight: 600;
}

.create {
  border: none;
  background: var(--color-primary);
  color: var(--color-surface);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.secondary {
  border: 1px solid var(--color-primary);
  background: var(--color-surface);
  color: var(--color-primary);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}
</style>
